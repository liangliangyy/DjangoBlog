/**
 * MathJax 智能加载器
 * 检测页面是否包含数学公式，如果有则动态加载和配置MathJax
 */
(function() {
    'use strict';
    
    /**
     * 检测页面是否包含数学公式
     * @returns {boolean} 是否包含数学公式
     */
    function hasMathFormulas() {
        const content = document.body.textContent || document.body.innerText || '';
        // 检测常见的数学公式语法
        return /\$.*?\$|\$\$.*?\$\$|\\begin\{.*?\}|\\end\{.*?\}|\\[a-zA-Z]+\{/.test(content);
    }
    
    /**
     * 配置MathJax
     */
    function configureMathJax() {
        window.MathJax = {
            tex: {
                // 行内公式和块级公式分隔符
                inlineMath: [['$', '$']],
                displayMath: [['$$', '$$']],
                // 处理转义字符和LaTeX环境
                processEscapes: true,
                processEnvironments: true,
                // 自动换行
                tags: 'ams'
            },
            options: {
                // 跳过这些HTML标签，避免处理代码块等
                skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code', 'a'],
                // CSS类控制
                ignoreHtmlClass: 'tex2jax_ignore',
                processHtmlClass: 'tex2jax_process'
            },
            // 启动配置
            startup: {
                ready() {
                    console.log('MathJax配置完成，开始初始化...');
                    MathJax.startup.defaultReady();
                    
                    // 处理特定区域的数学公式
                    const contentEl = document.getElementById('content');
                    const commentsEl = document.getElementById('comments');
                    
                    const promises = [];
                    if (contentEl) {
                        promises.push(MathJax.typesetPromise([contentEl]));
                    }
                    if (commentsEl) {
                        promises.push(MathJax.typesetPromise([commentsEl]));
                    }
                    
                    // 等待所有渲染完成
                    Promise.all(promises).then(() => {
                        console.log('MathJax渲染完成');
                        // 触发自定义事件，通知其他脚本MathJax已就绪
                        document.dispatchEvent(new CustomEvent('mathjaxReady'));
                    }).catch(error => {
                        console.error('MathJax渲染失败:', error);
                    });
                }
            },
            // 输出配置
            chtml: {
                scale: 1,
                minScale: 0.5,
                matchFontHeight: false,
                displayAlign: 'center',
                displayIndent: '0'
            }
        };
    }
    
    /**
     * 加载MathJax库
     */
    function loadMathJax() {
        console.log('检测到数学公式，开始加载MathJax...');
        
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js';
        script.async = true;
        script.defer = true;
        
        script.onload = function() {
            console.log('MathJax库加载成功');
        };
        
        script.onerror = function() {
            console.error('MathJax库加载失败，尝试备用CDN...');
            // 备用CDN
            const fallbackScript = document.createElement('script');
            fallbackScript.src = 'https://polyfill.io/v3/polyfill.min.js?features=es6';
            fallbackScript.onload = function() {
                const mathJaxScript = document.createElement('script');
                mathJaxScript.src = 'https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-MML-AM_CHTML';
                mathJaxScript.async = true;
                document.head.appendChild(mathJaxScript);
            };
            document.head.appendChild(fallbackScript);
        };
        
        document.head.appendChild(script);
    }
    
    /**
     * 初始化函数
     */
    function init() {
        // 等待DOM完全加载
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
            return;
        }
        
        // 检测是否需要加载MathJax
        if (hasMathFormulas()) {
            // 先配置，再加载
            configureMathJax();
            loadMathJax();
        } else {
            console.log('未检测到数学公式，跳过MathJax加载');
        }
    }
    
    // 提供重新渲染的全局方法，供动态内容使用
    window.rerenderMathJax = function(element) {
        if (window.MathJax && window.MathJax.typesetPromise) {
            const target = element || document.body;
            return window.MathJax.typesetPromise([target]);
        }
        return Promise.resolve();
    };
    
    // 启动初始化
    init();
})();
