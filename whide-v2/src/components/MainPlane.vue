<template>
  <div class="mainPlane">
    <p id="segmentationAlignment" align="center">
      <canvas id="virtCanvas" class="virtSegmentationCanvas" style="width: 70vw; height: 90vh"/>
      <canvas id="brightfield" class="brightfieldCanvas" style="width: 70vw; height: 90vh"/>
      <canvas id="segMap" class="segmentationCanvas" style="width: 70vw; height: 90vh"/>
      <canvas id="mzChannelImage" class="mzImageCanvas" style="width: 70vw; height: 90vh"/>
      <canvas id="highlightSeg" class="segmentationCanvas" style="width: 70vw; height: 90vh"/>
    </p>
    <div class="transparancy-container">
      <p style="color: white">Transparancy</p>
      <b-form-input v-model="alphaValue" v-bind:type="'range'" min="0" max="1" step="0.05" id="alphaChanger"
                    class="slider" @change="changeAlphaValue"/>

    </div>
    <div class="mzImageButtonContainer">
      <b-button-group>
        <b-button v-if="!this.showMzImage" id="mzImageOn" v-on:click="toggleMzImage">MZ-Image On</b-button>
        <b-button v-if="this.showMzImage" id="mzImageOff" v-on:click="toggleMzImage">MZ-Image Off</b-button>

        <b-dropdown right text="Method" >
          <b-dropdown-item id="methodMean" style="background-color: orange" v-on:click="chooseMethod('methodMean')">Mean</b-dropdown-item>
          <b-dropdown-item id="methodMedian" v-on:click="chooseMethod('methodMedian')">Median</b-dropdown-item>
          <b-dropdown-item id="methodMin" v-on:click="chooseMethod('methodMin')">Min</b-dropdown-item>
          <b-dropdown-item id="methodMax" v-on:click="chooseMethod('methodMax')">Max</b-dropdown-item>
        </b-dropdown>
        <b-dropdown right text="Colorscale">
          <b-dropdown-item id="interpolateViridis" style="background-color: orange" v-on:click="chooseColorscale('interpolateViridis')">Viridris</b-dropdown-item>
          <b-dropdown-item id="interpolateMagma" v-on:click="chooseColorscale('interpolateMagma')">Magma</b-dropdown-item>
          <b-dropdown-item id="interpolatePiYG" v-on:click="chooseColorscale('interpolatePiYG')">PiYG</b-dropdown-item>
          <b-dropdown-item id="interpolatePlasma" v-on:click="chooseColorscale('interpolatePlasma')">Plasma</b-dropdown-item>
          <b-dropdown-item id="interpolateInferno" v-on:click="chooseColorscale('interpolateInferno')">Inferno</b-dropdown-item>
        </b-dropdown>
      </b-button-group>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';
import * as sm from '../services/SegmentationService.js';
import store from '../store';
import * as d3 from 'd3';

