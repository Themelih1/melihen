from django.conf import settings

def global_settings(request):
    return {
        'debug': settings.DEBUG,
    }
