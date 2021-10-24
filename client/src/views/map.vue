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
    errors() {
      return this.$store.state.globalErrors;
    },
    hasErrors() {
      return this.$store.state.globalErrors != null;
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
    resolveError(errorMessage) {
      this.$store.dispatch('resolveErrors', [errorMessage]);
    },
  },
  mounted() {
    this.login();
    this.$store.dispatch('getEvents', { first: 10 });
    document.cookie = `timezone=${Intl.DateTimeFormat().resolvedOptions().timeZone}`;
  },
};
</script>

<template lang="html">
  <div class="map">
    <div class="errors">
      <span
          class="error"
          v-show="hasErrors"
          v-for="(error, idx) in errors"
          :key="idx"
          @click="resolveError(error)"
      >{{ error }}</span>
    </div>
    <router-link
        :to="{ name: 'create' }"
        v-slot="{href, navigate}"
        custom
    >
      <a class="creation__link" :href="href" @click="navigate"></a>
    </router-link>
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

  .creation__link {
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
  }
}

.errors {
  z-index: 10;
  position: absolute;
  align-self: center;
  display: flex;
  flex-flow: column;
  right: 0;
  left: 0;
  padding: 16px 0 0;
  align-items: center;

  .error {
    padding: 8px;
    margin: 8px 0 0;
    color: $white;
    background-color: $red;
    max-width: 224px;
    font: $help;

    &:first-child {
      margin: 0;
    }
  }
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

  &_opened {
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
  max-height: calc(100% - 56px);
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
