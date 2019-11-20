import Vue from 'vue';
import Vuex from 'vuex';
import * as d3 from 'd3';

import ApiService from './services/ApiService';
import MzService from './services/MzService';
import BookmarkService from './services/BookmarkService';
import axios from 'axios';
import { moebiustransformation } from './services/colorWheel';

const API_URL = 'http://localhost:5000';

Vue.use(Vuex);
let apiService = new ApiService();
let mzService = new MzService();
let bookmarkService = new BookmarkService();

export default new Vuex.Store({
  state: {
    rings: {},
    prototypesPosition: {},
    mzList: {
      showAnnotation: true,
      asc: false,
      mzItems: []
    },
    mzObjects: {
    },
    choosedBookmarksIds: [],
    choosedBookmarksOnlyIds: [],
    colorSlider: false,
    pixels: {},
    ringCoefficients: [],
    ringIdx: 'ring0',
    lastPrototypeIndex: 0,
    startingIndizes: [0],
    segmentationMapDim: {},
    currentRingData: {},
    colorsReady: false,
    currentHighlightedPrototype: String,
    highlightPrototypeFromOutside: undefined,
    bottomBarHeight: 0,
    segmentationTransformation: {
      k: 1,
      x: 0,
      y: 0
    },
    first: true

  },
  getters: {
    getMzAnnotations: state => {
      return Object.values(state.mzObjects);
    },
    getMzObject: state => {
      return state.mzObjects;
    },
    getPrototypesPosition: state => {
      return state.prototypesPosition;
    },
    mzShowAnnotation: state => {
      return state.mzList.showAnnotation;
    },
    mzAsc: state => {
      return state.mzList.asc;
    },
    getBookmarksData: (state) => (givenId) => {
      let bookmarkData = state.currentRingData[givenId];
      return {
        id: givenId,
        color: bookmarkData['color'],
        data: bookmarkData['data'],
        startPos: bookmarkData['startPos'],
        currentPos: bookmarkData['currentPos'],
        mzs: bookmarkData['mz']
      };
    },
    getBookmarkColor: (state) => (givenId) => {
      return state.currentRingData[givenId]['color'];
    },
    getRingCoefficients: state => {
      return state.ringCoefficients;
    },
    getRingIdx: state => {
      return state.ringIdx;
    },
    getNumberOfRings: state => {
      return (Object.keys(state.rings).length);
    },
    getBookmarkIds: state => {
      return state.choosedBookmarksIds;
    },
    getColorSlider: state => {
      return state.colorSlider;
    },
    getStartingIndizes: state => {
      return state.startingIndizes;
    },
    getSegmentationDim: state => {
      return state.segmentationMapDim;
    },
    getCurrentRingData: state => {
      return state.currentRingData;
    },
    getIfColorsReady: state => {
      return state.colorsReady;
    },
    getCurrentHighlightedPrototype: state => {
      return state.currentHighlightedPrototype;
    },
    getLastPrototypeIndex: state => {
      return state.lastPrototypeIndex;
    },
    getHighlightedPrototypeOutside: state => {
      return {
        'id': state.currentHighlightedPrototype,
        'outside': state.highlightPrototypeFromOutside
      };
    },
    getBottonBarHeight: state => {
      return state.bottomBarHeight;
    },
    getSegmentationTransformation: state => {
      return state.segmentationTransformation;
    }
  },
  mutations: {
    SET_ORIGINAL_DATA: (state, originalData) => {
      state.rings = originalData.rings;
      state.mzList.mzItems = originalData.mzs;
      state.pixels = originalData.pixels;
      let protoDict = {};
      Object.keys(originalData.rings[state.ringIdx]).forEach(function (prototype) {
        protoDict[prototype] = {
          'currentPos': originalData.rings[state.ringIdx][prototype]['pos'],
          'startPos': originalData.rings[state.ringIdx][prototype]['pos']
        };
      });
      state.prototypesPosition = protoDict;
    },
    SET_FULL_DATA: state => {
      let ringData = {};
      Object.keys(state.rings[state.ringIdx]).forEach(function (prototype) {
        let prototypeData = {};
        let pixelIds = [];
        Object.values(state.rings[state.ringIdx][prototype]['pixel']).forEach(function (pixelId) {
          pixelIds.push(pixelId);
        });
        let pixelPos = [];
        pixelIds.forEach(function (pixel) {
          pixelPos.push(state.pixels[pixel]['pos']);
        });
        prototypeData['pixels'] = pixelPos;
        prototypeData['currentPos'] = state.rings[state.ringIdx][prototype]['pos'];
        prototypeData['startPos'] = state.rings[state.ringIdx][prototype]['pos'];
        prototypeData['id'] = prototype;
        prototypeData['data'] = state.ringCoefficients[prototype];
        prototypeData['mz'] = state.mzList.mzItems;
        ringData[prototype] = prototypeData;
      });
      state.currentRingData = ringData;
    },
    ADD_COLOR_TO_FULL_DATA: (state, idWithColor) => {
      let prototype = Object.keys(idWithColor).toString();
      let color = Object.values(idWithColor);
      state.currentRingData[prototype.toString()]['color'] = color.toString();
    },
    MZLIST_TOOGLE_ASC: state => {
      state.mzList.asc = !state.mzList.asc;
    },
    MZLIST_SORT_MZ: state => {
      state.mzObjects = mzService.sortMzList(state.mzObjects, state.mzList.asc);
    },
    MZLIST_SHOW_ANNOTATIONS: state => {
      state.mzList.showAnnotation = !state.mzList.showAnnotation;
    },
    SET_MZ_OBJECT: state => {
      state.mzList.mzItems.forEach(function (element) {
        state.mzObjects[element] = element.toString();
      });
    },
    SET_MZ_ANNOTATION: (state, mzToAnnotated) => {
      state.mzObjects[mzToAnnotated[0]] = mzToAnnotated[1];
    },
    SET_POS_COLOR: (state, pos) => {
      state.currentRingData = bookmarkService.changePrototypeColor(pos, state.currentRingData);
    },
    SET_CHOOSED_BOOKMARK: (state, prototype) => {
      if (!(state.choosedBookmarksOnlyIds.includes(prototype))) {
        state.choosedBookmarksIds.push({
          id: prototype,
          value: prototype
        });
        state.choosedBookmarksOnlyIds.push(prototype);
        state.colorSlider = true;
      }
    },
    DELETE_BOOKMARK: (state, itemId) => {
      let currentIds = state.choosedBookmarksIds;
      let currentOnlyIds = state.choosedBookmarksOnlyIds;
      for (let i = 0; i < currentIds.length; i++) {
        if (currentIds[i]['id'] === itemId) {
          currentIds.splice(i, 1);
          currentOnlyIds.splice(i, 1);
        }
      }
      Vue.set(state, 'choosedBookmarksIds', currentIds);
      Vue.set(state, 'choosedBookmarksOnlyIds', currentOnlyIds);
      d3.select('#' + itemId).remove();
      if (state.choosedBookmarksIds.length === 0) {
        state.colorSlider = false;
      }
    },
    DELETE_ALL_BOOKMARKS: (state) => {
      state.choosedBookmarksIds = [];
      state.choosedBookmarksOnlyIds = [];
      state.colorSlider = false;
    },
    SET_RING_COEFFICIENTS: (state, coefficients) => {
      state.ringCoefficients = bookmarkService.normalizeCoefficients(coefficients);
    },
    SET_RING_IDX: (state, ringIdx) => {
      state.ringIdx = ringIdx;
    },
    SET_PROTOTYPES_POSITION: (state) => {
      let protoDict = {};
      Object.keys(state.rings[state.ringIdx]).forEach(function (prototype) {
        protoDict[prototype] = {
          'currentPos': state.rings[state.ringIdx][prototype]['pos'],
          'startPos': state.rings[state.ringIdx][prototype]['pos']
        };
      });
      state.prototypesPosition = protoDict;
    },
    SET_MOEBIUS: (state, xAndY) => {
      state.prototypesPosition = moebiustransformation(state.prototypesPosition, xAndY);
    },
    SET_DEFAULT_POSITION: (state) => {
      let protoDict = {};
      Object.keys(state.prototypesPosition).forEach(function (prototype) {
        protoDict[prototype] = {
          'currentPos': state.prototypesPosition[prototype]['startPos'],
          'startPos': state.prototypesPosition[prototype]['startPos']
        };
      });
      state.prototypesPosition = protoDict;
      let xAndY = { 'x': 0, 'y': 0 };
      state.prototypesPosition = moebiustransformation(state.prototypesPosition, xAndY);
    },
    SET_LASTIDX_OF_COEF: (state, idx) => {
      state.lastPrototypeIndex = idx;
    },
    SET_COEFF_INDEX: (state, indizes) => {
      state.startingIndizes = indizes['indizes'];
    },
    SET_SEGMENTATION_DIM: (state, dim) => {
      state.segmentationMapDim = dim;
    },
    SET_COLORS_READY: (state, bool) => {
      state.colorsReady = bool;
    },
    SET_FIRST: (state, bool) => {
      state.first = bool;
    },
    SET_CURRENT_HIGHLIGHTED_PROTOTYPE: (state, prototype) => {
      state.currentHighlightedPrototype = prototype;
    },
    UPDATE_COLOR: state => {
      return null;
    },
    HIGHLIGHT_PROTOTYPE_OUTSIDE: state => {
      state.highlightPrototypeFromOutside = state.highlightPrototypeFromOutside !== true;
      if (state.highlightPrototypeFromOutside === undefined) {
        state.highlightPrototypeFromOutside = true;
      }
    },
    SET_BOTTOMBAR_HEIGHT: (state, height) => {
      state.bottomBarHeight = height;
    },
    SET_SEGMENTATION_TRANSFORMATION: (state, transformation) => {
      state.segmentationTransformation = transformation;
    }
  },
  actions: {
    getDimensions: context => {
      const url = API_URL + '/dimensions';
      axios
        .get(url)
        .then(response => {
          context.commit('SET_SEGMENTATION_DIM', response.data);
        })
        .catch(function (e) {
          alert('Error while getting dimensions');
        });
    },
    fetchData: context => {
      context.commit('SET_ORIGINAL_DATA', apiService.fetchData());
      const url = API_URL + '/coefficientsindex';
      axios
        .get(url)
        .then(response => {
          context.commit('SET_COEFF_INDEX', response.data);
          context.commit('SET_FULL_DATA');
        })
        .catch(function (e) {
          console.log(e);
          alert('Error while fetching data');
        });
    },
    getRingCoefficients: (context) => {
      let ringIdx = context.state.ringIdx;
      let re = /\d+/;
      let i = ringIdx.match(re);
      let startingindizes = context.state.startingIndizes;
      let lastIdx = startingindizes[parseInt(i.toString())];
      context.commit('SET_LASTIDX_OF_COEF', lastIdx);
      const url = API_URL + '/coefficients?index=' + ringIdx + '&lastIndex=' + lastIdx.toString();
      axios
        .get(url)
        .then(response => {
          context.commit('SET_RING_COEFFICIENTS', response.data['coefficients']);
          if (!context.state.first) {
            context.commit('SET_FULL_DATA');
          } else {
            context.commit('SET_FIRST', false);
          }
        })
        .catch(function () {
          alert('Error while getting coefficients or set Focus');
        });
    }
  }
});
