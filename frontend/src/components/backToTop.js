/**
 * 回到顶部组件
 * 使用 IntersectionObserver 代替 scroll 事件，避免强制 reflow
 */

export default () => ({
  isVisible: false,
  isAnimating: false,
  _sentinel: null,
  _observer: null,
  handleScroll: null,

  init() {
    if ('IntersectionObserver' in window) {
      // 在文档顶部 200px 处插入 1px 哨兵元素
      // 哨兵离开视口时说明已滚动超过 200px，显示按钮
      this._sentinel = document.createElement('div');
      this._sentinel.style.cssText = 'position:absolute;top:200px;left:0;width:1px;height:1px;pointer-events:none;visibility:hidden;';
      document.body.prepend(this._sentinel);

      this._observer = new IntersectionObserver(([entry]) => {
        this.isVisible = !entry.isIntersecting;
      });
      this._observer.observe(this._sentinel);
    } else {
      // 降级：passive scroll + rAF 批处理，避免布局抖动
      let ticking = false;
      this.handleScroll = () => {
        if (!ticking) {
          requestAnimationFrame(() => {
            this.isVisible = window.scrollY > 200;
            ticking = false;
          });
          ticking = true;
        }
      };
      window.addEventListener('scroll', this.handleScroll, { passive: true });
      this.isVisible = window.scrollY > 200;
    }
  },

  destroy() {
    this._observer?.disconnect();
    this._sentinel?.remove();
    if (this.handleScroll) {
      window.removeEventListener('scroll', this.handleScroll);
    }
  },

  scrollToTop() {
    if (this.isAnimating) return;
    this.isAnimating = true;
    window.scrollTo({ top: 0, behavior: 'smooth' });
    const rocket = this.$el;
    rocket.classList.add('move');
    setTimeout(() => {
      rocket.classList.remove('move');
      this.isAnimating = false;
    }, 800);
  },
});
