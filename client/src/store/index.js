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

export default {
  state:{
    events: [],
    eventsInfo: {}
  },
  mutations: {
    setEvents(state, data) {
      state.events = data.events.edges.map(edge => (edge.node))
      state.eventsInfo = data.pageInfo
    }
  },
  actions: {
    async getEvents({ commit }) {
      const response = await client.query({
        query: gql`
        query events {
          events{
             pageInfo {
              startCursor
              endCursor
              hasNextPage
              hasPreviousPage
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
      })
      commit('setEvents', response.data)
    }
  }
}