// vue.config.js
const path = require('path');
module.exports = {
    lintOnSave: true,
    productionSourceMap: false,
    configureWebpack: config => {
        if (process.env.NODE_ENV === 'production') {
            config.output.filename = '[name].js';
            config.output.path = path.resolve(__dirname, '../efw/');
        }
    }
}
