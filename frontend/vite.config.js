import { defineConfig } from 'vite';
import path from 'path';

export default defineConfig({
  // 构建配置
  build: {
    // 输出目录 - 直接输出到Django的static目录
    outDir: '../blog/static/blog/dist',
    // 清空输出目录
    emptyOutDir: true,
    // 生成manifest文件，方便Django引用
    manifest: true,
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, 'src/main.js'),
        styles: path.resolve(__dirname, 'src/styles/main.css'),
      },
      output: {
        // 资源文件命名
        entryFileNames: 'js/[name]-[hash].js',
        chunkFileNames: 'js/[name]-[hash].js',
        assetFileNames: (assetInfo) => {
          // CSS文件放在css目录
          if (assetInfo.name.endsWith('.css')) {
            return 'css/[name]-[hash][extname]';
          }
          // 其他资源放在assets目录
          return 'assets/[name]-[hash][extname]';
        },
      },
    },
    // 压缩配置
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // 生产环境移除console
      },
    },
  },

  // 开发服务器配置
  server: {
    port: 5173,
    host: true,
    // CORS配置，允许Django访问
    cors: true,
    // HMR配置
    hmr: {
      overlay: true,
    },
  },

  // 路径解析
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      '@components': path.resolve(__dirname, 'src/components'),
      '@styles': path.resolve(__dirname, 'src/styles'),
    },
  },

  // CSS配置
  css: {
    postcss: './postcss.config.js',
  },
});
