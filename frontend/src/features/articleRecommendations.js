/**
 * 文章推荐系统
 * 包括: 相关文章、热门文章、个性化推荐
 */

// ======================== 相关文章推荐 ========================
export function setupRelatedArticles() {
  const container = document.querySelector('[data-related-articles]');
  if (!container) return;
  
  // 简单的基于标签的相关性计算
  const currentArticle = container.dataset.articleId;
  const currentTags = container.dataset.tags?.split(',') || [];
  
  console.log('[v0] Related articles setup - Current tags:', currentTags);
  
  // 可以添加动画效果
  const articles = container.querySelectorAll('[data-related-article-item]');
  articles.forEach((article, index) => {
    article.style.animationDelay = `${index * 100}ms`;
    article.classList.add('animate-fade-in-up');
  });
}

// ======================== 热门文章排行 ========================
export function setupHotArticles() {
  const container = document.querySelector('[data-hot-articles]');
  if (!container) return;
  
  const articlesData = [];
  const articles = container.querySelectorAll('[data-hot-article-item]');
  
  articles.forEach(article => {
    articlesData.push({
      id: article.dataset.articleId,
      title: article.dataset.title,
      views: parseInt(article.dataset.views || 0),
      comments: parseInt(article.dataset.comments || 0),
      timestamp: new Date(article.dataset.timestamp),
    });
  });
  
  // 设置排序功能
  const sortButtons = container.querySelectorAll('[data-sort-by]');
  sortButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const sortType = btn.dataset.sortBy;
      
      // 更新活跃按钮
      sortButtons.forEach(b => {
        b.classList.remove('bg-primary', 'text-primary-foreground');
        b.classList.add('bg-secondary', 'text-foreground');
      });
      btn.classList.remove('bg-secondary', 'text-foreground');
      btn.classList.add('bg-primary', 'text-primary-foreground');
      
      // 排序文章
      sortArticles(articlesData, sortType, container);
    });
  });
  
  console.log('[v0] Hot articles setup - Total articles:', articlesData.length);
}

function sortArticles(articles, sortType, container) {
  let sorted = [...articles];
  
  switch (sortType) {
    case 'views':
      sorted.sort((a, b) => b.views - a.views);
      break;
    case 'comments':
      sorted.sort((a, b) => b.comments - a.comments);
      break;
    case 'latest':
      sorted.sort((a, b) => b.timestamp - a.timestamp);
      break;
    default:
      sorted.sort((a, b) => b.views - a.views);
  }
  
  // 更新DOM顺序
  const listContainer = container.querySelector('[data-articles-list]');
  if (listContainer) {
    sorted.forEach((article, index) => {
      const element = container.querySelector(`[data-article-id="${article.id}"]`);
      if (element) {
        listContainer.appendChild(element);
        // 添加排行号动画
        const rankBadge = element.querySelector('[data-rank]');
        if (rankBadge) {
          rankBadge.textContent = index + 1;
          rankBadge.classList.add('scale-110');
          setTimeout(() => rankBadge.classList.remove('scale-110'), 300);
        }
      }
    });
  }
  
  console.log('[v0] Articles sorted by:', sortType);
}

// ======================== 阅读进度指示器 ========================
export function setupReadingProgress() {
  const progressBar = document.querySelector('[data-reading-progress]');
  if (!progressBar) return;
  
  const updateProgress = () => {
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const scrolled = window.scrollY;
    const progress = docHeight > 0 ? (scrolled / docHeight) * 100 : 0;
    
    progressBar.style.width = progress + '%';
  };
  
  // 监听滚动
  window.addEventListener('scroll', updateProgress, { passive: true });
  
  // 初始化
  updateProgress();
  
  console.log('[v0] Reading progress indicator initialized');
}

// ======================== 阅读时间显示 ========================
export function setupReadingTime() {
  const readingTimeElement = document.querySelector('[data-reading-time]');
  if (!readingTimeElement) return;
  
  // 计算文章内容的字数
  const content = document.querySelector('[data-article-content]');
  if (!content) return;
  
  const text = content.innerText;
  const wordCount = text.split(/\s+/).length;
  
  // 平均阅读速度: 200-250 中文字/分钟, 200 英文字/分钟
  const chineseChars = (text.match(/[\u4e00-\u9fff]/g) || []).length;
  const englishWords = wordCount - chineseChars;
  
  // 估算阅读时间（分钟）
  const readingMinutes = Math.max(1, Math.ceil((chineseChars / 250) + (englishWords / 200)));
  
  readingTimeElement.innerHTML = `
    <span class="inline-flex items-center gap-1 text-xs text-muted-foreground">
      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
      </svg>
      约${readingMinutes}分钟阅读
    </span>
  `;
  
  console.log('[v0] Reading time calculated:', readingMinutes, 'minutes');
}

