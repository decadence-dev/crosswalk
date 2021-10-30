<script>
export default {
  inheritAttrs: false,
  name: 'Button',
};
</script>

<template lang="html">
  <button class="button">
    <slot/>
  </button>
</template>

<style lang="scss">
@import "../styles/variables";

.button {
  width: fit-content;
  padding: 8px 16px;
  border-radius: 8px;
  background-color: $yellow;
  font: $help;
  color: $black;
  border: none;

  &:focus {
    outline: none;
    box-shadow: 0 0 0 2px $black, 0 0 0 4px $grey;
  }
}
</style>
