<script>
import RobberyIcon from '../icons/robbery.vue';
import FightIcon from '../icons/fight.vue';
import DeathIcon from '../icons/death.vue';
import GunrireIcon from '../icons/gunfire.vue';
import InsaneIcon from '../icons/insane.vue';
import AccidentIcon from '../icons/accident.vue';
import FireIcon from '../icons/fire.vue';
import PoliceIcon from '../icons/police.vue';

export default {
  inheritAttrs: false,
  name: 'EventType',
  components: {
    RobberyIcon, FightIcon, DeathIcon, GunrireIcon, InsaneIcon, AccidentIcon, FireIcon, PoliceIcon,
  },
  data: () => ({
    selectedType: null,
    types: [
      { name: 'ROBERRY', icon: 'RobberyIcon' },
      { name: 'FIGHT', icon: 'FightIcon' },
      { name: 'DEATH', icon: '' },
      { name: 'GUN', icon: 'GunrireIcon' },
      { name: 'INADEQUATE', icon: 'InsaneIcon' },
      { name: 'ACCEDENT', icon: 'AccidentIcon' },
      { name: 'FIRE', icon: 'FireIcon' },
      { name: 'POLICE', icon: 'PoliceIcon' },
    ],
  }),
  props: {
    name: {
      type: String,
      required: true,
    },
    value: String,
  },
  computed: {
    selected: {
      get() {
        return this.selectedType !== null ? this.selectedType : this.value || null;
      },
      set(value) {
        this.selectedType = value;
      },
    },
  },
  methods: {
    selectType(type) {
      this.selected = type;
      this.$emit('input', type);
    },
  },
};
</script>

<template lang="html">
  <div class="eventtype" v-on:focusout="$emit('blur', $event)" tabindex="0">
    <div
        class="eventtype__option"
        v-for="(type, idx) in types"
        v-bind:key="idx"
        v-bind:class="{ 'eventtype__option_selected': type.name === selected }"
        @click="selectType(type.name)"
    >
      <component class="eventtype__option-icon" v-bind:is="type.icon"></component>
    </div>
  </div>
</template>

<style lang="scss">
@import "../styles/variables";

.eventtype {
  display: flex;
  flex-flow: row;
  border-radius: 8px;
  border: 1px solid $yellow;
  padding: 4px 16px;

  &:focus {
    outline: none;
    box-shadow: 0 0 0 2px $black, 0 0 0 4px $grey;
  }

  &__option {
    margin: 0 8px 0 0;

    &:last-child {
      margin: 0;
    }

    &-icon {
      fill: $yellow;
    }

    &_selected {
      background-color: $yellow;
      border-radius: 16px;

      .eventtype__option-icon {
        fill: $black;
      }
    }
  }
}

</style>
