$(function () {
    MathJax.Hub.Config({
        showProcessingMessages: false, //关闭js加载过程信息
        messageStyle: "none", //不显示信息
        extensions: ["tex2jax.js"], jax: ["input/TeX", "output/HTML-CSS"], displayAlign: "left", tex2jax: {
            inlineMath: [["$", "$"]], //行内公式选择$
            displayMath: [["$$", "$$"]], //段内公式选择$$
            skipTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code', 'a'], //避开某些标签
        }, "HTML-CSS": {
            availableFonts: ["STIX", "TeX"], //可选字体
            showMathMenu: false //关闭右击菜单显示
        }
    });
    // 识别范围 => 文章内容、评论内容标签
    const contentId = document.getElementById("content");
    const commentId = document.getElementById("comments");
    MathJax.Hub.Queue(["Typeset", MathJax.Hub, contentId, commentId]);
})



