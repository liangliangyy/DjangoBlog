/**
 * 图片灯箱组件
 * 点击文章内容中的图片可以查看大图
 */
export default function imageLightbox() {
  return {
    showLightbox: false,
    currentImage: '',
    currentAlt: '',

    init() {
      // 为所有文章内容中的图片添加点击事件
      this.$nextTick(() => {
        const images = document.querySelectorAll('.entry-content img');
        images.forEach(img => {
          // 排除badge图片和小图片（不需要查看大图）
          const isBadge = img.src.includes('badge.svg') ||
                         img.src.includes('shields.io') ||
                         img.src.includes('/badge/') ||
                         img.alt.toLowerCase().includes('badge');

          // 排除小于200px的图片
          const isSmallImage = img.naturalWidth < 200 || img.naturalHeight < 200;

          if (!isBadge && !isSmallImage) {
            img.addEventListener('click', (e) => {
              e.preventDefault();
              this.openLightbox(img.src, img.alt || '');
            });
          }
        });
      });
    },

    openLightbox(src, alt) {
      this.currentImage = src;
      this.currentAlt = alt;
      this.showLightbox = true;
      document.body.style.overflow = 'hidden';
    },

    closeLightbox() {
      this.showLightbox = false;
      document.body.style.overflow = '';
    },

    handleKeydown(e) {
      if (e.key === 'Escape') {
        this.closeLightbox();
      }
    }
  };
}
