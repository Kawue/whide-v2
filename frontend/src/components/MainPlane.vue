<template>
  <div class="mainPlane" id="mp">
    <p id="segmentationAlignment" align="center">
      <canvas id="virtCanvas" class="virtSegmentationCanvas" style="width: 70vw; height: 90vh"/>
      <canvas id="brightfield" class="brightfieldCanvas" style="width: 70vw; height: 90vh"/>
      <canvas id="segMap" class="segmentationCanvas" style="width: 70vw; height: 90vh"/>
      <canvas id="mzChannelImage" class="mzImageCanvas" style="width: 70vw; height: 90vh"/>
      <canvas id="highlightSeg" class="segmentationCanvas" style="width: 70vw; height: 90vh"/>
    </p>
    <div class="mzImageButtonContainer">
      <b-button v-if="!this.showMzImage" class="onOffButton" id="mzImageOn" v-on:click="toggleMzImage">mz-Image On</b-button>
      <b-button v-if="this.showMzImage" class="onOffButton" id="mzImageOff" v-on:click="toggleMzImage">mz-Image Off</b-button>
      <b-form-select v-model="selectedMethod" :options="methods" class="mb-0" id="methodChooser" text-field="text" value-field="value" v-on:change="chooseMethod()"></b-form-select>
      <b-form-select v-model="selectedColorscale" :options="colorScales" class="mb-0" id="scaleChooser" text-field="text" value-field="value" v-on:change="chooseColorscale()"></b-form-select>
    </div>
    <div class="transparancy-container">
      <p style="color: white">Transparancy</p>
      <b-form-input v-model="alphaValue" v-bind:type="'range'" min="0" max="1" :disabled="this.showMzImage" step="0.05" id="alphaChanger"
                    class="slider" @change="changeAlphaValue"/>
    </div>
    <div class="inverse-container">
      <b-button  v-if="this.showMzImage" class="inverse" id="invBut" v-on:click="toggleInverse">Inverse</b-button>
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
      showMzImage: false,
      selectedMethod: 'methodMean',
      methods: [
        { value: 'methodMean', text: 'Mean' },
        { value: 'methodMedian', text: 'Median' },
        { value: 'methodMin', text: 'Min' },
        { value: 'methodMax', text: 'Max' }
      ],
      selectedColorscale: 'interpolateViridis',
      colorScales: [
        { value: 'interpolateViridis', text: 'Viridris' },
        { value: 'interpolateMagma', text: 'Magma' },
        { value: 'interpolatePiYG', text: 'PiYG' },
        { value: 'interpolatePlasma', text: 'Plasma' },
        { value: 'interpolateInferno', text: 'Inferno' }
      ],
      inverse: false
    };
  },
  computed: {
    ...mapGetters({
      dim: 'getSegmentationDim',
      colorsReady: 'getIfColorsReady',
      outsideHighlight: 'getHighlightedPrototypeOutside',
      transformation: 'getSegmentationTransformation',
      base64Image: 'getBase64Image',
      brightfieldImage: 'getBrightFieldImage'
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
        if (parseFloat(this.alphaValue) !== 1) {
          this.drawBrightfieldImage();
        } else {
          this.clearBrightfield();
        }
      }
      if (mutation.type === 'SET_CURRENT_HIGHLIGHTED_PROTOTYPE') {
        this.drawHighlight(this.outsideHighlight['id'], this.currentTransformation);
      }
      if (mutation.type === 'SET_IMAGE_DATA_VALUES') {
        this.drawMzImage();
      }
      if (mutation.type === 'SET_BRIGHTFIELD_IMAGE') {
        // this.drawBrightfieldImage();
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
          sm.highlightprototypeSegmentation(this.dim, prototyp, transformation, this.inverse);
        } else {
          const highlightCanvas = document.getElementById('highlightSeg');
          const highCtx = highlightCanvas.getContext('2d');
          highCtx.clearRect(0, 0, highlightCanvas.width, highlightCanvas.height);
        }
      }
    },
    drawMzImage: function () {
      sm.drawMzImage(this.base64Image, this.dim, this.transformation);
    },
    drawBrightfieldImage: function () {
      sm.brightfieldImage(this.brightfieldImage, this.dim, this.transformation);
    },
    clearBrightfield: function () {
      const canvas = document.getElementById('brightfield');
      const ctx = canvas.getContext('2d');
      ctx.clearRect(0, 0, canvas.width, canvas.height);
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
    chooseMethod: function () {
      store.commit('SET_MERGE_METHOD', this.selectedMethod);
      store.dispatch('fetchImageData');
    },
    chooseColorscale: function () {
      store.commit('SET_COLORSCALE', this.selectedColorscale);
      store.dispatch('fetchImageData');
    },
    toggleMzImage: function () {
      this.showMzImage = !this.showMzImage;
      if (!this.showMzImage) {
        this.inverse = false;
      }
      if (this.showMzImage) {
        store.dispatch('fetchImageData');
        d3.select('#mzChannelImage')
          .style('z-index', '104');
      } else {
        d3.select('#mzChannelImage')
          .style('z-index', '100');
      }
    },
    toggleInverse: function () {
      this.inverse = !this.inverse;
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
    width: 400px;
    z-index: 115;
    display: flex;
    flex-direction: row;
  }
  .onOffButton {
    padding: 0;
    width: 350px;
    color: orange;
    background-color: #4f5051;
    font-size: 0.95em;

  }
  #invBut {
    padding: 0;
    width: 100px;
    color: orange;
    background-color: #4f5051;
    font-size: 0.95em;
  }
  .inverse-container {
    position: absolute;
    right: 30vw;
    top: 10px;
    z-index: 115;
  }
  .methodChooser {
  }
  .scaleChooser {
    }

</style>
