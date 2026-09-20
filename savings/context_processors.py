from .models import AppSetting

def app_settings(request):
    try:
        settings = AppSetting.get_solo()
    except Exception:
        settings = None
    return {
        'app_settings': settings
    }
