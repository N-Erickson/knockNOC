const path = require('path');

module.exports = {
  outputDir: path.resolve(__dirname, '../app/static'),
  assetsDir: '',
  indexPath: '../templates/index.html',
  publicPath: '/static/',
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  },
  lintOnSave: false,  // This disables ESLint during development
  chainWebpack: config => {
    config.module.rules.delete('eslint');  // This removes the ESLint loader
  }
};