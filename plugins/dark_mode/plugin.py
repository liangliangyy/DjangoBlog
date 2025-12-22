"""
黑夜模式插件

提供完整的黑夜模式支持，包括：
- CSS变量驱动的主题切换
- localStorage持久化
- 系统主题跟随
- 防闪烁加载
- 响应式设计
"""

from djangoblog.plugin_manage.base_plugin import BasePlugin
from djangoblog.plugin_manage import hooks
from django.utils.safestring import mark_safe
import logging

logger = logging.getLogger(__name__)


class DarkModePlugin(BasePlugin):
    """黑夜模式插件"""

    # ==================== 插件元数据 ====================
    PLUGIN_NAME = '黑夜模式'
    PLUGIN_DESCRIPTION = '为博客提供浅色/深色主题切换功能，支持用户偏好保存和系统主题跟随。'
    PLUGIN_VERSION = '1.0.0'
    PLUGIN_AUTHOR = 'DjangoBlog Team'

    # ==================== 位置配置 ====================
    # 不使用位置widget，而是通过 head/body 资源注入
    SUPPORTED_POSITIONS = []

    # ==================== 插件配置 ====================
    CONFIG = {
        # 主题配置
        'default_theme': 'auto',  # 'light' | 'dark' | 'auto'
        'enable_system_preference': True,  # 是否跟随系统主题

        # 按钮配置
        'button_position': 'fixed',  # 'fixed' | 'header' | 'both'
        'button_icon_style': 'emoji',  # 'emoji' | 'svg'

        # 样式配置
        'transition_duration': '300ms',  # 主题切换动画时长
        'enable_image_filter': False,  # 是否对图片应用滤镜

        # 高级配置
        'storage_key': 'dark-mode-enabled',  # localStorage键名
        'theme_attribute': 'data-theme',  # HTML属性名
    }

    def init_plugin(self):
        """插件初始化"""
        logger.info(f"Initializing {self.PLUGIN_NAME} v{self.PLUGIN_VERSION}")

    def register_hooks(self):
        """注册钩子"""
        # 不注册任何钩子，完全通过资源注入实现
        pass

    # ==================== 资源注入 ====================

    def get_head_html(self, context=None):
        """
        注入到 <head> 的HTML内容

        关键：防闪烁脚本必须在 <head> 中同步执行
        """
        # 1. CSS变量定义（内联以确保最早加载）
        css_variables = '''
<style id="dark-mode-variables">
    /* 黑夜模式CSS变量系统 */
    :root {
        /* 颜色变量 - 亮色模式 */
        --dm-bg-primary: #ffffff;
        --dm-bg-secondary: #f4f4f4;
        --dm-bg-tertiary: #e6e6e6;
        --dm-bg-code: #f9f9f9;

        --dm-text-primary: #444444;
        --dm-text-secondary: #757575;
        --dm-text-tertiary: #636363;

        --dm-link-color: #21759b;
        --dm-link-hover: #0f3647;

        --dm-border-color: #cccccc;
        --dm-border-light: #d2d2d2;

        --dm-shadow: rgba(64, 64, 64, 0.1);

        --dm-button-bg: #e6e6e6;
        --dm-button-text: #7c7c7c;
        --dm-button-hover-bg: #ebebeb;

        /* 过渡时长 */
        --dm-transition: ''' + self.CONFIG['transition_duration'] + ''';
    }

    /* 黑夜模式变量覆盖 - Solarized Dark 主题风格 */
    html[data-theme="dark"] {
        --dm-bg-primary: #002b36;
        --dm-bg-secondary: #073642;
        --dm-bg-tertiary: #0e4450;
        --dm-bg-code: #073642;

        --dm-text-primary: #93a1a1;
        --dm-text-secondary: #839496;
        --dm-text-tertiary: #657b83;

        --dm-link-color: #2aa198;
        --dm-link-hover: #3bc1b6;

        --dm-border-color: #073642;
        --dm-border-light: #0e4450;

        --dm-shadow: rgba(0, 0, 0, 0.3);

        --dm-button-bg: #073642;
        --dm-button-text: #93a1a1;
        --dm-button-hover-bg: #0e4450;
    }
</style>
'''

        # 2. 防闪烁初始化脚本（必须同步执行）
        init_script = f'''
<script id="dark-mode-init">
    // 黑夜模式防闪烁初始化
    (function() {{
        'use strict';

        const STORAGE_KEY = '{self.CONFIG["storage_key"]}';
        const THEME_ATTR = '{self.CONFIG["theme_attribute"]}';
        const ENABLE_SYSTEM = {str(self.CONFIG["enable_system_preference"]).lower()};

        function getPreferredTheme() {{
            // 1. 优先使用用户保存的偏好
            const saved = localStorage.getItem(STORAGE_KEY);
            if (saved !== null) {{
                return saved === 'dark' ? 'dark' : 'light';
            }}

            // 2. 如果启用系统偏好跟随，检测系统设置
            if (ENABLE_SYSTEM && window.matchMedia) {{
                if (window.matchMedia('(prefers-color-scheme: dark)').matches) {{
                    return 'dark';
                }}
            }}

            // 3. 默认主题
            return '{self.CONFIG["default_theme"]}' === 'dark' ? 'dark' : 'light';
        }}

        function applyTheme(theme) {{
            if (theme === 'dark') {{
                document.documentElement.setAttribute(THEME_ATTR, 'dark');
            }} else {{
                document.documentElement.removeAttribute(THEME_ATTR);
            }}
        }}

        // 立即应用主题，避免闪烁
        const theme = getPreferredTheme();
        applyTheme(theme);

        // 如果body已经加载，也应用到body
        if (document.body) {{
            document.body.setAttribute(THEME_ATTR, theme);
        }}
    }})();
</script>
'''

        return mark_safe(css_variables + init_script)

    def get_body_html(self, context=None):
        """
        注入到 </body> 前的HTML内容

        包含完整的主题切换逻辑和UI
        """
        # 1. 固定位置切换按钮（如果配置启用）
        toggle_button = ''
        if self.CONFIG['button_position'] in ['fixed', 'both']:
            if self.CONFIG['button_icon_style'] == 'emoji':
                icon_light = '☀️'
                icon_dark = '🌙'
            else:
                # SVG图标可以在这里定义
                icon_light = '☀'
                icon_dark = '🌙'

            toggle_button = f'''
<div id="dark-mode-toggle-fixed" class="dark-mode-toggle-fixed">
    <button type="button"
            id="dark-mode-toggle-btn"
            class="dark-mode-toggle-btn"
            aria-label="切换主题"
            title="切换黑夜模式">
        <span class="icon-light">{icon_light}</span>
        <span class="icon-dark">{icon_dark}</span>
    </button>
</div>
'''

        # 2. 主题切换功能脚本
        toggle_script = f'''
<script id="dark-mode-toggle">
    (function() {{
        'use strict';

        const STORAGE_KEY = '{self.CONFIG["storage_key"]}';
        const THEME_ATTR = '{self.CONFIG["theme_attribute"]}';
        const ENABLE_SYSTEM = {str(self.CONFIG["enable_system_preference"]).lower()};

        // 全局黑夜模式API
        window.DarkMode = {{
            getCurrentTheme: function() {{
                return document.documentElement.getAttribute(THEME_ATTR) || 'light';
            }},

            setTheme: function(theme) {{
                const validTheme = theme === 'dark' ? 'dark' : 'light';

                if (validTheme === 'dark') {{
                    document.documentElement.setAttribute(THEME_ATTR, 'dark');
                    document.body.setAttribute(THEME_ATTR, 'dark');
                }} else {{
                    document.documentElement.removeAttribute(THEME_ATTR);
                    document.body.removeAttribute(THEME_ATTR);
                }}

                // 保存到localStorage
                localStorage.setItem(STORAGE_KEY, validTheme);

                // 触发自定义事件
                const event = new CustomEvent('themeChanged', {{
                    detail: {{ theme: validTheme }}
                }});
                document.dispatchEvent(event);

                return validTheme;
            }},

            toggle: function() {{
                const current = this.getCurrentTheme();
                const next = current === 'dark' ? 'light' : 'dark';
                return this.setTheme(next);
            }}
        }};

        // DOM加载完成后绑定事件
        function init() {{
            const toggleBtn = document.getElementById('dark-mode-toggle-btn');
            if (toggleBtn) {{
                toggleBtn.addEventListener('click', function() {{
                    window.DarkMode.toggle();
                }});
            }}

            // 监听系统主题变化
            if (ENABLE_SYSTEM && window.matchMedia) {{
                const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');

                // 使用现代API或降级方案
                const listener = function(e) {{
                    // 只有在用户未手动设置时才跟随系统
                    if (localStorage.getItem(STORAGE_KEY) === null) {{
                        window.DarkMode.setTheme(e.matches ? 'dark' : 'light');
                    }}
                }};

                if (darkModeQuery.addEventListener) {{
                    darkModeQuery.addEventListener('change', listener);
                }} else if (darkModeQuery.addListener) {{
                    darkModeQuery.addListener(listener);
                }}
            }}
        }}

        // 初始化
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', init);
        }} else {{
            init();
        }}
    }})();
</script>
'''

        return mark_safe(toggle_button + toggle_script)

    # ==================== 静态资源 ====================

    def get_css_files(self):
        """返回CSS文件列表（会被自动压缩）"""
        return [
            'css/dark-mode.css',              # 核心样式
            'css/dark-mode-bootstrap.css',    # Bootstrap适配
            'css/dark-mode-components.css',   # 组件适配
        ]

    def get_js_files(self):
        """返回JS文件列表（会被自动压缩）"""
        return [
            'js/dark-mode.js',  # 增强功能和辅助函数
        ]


# ==================== 插件实例（必需）====================
plugin = DarkModePlugin()
