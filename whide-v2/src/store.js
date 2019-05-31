import Vue from 'vue'
import Vuex from 'vuex'

import ApiService from './services/ApiService'
import MzService from './services/MzService'

Vue.use(Vuex)
let apiService = new ApiService()
let mzService = new MzService()

export default new Vuex.Store({
  state: {
    rings: {},
    mzList: {
      showAnnotation: true,
      asc: true
    },
    pixels: {},
    data: {}

  },
  getters: {
    getMzValues: state => {
      return state.mzList
    },
    getRings: state => {
      return state.rings
    },
    getPixels: state => {
      return state.pixels
    },
    mzShowAnnotation: state => {
      return state.mzList.showAnnotation
    },
    mzAsc: state => {
      return state.mzList.asc
    }
  },
  mutations: {
    SET_ORIGINAL_DATA: (state, originalData) => {
      state.rings = originalData.rings
      state.mzList = originalData.mzs
      state.pixels = originalData.pixels
    },
    MZLIST_TOOGLE_ASC: state => {
      state.mzList.asc = !state.mzList.asc
    },
    MZLIST_SORT_MZ: state => {
      state.mzList = mzService.sortMzList(
        state.mzList,
        state.mzList.asc
      )
    },
    MZLIST_SHOW_ANNOTATIONS: state => {
      state.mzList.showAnnotation = !state.mzList.showAnnotation
    }
  },
  actions: {
    fetchData: context => {
      context.commit('SET_ORIGINAL_DATA', apiService.fetchData())
    }
  }
})
