import Vue from 'vue'
import Vuex from 'vuex'

import ApiService from './services/ApiService'
import MzService from './services/MzService'
import BookmarkService from './services/BookmarkService'

Vue.use(Vuex)
let apiService = new ApiService()
let mzService = new MzService()
let bookmarkService = new BookmarkService()

export default new Vuex.Store({
  state: {
    rings: {
    },
    mzList: {
      showAnnotation: true,
      asc: false,
      mzItems: []
    },
    mzObjects: {
    },
    choosedBookmarks: [],
    choosedBookmarkChart: null,
    pixels: {},
    data: {},
    pos: {}

  },
  getters: {
    getMzValues: state => {
      return Object.keys(state.mzObjects)
    },
    getMzAnnotations: state => {
      return Object.values(state.mzObjects)
    },
    getMzObject: state => {
      return state.mzObjects
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
    },
    getBookmarks: state => {
      return state.choosedBookmarks
    },
    getBookmarkChart: state => {
      let bars = []
      state.choosedBookmarks.forEach(function (elem) {
        bars.push(bookmarkService.createBookmarkObject(elem['color']))
      })
      return bars
    }
  },
  mutations: {
    SET_ORIGINAL_DATA: (state, originalData) => {
      state.rings = originalData.rings
      state.mzList.mzItems = originalData.mzs
      state.pixels = originalData.pixels
    },
    MZLIST_TOOGLE_ASC: state => {
      state.mzList.asc = !state.mzList.asc
    },
    MZLIST_SORT_MZ: state => {
      state.mzObjects = mzService.sortMzList(state.mzObjects, state.mzList.asc)
    },
    MZLIST_SHOW_ANNOTATIONS: state => {
      state.mzList.showAnnotation = !state.mzList.showAnnotation
    },
    SET_MZ_OBJECT: state => {
      state.mzList.mzItems.forEach(function (element) {
        state.mzObjects[element] = element.toString()
      })
    },
    SET_MZ_ANNOTATION: (state, mzToAnnotated) => {
      state.mzObjects[mzToAnnotated[0]] = mzToAnnotated[1]
    },
    SET_POS_COLOR: (state, pos) => {
      state.pos = pos
    },
    SET_CHOOSED_BOOKMARKS: (state, posDict) => {
      if (state.choosedBookmarks.length === 0) {
        state.choosedBookmarks.push(posDict)
        return null
      }
      state.choosedBookmarks.forEach(function (elem) {
        if (elem['pos']['startPos'][0] === posDict['pos']['startPos'][0] && elem['pos']['startPos'][1] === posDict['pos']['startPos'][1]) {
          let index = state.choosedBookmarks.indexOf(elem)
          if (index > -1) {
            state.choosedBookmarks.splice(index, 1)
          }
        }
      })
      state.choosedBookmarks.push(posDict)
    }
  },
  actions: {
    fetchData: context => {
      context.commit('SET_ORIGINAL_DATA', apiService.fetchData())
    }
  }
})
