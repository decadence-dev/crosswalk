<script>
import { mapState } from 'vuex';
import MenuIcon from '../icons/menu.vue';
import NotificationsIcon from '../icons/notifications.vue';
import CloseIcon from '../icons/close.vue';
import DashIcon from '../icons/dash.vue';
import Navbar from '../components/navbar.vue';
import EventsList from '../components/events-list.vue';

export default {
  name: 'Map',
  components: {
    EventsList, Navbar, MenuIcon, CloseIcon, NotificationsIcon, DashIcon,
  },
  data: () => ({
    isMenuOpened: false,
    isEventsListOpened: false,
  }),
  computed: {
    ...mapState({
      events: (state) => state.events,
    }),
    hasEvents: {
      get() {
        return this.$store.state.events.length !== 0;
      },
    },
    query: {
      get() {
        return this.$route.query || {};
      },
      set(value) {
        this.query = value;
      },
    },
  },
  methods: {
    login() {
      fetch('http://localhost:8000/token', { method: 'POST' })
        .then((response) => {
          response.json().then((data) => {
            localStorage.setItem('token', data);
          });
        });
    },
    searchSubmit(e) {
      e.preventDefault();
      this.$store.dispatch(
        'getEvents',
        { ...this.query, first: 10 },
      );
    },
    fetchMore(e) {
      e.preventDefault();
      this.$store.dispatch(
        'fetchMoreEvents',
        {
          ...this.query,
          after: this.$store.state.endCursor,
          first: 10,
        },
      );
    },
  },
  mounted() {
    this.login();
    this.$store.dispatch('getEvents', { first: 10 });
  },
};
</script>

<template lang="html">
  <div class="map">
    <div class="header">
      <div
          class="menu-btn"
          v-on:click="isMenuOpened = !isMenuOpened"
      >
        <MenuIcon v-if="!isMenuOpened"></MenuIcon>
        <CloseIcon v-if="isMenuOpened"></CloseIcon>
      </div>
      <NotificationsIcon></NotificationsIcon>
    </div>
    <aside
        class="menu"
        v-bind:class="{ menu_opened: isMenuOpened }"
    >
      <Navbar></Navbar>
    </aside>
    <router-view></router-view>
    <aside
        class="events-sidebar"
        v-bind:class="{ 'events-sidebar_opened': isEventsListOpened }"
    >
      <div
          class="events-sidebar__header"
          v-on:click="isEventsListOpened = !isEventsListOpened"
      >
        <DashIcon></DashIcon>
      </div>
      <EventsList></EventsList>
    </aside>
    <router-view></router-view>
  </div>
</template>

<style lang="scss">
@import "src/styles/variables";

.map {
  position: relative;
  display: flex;
  flex-flow: column wrap;
  flex: 1 0 auto;
  max-width: 100%;
  background-color: $black;
}

.header {
  z-index: 1000;
  position: absolute;
  display: flex;
  justify-content: space-between;
  top: 16px;
  left: 16px;
  right: 16px;
  fill: $yellow;
}

.menu {
  z-index: 100;
  display: none;
  height: 100%;
  padding: 56px 16px;
  text-align: center;
  background-color: $black;

  &_opened{
    display: block;
  }
}

.events-sidebar {
  position: absolute;
  display: flex;
  flex-flow: column;
  bottom: 0;
  width: 100%;
  height: 48px;
  max-height: calc(100% - 56px);;
  padding: 0 0 32px;
  border-radius: 8px 8px 0 0;
  background-color: $black;
  overflow: hidden;

  &_opened {
    height: calc(100% - 56px);
  }

  &__header {
    position: relative;
    display: flex;
    padding: 12px 0;
    align-items: center;
    justify-content: center;
    background-color: $yellow;
  }
}
</style>
