import {
  ApolloClient, ApolloLink, HttpLink, InMemoryCache,
} from 'apollo-boost';
import gql from 'graphql-tag';
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

const EVENT_QUERY = gql`
  query getEvent($id: ID!) {
    event(id: $id) {
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

const EVENTS_QUERY = gql`
  query geteEvents($search: String, $first: Int, $after: String) {
    events (search: $search, first: $first, after: $after) {
      pageInfo {
        endCursor
        hasNextPage
      }
      edges{
        node {
          id
          address
          eventType
        }
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

export default {
  state: {
    event: {},
    globalErrors: [],
    events: [],
    pageInfo: {},
  },
  mutations: {
    /* eslint-disable */
    setEvent(state, event) {
      state.event = event;
    },
    updateErrors(state, errors) {
      state.globalErrors = [...state.globalErrors, ...errors]
    },
    resolveErrors(state, errors) {
      state.globalErrors = state.globalErrors.filter((error) => !errors.includes(error))
    },
    insertEvent(state, event) {
      state.events = [...[event], ...state.events]
    },
    setEvents(state, data) {
      state.events = data.events.edges.map((edge) => (edge.node));
      state.hasNextPage = data.events.pageInfo.hasNextPage;
      state.endCursor = data.events.pageInfo.endCursor;
    },
    updateEvents(state, data) {
      state.events = [...state.events, ...data.events.edges.map((edge) => (edge.node))];
      state.hasNextPage = data.events.pageInfo.hasNextPage;
      state.endCursor = data.events.pageInfo.endCursor;
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
    async getEvents({ commit }, variables = {}) {
      const response = await client.query({ query: EVENTS_QUERY, variables });
      commit('setEvents', response.data);
    },
    async fetchMoreEvents({ commit }, variables = {}) {
      const response = await client.query({ query: EVENTS_QUERY, variables });
      commit('updateEvents', response.data);
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
    async updateErrors({ commit }, errors) {
      commit('updateErrors', errors);
    },
    async resolveErrors({ commit }, errors) {
      commit('resolveErrors', errors);
    },
  },
};
