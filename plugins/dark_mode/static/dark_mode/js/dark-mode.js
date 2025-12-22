/**
 * 黑夜模式增强功能
 *
 * 提供额外的辅助功能和事件监听
 */

(function() {
    'use strict';

    // 等待DOM加载完成
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    function init() {
        // 添加键盘快捷键支持 (Ctrl/Cmd + Shift + D)
        document.addEventListener('keydown', function(e) {
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'D') {
                e.preventDefault();
                if (window.DarkMode) {
                    window.DarkMode.toggle();
                    showToast('主题已切换');
                }
            }
        });

        // 监听主题变化事件
        document.addEventListener('themeChanged', function(e) {
            console.log('主题已切换为:', e.detail.theme);

            // 可以在这里添加额外的处理逻辑
            // 例如：通知其他组件、记录统计等
        });

        // 为按钮添加 aria 属性
        updateAriaAttributes();
        document.addEventListener('themeChanged', updateAriaAttributes);
    }

    /**
     * 更新按钮的辅助功能属性
     */
    function updateAriaAttributes() {
        const btn = document.getElementById('dark-mode-toggle-btn');
        if (!btn) return;

        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        const isDark = currentTheme === 'dark';

        btn.setAttribute('aria-pressed', isDark ? 'true' : 'false');
        btn.setAttribute('aria-label', isDark ? '切换到浅色模式' : '切换到深色模式');
    }

    /**
     * 显示临时提示
     */
    function showToast(message) {
        // 创建提示元素
        const toast = document.createElement('div');
        toast.className = 'dark-mode-toast';
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            bottom: 140px;
            right: 20px;
            background-color: var(--dm-bg-tertiary);
            color: var(--dm-text-primary);
            padding: 10px 20px;
            border-radius: 4px;
            box-shadow: 0 2px 8px var(--dm-shadow);
            z-index: 10000;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;

        document.body.appendChild(toast);

        // 渐显
        setTimeout(() => {
            toast.style.opacity = '1';
        }, 10);

        // 2秒后移除
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 2000);
    }

    /**
     * 导出额外的辅助函数
     */
    if (window.DarkMode) {
        // 获取当前主题的颜色值
        window.DarkMode.getColorValue = function(varName) {
            return getComputedStyle(document.documentElement)
                .getPropertyValue(varName).trim();
        };

        // 检测是否支持黑夜模式
        window.DarkMode.isSupported = function() {
            return CSS.supports && CSS.supports('color', 'var(--test)');
        };

        // 预加载图片（可选）
        window.DarkMode.preloadImages = function() {
            // 在主题切换前预加载图片，减少闪烁
            const images = document.querySelectorAll('img[data-dark-src]');
            images.forEach(img => {
                const darkSrc = img.getAttribute('data-dark-src');
                if (darkSrc) {
                    const preloadImg = new Image();
                    preloadImg.src = darkSrc;
                }
            });
        };
    }

})();
