import {
  ApolloClient, ApolloLink, HttpLink, InMemoryCache,
} from 'apollo-boost';
import gql from 'graphql-tag';
import { v4 as uuid4 } from 'uuid';
import router from './router';

const client = new ApolloClient({
  link: new ApolloLink((operation, forward) => {
    const token = localStorage.getItem('token');
    operation.setContext({
      headers: {
        authorization: token ? `Bearer ${token}` : '',
      },
    });
    return forward(operation);
  }).concat(
    new HttpLink({ uri: 'http://localhost:8000' }),
  ),
  cache: new InMemoryCache(),
});

const EVENTS_LIMIT = 10;

const EVENT_QUERY = gql`
  query getEvent($id: ID!) {
    event(id: $id) {
      id
      eventType
      address
      longitude
      latitude
      description
      createdDate
      createdBy {
        username
      }
    }
  }
`;

const EVENTS_QUERY = gql`
  query geteEvents($search: String, $limit: Int, $offset: Int) {
    events (search: $search, limit: $limit, offset: $offset) {
      count
      hasNext
      items{
        id
        address
        eventType
      }
    }
  }
`;

const EVENT_CREATE_MUTATION = gql`
  mutation createEvent(
    $eventType: EventType!, 
    $address: String!, 
    $longitude: Float!, 
    $latitude: Float!,
    $description: String
  ) {
    createEvent (
      input: { 
        eventType: $eventType, 
        address: $address, 
        longitude: $longitude, 
        latitude: $latitude,
        description: $description
      }
    ) {
      id
      eventType
      address
      description
      createdDate
      createdBy {
        username
      }
    }
  }
`;

const EVENT_UPDATE_MUTATION = gql`
  mutation updateEvent(
    $id: ID!,
    $eventType: EventType!, 
    $address: String!, 
    $longitude: Float!, 
    $latitude: Float!,
    $description: String
  ) {
    updateEvent (
      input: { 
        id: $id,
        eventType: $eventType, 
        address: $address, 
        longitude: $longitude, 
        latitude: $latitude,
        description: $description
      }
    ) {
      id
      eventType
      address
      description
      createdDate
      createdBy {
        username
      }
    }
  }
`;

const EVENT_DELETE_MUTATION = gql`
  mutation deleteEvent($id: ID!) {
    deleteEvent(input: {id: $id}) {
      id
    }
  }
`;

export default {
  state: {
    event: {},
    hasNext: false,
    count: 0,
    offset: EVENTS_LIMIT,
    globalErrors: [],
    events: [],
    pageInfo: {},
  },
  mutations: {
    /* eslint-disable */
    setEvent(state, event) {
      state.event = event;
    },
    updateErrors(state, messages) {
      const errs = messages.map((error) => ({key: uuid4(), message: error}))
      state.globalErrors = [...state.globalErrors, ...errs]
    },
    resolveErrors(state, keys) {
      state.globalErrors = state.globalErrors.filter((error) => !keys.includes(error.key))
    },
    insertEvent(state, event) {
      state.events = [...[event], ...state.events]
    },
    updateeEvent(state, event) {
      state.events = [...[event], ...state.events.filter((evt) => evt.id !== event.id)]
    },
    removeEvent(state, id) {
      state.events = state.events.filter((evt) => evt.id !== id)
    },
    SET_EVENTS(state, data) {
      state.events = data.events.items
      state.hasNext = data.events.hasNext;
      state.count = data.events.count;
    },
    UPDATE_EVENTS_LIST(state, data) {
      state.offset += EVENTS_LIMIT;
      state.events = [...state.events, ...data.events.items];
      state.hasNext = data.events.hasNext;
      state.count = data.events.count;
    },
    /* eslint-enable */
  },
  actions: {
    async getEvent({ commit }, variables) {
      const response = await client.query({ query: EVENT_QUERY, variables });
      commit('setEvent', response.data.event);
    },
    async resetEvent({ commit }) {
      commit('setEvent', {});
    },
    async GET_EVENTS({ commit }, variables = {}) {
      const response = await client.query({
        query: EVENTS_QUERY,
        variables: { limit: EVENTS_LIMIT, ...variables },
      });
      commit('SET_EVENTS', response.data);
    },
    async FETCH_MORE_EVENTS({ commit, state }, variables = {}) {
      const response = await client.query({
        query: EVENTS_QUERY,
        variables: {
          limit: EVENTS_LIMIT,
          offset: state.offset,
          ...variables,
        },
      });
      commit('UPDATE_EVENTS_LIST', response.data);
    },
    async createEvent({ commit, state }) {
      await client.mutate({
        mutation: EVENT_CREATE_MUTATION,
        variables: { ...state.event, longitude: 0.0, latitude: 0.0 },
      }).then((response) => {
        const event = response.data.createEvent;
        commit('insertEvent', event);
        router.push({ name: 'detail', params: { id: event.id } });
      }).catch((errors) => {
        const errs = errors.networkError.result.errors.map((error) => (error.message));
        commit('updateErrors', errs);
      });
    },
    async updateEvent({ commit, state }) {
      await client.mutate({
        mutation: EVENT_UPDATE_MUTATION,
        variables: { ...state.event },
      }).then((response) => {
        const event = response.data.updateEvent;
        commit('updateeEvent', event);
        router.push({ name: 'detail', params: { id: event.id } });
      }).catch((errors) => {
        const errs = errors.networkError.result.errors.map((error) => (error.message));
        commit('updateErrors', errs);
      });
    },
    async deleteEvent({ commit, state }) {
      await client.mutate({
        mutation: EVENT_DELETE_MUTATION,
        variables: { id: state.event.id },
      }).then((response) => {
        const { id } = response.data.deleteEvent;
        commit('removeEvent', id);
        router.push({ name: 'map' });
      });
    },
    async updateErrors({ commit }, errors) {
      commit('updateErrors', errors);
    },
    async resolveErrors({ commit }, errors) {
      commit('resolveErrors', errors);
    },
  },
};
