<script>
import MenuIcon from './icons/menu'
import NotificationsIcon from './icons/notifications'
import CloseIcon from './icons/close'
import DashIcon from './icons/dash'
import Navbar from './navbar'
import Input from './common/input'
import {mapState} from "vuex";

export default {
  name: 'Map',
  components: {Input, Navbar, MenuIcon, CloseIcon, NotificationsIcon, DashIcon},
  data: () => ({
    isMenuOpened: false,
    isEventsListOpened: false
  }),
  computed: {
    ...mapState({
      events: state => state.events
    })
  },
  methods: {
    login() {
      fetch('http://localhost:8000/token', {method: "POST"})
          .then(response => {
            response.json().then(data => {
              localStorage.setItem("token", data)
            })
          })
    }
  },
  mounted() {
    this.login()
    this.$store.dispatch('getEvents')
  }
}
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
      <div class="searchbar">
        <Input id="eventsSearch" name="search" placeholder="Enter address or event name"/>
      </div>
      <div class="items">
        <div
            class="item"
            v-for="event in events"
        >
          <span class="item__name">
            {{ event.name }}
          </span>
          <span class="item__address">
            {{ event.address }}
          </span>
        </div>
      </div>
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
    bottom: 0;
    width: 100%;
    //height: 48px;
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
      height: 48px;
      align-items: center;
      justify-content: center;
      background-color: $yellow;
    }

    .searchbar {
      display: flex;
      flex-flow: column;
      align-items: stretch;
      padding: 0 16px;
      margin: 24px 0 0;
    }

    .items {
      display: flex;
      flex-flow: column;
      margin: 24px 0 0;

      .item {
        display: flex;
        flex-flow: column nowrap;
        margin: 0 0 8px;
        padding: 4px 16px;

        &:hover {
          background-color: $yellow;

          & > span {
            color: $black;
          }
        }

        &:last-child {
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
    }
  }
</style>
