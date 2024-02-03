from django.apps import AppConfig


class AdminPanelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Admin_Panel'
    
    def ready(self):
        import Admin_Panel.signals


from django.apps import AppConfig

    