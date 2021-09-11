<script>
export default {
  name: "Input",
  props: {
    name: {
      type: String,
      required: true
    },
    value: String,
    placeholder: String
  },
  model: {
    prop: 'value',
    event: 'update'
  }
}
</script>

<template lang="html">
  <input :name="name" :placeholder="placeholder" class="input" type="text">
</template>

<style lang="scss">
@import "../../styles/variables";
.input {
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid $yellow;
  background-color: transparent;
  font: 14px sans-serif;
  color: white;

  &:focus {
    outline: none;
  }

  &::placeholder {
    color: $grey;
  }
}
</style>
