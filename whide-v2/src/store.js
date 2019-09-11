import Vue from 'vue'
import Vuex from 'vuex'

import ApiService from './services/ApiService'
import MzService from './services/MzService'
import BookmarkService from './services/BookmarkService'
import axios from 'axios'
import { moebiustransformation } from './services/colorWheel'

const API_URL = 'http://localhost:5000'

Vue.use(Vuex)
let apiService = new ApiService()
let mzService = new MzService()
let bookmarkService = new BookmarkService()

export default new Vuex.Store({
  state: {
    rings: {},
    prototypesPosition: {},
    focus: {},
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
    // pos: {},
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
    getPrototypesPosition: state => {
      return state.prototypesPosition
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
    },
    getRingIdx: state => {
      return state.ringIdx
    },
    getNumberOfRings: state => {
      return (Object.keys(state.rings).length)
    }
  },
  mutations: {
    SET_ORIGINAL_DATA: (state, originalData) => {
      state.rings = originalData.rings
      state.mzList.mzItems = originalData.mzs
      state.pixels = originalData.pixels
      let protoDict = {}
      Object.keys(originalData.rings[state.ringIdx]).forEach(function (prototype) {
        let proPos = {
          'currentPos': originalData.rings[state.ringIdx][prototype]['pos'],
          'startPos': originalData.rings[state.ringIdx][prototype]['pos']
        }
        protoDict[prototype] = proPos
      })
      state.prototypesPosition = protoDict
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
      let prototypId = prototypePosDict['id']
      let prototypeData = state.ringCoefficients[prototypId.toString()]
      let currentColor = prototypePosDict['color']
      let fullBookmarksDict = {
        id: prototypId,
        color: currentColor,
        data: prototypeData,
        startPos: prototypePosDict['startPos'],
        currentPos: prototypePosDict['currentPos'],
        mzs: state.mzList.mzItems
      }
      if (state.choosedBookmarks.length === 0) {
        state.choosedBookmarksColor.push(currentColor)
        state.choosedBookmarks.push(fullBookmarksDict)
        return null
      }
      if (!state.choosedBookmarksColor.includes(currentColor)) {
        state.choosedBookmarksColor.push(currentColor)
        state.choosedBookmarks.push(fullBookmarksDict)
      }
    },
    DELETE_CHOOSED_BOOKMARK: (state, prototypeId) => {
      let currentChoosedBookmarks = state.choosedBookmarks
      let currentChoosedBookmarksColor = state.choosedBookmarksColor
      for (var i = 0; i < currentChoosedBookmarks.length; i++) {
        console.log(currentChoosedBookmarks[i]['id'])
        if (currentChoosedBookmarks[i]['id'].toString() === prototypeId.toString()) {
          currentChoosedBookmarks.splice(i, 1)
          currentChoosedBookmarksColor.splice(i, 1)
        }
      }
      state.choosedBookmarks = currentChoosedBookmarks
      state.choosedBookmarksColor = currentChoosedBookmarksColor
    },
    SET_RING_COEFFICIENTS: (state, coefficients) => {
      state.ringCoefficients = bookmarkService.normalizeCoefficients(coefficients)
    },
    SET_RING_IDX: (state, ringIdx) => {
      state.ringIdx = ringIdx
    },
    SET_PROTOTYPES_POSITION: (state) => {
      let protoDict = {}
      Object.keys(state.rings[state.ringIdx]).forEach(function (prototype) {
        let proPos = {
          'currentPos': state.rings[state.ringIdx][prototype]['pos'],
          'startPos': state.rings[state.ringIdx][prototype]['pos']
        }
        protoDict[prototype] = proPos
      })
      state.prototypesPosition = protoDict
    },
    SET_MOEBIUS: (state, xAndY) => {
      // console.log(state.prototypesPosition)
      state.prototypesPosition = moebiustransformation(state.prototypesPosition, xAndY, state.focus)
      // console.log(state.prototypesPosition)
    },
    SET_DEFAULT_POSITION: (state) => {
      let protoDict = {}
      Object.keys(state.prototypesPosition).forEach(function (prototype) {
        let proPos = {
          'currentPos': state.prototypesPosition[prototype]['startPos'],
          'startPos': state.prototypesPosition[prototype]['startPos']
        }
        protoDict[prototype] = proPos
      })
      state.prototypesPosition = protoDict
    },
    SET_FOCUS_DEFAULT: (state) => {
      state.focus = {
        'x': 0,
        'y': 0
      }
    },
    SET_MOVED_FOCUS: (state, focus) => {
      state.focus = focus
    }
  },
  actions: {
    fetchData: context => {
      context.commit('SET_RING_IDX', 'ring0')
      context.commit('SET_ORIGINAL_DATA', apiService.fetchData())
      context.commit('SET_FOCUS_DEFAULT')
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
