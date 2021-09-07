<script>
import MenuIcon from './icons/menu'
import NotificationsIcon from './icons/notifications'

export default {
  name: 'Map',
  components: {MenuIcon, NotificationsIcon}
}
</script>

<template lang="html">
  <div class="map">
    <div class="header">
      <MenuIcon></MenuIcon>
      <NotificationsIcon></NotificationsIcon>
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
</style>
