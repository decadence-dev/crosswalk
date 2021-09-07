import Vue from 'vue'
import Vuex from 'vuex'

import App from './app'

Vue.use(Vuex)

new Vue({
  el: '#app',
  store: new Vuex.Store({}),
  render: h => h(App)
})