export default {
  name: 'MainPlane.vue',
  data: function () {
    return {
      alphaValue: 1,
      currentTransformation: { k: 1, x: 0, y: 0 },
      currentMethod: 'mean',
      currentColorscale: 'interpolateViridis',
      showMzImage: false
    };
  },
  computed: {
    ...mapGetters({
      dim: 'getSegmentationDim',
      colorsReady: 'getIfColorsReady',
      outsideHighlight: 'getHighlightedPrototypeOutside',
      transformation: 'getSegmentationTransformation',
      base64Image: 'getBase64Image'
    })
  },
  mounted () {
    this.unsubscribe = store.subscribe(mutation => {
      if (mutation.type === 'SET_COLORS_READY') {
        this.clearSegmentation();
        this.drawSegmentation(this.outsideHighlight['id'], this.currentTransformation, this.alphaValue);
      }
      if (mutation.type === 'HIGHLIGHT_PROTOTYPE_OUTSIDE') {
        if (this.outsideHighlight['outside']) {
          this.drawHighlight(this.outsideHighlight['id'], this.currentTransformation);
        }
      }
      if (mutation.type === 'SET_SEGMENTATION_TRANSFORMATION') {
        this.currentTransformation = this.transformation;
        this.drawMzImage();
      }
      if (mutation.type === 'SET_CURRENT_HIGHLIGHTED_PROTOTYPE') {
        this.drawHighlight(this.outsideHighlight['id'], this.currentTransformation);
      }
      if (mutation.type === 'SET_IMAGE_DATA_VALUES') {
        this.drawMzImage();
      }
    });
  },
  beforeDestroy () {
    this.unsubscribe();
  },
  methods: {
    drawSegmentation: function (prototype = '', transformation = { k: 1, x: 0, y: 0 }, alpha = 1) {
      if (this.colorsReady) {
        sm.drawSegmentationMap(this.dim, prototype, transformation, alpha);
      }
    },
    drawHighlight: function (prototyp, transformation) {
      if (this.colorsReady) {
        if (prototyp !== null) {
          sm.highlightprototypeSegmentation(this.dim, prototyp, transformation);
        } else {
          const highlightCanvas = document.getElementById('highlightSeg');
          const highCtx = highlightCanvas.getContext('2d');
          highCtx.clearRect(0, 0, highlightCanvas.width, highlightCanvas.height);
        }
      }
    },
    drawMzImage: function () {
      const mzCanvas = document.getElementById('mzChannelImage');
      const mzCtx = mzCanvas.getContext('2d');
      mzCtx.clearRect(0, 0, mzCanvas.width, mzCanvas.height);
      sm.drawMzImage(this.base64Image, this.dim, this.transformation);
    },
    clearSegmentation: function () {
      const virtCanvas = document.getElementById('virtCanvas');
      const virtCtx = virtCanvas.getContext('2d');
      virtCtx.clearRect(0, 0, virtCanvas.width, virtCanvas.height);

      const canvas = document.getElementById('segMap');
      const ctx = canvas.getContext('2d');
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const highlightCanvas = document.getElementById('highlightSeg');
      const highCtx = highlightCanvas.getContext('2d');
      highCtx.clearRect(0, 0, highlightCanvas.width, highlightCanvas.height);
    },
    changeAlphaValue: function () {
      this.clearSegmentation();
      this.drawSegmentation(this.outsideHighlight['id'], this.currentTransformation, this.alphaValue);
    },
    chooseMethod: function (id) {
      d3.select('#' + this.currentMethod).style('background-color', '');
      d3.select('#' + id).style('background-color', 'orange');
      this.currentMethod = id;
      store.commit('SET_MERGE_METHOD', id);
    },
    chooseColorscale: function (id) {
      d3.select('#' + this.currentColorscale).style('background-color', '');
      d3.select('#' + id).style('background-color', 'orange');
      this.currentColorscale = id;
      store.commit('SET_COLORSCALE', id);
    },
    toggleMzImage: function () {
      this.showMzImage = !this.showMzImage;
      if (this.showMzImage) {
        d3.select('#mzChannelImage')
          .style('z-index', '104');
      } else {
        d3.select('#mzChannelImage')
          .style('z-index', '100');
      }
    }
  }
};

</script>

<style scoped lang="scss">
.mainPlane {
  position: absolute;
  top: 0px;
  left: 0px;
  right: 0px;
  bottom: 0px;
  background-color: #404040;
  z-index: 100;
  color:  #404040;;
}
  .segmentationCanvas {
    position: absolute;
    pointer-events: none;
    top: 30px;
    left: 0px;
    margin-left:10vw;
    margin-right: 310px;
  }

.virtSegmentationCanvas {
  position: absolute;
  top: 30px;
  left: 0px;
  margin-left:10vw;
  margin-right: 310px;
}

.transparancy-container{
  position: absolute;
  left: 45vw;
  top:10px;
  align-content: center;
  z-index: 110;
  .slider{
    width: 7vw;
  }
}
#highlightSeg {
  position: absolute;
  pointer-events: none;
  width: 70vw;
  height: 90vh;
  top: 30px;
  z-index: 105;
  left: 0;
  margin-left: 190px;
  margin-right: 350px;
}
#mzChannelImage {
  position: absolute;
  pointer-events: none;
  width: 70vw;
  height: 90vh;
  top: 30px;
  z-index: 100;
  left: 0;
  margin-left: 190px;
  margin-right: 350px;
}
#segMap {
  position: absolute;
  pointer-events: none;
  width: 70vw;
  height: 90vh;
  top: 30px;
  z-index: 104;
  left: 0;
  margin-left: 190px;
  margin-right: 350px;
}
  #brightfield {
    position: absolute;
    pointer-events: none;
    width: 70vw;
    height: 90vh;
    top: 30px;
    z-index: 102;
    left: 0;
    margin-left: 190px;
    margin-right: 350px;
  }
  #virtCanvas {
    position: absolute;
    width: 70vw;
    height: 90vh;
    top: 30px;
    z-index: 101;
    left: 0;
    margin-left: 190px;
    margin-right: 350px;
  }
  .mzImageButtonContainer{
    position: absolute;
    left: 11vw;
    top: 10px;
    width: auto;
  }

</style>
