import VueRouter from 'vue-router';
import Map from './views/map.vue';
import EventForm from './views/event-form.vue';
import Event from './views/event.vue';

export default new VueRouter({
  mode: 'history',
  routes: [
    {
      name: 'map',
      path: '/',
      component: Map,
      children: [
        { name: 'create', path: '/create', component: EventForm },
        { name: 'detail', path: '/:id', component: Event },
      ],
    },
  ],
});
