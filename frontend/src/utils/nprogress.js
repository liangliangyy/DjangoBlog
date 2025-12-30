/**
 * 简化版 NProgress 进度条
 * 保留原有功能
 */

const NProgress = {
  settings: {
    minimum: 0.08,
    easing: 'ease',
    speed: 200,
    trickle: true,
    trickleSpeed: 200,
    showSpinner: true,
  },

  status: null,

  configure(options) {
    Object.assign(this.settings, options);
    return this;
  },

  set(n) {
    const started = this.isStarted();
    n = this.clamp(n, this.settings.minimum, 1);
    this.status = n === 1 ? null : n;

    const progress = this.render(!started);
    const bar = progress.querySelector('.bar');
    const speed = this.settings.speed;
    const ease = this.settings.easing;

    progress.offsetWidth; // Repaint

    this.queue((next) => {
      bar.style.transition = `all ${speed}ms ${ease}`;
      bar.style.width = n * 100 + '%';

      if (n === 1) {
        progress.style.transition = `all ${speed}ms ${ease}`;
        progress.style.opacity = '0';
        setTimeout(() => {
          this.remove();
          next();
        }, speed);
      } else {
        setTimeout(next, speed);
      }
    });

    return this;
  },

  isStarted() {
    return typeof this.status === 'number';
  },

  start() {
    if (!this.status) this.set(0);

    const work = () => {
      setTimeout(() => {
        if (!this.status) return;
        this.trickle();
        work();
      }, this.settings.trickleSpeed);
    };

    if (this.settings.trickle) work();

    return this;
  },

  done(force) {
    if (!force && !this.status) return this;
    return this.inc(0.3 + 0.5 * Math.random()).set(1);
  },

  inc(amount) {
    let n = this.status;

    if (!n) {
      return this.start();
    }

    if (typeof amount !== 'number') {
      amount = (1 - n) * this.clamp(Math.random() * n, 0.1, 0.95);
    }

    n = this.clamp(n + amount, 0, 0.994);
    return this.set(n);
  },

  trickle() {
    return this.inc(Math.random() * 0.02);
  },

  render(fromStart) {
    if (this.isRendered()) return document.getElementById('nprogress');

    const progress = document.createElement('div');
    progress.id = 'nprogress';
    progress.innerHTML = '<div class="bar"><div class="peg"></div></div>';

    const bar = progress.querySelector('.bar');
    const perc = fromStart ? 0 : (this.status || 0) * 100;

    bar.style.transition = 'none';
    bar.style.width = perc + '%';

    if (!this.settings.showSpinner) {
      const spinner = progress.querySelector('.spinner');
      spinner && spinner.remove();
    }

    document.body.appendChild(progress);
    return progress;
  },

  remove() {
    const progress = document.getElementById('nprogress');
    progress && progress.remove();
  },

  isRendered() {
    return !!document.getElementById('nprogress');
  },

  clamp(n, min, max) {
    if (n < min) return min;
    if (n > max) return max;
    return n;
  },

  toBarPerc(n) {
    return (-1 + n) * 100;
  },

  queue: (function () {
    const pending = [];

    function next() {
      const fn = pending.shift();
      if (fn) fn(next);
    }

    return function (fn) {
      pending.push(fn);
      if (pending.length === 1) next();
    };
  })(),
};

export default NProgress;
