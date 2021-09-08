<script>
import MenuIcon from './icons/menu'
import NotificationsIcon from './icons/notifications'
import Navbar from './navbar'

export default {
  name: 'Map',
  components: {Navbar, MenuIcon, NotificationsIcon}
}
</script>

<template lang="html">
  <div class="map">
    <div class="header">
      <MenuIcon></MenuIcon>
      <NotificationsIcon></NotificationsIcon>
    </div>
    <aside class="menu">
      <Navbar></Navbar>
    </aside>
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
    margin: 56px 16px;
    text-align: center;
  }
</style>
