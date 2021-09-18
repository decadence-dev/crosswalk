<script>
import Vue from 'vue';
import VueRouter from 'vue-router';

import Map from './views/map'; // eslint-disable-line import/no-unresolved, import/extensions

Vue.use(VueRouter);

export default {
  name: 'App',
  router: new VueRouter({
    mode: 'history',
    routes: [
      { name: 'main', path: '/', component: Map },
    ],
  }),
};
</script>

<template>
  <router-view></router-view>
</template>
