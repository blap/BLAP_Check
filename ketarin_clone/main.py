# main.py

import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import NumericProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from packaging.version import Version, InvalidVersion
import config_manager
from database import manager as db_manager
from engine import extension_manager
import json
import threading
from kivy.uix.progressbar import ProgressBar
from kivy.animation import Animation
from kivy.clock import mainthread
import downloader

kivy.require('2.1.0')

class ApplicationItem(BoxLayout):
    app_id = NumericProperty()

class AddEditPopup(ModalView):
    app_id = NumericProperty(None)

    def on_open(self):
        self.ids.extension_spinner.values = list(extension_manager.extensions.keys())

    def open_for_edit(self, app_item):
        self.app_id = app_item['id']
        self.title = "Editar Aplicação"
        self.ids.app_name_input.text = app_item.get('name', '')
        self.ids.local_version_input.text = app_item.get('local_version', '')
        self.ids.extension_spinner.text = app_item.get('extension_id', 'Selecione')
        self.ids.extension_config_input.text = app_item.get('extension_config', '')
        self.open()

    def open_for_add(self):
        self.app_id = None
        self.title = "Adicionar Nova Aplicação"
        self.ids.app_name_input.text = ""
        self.ids.local_version_input.text = ""
        self.ids.extension_spinner.text = "Selecione um método"
        self.ids.extension_config_input.text = ""
        self.open()

    def save(self):
        app_data = {
            'name': self.ids.app_name_input.text,
            'local_version': self.ids.local_version_input.text,
            'extension_id': self.ids.extension_spinner.text,
            'extension_config': self.ids.extension_config_input.text
        }

        if not all(app_data.values()) or app_data['extension_id'] == 'Selecione um método':
            self.show_notification("Erro: Todos os campos são obrigatórios.", is_error=True)
            return

        if app_data['extension_id'] == 'regex_pattern':
            try:
                json.loads(app_data['extension_config'])
            except json.JSONDecodeError:
                self.show_notification("Erro: Configuração para Regex deve ser um JSON válido.", is_error=True)
                return

        if self.app_id:
            db_manager.update_application(self.app_id, app_data)
        else:
            db_manager.add_application(app_data)

        App.get_running_app().refresh_app_list()
        self.dismiss()

class DownloadPopup(ModalView):
    pass

class MainScreen(Screen):
    pass

class SettingsScreen(Screen):
    pass

