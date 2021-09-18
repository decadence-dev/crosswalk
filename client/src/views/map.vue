<script>
import { mapState } from 'vuex';
import MenuIcon from '../icons/menu.vue';
import NotificationsIcon from '../icons/notifications.vue';
import CloseIcon from '../icons/close.vue';
import DashIcon from '../icons/dash.vue';
import Navbar from '../components/navbar.vue';
import Input from '../components/input.vue';
import Button from '../components/button.vue';

export default {
  name: 'Map',
  components: {
    Input, Button, Navbar, MenuIcon, CloseIcon, NotificationsIcon, DashIcon,
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
    <div
        class="events-list"
        v-bind:class="{ 'events-list_opened': isEventsListOpened }"
    >
      <div
          class="events-list__header"
          v-on:click="isEventsListOpened = !isEventsListOpened"
      >
        <DashIcon></DashIcon>
      </div>
      <form
          class="searchbar"
          @submit="searchSubmit"
      >
        <Input
            v-model="query.search"
            name="search"
            placeholder="Enter address or event name"
        />
      </form>
      <div
          class="items"
          v-show="hasEvents"
      >
        <div
            class="item"
            v-bind:key="event.id"
            v-for="event in events"
        >
          <span class="item__name">
            {{ event.name }}
          </span>
          <span class="item__address">
            {{ event.address }}
          </span>
        </div>
        <div class="items__fetch-more">
          <Button
              v-show="this.$store.state.hasNextPage"
              @click.native="fetchMore"
          >
            Fetch more
          </Button>
        </div>
      </div>
      <span v-show="!hasEvents" class="events-list__empty">No events found</span>
    </div>
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

.events-list {
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

  &__empty {
    font: $main;
    color: $yellow;
    text-align: center;
  }

  .searchbar {
    position: relative;
    display: flex;
    flex-flow: column;
    align-items: stretch;
    padding: 24px 16px;
    margin: 0;
  }

  .items {
    display: flex;
    flex-flow: column;
    overflow-y: scroll;

    .item {
      display: flex;
      flex-flow: column nowrap;
      margin: 8px 0 0;
      padding: 4px 16px;

      &:hover {
        background-color: $yellow;

        & > span {
          color: $black;
        }
      }

      &:first-child {
        margin: 0;
      }

      &__name {
        display: block;
        margin: 0 0 4px 0;
        color: $yellow;
      }

      &__address {
        font-size: 12px;
      }
    }

    .items__fetch-more {
      display: flex;
      flex-flow: column;
      align-items: center;
      margin: 24px 0 0;
    }
  }
}
</style>
