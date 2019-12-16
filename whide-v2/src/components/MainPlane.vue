<template>
  <div class="mainPlane">
    <p id="segmentationAlignment" align="center">
      <canvas id="virtCanvas" class="virtSegmentationCanvas" style="width: 70vw; height: 90vh"></canvas>
      <canvas id="segMap" class="segmentationCanvas" style="width: 70vw; height: 90vh"></canvas>
      <canvas id="highlightSeg" class="segmentationCanvas" style="width: 70vw; height: 90vh"></canvas>
    </p>
    <div class="transparancy-container">
      <p style="color: white">Transparancy</p>
      <b-form-input v-model="alphaValue" v-bind:type="'range'" min="0" max="1" step="0.05" id="alphaChanger" class="slider" @change="changeAlphaValue"></b-form-input>

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
      currentTransformation: { k: 1, x: 0, y: 0 }
    };
  },
  computed: {
    ...mapGetters({
      dim: 'getSegmentationDim',
      colorsReady: 'getIfColorsReady',
      outsideHighlight: 'getHighlightedPrototypeOutside',
      transformation: 'getSegmentationTransformation'
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
      }
      if (mutation.type === 'SET_CURRENT_HIGHLIGHTED_PROTOTYPE') {
        this.drawHighlight(this.outsideHighlight['id'], this.currentTransformation);
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
          d3.select('#highlightSeg').remove();
          d3.select('#segmentationAlignment')
            .append('canvas')
            .style('position', 'absolute')
            .attr('class', 'segmentationCanvas')
            .attr('id', 'highlightSeg')
            .style('pointer-events', 'none')
            .style('width', '70vw')
            .style('height', '90vh')
            .style('top', '30px')
            .style('z-index', '101')
            .style('left', '0px')
            .style('margin-left', '190px')
            .style('margin-right', '350px');
        }
      }
    },
    clearSegmentation: function () {
      d3.select('#virtCanvas').remove();
      d3.select('#segMap').remove();
      d3.select('#highlightSeg').remove();

      d3.select('#segmentationAlignment')
        .append('canvas')
        .style('position', 'absolute')
        .attr('class', 'virtSegmentationCanvas')
        .attr('id', 'virtCanvas')
        .style('z-index', '101')
        .style('width', '70vw')
        .style('  height', '90vh')
        .style('top', '30px')
        .style('left', '0px')
        .style('margin-left', '190px')
        .style('margin-right', '350px');

      d3.select('#segmentationAlignment')
        .append('canvas')
        .style('position', 'absolute')
        .attr('class', 'segmentationCanvas')
        .attr('id', 'segMap')
        .style('pointer-events', 'none')
        .style('width', '70vw')
        .style('height', '90vh')
        .style('top', '30px')
        .style('z-index', '101')
        .style('left', '0px')
        .style('margin-left', '190px')
        .style('margin-right', '350px');

      d3.select('#segmentationAlignment')
        .append('canvas')
        .style('position', 'absolute')
        .attr('class', 'segmentationCanvas')
        .attr('id', 'highlightSeg')
        .style('pointer-events', 'none')
        .style('width', '70vw')
        .style('height', '90vh')
        .style('top', '30px')
        .style('z-index', '101')
        .style('left', '0px')
        .style('margin-left', '190px')
        .style('margin-right', '350px');
    },
    changeAlphaValue: function () {
      this.clearSegmentation();
      this.drawSegmentation(this.outsideHighlight['id'], this.currentTransformation, this.alphaValue);
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
  align-content: center;
  z-index: 102;
  .slider{
    width: 7vw;
  }
}

</style>
