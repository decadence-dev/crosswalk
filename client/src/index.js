import Vue from 'vue';
import Vuex from 'vuex';

import App from './app.vue';
import store from './store';

Vue.use(Vuex);

new Vue({ // eslint-disable-line no-new
  el: '#app',
  store: new Vuex.Store(store),
  render: (h) => h(App),
});
