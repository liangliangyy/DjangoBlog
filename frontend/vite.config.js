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
    // 压缩配置 - 最高级别
    minify: 'terser',
    terserOptions: {
      compress: {
        // 移除 console 和 debugger
        drop_console: true,
        drop_debugger: true,
        // 移除未使用的代码
        pure_funcs: ['console.log', 'console.info', 'console.debug', 'console.warn'],
        // 移除死代码
        dead_code: true,
        // 使用更激进的优化
        passes: 3,
        // 移除未使用的函数参数
        keep_fargs: false,
        // 移除未使用的函数名
        keep_fnames: false,
        // 移除未使用的类名
        keep_classnames: false,
        // 内联函数
        inline: 3,
        // 移除不可达代码
        conditionals: true,
        // 优化布尔表达式
        booleans: true,
        // 优化循环
        loops: true,
        // 合并变量声明
        join_vars: true,
        // 移除未使用的变量
        unused: true,
        // 折叠常量
        evaluate: true,
        // 优化 if 语句
        if_return: true,
        // 移除空语句
        sequences: true,
        // 压缩属性访问
        properties: true,
      },
      mangle: {
        // 混淆变量名
        toplevel: true,
        // 混淆属性名（谨慎使用）
        properties: false,
        // 保留类名（避免 Alpine.js 等框架问题）
        keep_classnames: false,
        keep_fnames: false,
        // Safari 10 兼容
        safari10: true,
      },
      format: {
        // 移除注释
        comments: false,
        // 使用 ASCII 输出
        ascii_only: true,
        // 紧凑输出
        beautify: false,
        // 压缩到极致
        ecma: 2020,
      },
    },
    // 启用 CSS 压缩
    cssMinify: true,
    // 代码分割阈值（字节）
    chunkSizeWarningLimit: 500,
    // 报告压缩后的大小
    reportCompressedSize: true,
    // Rollup 优化配置（合并后）
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, 'src/main.js'),
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
        // 手动代码分割
        manualChunks: (id) => {
          // 将 node_modules 中的包分离
          if (id.includes('node_modules')) {
            if (id.includes('alpinejs')) return 'alpine';
            if (id.includes('htmx')) return 'htmx';
            return 'vendor';
          }
        },
        // 最小化输出
        compact: true,
        // 不生成 sourcemap
        sourcemap: false,
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
