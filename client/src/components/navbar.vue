<script>
export default {
  name: 'Navbar',
  data: () => ({
    links: [
        {link: '#', text: 'Profile'},
        {link: '#', text: 'Settings'},
        {link: '#', text: 'Feedback'},
        {link: '#', text: 'Rules'},
    ]
  })
}
</script>

<template lang="html">
  <nav class="navbar">
    <div
        class="navlink"
        v-for="item in links"
    >
      <a href="#" class="navlink__link"></a>
      <span class="navlink__text">{{ item.text }}</span>
    </div>
  </nav>
</template>

<style lang="scss">
  .navbar {
    font: 16px sans-serif;

    .navlink {
      margin: 0 0 16px;

      &:last-child {
        margin: 0;
      }
    }
  }
</style>
