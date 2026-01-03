export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
    // 生产环境 CSS 压缩
    ...(process.env.NODE_ENV === 'production' ? {
      cssnano: {
        preset: ['advanced', {
          // 最激进的优化
          discardComments: { removeAll: true },
          // 规范化显示值
          normalizeDisplayValues: true,
          // 规范化位置
          normalizePositions: true,
          // 规范化重复样式
          normalizeRepeatStyle: true,
          // 规范化字符串
          normalizeString: true,
          // 规范化时间
          normalizeTiming: true,
          // 规范化 Unicode
          normalizeUnicode: true,
          // 规范化 URL
          normalizeUrl: true,
          // 规范化空白
          normalizeWhitespace: true,
          // 合并长手属性
          mergeLonghand: true,
          // 合并规则
          mergeRules: true,
          // 最小化选择器
          minifySelectors: true,
          // 最小化字体值
          minifyFontValues: true,
          // 最小化渐变
          minifyGradients: true,
          // 最小化参数
          minifyParams: true,
          // 转换颜色为最短形式
          colormin: true,
          // 转换字体粗细
          convertValues: true,
          // 丢弃重复项
          discardDuplicates: true,
          // 丢弃空规则
          discardEmpty: true,
          // 丢弃覆盖的声明
          discardOverridden: true,
          // 丢弃未使用的规则
          discardUnused: true,
          // 合并媒体查询
          mergeMedia: true,
          // 减少初始值
          reduceInitial: true,
          // 减少变换
          reduceTransforms: true,
          // SVG 优化
          svgo: {
            encode: true,
            plugins: [
              { removeViewBox: false },
              { cleanupIDs: true }
            ]
          },
          // Z-index 优化
          zindex: true,
          // 排序属性
          cssDeclarationSorter: { order: 'smacss' }
        }]
      }
    } : {})
  },
};
