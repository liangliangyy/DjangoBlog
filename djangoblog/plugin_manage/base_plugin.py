import logging

logger = logging.getLogger(__name__)


class BasePlugin:
    # 插件元数据
    PLUGIN_NAME = None
    PLUGIN_DESCRIPTION = None
    PLUGIN_VERSION = None

    def __init__(self):
        if not all([self.PLUGIN_NAME, self.PLUGIN_DESCRIPTION, self.PLUGIN_VERSION]):
            raise ValueError("Plugin metadata (PLUGIN_NAME, PLUGIN_DESCRIPTION, PLUGIN_VERSION) must be defined.")
        self.init_plugin()
        self.register_hooks()

    def init_plugin(self):
        """
        插件初始化逻辑
        子类可以重写此方法来实现特定的初始化操作
        """
        logger.info(f'{self.PLUGIN_NAME} initialized.')

    def register_hooks(self):
        """
        注册插件钩子
        子类可以重写此方法来注册特定的钩子
        """
        pass

    def get_plugin_info(self):
        """
        获取插件信息
        :return: 包含插件元数据的字典
        """
        return {
            'name': self.PLUGIN_NAME,
            'description': self.PLUGIN_DESCRIPTION,
            'version': self.PLUGIN_VERSION
        }
