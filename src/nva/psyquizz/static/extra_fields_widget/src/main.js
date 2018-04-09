import Vue from 'vue'
import ExtraFieldsWidget from './ExtraFieldsWidget.vue'
import vueCustomElement from 'vue-custom-element'
import 'document-register-element/build/document-register-element';


Vue.use(vueCustomElement)
Vue.config.productionTip = false


Vue.config.ignoredElements = [
  'extra-fields-widget'
];


Vue.customElement('extra-fields-widget', ExtraFieldsWidget, {
  // Additional Options: https://github.com/karol-f/vue-custom-element#options
});
