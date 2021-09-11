import Vue from 'vue'
import Vuex from 'vuex'

import App from './app'
import store from './store'

Vue.use(Vuex)

new Vue({
  el: '#app',
  store: new Vuex.Store(store),
  render: h => h(App)
})
