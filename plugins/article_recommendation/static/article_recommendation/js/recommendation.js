/**
 * 文章推荐插件JavaScript
 */

(function() {
    'use strict';
    
    // 等待DOM加载完成
    document.addEventListener('DOMContentLoaded', function() {
        initRecommendations();
    });
    
    function initRecommendations() {
        // 添加点击统计
        trackRecommendationClicks();
        
        // 懒加载优化（如果需要）
        lazyLoadRecommendations();
    }
    
    function trackRecommendationClicks() {
        const recommendationLinks = document.querySelectorAll('.recommendation-item a');
        
        recommendationLinks.forEach(function(link) {
            link.addEventListener('click', function(e) {
                // 可以在这里添加点击统计逻辑
                const articleTitle = this.textContent.trim();
                const articleUrl = this.href;
                
                // 发送统计数据到后端（可选）
                if (typeof gtag !== 'undefined') {
                    gtag('event', 'click', {
                        'event_category': 'recommendation',
                        'event_label': articleTitle,
                        'value': 1
                    });
                }
                
                console.log('Recommendation clicked:', articleTitle, articleUrl);
            });
        });
    }
    
    function lazyLoadRecommendations() {
        // 如果推荐内容很多，可以实现懒加载
        const recommendationContainer = document.querySelector('.article-recommendations');
        
        if (!recommendationContainer) {
            return;
        }
        
        // 检查是否在视窗中
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('loaded');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1
        });
        
        const recommendationItems = document.querySelectorAll('.recommendation-item');
        recommendationItems.forEach(function(item) {
            observer.observe(item);
        });
    }
    
    // 添加一些动画效果
    function addAnimations() {
        const recommendationItems = document.querySelectorAll('.recommendation-item');
        
        recommendationItems.forEach(function(item, index) {
            item.style.opacity = '0';
            item.style.transform = 'translateY(20px)';
            item.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            
            setTimeout(function() {
                item.style.opacity = '1';
                item.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }
    
    // 如果需要，可以在这里添加更多功能
    window.ArticleRecommendation = {
        init: initRecommendations,
        track: trackRecommendationClicks,
        animate: addAnimations
    };
    
})();
