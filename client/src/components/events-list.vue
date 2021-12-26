<script>
import { mapState } from 'vuex';
import Input from './input.vue';
import Button from './button.vue';

export default {
  name: 'EventsList',
  components: {
    Input, Button,
  },
  computed: {
    ...mapState(['events']),
    hasEvents() {
      return this.$store.state.events.length !== 0;
    },
    hasNext() {
      return this.$store.state.hasNext;
    },
    query: {
      get() {
        return this.$route.query || {};
      },
      set(value) {
        this.query = value;
      },
    },
  },
  methods: {
    searchSubmit(e) {
      e.preventDefault();
      this.$store.dispatch('GET_EVENTS', this.query);
    },
    fetchMore(e) {
      e.preventDefault();
      this.$store.dispatch('FETCH_MORE_EVENTS', this.query);
    },
  },
};
</script>

<template lang="html">
  <div class="events-list">
    <form
        class="searchbar"
        @submit="searchSubmit"
    >
      <Input
          v-model="query.search"
          name="search"
          placeholder="Enter address or event name"
      />
    </form>
    <div
        class="items"
        v-show="hasEvents"
    >
      <div
          class="item"
          v-bind:key="event.id"
          v-for="event in events"
      >
        <span class="item__name">
          {{ event.address }}
        </span>
        <div class="item__address">
          <span v-bind:key="idx" v-for="(typeName, idx) in event.eventType">{{ typeName }}</span>
        </div>
        <router-link
            :to="{ name: 'detail', params: { id: event.id }}"
            v-slot="{href, navigate}"
            custom
        >
          <a class="item__link" :href="href" @click="navigate"></a>
        </router-link>
      </div>
      <div class="items__fetch-more">
        <Button v-show="hasNext" @click.native="fetchMore">
          Fetch more
        </Button>
      </div>
    </div>
    <span v-show="!hasEvents" class="events-list__empty">No events found</span>
  </div>
</template>

<style lang="scss">
@import "src/styles/variables";

.events-list {
  display: flex;
  flex-flow: column;
  width: 100%;
  overflow: hidden;

  &__empty {
    font: $main;
    color: $yellow;
    text-align: center;
  }

  .searchbar {
    position: relative;
    display: flex;
    flex-flow: column;
    align-items: stretch;
    padding: 24px 16px;
    margin: 0;
  }

  .items {
    display: flex;
    flex-flow: column;
    overflow-y: scroll;

    .item {
      position: relative;
      display: flex;
      flex-flow: column nowrap;
      margin: 8px 0 0;
      padding: 4px 16px;

      &:hover {
        background-color: $yellow;

        & > span {
          color: $black;
        }
      }

      &:first-child {
        margin: 0;
      }

      &__name {
        display: block;
        margin: 0 0 4px 0;
        color: $yellow;
      }

      &__address {
        font-size: 12px;
      }

      &__link {
        position: absolute;
        top: 0;
        bottom: 0;
        left: 0;
        right: 0;
      }
    }

    .items__fetch-more {
      display: flex;
      flex-flow: column;
      align-items: center;
      margin: 24px 0 4px;
    }
  }
}
</style>
