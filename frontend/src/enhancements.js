/**
 * DjangoBlog 前端优化主入口
 * 统一加载所有增强功能模块
 */

// 导入所有增强功能
import { initCommentEnhancements } from './features/commentEnhancements.js';
import { initSearchEnhancements } from './features/searchEnhancements.js';
import { initFormEnhancements } from './features/formEnhancements.js';
import { initArticleRecommendations } from './features/articleRecommendations.js';

/**
 * 初始化所有前端优化
 * 在DOM加载完成后调用
 */
export function initializeAllEnhancements() {
  console.log('[v0] Initializing frontend enhancements...');
  
  // 等待DOM完全加载
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      executeEnhancements();
    });
  } else {
    executeEnhancements();
  }
}

function executeEnhancements() {
  console.log('[v0] DOM ready, loading enhancements...');
  
  try {
    // 1. 初始化评论系统增强
    console.group('[v0] Comment System');
    initCommentEnhancements();
    console.groupEnd();
  } catch (e) {
    console.error('[v0] Comment enhancements error:', e);
  }
  
  try {
    // 2. 初始化搜索功能
    console.group('[v0] Search Features');
    initSearchEnhancements();
    console.groupEnd();
  } catch (e) {
    console.error('[v0] Search enhancements error:', e);
  }
  
  try {
    // 3. 初始化表单验证
    console.group('[v0] Form Validation');
    initFormEnhancements();
    console.groupEnd();
  } catch (e) {
    console.error('[v0] Form enhancements error:', e);
  }
  
  try {
    // 4. 初始化文章推荐
    console.group('[v0] Article Recommendations');
    initArticleRecommendations();
    console.groupEnd();
  } catch (e) {
    console.error('[v0] Article recommendation error:', e);
  }
  
  console.log('[v0] All enhancements loaded successfully!');
  
  // 记录性能数据
  if (window.performance && performance.timing) {
    const perfData = performance.timing;
    const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
    const connectTime = perfData.responseEnd - perfData.requestStart;
    const renderTime = perfData.domComplete - perfData.domLoading;
    
    console.log('[v0] Performance Metrics:', {
      'Total Load Time': pageLoadTime + 'ms',
      'Connect Time': connectTime + 'ms',
      'Render Time': renderTime + 'ms',
    });
  }
}

// 导出为全局函数以便在HTML中调用
window.v0 = {
  initializeAllEnhancements,
  version: '1.0.0',
};

// 如果在非生产环境，自动初始化
if (process.env.NODE_ENV !== 'production' || document.documentElement.dataset.autoInit === 'true') {
  initializeAllEnhancements();
}

export { initializeAllEnhancements };
