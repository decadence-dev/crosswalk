<script>
export default {
  name: 'Navbar',
  data: () => ({
    links: [
      { link: '/profile', text: 'Profile' },
      { link: '/settings', text: 'Settings' },
      { link: '/feedback', text: 'Feedback' },
      { link: '/rules', text: 'Rules' },
    ],
  }),
};
</script>

<template lang="html">
  <nav class="navbar">
    <div
        class="navlink"
        v-bind:key="item.link"
        v-for="item in links"
    >
      <a href="#" class="navlink__link"></a>
      <span class="navlink__text">{{ item.text }}</span>
    </div>
  </nav>
</template>

<style lang="scss">
@import "../styles/variables";

.navbar {
  font: $main;

  .navlink {
    margin: 0 0 16px;

    &:last-child {
      margin: 0;
    }
  }
}
</style>
