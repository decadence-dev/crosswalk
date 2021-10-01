<script>
import Vue from 'vue';
import VueRouter from 'vue-router';

import Map from './views/map.vue';
import Event from './views/event.vue';

Vue.use(VueRouter);

const routes = [
  {
    name: 'map',
    path: '/',
    component: Map,
    children: [
      { name: 'event', path: '/:id', component: Event },
    ],
  },
];

export default {
  name: 'App',
  router: new VueRouter({
    mode: 'history',
    routes,
  }),
};
</script>

<template>
  <router-view></router-view>
</template>
