<script>
import MenuIcon from './icons/menu'
import NotificationsIcon from './icons/notifications'
import CloseIcon from './icons/close'
import DashIcon from './icons/dash'
import Navbar from './navbar'

export default {
  name: 'Map',
  components: {Navbar, MenuIcon, CloseIcon, NotificationsIcon, DashIcon},
  data: () => ({
    isMenuOpened: false,
    isEventsListOpened: false
  })
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
    position: absolute;
    display: flex;
    justify-content: space-between;
    top: 16px;
    left: 16px;
    right: 16px;
  }

  .menu {
    display: none;
    height: 100%;
    padding: 56px 16px;
    text-align: center;

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
  }
</style>
