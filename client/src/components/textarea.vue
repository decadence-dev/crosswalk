<script>
import ResizeIcon from '../icons/resize.vue';

export default {
  inheritAttrs: false,
  name: 'Textarea',
  components: { ResizeIcon },
  props: {
    name: {
      type: String,
      required: true,
    },
    label: String,
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
  <div class="textarea">
    <ResizeIcon class="textarea__resize"></ResizeIcon>
    <textarea
        class="textarea__element"
        v-on="$listeners"
        @input="$emit('update', $event.target.value)"
        :name="name"
        :value="value"
        :placeholder="placeholder"
    ></textarea>
  </div>
</template>

<style lang="scss">
@import "../styles/variables";

.textarea {
  position: relative;
  fill: $yellow;

  .textarea__element {
    padding: 8px 12px;
    border-radius: 8px;
    border: 1px solid $yellow;
    background-color: transparent;
    font: $input;
    color: $white;
    resize: vertical;
    width: 100%;
    min-height: 64px;
    max-height: 128px;

    &:focus {
      outline: none;
      box-shadow: 0 0 0 2px $black, 0 0 0 4px $grey;
    }

    &::placeholder {
      color: $grey;
    }
  }

  .textarea__resize {
    position: absolute;
    bottom: 6px;
    right: 6px;
  }
}
</style>
