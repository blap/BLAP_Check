# main.py

import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import NumericProperty
from database import manager as db_manager
from engine import extension_manager # Importa a nossa instância do gestor
import json

kivy.require('2.1.0')

class ApplicationItem(BoxLayout):
    app_id = NumericProperty()

class AddEditPopup(ModalView):
    app_id = NumericProperty(None)

    def on_open(self):
        """ Popula o Spinner com as extensões carregadas. """
        self.ids.extension_spinner.values = list(extension_manager.extensions.keys())

    def open_for_edit(self, app_item):
        self.app_id = app_item['id']
        self.title = "Editar Aplicação"
        self.ids.app_name_input.text = app_item.get('name', '')
        self.ids.extension_spinner.text = app_item.get('extension_id', 'Selecione')
        self.ids.extension_config_input.text = app_item.get('extension_config', '')
        self.open()

    def open_for_add(self):
        self.app_id = None
        self.title = "Adicionar Nova Aplicação"
        self.ids.app_name_input.text = ""
        self.ids.extension_spinner.text = "Selecione um método"
        self.ids.extension_config_input.text = ""
        self.open()

    def save(self):
        app_data = {
            'name': self.ids.app_name_input.text,
            'extension_id': self.ids.extension_spinner.text,
            'extension_config': self.ids.extension_config_input.text
        }

        if not all(app_data.values()) or app_data['extension_id'] == 'Selecione um método':
            print("Erro: Todos os campos são obrigatórios.")
            return

        # Para o regex, a config é um JSON. Para outros, é um texto simples.
        # Isto é uma simplificação, poderia ser melhorado no futuro.
        if app_data['extension_id'] == 'regex_pattern':
            try:
                # Exemplo para regex: {"url": "http://site.com", "pattern": "regex"}
                json.loads(app_data['extension_config'])
            except json.JSONDecodeError:
                print("Erro: Configuração para Regex deve ser um JSON válido.")
                return

        if self.app_id:
            db_manager.update_application(self.app_id, app_data)
        else:
            db_manager.add_application(app_data)

        App.get_running_app().refresh_app_list()
        self.dismiss()

class MainScreen(BoxLayout):
    pass

class KetarinCloneApp(App):
    selected_app_widget = None
    selected_app_data = None

    def build(self):
        db_manager.initialize_database()
        return MainScreen()

    def on_start(self):
        self.refresh_app_list()

    def refresh_app_list(self):
        self.selected_app_widget = None
        self.selected_app_data = None
        apps = db_manager.get_all_applications()
        self.root.ids.app_list_rv.data = [
            {
                'app_id': app['id'],
                'name': app['name'],
                'extension_id': app.get('extension_id'),
                'extension_config': app.get('extension_config'),
                'ids.app_name_label.text': app['name'],
                'ids.app_version_label.text': f"Versão: {app.get('latest_version') or app.get('local_version', 'N/A')}"
            } for app in apps
        ]

    def set_selected_app(self, app_widget):
        self.selected_app_widget = app_widget
        for item in self.root.ids.app_list_rv.data:
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
            print("Nenhuma aplicação selecionada para editar.")
            return
        self.open_add_edit_popup(self.selected_app_data)

    def delete_selected_app(self):
        if not self.selected_app_data:
            print("Nenhuma aplicação selecionada para remover.")
            return

        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        app_name = self.selected_app_data.get('name', 'N/A')
        content.add_widget(Label(text=f"Tem a certeza que quer remover '{app_name}'?"))
        btn_layout = BoxLayout(spacing=10, size_hint_y=None, height=40)

        popup = Popup(title='Confirmar Remoção', content=content, size_hint=(0.6, 0.4))

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

    def check_selected_app(self):
        if not self.selected_app_data:
            print("Nenhuma aplicação selecionada para verificar.")
            return
        self.check_single_app(self.selected_app_data['app_id'])

    def check_single_app(self, app_id):
        app_data = next((item for item in self.root.ids.app_list_rv.data if item['app_id'] == app_id), None)

        if not app_data or not app_data.get('extension_id') or not app_data.get('extension_config'):
            print("Erro: Configuração de verificação em falta.")
            return

        extension_name = app_data['extension_id']
        config_str = app_data['extension_config']

        try:
            if extension_name == 'regex_pattern':
                config = json.loads(config_str)
            else:
                config = {'repo': config_str}
        except json.JSONDecodeError:
            print(f"Erro: Configuração para '{app_data['name']}' não é um JSON válido.")
            return

        result = extension_manager.run_check(extension_name, config)

        if result['status'] == 'success':
            latest_version = result['version']
            print(f"Versão encontrada para '{app_data['name']}': {latest_version}")
            db_manager.update_app_latest_version(app_id, latest_version)
        else:
            print(f"Erro ao verificar '{app_data['name']}': {result['message']}")

        self.refresh_app_list()

    def check_all_apps(self):
        print("A verificar todas as aplicações...")
        for app_data in self.root.ids.app_list_rv.data:
            self.check_single_app(app_data['app_id'])


if __name__ == '__main__':
    KetarinCloneApp().run()
