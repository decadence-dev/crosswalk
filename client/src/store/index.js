import {
  ApolloClient, ApolloLink, HttpLink, InMemoryCache,
} from 'apollo-boost';
import gql from 'graphql-tag';

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

export default {
  state: {
    event: {},
    events: [],
    pageInfo: {},
  },
  mutations: {
    /* eslint-disable */
    setEvent(state, data) {
      state.event = {...data.event, eventType: EVENT_TYPE_MAP[data.event.eventType]};
    },
    setEvents(state, data) {
      state.events = data.events.edges.map(
        (edge) => ({
          ...edge.node, eventType: EVENT_TYPE_MAP[edge.node.eventType]
        })
      );
      state.hasNextPage = data.events.pageInfo.hasNextPage;
      state.endCursor = data.events.pageInfo.endCursor;
    },
    updateEvents(state, data) {
      state.events = [
        ...state.events,
        data.events.edges.map(
          (edge) => ({
            ...edge.node, eventType: EVENT_TYPE_MAP[edge.node.eventType]
          })
        )
      ];
      state.hasNextPage = data.events.pageInfo.hasNextPage;
      state.endCursor = data.events.pageInfo.endCursor;
    },
    /* eslint-enable */

  },
  actions: {
    async getEvent({ commit }, variables) {
      const response = await client.query({ query: EVENT_QUERY, variables });
      commit('setEvent', response.data);
    },
    async getEvents({ commit }, variables = {}) {
      const response = await client.query({ query: EVENTS_QUERY, variables });
      commit('setEvents', response.data);
    },
    async fetchMoreEvents({ commit }, variables = {}) {
      const response = await client.query({ query: EVENTS_QUERY, variables });
      commit('updateEvents', response.data);
    },
  },
};
