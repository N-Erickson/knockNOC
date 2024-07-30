import { createStore } from 'vuex'

export default createStore({
  state: {
    displayMode: 'default'
  },
  mutations: {
    setDisplayMode(state, mode) {
      state.displayMode = mode
    }
  },
  actions: {
    cycleDisplayMode({ commit, state }) {
      const modes = ['default', 'neon', 'matrix']
      const currentIndex = modes.indexOf(state.displayMode)
      const nextIndex = (currentIndex + 1) % modes.length
      commit('setDisplayMode', modes[nextIndex])
    }
  }
})