// ======================== 文章点赞系统 ========================
export function setupArticleLike() {
  const likeBtn = document.querySelector('[data-article-like]');
  if (!likeBtn) return;
  
  const articleId = likeBtn.dataset.articleId;
  
  likeBtn.addEventListener('click', async (e) => {
    e.preventDefault();
    
    const isLiked = likeBtn.classList.contains('liked');
    likeBtn.classList.toggle('liked');
    
    // 添加动画反馈
    likeBtn.classList.add('scale-110');
    setTimeout(() => likeBtn.classList.remove('scale-110'), 200);
    
    // 更新计数
    const likeCount = likeBtn.querySelector('[data-like-count]');
    if (likeCount) {
      let count = parseInt(likeCount.textContent || 0);
      count = isLiked ? count - 1 : count + 1;
      likeCount.textContent = count;
    }
    
    // 发送到服务器（可选）
    try {
      const csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]')?.value;
      await fetch(`/api/articles/${articleId}/like/`, {
        method: isLiked ? 'DELETE' : 'POST',
        headers: {
          'X-CSRFToken': csrfToken,
          'Content-Type': 'application/json',
        },
      });
      console.log('[v0] Article like updated');
    } catch (err) {
      console.error('[v0] Failed to sync like:', err);
    }
  });
}

// ======================== 文章分享功能 ========================
export function setupArticleShare() {
  const shareButtons = document.querySelectorAll('[data-share-button]');
  
  shareButtons.forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.preventDefault();
      
      const shareType = btn.dataset.shareButton;
      const url = window.location.href;
      const title = document.title;
      
      const shareUrls = {
        twitter: `https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(title)}`,
        facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`,
        linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`,
        weibo: `https://service.weibo.com/share/share.php?url=${encodeURIComponent(url)}&title=${encodeURIComponent(title)}`,
        copy: null,
      };
      
      if (shareType === 'copy') {
        // 复制链接
        try {
          await navigator.clipboard.writeText(url);
          showNotification('链接已复制到剪贴板', 'success');
          console.log('[v0] Link copied to clipboard');
        } catch (err) {
          console.error('[v0] Failed to copy link:', err);
          showNotification('复制失败，请手动复制', 'error');
        }
      } else if (shareUrls[shareType]) {
        // 打开分享链接
        window.open(shareUrls[shareType], '_blank', 'width=600,height=400');
      }
    });
  });
}

// ======================== 文章目录（TOC）增强 ========================
export function setupTableOfContents() {
  const tocContainer = document.querySelector('[data-table-of-contents]');
  if (!tocContainer) return;
  
  const tocLinks = tocContainer.querySelectorAll('a');
  const content = document.querySelector('[data-article-content]');
  if (!content) return;
  
  // 平滑滚动和高亮
  tocLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const target = link.getAttribute('href').substring(1);
      const element = content.querySelector(`#${target}`);
      
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
        
        // 高亮链接
        tocLinks.forEach(l => l.classList.remove('text-primary', 'font-semibold'));
        link.classList.add('text-primary', 'font-semibold');
      }
    });
  });
  
  // 监听滚动更新活跃链接
  const updateActiveToc = () => {
    const headings = content.querySelectorAll('h2, h3');
    let current = null;
    
    headings.forEach(heading => {
      const rect = heading.getBoundingClientRect();
      if (rect.top <= 100) {
        current = heading;
      }
    });
    
    if (current) {
      tocLinks.forEach(link => {
        const target = link.getAttribute('href').substring(1);
        if (target === current.id) {
          link.classList.add('text-primary', 'font-semibold');
        } else {
          link.classList.remove('text-primary', 'font-semibold');
        }
      });
    }
  };
  
  window.addEventListener('scroll', updateActiveToc, { passive: true });
  console.log('[v0] Table of contents enhanced');
}

// ======================== 通知辅助函数 ========================
function showNotification(message, type = 'info') {
  const notification = document.createElement('div');
  const bgClass = {
    success: 'bg-green-500/90',
    error: 'bg-red-500/90',
    info: 'bg-blue-500/90',
  }[type] || 'bg-blue-500/90';
  
  notification.className = `fixed bottom-4 right-4 z-50 px-4 py-3 rounded-lg text-white shadow-lg ${bgClass} animate-slide-in-left`;
  notification.textContent = message;
  
  document.body.appendChild(notification);
  
  setTimeout(() => {
    notification.classList.add('opacity-0', 'transition-opacity', 'duration-300');
    setTimeout(() => notification.remove(), 300);
  }, 2000);
}

// ======================== 初始化所有文章推荐功能 ========================
export function initArticleRecommendations() {
  setupRelatedArticles();
  setupHotArticles();
  setupReadingProgress();
  setupReadingTime();
  setupArticleLike();
  setupArticleShare();
  setupTableOfContents();
  
  console.log('[v0] Article recommendations initialized');
}
