from django.conf import settings


def archive_mode(request):
    return {
        'is_archive': getattr(settings, 'ARCHIVE', False)
    }


def test_mode(request):
    return {
        'is_test': getattr(settings, 'TEST', False)
    }

