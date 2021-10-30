<script>
import { mapState } from 'vuex';
import CloseIcon from '../icons/close.vue';
import OptionsIcon from '../icons/options.vue';

const EVENT_TYPE_MAP = {
  ROBBERY: 'Robbery',
  FIGHT: 'Fight',
  DEATH: 'Death',
  GUN: 'Gun',
  INADEQUATE: 'Inadequate',
  ACCEDENT: 'Accedent',
  FIRE: 'Fire',
  POLICE: 'Police',
};

export default {
  name: 'Event',
  components: { CloseIcon, OptionsIcon },
  computed: {
    ...mapState({
      event: (state) => ({ ...state.event, eventType: EVENT_TYPE_MAP[state.event.eventType] }),
    }),
    publicationDate() {
      const { createdDate } = this.$store.state.event;
      if (createdDate !== undefined) {
        const dt = new Date(createdDate);
        const year = dt.getFullYear();
        const month = (dt.getUTCMonth() + 1).toString().padStart(2, '0');
        const day = dt.getDate().toString().padStart(2, '0');
        return `${year}.${month}.${day}`;
      }
      return '';
    },
    publicationAuthor() {
      const { createdBy } = this.$store.state.event;
      return createdBy !== undefined ? createdBy.username : '';
    },
  },
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
    <div class="event__header">
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
      <span class="info__type">{{ event.eventType }}</span>
      <span class="info__address">{{ event.address }}</span>
      <div class="publication">
        <span class="publication__author">{{ publicationAuthor }}</span>
        <span class="publication__date">{{ publicationDate }}</span>
      </div>
      <span class="info__description">{{ event.description }}</span>
    </div>
    <OptionsIcon class="options"></OptionsIcon>
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
  height: calc(100% - 56px);
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

    .close-link {
      position: absolute;
      top: 0;
      bottom: 0;
      left: 0;
      right: 0;
    }
  }

  .info {
    display: flex;
    flex-flow: column;
    padding: 24px 16px 0;

    &__type {
      font: $help;
      color: $grey;
    }

    &__address {
      font: $header;
      color: $yellow;
      margin: 8px 0 0;
    }

    &__description {
      font: $main;
      margin: 16px 0 0;
    }

    .publication {
      font: $help;
      color: $yellow;
      margin: 8px 0 0;
    }
  }

  .options {
    position: absolute;
    top: 72px;
    right: 16px;
    fill: $yellow;
  }
}
</style>
