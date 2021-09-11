import { ApolloClient, ApolloLink, HttpLink, InMemoryCache } from 'apollo-boost'
import gql from 'graphql-tag'


const client = new ApolloClient({
  link: new ApolloLink((operation, forward) => {
    const token = localStorage.getItem('token')
    operation.setContext({
      headers: {
        authorization: token ? `Bearer ${token}`: ''
      }
    })
    return forward(operation)
  }).concat(
    new HttpLink({uri: 'http://localhost:8000'})
  ),
  cache: new InMemoryCache()
})

const EVENTS_QUERY = gql`
  query events($search: String, $first: Int, $after: String) {
    events (search: $search, first: $first, after: $after) {
       pageInfo {
        endCursor
        hasNextPage
      }
      edges{
        node {
          id
          name
          address
        }
      }
    }
  }
`

export default {
  state:{
    events: [],
    pageInfo: {},
  },
  mutations: {
    setEvents(state, data) {
      state.events = data.events.edges.map(edge => (edge.node))
      state.hasNextPage = data.events.pageInfo.hasNextPage
      state.endCursor = data.events.pageInfo.endCursor
    },
    updateEvents(state, data) {
      state.events = [...state.events, ...data.events.edges.map(edge => (edge.node))]
      state.hasNextPage = data.events.pageInfo.hasNextPage
      state.endCursor = data.events.pageInfo.endCursor
    }
  },
  actions: {
    async getEvents({ commit }, variables = {}) {
      const response = await client.query({query: EVENTS_QUERY, variables})
      commit('setEvents', response.data)
    },
    async fetchMoreEvents({ commit }, variables = {}) {
      const response = await client.query({query: EVENTS_QUERY, variables})
      commit('updateEvents', response.data)
    }
  }
}