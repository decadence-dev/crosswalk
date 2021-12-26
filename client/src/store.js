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
  query getEvent($id: UUID!) {
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
    $eventType: [String]!, 
    $address: String!, 
    $longitude: Float!, 
    $latitude: Float!,
    $description: String
  ) {
    createEvent (
      data: { 
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
    $id: UUID!,
    $eventType: [String]!, 
    $address: String!, 
    $longitude: Float!, 
    $latitude: Float!,
    $description: String
  ) {
    updateEvent (
      id: $id,
      data: {
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
  mutation deleteEvent($id: UUID!) {
    deleteEvent(id: $id) {
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
    SET_EVENT(state, event) {
      state.event = event;
    },
    UPDATE_ERRORS(state, messages) {
      const errs = messages.map((error) => ({key: uuid4(), message: error}))
      state.globalErrors = [...state.globalErrors, ...errs]
    },
    RESOLVE_ERRORS(state, keys) {
      state.globalErrors = state.globalErrors.filter((error) => !keys.includes(error.key))
    },
    INSERT_EVENT_DATA(state, event) {
      state.events = [...[event], ...state.events]
    },
    UPDATE_EVENT_DATA(state, event) {
      state.events = [...[event], ...state.events.filter((evt) => evt.id !== event.id)]
    },
    REMOVE_EVENT_DATA(state, id) {
      state.events = state.events.filter((evt) => evt.id !== id)
    },
    SET_EVENTS(state, data) {
      state.offset = EVENTS_LIMIT
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
    async GET_EVENT({ commit }, variables) {
      const response = await client.query({ query: EVENT_QUERY, variables });
      commit('SET_EVENT', response.data.event);
    },
    async RESET_EVENT({ commit }) {
      commit('SET_EVENT', {});
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
    async CREATE_EVENT({ commit, state }) {
      await client.mutate({
        mutation: EVENT_CREATE_MUTATION,
        variables: { ...state.event, longitude: 0.0, latitude: 0.0 },
      }).then((response) => {
        const event = response.data.createEvent;
        router.push({ name: 'detail', params: { id: event.id } });
      }).catch((errors) => {
        const errs = errors.networkError.result.errors.map((error) => (error.message));
        commit('UPDATE_ERRORS', errs);
      });
    },
    async UPDATE_EVENT({ commit, state }) {
      await client.mutate({
        mutation: EVENT_UPDATE_MUTATION,
        variables: { ...state.event },
      }).then((response) => {
        const event = response.data.updateEvent;
        router.push({ name: 'detail', params: { id: event.id } });
      }).catch((errors) => {
        const errs = errors.networkError.result.errors.map((error) => (error.message));
        commit('UPDATE_ERRORS', errs);
      });
    },
    async DELETE_EVENT({ state }) {
      await client.mutate({
        mutation: EVENT_DELETE_MUTATION,
        variables: { id: state.event.id },
      }).then(() => {
        router.push({ name: 'map' });
      });
    },
    async UPDATE_ERRORS({ commit }, errors) {
      commit('UPDATE_ERRORS', errors);
    },
    async RESOLVE_ERRORS({ commit }, errors) {
      commit('RESOLVE_ERRORS', errors);
    },
    async RECEIVE_EVENT_ACTION({ commit }, data) {
      switch (data.status) {
        case 1:
          commit('INSERT_EVENT_DATA', data.event);
          break;
        case 2:
          commit('UPDATE_EVENT_DATA', data.event);
          break;
        case 3:
          commit('REMOVE_EVENT_DATA', data.id);
          break;
        case 4:
          break;
        case 5:
          commit('UPDATE_ERRORS', [data.errors]);
          break;
        default:
          /* eslint-disable */
          console.warn(data);
          /* eslint-enable */
      }
    },
  },
};
