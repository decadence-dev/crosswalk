<script>
import Button from '../components/button.vue';
import Input from '../components/input.vue';
import Textarea from '../components/textarea.vue';
import EventType from '../components/eventtype.vue';
import CloseIcon from '../icons/close.vue';

export default {
  name: 'CreateForm',
  components: {
    Textarea, Input, CloseIcon, EventType, Button,
  },
  data: () => ({
    errors: [],
  }),
  computed: {
    event() {
      return this.$store.state.event;
    },
    hasErrors() {
      return this.errors.length > 0;
    },
  },
  methods: {
    submitEvent(e) {
      e.preventDefault();
      this.validateRequired('address');
      this.validateRequired('eventType');
      if (!this.hasErrors) {
        this.$store.dispatch('createEvent');
      } else {
        this.$store.dispatch('updateErrors', ['Please resolve form errors before submit']);
      }
    },
    getEvent() {
      if (this.$route.params.id != null) {
        this.$store.dispatch('getEvent', { id: this.$route.params.id });
      } else {
        this.$store.dispatch('resetEvent');
      }
    },
    validateRequired(name) {
      if (this.$store.state.event[name] == null || this.$store.state.event[name].trim() === '') {
        this.errors = [...this.errors, ...[name]];
      } else {
        this.errors = this.errors.filter((error) => error !== name);
      }
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
  <aside class="event-sidepar">
    <div class="event-sidepar__header">
      <router-link
          :to="{name: 'map'}"
          v-slot="{href, navigate}"
          custom
      >
        <a class="close-link" :href="href" @click="navigate"></a>
      </router-link>
      <CloseIcon></CloseIcon>
    </div>
    <form @submit="submitEvent" class="event-form">
      <div class="field">
        <label class="field__label field__label_required" for="address">
          Address
        </label>
        <Input
            @blur="validateRequired('address')"
            id="address"
            v-model="event.address"
            class="field__input"
            name="address"
            placeholder="Enter address"
        ></Input>
        <small v-show="errors.includes('address')" class="field__error">
          This field is required
        </small>
      </div>
      <div class="field">
        <label class="field__label field__label_required" for="eventType">
          Event type
        </label>
        <EventType
            @blur="validateRequired('eventType', $event.target.value)"
            id="eventType"
            name="eventType"
            v-model="event.eventType"
        ></EventType>
        <small v-show="errors.includes('eventType')" class="field__error">
          This field is required
        </small>
      </div>
      <div class="field">
        <label class="field__label" for="description">
          Description
        </label>
        <Textarea
            id="description"
            v-model="event.description"
            class="file"
            name="description"
            placeholder="Enter description"
            label="Description"
        />
      </div>
      <div class="buttons">
        <Button
            @click.native="submitEvent"
        >
          Submit
        </Button>
      </div>
    </form>
  </aside>
</template>

<style lang="scss">
@import "src/styles/variables";

.event-sidepar {
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

  .event-form {
    padding: 24px 16px;

    .field {
      display: flex;
      flex-flow: column;
      margin: 0 0 16px;

      &__label {
        font: $help;
        color: $yellow;
        margin: 0 0 8px;

        &_required::after {
          content: "*";
          color: $red;
        }
      }

      &__error {
        margin: 4px 0 0;
        color: $red;
      }

      &:last-child {
        margin: 0;
      }

      &__input {
        margin: 8px 0 0;
      }
    }
  }
}
</style>
