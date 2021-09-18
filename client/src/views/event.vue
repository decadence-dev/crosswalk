<script>
import { mapState } from 'vuex';
import CloseIcon from '../icons/close.vue';

export default {
  name: 'Event',
  components: { CloseIcon },
  computed: mapState({
    event: (state) => state.event,
  }),
  methods: {
    getEvent() {
      this.$store.dispatch('getEvent', { id: this.$route.params.id });
    },
  },
  mounted() {
    this.getEvent();
  },
  watch: {
    $route: 'getEvent',
  },
};
</script>

<template lang="html">
  <aside class="event">
    <div class="events-sidebar__header">
      <router-link
          :to="{name: 'map'}"
          v-slot="{href, navigate}"
          custom
      >
        <a class="close-link" :href="href" @click="navigate"></a>
      </router-link>
      <CloseIcon></CloseIcon>
    </div>
    <div class="info">
      <span class="event__name">{{ event.name }}</span>
      <span class="event__address">{{ event.address }}</span>
      <span class="event__description">{{ event.description }}</span>
    </div>
  </aside>
</template>

<style lang="scss">
@import "src/styles/variables";

.event {
  position: absolute;
  display: flex;
  flex-flow: column;
  bottom: 0;
  width: 100%;
  height: calc(100% - 56px);;
  padding: 0 0 32px;
  border-radius: 8px 8px 0 0;
  background-color: $black;
  overflow: hidden;

  &__header {
    position: relative;
    display: flex;
    padding: 12px 0;
    align-items: center;
    justify-content: center;
    background-color: $yellow;
    fill: $black;
  }

  .close-link {
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
  }
}
</style>
