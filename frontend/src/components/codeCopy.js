/**
 * 代码块复制按钮
 * 在 .article.prose pre 中注入复制按钮，支持 HTMX 导航后重新初始化
 */

const COPY_SVG = '<svg class="size-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg><span>复制</span>';
const CHECK_SVG = '<svg class="size-3 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg><span>已复制</span>';

function initCodeCopy(root) {
  const scope = root || document;
  scope.querySelectorAll('.article.prose pre').forEach(function (pre) {
    if (pre.querySelector('.copy-code-btn')) return;
    var btn = document.createElement('button');
    btn.className = 'copy-code-btn absolute right-2 top-2 flex items-center gap-1 rounded-md border border-border/60 bg-card/80 px-2 py-1 text-[11px] text-muted-foreground backdrop-blur-sm transition-all hover:border-primary/40 hover:text-primary opacity-0 group-hover/pre:opacity-100';
    btn.innerHTML = COPY_SVG;
    btn.setAttribute('aria-label', '复制代码');
    pre.classList.add('relative', 'group/pre');
    pre.appendChild(btn);
    btn.addEventListener('click', function () {
      var code = pre.querySelector('code');
      var text = code ? code.innerText : pre.innerText;
      navigator.clipboard.writeText(text).then(function () {
        btn.innerHTML = CHECK_SVG;
        btn.classList.add('opacity-100');
        setTimeout(function () {
          btn.innerHTML = COPY_SVG;
          btn.classList.remove('opacity-100');
        }, 2000);
      });
    });
  });
}

export function initCodeCopyFeature() {
  // 初始页面
  initCodeCopy();
  // HTMX boost 导航后重新初始化
  document.body.addEventListener('htmx:afterSwap', function () {
    initCodeCopy();
  });
}
