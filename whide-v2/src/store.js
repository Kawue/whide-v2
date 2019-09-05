import Vue from 'vue'
import Vuex from 'vuex'

import ApiService from './services/ApiService'
import MzService from './services/MzService'
import BookmarkService from './services/BookmarkService'
import axios from 'axios'

const API_URL = 'http://localhost:5000'

Vue.use(Vuex)
let apiService = new ApiService()
let mzService = new MzService()
let bookmarkService = new BookmarkService()

export default new Vuex.Store({
  state: {
    rings: {},
    ringsPos: {},
    mzList: {
      showAnnotation: true,
      asc: false,
      mzItems: []
    },
    mzObjects: {
    },
    choosedBookmarks: [],
    choosedBookmarksColor: [],
    pixels: {},
    data: {},
    pos: {},
    ringCoefficients: [],
    ringIdx: String

  },
  getters: {
    getMzAnnotations: state => {
      return Object.values(state.mzObjects)
    },
    getMzObject: state => {
      return state.mzObjects
    },
    getRings: state => {
      return state.ringsPos
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
    getRingCoefficients: state => {
      return state.ringCoefficients
    }
  },
  mutations: {
    SET_ORIGINAL_DATA: (state, originalData) => {
      state.rings = originalData.rings
      state.mzList.mzItems = originalData.mzs
      state.pixels = originalData.pixels
      let posDict = {}
      Object.keys(originalData.rings).forEach(function (ring) {
        let protoDict = {}
        Object.keys(originalData.rings[ring]).forEach(function (prototype) {
          let proPos = {
            'currentPos': originalData.rings[ring][prototype]['pos'],
            'startPos': originalData.rings[ring][prototype]['pos']
          }
          protoDict[prototype] = proPos
        })
        posDict[ring] = protoDict
      })
      state.ringsPos = posDict
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
    SET_CHOOSED_BOOKMARKS: (state, prototypePosDict) => {
      let prototypId = Object.keys(prototypePosDict)
      let prototypeData = state.ringCoefficients[prototypId[0].toString()]
      let currentColor = Object.keys(prototypePosDict[prototypId])

      let fullBookmarksDict = {
        id: prototypId,
        color: currentColor,
        data: prototypeData,
        startPos: prototypePosDict[prototypId][currentColor]['startPos'],
        currentPos: prototypePosDict[prototypId][currentColor]['currentPos'],
        mzs: state.mzList.mzItems
      }

      if (state.choosedBookmarks.length === 0) {
        state.choosedBookmarksColor.push(currentColor[0])
        state.choosedBookmarks.push(fullBookmarksDict)
        return null
      }
      if (!state.choosedBookmarksColor.includes(currentColor[0])) {
        state.choosedBookmarksColor.push(currentColor[0])
        state.choosedBookmarks.push(fullBookmarksDict)
      }
    },
    DELETE_CHOOSED_BOOKMARK: (state, prototypeId) => {
      for (var i = 0; i < state.choosedBookmarks.length; i++) {
        // console.log(state.choosedBookmarks[i]['id'].toString())
        if (state.choosedBookmarks[0]['id'].toString() === prototypeId.toString()) {
          state.choosedBookmarks.splice(i, 1)
          state.choosedBookmarksColor.splice(i, 1)
        }
      }
    },
    SET_RING_COEFFICIENTS: (state, coefficients) => {
      state.ringCoefficients = bookmarkService.normalizeCoefficients(coefficients)
    },
    SET_RING_IDX: (state, ringIdx) => {
      state.ringIdx = ringIdx
    }
  },
  actions: {
    fetchData: context => {
      context.commit('SET_ORIGINAL_DATA', apiService.fetchData())
    },
    simpleHelloWorld: context => {
      const url = API_URL + '/hello'
      axios
        .get(url)
        .then(response => {
          window.alert(response.data)
        })
        .catch(function () {
          alert('Error While printing Hello World')
        })
    },
    getRingCoefficients: (context, index) => {
      const url = API_URL + '/coefficients?index=' + index
      axios
        .get(url)
        .then(response => {
          context.commit('SET_RING_COEFFICIENTS', response.data)
        })
        .catch(function () {
          alert('Error while getting coefficients')
        })
    }
  }
})
