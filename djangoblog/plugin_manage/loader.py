import os
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def load_plugins():
    """
    Dynamically loads and initializes plugins from the 'plugins' directory.
    This function is intended to be called when the Django app registry is ready.
    """
    for plugin_name in settings.ACTIVE_PLUGINS:
        plugin_path = os.path.join(settings.PLUGINS_DIR, plugin_name)
        if os.path.isdir(plugin_path) and os.path.exists(os.path.join(plugin_path, 'plugin.py')):
            try:
                __import__(f'plugins.{plugin_name}.plugin')
                logger.info(f"Successfully loaded plugin: {plugin_name}")
            except ImportError as e:
                logger.error(f"Failed to import plugin: {plugin_name}", exc_info=e) 