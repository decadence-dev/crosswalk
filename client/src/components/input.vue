<script>
export default {
  inheritAttrs: false,
  name: 'Input',
  props: {
    name: {
      type: String,
      required: true,
    },
    value: String,
    placeholder: String,
  },
  model: {
    prop: 'value',
    event: 'update',
  },
};
</script>

<template lang="html">
  <input
      type="text"
      class="input"
      v-on="$listeners"
      @input="$emit('update', $event.target.value)"
      :name="name"
      :value="value"
      :placeholder="placeholder"
  >
</template>

<style lang="scss">
@import "../styles/variables";

.input {
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid $yellow;
  background-color: transparent;
  font: $input;
  color: $white;

  &:focus {
    outline: none;
    box-shadow: 0 0 0 2px $black, 0 0 0 4px $grey;
  }

  &::placeholder {
    color: $grey;
  }
}
</style>
