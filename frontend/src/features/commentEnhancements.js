/**
 * 评论系统增强功能
 * 包括: 排序、筛选、点赞、通知等
 */

// ======================== 评论排序和筛选 ========================
export function setupCommentFiltering() {
  const filterButtons = document.querySelectorAll('[data-comment-filter]');
  
  filterButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      const filterType = btn.dataset.commentFilter;
      const containerid = btn.dataset.container || 'commentlist-container';
      const container = document.getElementById(containerid);
      
      if (!container) return;
      
      // 更新活跃按钮状态
      filterButtons.forEach(b => b.classList.remove('bg-primary', 'text-primary-foreground'));
      filterButtons.forEach(b => b.classList.add('bg-secondary', 'text-foreground'));
      btn.classList.remove('bg-secondary', 'text-foreground');
      btn.classList.add('bg-primary', 'text-primary-foreground');
      
      // 获取所有评论项
      const comments = Array.from(container.querySelectorAll('li.comment'));
      
      // 排序逻辑
      switch (filterType) {
        case 'latest':
          comments.sort((a, b) => {
            const timeA = new Date(a.querySelector('time')?.datetime || 0);
            const timeB = new Date(b.querySelector('time')?.datetime || 0);
            return timeB - timeA;
          });
          break;
          
        case 'oldest':
          comments.sort((a, b) => {
            const timeA = new Date(a.querySelector('time')?.datetime || 0);
            const timeB = new Date(b.querySelector('time')?.datetime || 0);
            return timeA - timeB;
          });
          break;
          
        case 'popular':
          // 按反应数和点赞数排序
          comments.sort((a, b) => {
            const countA = (a.querySelectorAll('[data-reaction]').length || 0) + 
                          (parseInt(a.dataset.likes || 0));
            const countB = (b.querySelectorAll('[data-reaction]').length || 0) + 
                          (parseInt(b.dataset.likes || 0));
            return countB - countA;
          });
          break;
      }
      
      // 重新排序DOM
      const list = container.querySelector('ol');
      if (list) {
        comments.forEach(comment => {
          list.appendChild(comment);
        });
      }
      
      console.log('[v0] Comments sorted by:', filterType);
    });
  });
}

// ======================== 评论点赞系统 ========================
export function setupCommentLikes() {
  const likeButtons = document.querySelectorAll('[data-comment-like]');
  
  likeButtons.forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.preventDefault();
      e.stopPropagation();
      
      const commentId = btn.dataset.commentLike;
      const isLiked = btn.classList.contains('liked');
      const countSpan = btn.querySelector('[data-like-count]');
      
      // 本地UI更新
      btn.classList.toggle('liked');
      let count = parseInt(countSpan?.textContent || 0);
      count = isLiked ? count - 1 : count + 1;
      if (countSpan) countSpan.textContent = count;
      
      // 添加动画反馈
      btn.classList.add('scale-110');
      setTimeout(() => btn.classList.remove('scale-110'), 200);
      
      // 发送到服务器（可选）
      try {
        const csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]')?.value;
        await fetch(`/api/comments/${commentId}/like/`, {
          method: isLiked ? 'DELETE' : 'POST',
          headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json',
          },
        });
      } catch (err) {
        console.error('[v0] Failed to sync like:', err);
        // 回滚UI
        btn.classList.toggle('liked');
        if (countSpan) countSpan.textContent = isLiked ? count + 1 : count - 1;
      }
    });
  });
}

// ======================== 评论通知系统 ========================
export function showCommentNotification(message, type = 'success') {
  const notification = document.createElement('div');
  const bgClass = {
    success: 'bg-green-500/90',
    error: 'bg-red-500/90',
    warning: 'bg-yellow-500/90',
    info: 'bg-blue-500/90',
  }[type] || 'bg-blue-500/90';
  
  const iconSvg = {
    success: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>',
    error: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/></svg>',
    warning: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/></svg>',
    info: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/></svg>',
  }[type] || '';
  
  notification.className = `fixed top-4 right-4 z-50 flex items-center gap-3 px-4 py-3 rounded-lg text-white shadow-lg ${bgClass} animate-slide-in-right`;
  notification.innerHTML = `
    ${iconSvg}
    <span>${message}</span>
    <button class="ml-2 opacity-75 hover:opacity-100" onclick="this.parentElement.remove()">
      <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/></svg>
    </button>
  `;
  
  document.body.appendChild(notification);
  
  // 3秒后自动移除
  setTimeout(() => {
    notification.classList.add('opacity-0', 'transition-opacity', 'duration-300');
    setTimeout(() => notification.remove(), 300);
  }, 3000);
}

// ======================== 评论计数更新 ========================
export function updateCommentCount(count) {
  const countBadges = document.querySelectorAll('[data-comment-count]');
  countBadges.forEach(badge => {
    badge.textContent = count;
    badge.parentElement?.classList.add('ring-2', 'ring-primary');
    setTimeout(() => {
      badge.parentElement?.classList.remove('ring-2', 'ring-primary');
    }, 500);
  });
}

// ======================== 初始化所有功能 ========================
export function initCommentEnhancements() {
  setupCommentFiltering();
  setupCommentLikes();
  
  // 监听HTMX事件，当评论列表更新时重新初始化
  document.addEventListener('htmx:afterSwap', () => {
    setupCommentFiltering();
    setupCommentLikes();
    console.log('[v0] Comment enhancements re-initialized after swap');
  });
  
  console.log('[v0] Comment enhancements initialized');
}
