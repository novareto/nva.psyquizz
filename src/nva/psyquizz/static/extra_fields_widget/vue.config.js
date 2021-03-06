// vue.config.js
const path = require('path');
module.exports = {
    lintOnSave: false,
    productionSourceMap: false,
    configureWebpack: config => {
        if (process.env.NODE_ENV === 'production') {
            config.output.filename = '[name].js';
        }
    }
}
