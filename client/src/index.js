import Vue from 'vue';
import Vuex from 'vuex';

import App from './app.vue';
import store from './store';

Vue.use(Vuex);

const appStore = new Vuex.Store(store);

new Vue({ // eslint-disable-line no-new
  el: '#app',
  store: appStore,
  render: (h) => h(App),
});
