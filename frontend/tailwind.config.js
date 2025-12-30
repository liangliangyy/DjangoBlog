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
      // 自定义颜色，保持与现有设计一致
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#21759b', // 现有主题色
          600: '#1b6280',
          700: '#155166',
          800: '#0f404d',
          900: '#0a2f3a',
        },
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