class KetarinCloneApp(App):
    selected_app_widget = None
    selected_app_data = None

    def build(self):
        self.config = config_manager.load_config()
        db_manager.initialize_database()
        return ScreenManager()

    def on_start(self):
        self.apply_theme()

    def apply_theme(self):
        print(f"Tema '{self.config['theme']}' aplicado.")
        self.refresh_app_list()

    def change_theme(self, theme_name):
        self.config['theme'] = theme_name
        config_manager.save_config(self.config)
        self.apply_theme()

    def refresh_app_list(self):
        self.selected_app_widget = None
        self.selected_app_data = None
        apps = db_manager.get_all_applications()
        rv_data = []
        for app in apps:
            local_v_str = app.get('local_version')
            latest_v_str = app.get('latest_version')
            status_color = (0.17, 0.2, 0.24, 1) if self.config.get('theme') != 'Claro' else (0.9, 0.9, 0.9, 1)
            status = "N/A"
            if local_v_str and latest_v_str:
                try:
                    local_v, latest_v = Version(local_v_str), Version(latest_v_str)
                    if latest_v > local_v:
                        status_color, status = ((0.8, 0.2, 0.2, 0.5), f"{local_v_str} -> {latest_v_str}")
                    else:
                        status_color, status = ((0.2, 0.8, 0.2, 0.4), f"{local_v_str} (Atualizado)")
                except InvalidVersion:
                    status = "Versão inválida"
            elif latest_v_str: status = f"Última: {latest_v_str}"
            elif local_v_str: status = f"Local: {local_v_str}"
            app_data_dict = app.copy()
            app_data_dict.update({
                'ids.app_name_label.text': app['name'],
                'ids.app_version_label.text': status,
                'status_color': status_color
            })
            rv_data.append(app_data_dict)
        self.root.get_screen('main').ids.app_list_rv.data = rv_data

    def set_selected_app(self, app_widget):
        self.selected_app_widget = app_widget
        for item in self.root.get_screen('main').ids.app_list_rv.data:
            if item['app_id'] == app_widget.app_id:
                self.selected_app_data = item
                break

    def open_add_edit_popup(self, app_item=None):
        popup = AddEditPopup()
        if app_item:
            popup.open_for_edit(app_item)
        else:
            popup.open_for_add()

    def open_edit_popup_for_selected(self):
        if not self.selected_app_data:
            return
        self.open_add_edit_popup(self.selected_app_data)

    def delete_selected_app(self):
        if not self.selected_app_data:
            return
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        app_name = self.selected_app_data.get('name', 'N/A')
        content.add_widget(Label(text=f"Tem a certeza que quer remover '{app_name}'?"))
        btn_layout = BoxLayout(spacing=10, size_hint_y=None, height=40)
        popup = Popup(title='Confirmar Remoção', content=content, size_hint=(0.8, 0.5))
        def confirm_delete(instance):
            db_manager.delete_application(self.selected_app_data['app_id'])
            self.refresh_app_list()
            popup.dismiss()
        yes_btn = Button(text='Sim', on_release=confirm_delete)
        no_btn = Button(text='Não', on_release=popup.dismiss)
        btn_layout.add_widget(yes_btn)
        btn_layout.add_widget(no_btn)
        content.add_widget(btn_layout)
        popup.open()

    def start_download(self, app_widget):
        app_data = next((item for item in self.root.get_screen('main').ids.app_list_rv.data if item['app_id'] == app_widget.app_id), None)
        if not app_data:
            self.show_notification("Não foi possível encontrar os dados da aplicação.", is_error=True)
            return
        latest_version = app_data.get('latest_version')
        if not latest_version:
            self.show_notification("Não foi possível encontrar a versão mais recente para descarregar.", is_error=True)
            return
        download_url = f"https://kivy.org/downloads/1.11.1/Kivy-1.11.1-py3.7-win32-x64.zip" # Placeholder
        destination_path = f"{app_data['name']}-{latest_version}.zip"
        self.download_popup = DownloadPopup()
        self.download_popup.ids.file_name_label.text = f"A descarregar: {destination_path}"
        self.download_popup.open()
        @mainthread
        def update_progress(progress):
            self.download_popup.ids.progress_bar.value = progress
            self.download_popup.ids.progress_label.text = f"{progress:.1f}%"
        @mainthread
        def on_completion(success, message):
            self.download_popup.dismiss()
            self.show_notification(message, is_error=not success)
        thread = threading.Thread(target=downloader.download_file, args=(download_url, destination_path, update_progress, on_completion))
        thread.start()

    def show_notification(self, message, is_error=False):
        color = (0.9, 0.2, 0.2, 1) if is_error else (0.2, 0.9, 0.2, 1)
        notification = Label(text=message, size_hint=(None, None), size=('300dp', '50dp'), pos_hint={'center_x': 0.5, 'y': 0.05}, color=(1,1,1,1), padding=('10dp', '10dp'))
        with notification.canvas.before:
            kivy.graphics.Color(*color)
            kivy.graphics.Rectangle(size=notification.size, pos=notification.pos)
        anim = Animation(opacity=1, duration=0.5) + Animation(duration=3) + Animation(opacity=0, duration=0.5)
        anim.bind(on_complete=lambda *args: self.root.remove_widget(notification))
        self.root.add_widget(notification)
        anim.start(notification)

    def show_error_popup(self, message):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message, text_size=(self.root.width * 0.75, None)))
        ok_btn = Button(text='OK', size_hint_y=None, height=40)
        content.add_widget(ok_btn)
        popup = Popup(title='Ocorreu um Erro', content=content, size_hint=(0.8, 0.5))
        ok_btn.bind(on_release=popup.dismiss)
        popup.open()

    def check_selected_app(self):
        if not self.selected_app_data:
            return
        self.check_single_app(self.selected_app_data['app_id'])

    def check_single_app(self, app_id):
        app_data = next((item for item in self.root.get_screen('main').ids.app_list_rv.data if item['app_id'] == app_id), None)
        if not app_data or not app_data.get('extension_id') or not app_data.get('extension_config'):
            self.show_error_popup("Erro: Configuração de verificação em falta.")
            return
        extension_name, config_str = app_data['extension_id'], app_data['extension_config']
        try:
            config = json.loads(config_str) if extension_name == 'regex_pattern' else {'repo': config_str}
        except json.JSONDecodeError:
            self.show_error_popup(f"Erro: Configuração para '{app_data['name']}' não é um JSON válido.")
            return
        result = extension_manager.run_check(extension_name, config)
        if result['status'] == 'success':
            latest_version = result['version']
            self.show_notification(f"Versão encontrada para '{app_data['name']}': {latest_version}")
            db_manager.update_app_latest_version(app_id, latest_version)
        else:
            self.show_error_popup(f"Erro ao verificar '{app_data['name']}':\n{result['message']}")
        self.refresh_app_list()

    def check_all_apps(self):
        for app_data in self.root.get_screen('main').ids.app_list_rv.data:
            self.check_single_app(app_data['app_id'])

if __name__ == '__main__':
    KetarinCloneApp().run()
