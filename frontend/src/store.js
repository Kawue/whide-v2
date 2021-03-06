import Vue from 'vue';
import Vuex from 'vuex';
import * as d3 from 'd3';

import BookmarkService from './services/BookmarkService';
import axios from 'axios';
import { moebiustransformation } from './services/colorWheel';
import MzService from './services/mzService';

const API_URL = 'http://localhost:5000';

Vue.use(Vuex);
let bookmarkService = new BookmarkService();
let mzService = new MzService();

export default new Vuex.Store({
  /*
  state holds every importent information
   */
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
    bottomBarHeight: 50,
    segmentationTransformation: {
      k: 1,
      x: 0,
      y: 0
    },
    first: true,
    showMzInBchart: false,
    showAnnotationInBchart: false,
    horizonatlCharts: false,
    lineChart: false,
    mzImage: {
      colorScale: 'interpolateViridis',
      colorScales: {
        interpolateMagma: 'Magma',
        interpolatePiYG: 'PiYG',
        interpolateViridis: 'Viridis',
        interpolatePlasma: 'Plasma',
        interpolateInferno: 'Inferno'
      },
      currentMergeMethod: 'methodMean',
      mergeMethods: {
        methodMean: 'mean',
        methodMedian: 'median',
        methodMin: 'min',
        methodMax: 'max'
      },
      selectedMzValues: [],
      base64Image: null
    },
    brightFieldImage: null,
    focusMzList: false,
    addMzToAggregationList: ''

  },
  // Methods to get the current state
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
    getBookmarksData: (state) => (givenId) => {
      let bookmarkData = state.currentRingData[givenId];
      return {
        id: givenId,
        color: bookmarkData['color'],
        data: bookmarkData['data'],
        startPos: bookmarkData['startPos'],
        currentPos: bookmarkData['currentPos'],
        mzObject: state.mzObjects
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
    getOnlyBookmarkIds: state => {
      return state.choosedBookmarksOnlyIds;
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
    },
    getShowMzInBchart: state => {
      return state.showMzInBchart;
    },
    getShowAnnotationInBchart: state => {
      return state.showAnnotationInBchart;
    },
    getBookmarkOrientation: state => {
      return state.horizonatlCharts;
    },
    getBookmarkLinechart: state => {
      return state.lineChart;
    },
    getBase64Image: state => {
      return state.mzImage.base64Image;
    },
    getBrightFieldImage: state => {
      return state.brightFieldImage;
    },
    getFocusMzList: state => {
      return state.focusMzList;
    },
    getMzForAggregationList: state => {
      return state.addMzToAggregationList;
    }
  },
  mutations: {
    // build the orginal data from the backend in the store
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
    // Fills the data in the store with every information for the visualisation
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
    // Add color to the Data in store, gets color from colowheel service
    ADD_COLOR_TO_FULL_DATA: (state, allPrototypeColors) => {
      Object.keys(allPrototypeColors).forEach(function (pro) {
        state.currentRingData[pro.toString()]['color'] = allPrototypeColors[pro].toString();
      });
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
    // if bookmark is choosed it will be added
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
    // if bookmark is deleted it removes the bookmark from store
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
      d3.select('#' + itemId).selectAll('*').remove();
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
      state.ringCoefficients = mzService.normalizeCoefficients(coefficients);
    },
    SET_RING_IDX: (state, ringIdx) => {
      state.ringIdx = ringIdx;
    },
    // Sets the prototype position after moebius transformation
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
    // applys moebiustransformation on all prototyp positions
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
      state.startingIndizes = indizes;
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
    },
    SET_SHOW_MZ_IN_BCHART: state => {
      state.showMzInBchart = !state.showMzInBchart;
    },
    SET_SHOW_ANNOTATION_IN_BCHART: state => {
      state.showAnnotationInBchart = !state.showAnnotationInBchart;
    },
    SET_BOOKMARKS_HORIZONTAL: state => {
      state.horizonatlCharts = !state.horizonatlCharts;
    },
    SET_BOOKMARKS_LINECHART: state => {
      state.lineChart = !state.lineChart;
    },
    SET_IMAGE_DATA_VALUES: (state, image) => {
      state.mzImage.base64Image = image;
    },
    SET_MERGE_METHOD: (state, method) => {
      state.mzImage.currentMergeMethod = method;
    },
    SET_COLORSCALE: (state, colorscale) => {
      state.mzImage.colorScale = colorscale;
    },
    SET_NEW_MZ_VALUE: (state, mzList) => {
      state.mzImage.selectedMzValues = mzList;
    },
    SET_BRIGHTFIELD_IMAGE: (state, image) => {
      if (image === 'No_Img') {
        state.brightFieldImage = false;
      } else {
        state.brightFieldImage = image;
      }
    },
    SET_FOCUS_MZ_LIST: (state, bool) => {
      state.focusMzList = bool;
    },
    SET_MZ_TO_AGGREGATIONLIST: (state, mz) => {
      state.addMzToAggregationList = mz;
    }
  },
  actions: {
    // gets the informations from the backend and the ring
    getDimAndIndizes: context => {
      const url = API_URL + '/ringdata';
      axios
        .get(url)
        .then(response => {
          context.commit('SET_COEFF_INDEX', response.data.indizes);
          context.commit('SET_SEGMENTATION_DIM', response.data.dim);
          context.dispatch('getRingCoefficients');
        })
        .catch(function (e) {
          console.error(e);
          alert('Error while fetching data');
        });
    },
    // open and reads Json
    openJson: context => {
      const url = API_URL + '/getjson';
      axios
        .get(url)
        .then(response => {
          context.commit('SET_ORIGINAL_DATA', response.data);
          context.commit('SET_FULL_DATA');
        })
        .catch(function (e) {
          console.error(e);
        });
    },
    // gets the coefficients for all mz in all prototypes if the current ring changes while WHIDE runs
    getCoeff: context => {
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
          context.commit('SET_FULL_DATA');
        })
        .catch(function (e) {
          console.error(e);
          alert('Error while getting coefficients or set Focus');
        });
    },
    // getting the coeeficents for all prototypes in the first ring, gets only called at starting
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
          context.dispatch('openJson');
        })
        .catch(function (e) {
          console.error(e);
          alert('Error while getting coefficients or set Focus');
        });
    },
    // load brightfiel image
    getBrightfieldImage: context => {
      const url = API_URL + '/brightfieldimage';
      axios
        .get(url)
        .then(response => {
          context.commit('SET_BRIGHTFIELD_IMAGE', response.data);
        })
        .catch(function (err) {
          console.error(err);
        });
    },
    // Get the mzImage for choosen mz values or value
    fetchImageData: (context) => {
      let mzValues = context.state.mzImage.selectedMzValues;
      // do an api fetch for a combination image of multiple mz values
      if (mzValues.length > 0) {
        const mergeMethod = context.state.mzImage.currentMergeMethod;
        const colorscale = context.state.mzImage.colorScale;
        const url = API_URL + '/mzimage';
        const postData = {
          mzValues: mzValues,
          colorscale: context.state.mzImage.colorScales[colorscale],
          method: context.state.mzImage.mergeMethods[mergeMethod]
        };
        axios
          .post(url, postData)
          .then(response => {
            context.commit('SET_IMAGE_DATA_VALUES', response.data);
          })
          .catch(function (e) {
            console.error(e);
          });
      }
    }
  }
});
