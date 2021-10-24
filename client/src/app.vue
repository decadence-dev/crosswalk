<script>
import Vue from 'vue';
import VueRouter from 'vue-router';
import router from './router';

Vue.use(VueRouter);

export default {
  name: 'App',
  router,
};
</script>

<template>
  <router-view></router-view>
</template>
