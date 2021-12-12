<script>
import { mapState } from 'vuex';
import CloseIcon from '../icons/close.vue';
import OptionsIcon from '../icons/options.vue';
import EditIcon from '../icons/edit.vue';
import TrashIcon from '../icons/trash.vue';

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
  data: () => ({
    isOptionsOpen: false,
  }),
  components: {
    TrashIcon, EditIcon, CloseIcon, OptionsIcon,
  },
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
      this.$store.dispatch('GET_EVENT', { id: this.$route.params.id });
    },
    deleteEvent() {
      this.$store.dispatch('deleteEvent', { id: this.$route.params.id });
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
    <div class="options">
      <div
          class="options__button"
          v-bind:class="{options__button_active: isOptionsOpen}"
          @click="isOptionsOpen = !isOptionsOpen"
      >
        <OptionsIcon class="options__button-icon"></OptionsIcon>
      </div>
      <div v-show="isOptionsOpen" class="options__list">
        <div class="option">
          <router-link
              :to="{ name: 'update', params: { id: event.id } }"
              v-slot="{href, navigate}"
              custom
          >
            <a :href="href" class="option__link" @click="navigate"></a>
          </router-link>
          <EditIcon class="option__icon"></EditIcon>
          <span class="option__text">Update</span>
        </div>
        <div class="option option_danger" @click="deleteEvent">
          <TrashIcon class="option__icon"></TrashIcon>
          <span class="option__text">Delete</span>
        </div>
      </div>
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
    display: flex;
    flex-flow: column;
    align-items: flex-end;
    top: 72px;
    right: 16px;
    cursor: pointer;

    &__button {
      &-icon {
        fill: $yellow;
      }

      &_active {
        border-radius: 8px;
        background-color: $yellow;

        .options__button-icon {
          fill: $black;
        }
      }
    }

    &__list {
      margin: 6px 0 0;
      position: relative;
      display: flex;
      flex-flow: column;
      border-radius: 8px;
      border: 1px solid $yellow;
      background-color: $black;
      min-width: 128px;

      &::before {
        content: "";
        position: absolute;
        border-bottom: 6px solid $yellow;
        border-left: 6px solid transparent;
        border-right: 6px solid transparent;
        right: 5px;
        top: -6px;
      }

      .option {
        position: relative;
        display: flex;
        align-items: center;
        text-decoration: none;
        padding: 4px 8px;

        &__link {
          position: absolute;
          top: 0;
          right: 0;
          left: 0;
          bottom: 0;
        }

        &__icon {
          margin: 0 4px 0 0;
          fill: $yellow;
        }

        &__text {
          color: $white;
          font: $help;
        }

        &_danger {
          .option__icon {
            fill: $red;
          }

          .option__text {
            color: $red;
          }
        }
      }
    }
  }
}
</style>
