from django.contrib.staticfiles.finders import AppDirectoriesFinder
from django.contrib.staticfiles.storage import AppStaticStorage


class LegacyAppMediaStorage(AppStaticStorage):
    """
    A legacy app storage backend that provides a migration path for the
    default directory name in previous versions of staticfiles, "media".
    """
    source_dir = 'media'


class LegacyAppDirectoriesFinder(AppDirectoriesFinder):
    """
    A legacy file finder that provides a migration path for the
    default directory name in previous versions of staticfiles, "media".
    """
    storage_class = LegacyAppMediaStorage
