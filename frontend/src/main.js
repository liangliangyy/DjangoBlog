/**
 * DjangoBlog 前端主入口文件
 * 使用 Alpine.js + HTMX 实现现代化服务端渲染
 */

// 导入样式文件（Vite开发模式必需）
import './styles/main.css';

import Alpine from 'alpinejs';
import focus from '@alpinejs/focus';
import intersect from '@alpinejs/intersect';
import collapse from '@alpinejs/collapse';
import htmx from 'htmx.org';

// 导入Dark Mode（会自动初始化防闪烁）
import { initDarkMode } from './features/darkMode.js';

// 注册Alpine插件
Alpine.plugin(focus);
Alpine.plugin(intersect);
Alpine.plugin(collapse);

// 导入组件
import commentSystem from './components/commentSystem.js';
import backToTop from './components/backToTop.js';
import navigation from './components/navigation.js';
import imageLightbox from './components/imageLightbox.js';
import reactionPicker from './components/reactionPicker.js';

// 注册全局Alpine数据
Alpine.data('commentSystem', commentSystem);
Alpine.data('backToTop', backToTop);
Alpine.data('navigation', navigation);
Alpine.data('imageLightbox', imageLightbox);
Alpine.data('reactionPicker', reactionPicker);

// 全局工具函数
window.Alpine = Alpine;
window.htmx = htmx;

// 启动Alpine
Alpine.start();

// 初始化Dark Mode
initDarkMode();

// HTMX 配置
htmx.config.defaultSwapStyle = 'innerHTML';
htmx.config.defaultSwapDelay = 0;
htmx.config.defaultSettleDelay = 20;

// HTMX boost 配置：自动提取 #main 内容
document.body.addEventListener('htmx:beforeSwap', function(evt) {
    // 对于 boost 的请求，确保正确提取内容
    if (evt.detail.boosted && evt.detail.target.id === 'main') {
        console.log('HTMX boost navigation:', evt.detail.pathInfo.requestPath);
    }
});

// HTMX 加载完成后重新初始化 Alpine 组件
document.body.addEventListener('htmx:afterSwap', function(evt) {
    // Alpine 会自动检测新的 DOM 元素并初始化
    console.log('Content swapped, Alpine auto-initializing new components');

    // 滚动到顶部（可选）
    if (evt.detail.boosted) {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
});

// NProgress页面加载进度条（保留原有功能）
import NProgress from './utils/nprogress.js';
NProgress.configure({ showSpinner: false });

// 页面加载时的进度条
NProgress.start();
NProgress.set(0.4);

const interval = setInterval(() => {
    NProgress.inc();
}, 1000);

window.addEventListener('DOMContentLoaded', () => {
    NProgress.done();
    clearInterval(interval);
});

// 页面导航时的进度条
window.addEventListener('beforeunload', () => {
    NProgress.start();
});

// HTMX 事件监听 - 配合 NProgress
document.body.addEventListener('htmx:beforeRequest', () => {
  NProgress.start();
});

document.body.addEventListener('htmx:afterRequest', () => {
  NProgress.done();
});

console.log('✨ DjangoBlog Frontend Loaded (Alpine.js + HTMX + Tailwind CSS)');
