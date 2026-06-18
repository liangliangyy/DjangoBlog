/**
 * 前端工具函数库
 */

/**
 * 防抖函数
 * @param {Function} func - 要防抖的函数
 * @param {number} delay - 延迟时间（毫秒）
 * @returns {Function} 防抖后的函数
 */
export function debounce(func, delay = 300) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, delay);
  };
}

/**
 * 节流函数
 * @param {Function} func - 要节流的函数
 * @param {number} limit - 调用间隔（毫秒）
 * @returns {Function} 节流后的函数
 */
export function throttle(func, limit = 300) {
  let inThrottle;
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

/**
 * 平滑滚动到元素
 * @param {HTMLElement} element - 目标元素
 * @param {number} offset - 滚动偏移量（像素）
 * @param {number} duration - 动画时长（毫秒）
 */
export function smoothScrollToElement(element, offset = 0, duration = 300) {
  if (!element) return;
  
  const targetPosition = element.getBoundingClientRect().top + window.scrollY - offset;
  const startPosition = window.scrollY;
  const distance = targetPosition - startPosition;
  let start = null;
  
  const animation = (currentTime) => {
    if (start === null) start = currentTime;
    const elapsed = currentTime - start;
    const progress = Math.min(elapsed / duration, 1);
    
    // 缓动函数 (ease-in-out)
    const ease = progress < 0.5
      ? 2 * progress * progress
      : -1 + (4 - 2 * progress) * progress;
    
    window.scrollTo(0, startPosition + distance * ease);
    
    if (elapsed < duration) {
      requestAnimationFrame(animation);
    }
  };
  
  requestAnimationFrame(animation);
}

/**
 * 复制文本到剪贴板
 * @param {string} text - 要复制的文本
 * @returns {Promise<boolean>} 复制是否成功
 */
export async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (err) {
    console.error('[v0] Failed to copy to clipboard:', err);
    return false;
  }
}

/**
 * 格式化日期
 * @param {Date|string} date - 日期对象或字符串
 * @param {string} format - 格式字符串 (YYYY-MM-DD HH:mm:ss)
 * @returns {string} 格式化后的日期字符串
 */
export function formatDate(date, format = 'YYYY-MM-DD') {
  const d = new Date(date);
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const hours = String(d.getHours()).padStart(2, '0');
  const minutes = String(d.getMinutes()).padStart(2, '0');
  const seconds = String(d.getSeconds()).padStart(2, '0');
  
  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds);
}

/**
 * 计算相对时间（如 "1小时前"）
 * @param {Date|string} date - 日期对象或字符串
 * @returns {string} 相对时间描述
 */
export function getRelativeTime(date) {
  const d = new Date(date);
  const now = new Date();
  const diff = Math.floor((now - d) / 1000);
  
  if (diff < 60) return '刚刚';
  if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`;
  if (diff < 604800) return `${Math.floor(diff / 86400)}天前`;
  if (diff < 2592000) return `${Math.floor(diff / 604800)}周前`;
  if (diff < 31536000) return `${Math.floor(diff / 2592000)}个月前`;
  
  return `${Math.floor(diff / 31536000)}年前`;
}

/**
 * 生成UUID
 * @returns {string} UUID字符串
 */
export function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

/**
 * 检查元素是否在视口中
 * @param {HTMLElement} element - 要检查的元素
 * @param {number} offset - 偏移量（像素）
 * @returns {boolean} 是否在视口中
 */
export function isElementInViewport(element, offset = 0) {
  const rect = element.getBoundingClientRect();
  return (
    rect.top <= (window.innerHeight + offset) &&
    rect.bottom >= (-offset) &&
    rect.left <= (window.innerWidth + offset) &&
    rect.right >= (-offset)
  );
}

/**
 * 懒加载图片
 * @param {string} selector - 图片选择器
 */
export function setupLazyLoading(selector = 'img[loading="lazy"]') {
  if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src;
          img.classList.remove('opacity-0');
          img.classList.add('opacity-100', 'transition-opacity', 'duration-300');
          observer.unobserve(img);
        }
      });
    });
    
    document.querySelectorAll(selector).forEach((img) => {
      imageObserver.observe(img);
    });
    
    console.log('[v0] Lazy loading initialized');
  }
}

/**
 * 显示加载中动画
 * @param {HTMLElement} element - 目标元素
 * @param {string} message - 加载信息
 */
export function showLoading(element, message = '加载中...') {
  element.innerHTML = `
    <div class="flex items-center justify-center gap-2">
      <svg class="animate-spin w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
      </svg>
      <span>${message}</span>
    </div>
  `;
}

/**
 * 显示错误信息
 * @param {HTMLElement} element - 目标元素
 * @param {string} message - 错误信息
 */
export function showError(element, message = '加载失败') {
  element.innerHTML = `
    <div class="flex items-center justify-center gap-2 text-destructive">
      <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
      </svg>
      <span>${message}</span>
    </div>
  `;
}

/**
 * 获取URL参数
 * @param {string} param - 参数名
 * @returns {string|null} 参数值
 */
export function getURLParam(param) {
  const params = new URLSearchParams(window.location.search);
  return params.get(param);
}

/**
 * 更新URL参数（不刷新页面）
 * @param {string} param - 参数名
 * @param {string} value - 参数值
 */
export function updateURLParam(param, value) {
  const params = new URLSearchParams(window.location.search);
  params.set(param, value);
  window.history.replaceState({}, '', `?${params.toString()}`);
}

/**
 * 防止事件冒泡
 * @param {Event} event - 事件对象
 */
export function stopPropagation(event) {
  event.stopPropagation();
  event.preventDefault();
}

/**
 * 尝试解析JSON
 * @param {string} json - JSON字符串
 * @param {*} fallback - 解析失败时的默认值
 * @returns {*} 解析结果
 */
export function tryParseJSON(json, fallback = null) {
  try {
    return JSON.parse(json);
  } catch (e) {
    console.error('[v0] Failed to parse JSON:', e);
    return fallback;
  }
}

/**
 * 请求动画帧的Promise版本
 * @returns {Promise} 下一帧的Promise
 */
export function nextFrame() {
  return new Promise(resolve => requestAnimationFrame(resolve));
}

/**
 * 延迟执行
 * @param {number} ms - 延迟时间（毫秒）
 * @returns {Promise} 延迟完成的Promise
 */
export function delay(ms = 0) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
