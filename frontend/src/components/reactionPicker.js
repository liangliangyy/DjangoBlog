/**
 * Emoji Reaction Picker 组件
 * 为评论添加 GitHub 风格的 emoji 反应功能
 */

export default (commentId) => {
  return {
    // ==================== 状态管理 ====================
    reactions: {},
    showPicker: false,
    isLoading: false,

    // ==================== 初始化 ====================
    init() {
      // 优先从 data 属性读取初始数据（SSR）
      this.loadFromDataAttribute();
    },

    // ==================== 从 data 属性加载（SSR 数据）====================
    loadFromDataAttribute() {
      try {
        const dataAttr = this.$el.dataset.reactions;
        if (dataAttr) {
          this.reactions = JSON.parse(dataAttr);
        } else {
          // 如果没有 SSR 数据，降级到 API 加载
          this.loadFromAPI();
        }
      } catch (error) {
        console.error('Error parsing reactions from data attribute:', error);
        // 解析失败，降级到 API 加载
        this.loadFromAPI();
      }
    },

    // ==================== 从 API 加载（降级方案）====================
    async loadFromAPI() {
      try {
        this.isLoading = true;
        const response = await fetch(`/comment/${commentId}/react`);

        if (!response.ok) {
          throw new Error('Failed to load reactions');
        }

        const data = await response.json();
        if (data.success) {
          this.reactions = data.reactions || {};
        }
      } catch (error) {
        console.error('Error loading reactions from API:', error);
        this.reactions = {};
      } finally {
        this.isLoading = false;
      }
    },

  // ==================== 格式化用户列表 ====================
  /**
   * 格式化用户列表文本，用于 tooltip 显示
   * @param {Array} users - 用户名数组
   * @param {number} totalCount - 总点赞数
   * @returns {string} 格式化后的文本
   */
  formatUsersText(users, totalCount) {
    if (!users || users.length === 0) {
      return '暂无';
    }

    if (users.length === totalCount) {
      // 显示所有用户
      return users.join(', ');
    } else {
      // 显示前几个用户，并标注还有多少人
      const displayUsers = users.slice(0, 5).join(', ');
      const remaining = totalCount - users.length;
      if (remaining > 0) {
        return `${displayUsers} 和其他 ${remaining} 人`;
      }
      return displayUsers;
    }
  },

  // ==================== 检查登录状态 ====================
  /**
   * 检查用户是否已登录
   * @returns {boolean}
   */
  isAuthenticated() {
    return document.body.dataset.authenticated === 'true';
  },

  // ==================== 显示登录提示 ====================
  showLoginPrompt() {
    const loginUrl = `/login/?next=${encodeURIComponent(window.location.pathname)}`;

    // 创建美观的提示框
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50 animate-fade-in';
    modal.innerHTML = `
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full p-6 animate-scale-in">
        <div class="flex items-center mb-4">
          <svg class="w-6 h-6 text-primary-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
          </svg>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">需要登录</h3>
        </div>
        <p class="text-gray-600 dark:text-gray-300 mb-6">
          点赞功能需要登录后才能使用，是否前往登录页面？
        </p>
        <div class="flex gap-3 justify-end">
          <button id="modal-cancel" class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors">
            取消
          </button>
          <button id="modal-confirm" class="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors">
            前往登录
          </button>
        </div>
      </div>
    `;

    document.body.appendChild(modal);

    // 绑定事件
    const cancelBtn = modal.querySelector('#modal-cancel');
    const confirmBtn = modal.querySelector('#modal-confirm');

    cancelBtn.addEventListener('click', () => {
      modal.classList.add('animate-fade-out');
      setTimeout(() => modal.remove(), 200);
    });

    confirmBtn.addEventListener('click', () => {
      window.location.href = loginUrl;
    });

    // 点击背景关闭
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.classList.add('animate-fade-out');
        setTimeout(() => modal.remove(), 200);
      }
    });
  },

  // ==================== 切换 Reaction ====================
  /**
   * 切换 reaction（添加或删除）
   * @param {string} emoji - emoji 字符
   */
  async toggleReaction(emoji) {
    // 检查登录状态
    if (!this.isAuthenticated()) {
      this.showLoginPrompt();
      return;
    }

    try {
      // 获取 CSRF token
      const csrfToken = this.getCsrfToken();

      if (!csrfToken) {
        console.error('CSRF token not found');
        this.showNotification('无法获取安全令牌，请刷新页面重试', 'error');
        return;
      }

      // 发送请求
      const formData = new FormData();
      formData.append('reaction_type', emoji);
      formData.append('csrfmiddlewaretoken', csrfToken);

      const response = await fetch(`/comment/${commentId}/react`, {
        method: 'POST',
        body: formData,
        headers: {
          'X-CSRFToken': csrfToken
        }
      });

      if (!response.ok) {
        // 处理 401 未授权错误
        if (response.status === 401) {
          this.showNotification('登录已过期，请重新登录', 'error');
          setTimeout(() => {
            window.location.href = `/login/?next=${encodeURIComponent(window.location.pathname)}`;
          }, 1500);
          return;
        }
        throw new Error('Failed to toggle reaction');
      }

      const data = await response.json();

      if (data.success) {
        // 更新本地 reactions 数据
        this.reactions = data.reactions;
        this.showPicker = false;
      } else {
        throw new Error(data.error || '操作失败');
      }
    } catch (error) {
      console.error('Error toggling reaction:', error);
      this.showNotification('操作失败，请重试', 'error');
    }
  },

  // ==================== 显示通知 ====================
  /**
   * 显示美观的通知消息
   * @param {string} message - 消息内容
   * @param {string} type - 消息类型：success, error, info
   */
  showNotification(message, type = 'info') {
    const colors = {
      success: 'bg-green-500',
      error: 'bg-red-500',
      info: 'bg-blue-500'
    };

    const icons = {
      success: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>',
      error: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>',
      info: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>'
    };

    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 ${colors[type]} text-white px-6 py-4 rounded-lg shadow-lg z-50 flex items-center gap-3 animate-slide-in-right max-w-md`;
    notification.innerHTML = `
      <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        ${icons[type]}
      </svg>
      <span>${message}</span>
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
      notification.classList.add('animate-fade-out');
      setTimeout(() => notification.remove(), 300);
    }, 3000);
  },

  // ==================== 工具函数 ====================
  /**
   * 从 cookie 中获取 CSRF token
   * @returns {string|null} CSRF token
   */
  getCsrfToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  },
  };
};
