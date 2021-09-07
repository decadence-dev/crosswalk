<script>
import Vue from 'vue'
import VueRouter from 'vue-router'

import Map from './components/map'

Vue.use(VueRouter)

export default {
  name: 'App',
  router: new VueRouter({
    mode: 'history',
    routes: [
      {name: 'main', path: '/', component: Map}
    ]
  })
}
</script>

<template>
  <router-view></router-view>
</template>
