/** @type {import('tailwindcss').Config} */
export default {
  // 扫描这些文件以提取使用的CSS类
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "../templates/**/*.html",
    "../blog/templates/**/*.html",
    "../accounts/templates/**/*.html",
    "../comments/templates/**/*.html",
    "../oauth/templates/**/*.html",
  ],

  // 深色模式配置 - 使用 data-theme 属性，与 dark_mode 插件配合
  darkMode: ['selector', '[data-theme="dark"]'],

  theme: {
    extend: {
      // 自定义颜色，使用CSS变量支持动态主题
      colors: {
        primary: {
          50: 'rgb(var(--color-primary-50) / <alpha-value>)',
          100: 'rgb(var(--color-primary-100) / <alpha-value>)',
          200: 'rgb(var(--color-primary-200) / <alpha-value>)',
          300: 'rgb(var(--color-primary-300) / <alpha-value>)',
          400: 'rgb(var(--color-primary-400) / <alpha-value>)',
          500: 'rgb(var(--color-primary-500) / <alpha-value>)',
          600: 'rgb(var(--color-primary-600) / <alpha-value>)',
          700: 'rgb(var(--color-primary-700) / <alpha-value>)',
          800: 'rgb(var(--color-primary-800) / <alpha-value>)',
          900: 'rgb(var(--color-primary-900) / <alpha-value>)',
        },
      },

      // Z-index 层级定义
      zIndex: {
        'modal': '9999',  // 深色模式按钮等固定元素
      },

      // 字体家族
      fontFamily: {
        sans: ['Open Sans', 'Helvetica Neue', 'Helvetica', 'Arial', 'sans-serif'],
        mono: ['Consolas', 'Monaco', 'Courier New', 'monospace'],
      },

      // 容器最大宽度，与现有布局一致
      maxWidth: {
        'site': '1040px',
      },

      // 动画
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
      },

      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },

  plugins: [
    require('@tailwindcss/typography'),
  ],
};
