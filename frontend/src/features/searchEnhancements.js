/**
 * 搜索功能增强
 * 包括: 实时搜索预览、搜索历史、高级搜索
 */

import { debounce } from './utils.js';

// ======================== 搜索历史管理 ========================
class SearchHistoryManager {
  constructor(storageKey = 'blog_search_history', maxItems = 10) {
    this.storageKey = storageKey;
    this.maxItems = maxItems;
  }
  
  add(query) {
    if (!query.trim()) return;
    
    let history = this.getAll();
    // 移除重复项
    history = history.filter(q => q !== query);
    // 将新项插入开头
    history.unshift(query);
    // 限制数量
    history = history.slice(0, this.maxItems);
    
    localStorage.setItem(this.storageKey, JSON.stringify(history));
    console.log('[v0] Search history updated:', history);
  }
  
  getAll() {
    try {
      return JSON.parse(localStorage.getItem(this.storageKey) || '[]');
    } catch (e) {
      console.error('[v0] Failed to parse search history:', e);
      return [];
    }
  }
  
  clear() {
    localStorage.removeItem(this.storageKey);
    console.log('[v0] Search history cleared');
  }
  
  remove(query) {
    let history = this.getAll();
    history = history.filter(q => q !== query);
    localStorage.setItem(this.storageKey, JSON.stringify(history));
  }
}

const searchHistory = new SearchHistoryManager();

// ======================== 实时搜索预览 ========================
export function setupSearchPreview() {
  const searchInput = document.querySelector('[data-search-input]');
  const searchPreview = document.querySelector('[data-search-preview]');
  
  if (!searchInput || !searchPreview) return;
  
  // 防抖搜索
  const performSearch = debounce(async (query) => {
    if (query.length < 2) {
      searchPreview.innerHTML = '';
      searchPreview.style.display = 'none';
      return;
    }
    
    try {
      searchPreview.innerHTML = '<div class="p-4 text-center text-sm text-muted-foreground">搜索中...</div>';
      searchPreview.style.display = 'block';
      
      // 获取搜索结果预览
      const response = await fetch(`/search/preview/?q=${encodeURIComponent(query)}`);
      if (!response.ok) throw new Error('Search failed');
      
      const html = await response.text();
      searchPreview.innerHTML = html;
      
      console.log('[v0] Search preview updated for:', query);
    } catch (err) {
      console.error('[v0] Search preview error:', err);
      searchPreview.innerHTML = '<div class="p-4 text-center text-sm text-destructive">搜索出错</div>';
    }
  }, 300);
  
  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.trim();
    performSearch(query);
  });
  
  // 点击预览项时执行搜索
  searchPreview.addEventListener('click', (e) => {
    const link = e.target.closest('[data-search-result]');
    if (link) {
      searchHistory.add(searchInput.value);
    }
  });
  
  // 失焦时隐藏预览
  searchInput.addEventListener('blur', () => {
    setTimeout(() => {
      searchPreview.style.display = 'none';
    }, 200);
  });
  
  // 聚焦时显示历史
  searchInput.addEventListener('focus', () => {
    if (searchInput.value.length < 2) {
      showSearchHistory(searchInput, searchPreview);
    }
  });
}

// ======================== 显示搜索历史 ========================
function showSearchHistory(input, preview) {
  const history = searchHistory.getAll();
  
  if (history.length === 0) {
    preview.innerHTML = '<div class="p-4 text-center text-sm text-muted-foreground">暂无搜索历史</div>';
  } else {
    preview.innerHTML = `
      <div class="p-2">
        <div class="text-xs font-semibold text-muted-foreground mb-2 px-2">搜索历史</div>
        <div class="space-y-1">
          ${history.map(query => `
            <button 
              type="button"
              class="w-full text-left px-3 py-2 rounded hover:bg-secondary transition-colors text-sm"
              data-search-history="${query}"
            >
              <svg class="inline w-4 h-4 mr-2 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              ${query}
            </button>
          `).join('')}
        </div>
        <div class="border-t border-border mt-2 pt-2">
          <button 
            type="button"
            class="w-full text-left px-3 py-2 rounded text-xs text-muted-foreground hover:text-destructive transition-colors"
            id="clear-search-history"
          >
            清除历史
          </button>
        </div>
      </div>
    `;
  }
  
  preview.style.display = 'block';
  
  // 处理历史项点击
  preview.querySelectorAll('[data-search-history]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const query = btn.dataset.searchHistory;
      input.value = query;
      input.form?.submit();
    });
  });
  
  // 处理清除历史
  document.getElementById('clear-search-history')?.addEventListener('click', (e) => {
    e.preventDefault();
    searchHistory.clear();
    showSearchHistory(input, preview);
  });
}

// ======================== 高级搜索 ========================
export function setupAdvancedSearch() {
  const advancedSearchBtn = document.querySelector('[data-advanced-search-toggle]');
  const advancedSearchPanel = document.querySelector('[data-advanced-search-panel]');
  
  if (!advancedSearchBtn || !advancedSearchPanel) return;
  
  advancedSearchBtn.addEventListener('click', () => {
    advancedSearchPanel.classList.toggle('hidden');
  });
  
  // 处理高级搜索表单提交
  const form = advancedSearchPanel?.querySelector('form');
  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const formData = new FormData(form);
      const params = new URLSearchParams(formData);
      window.location.href = `/search/?${params.toString()}`;
    });
  }
}

// ======================== 搜索提交保存历史 ========================
export function setupSearchFormTracking() {
  const searchForms = document.querySelectorAll('[data-search-form]');
  
  searchForms.forEach(form => {
    form.addEventListener('submit', (e) => {
      const input = form.querySelector('input[name="q"]');
      if (input) {
        searchHistory.add(input.value);
      }
    });
  });
}

// ======================== 关键词高亮 ========================
export function highlightSearchTerms(query) {
  if (!query) return;
  
  const results = document.querySelectorAll('[data-search-result-content]');
  const regex = new RegExp(`(${query})`, 'gi');
  
  results.forEach(result => {
    result.innerHTML = result.innerHTML.replace(regex, '<mark class="bg-yellow-200/60 dark:bg-yellow-900/40 px-0.5">$1</mark>');
  });
}

// ======================== 初始化所有搜索功能 ========================
export function initSearchEnhancements() {
  setupSearchPreview();
  setupAdvancedSearch();
  setupSearchFormTracking();
  
  // 从URL参数提取搜索词进行高亮
  const params = new URLSearchParams(window.location.search);
  const query = params.get('q');
  if (query) {
    highlightSearchTerms(query);
  }
  
  console.log('[v0] Search enhancements initialized');
}

// ======================== 工具函数 ========================
export { searchHistory };
