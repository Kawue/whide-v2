<template>
  <div class="mainPlane">
    <p id="segmentationAlignment" align="center">
      <canvas id="virtCanvas" class="virtSegmentationCanvas" style="width: 70vw; height: 90vh"></canvas>
      <canvas id="segMap" class="segmentationCanvas" style="width: 70vw; height: 90vh"></canvas>
    </p>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';
import * as sm from '../services/SegmentationService.js';
import store from '../store';
import * as d3 from 'd3';

export default {
  name: 'MainPlane.vue',
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
        this.drawSegmentation();
      }
      if (mutation.type === 'HIGHLIGHT_PROTOTYPE_OUTSIDE') {
        if (this.outsideHighlight['outside']) {
          this.clearSegmentation();
          console.log(this.transformation)
          this.drawSegmentation(this.outsideHighlight['outside'], this.outsideHighlight['id'], this.transformation);
        } else {
          this.clearSegmentation();
          this.drawSegmentation(false, '', this.transformation);
        }
      }
    });
  },
  beforeDestroy () {
    this.unsubscribe();
  },
  methods: {
    drawSegmentation: function (outside = false, prototype = '', transformation = { k: 1, x: 0, y: 0 }) {
      if (this.colorsReady) {
        sm.drawSegmentationMap(this.dim, outside, prototype, transformation);
      }
    },
    clearSegmentation: function () {
      d3.select('#virtCanvas').remove();
      d3.select('#segMap').remove();
      d3.select('#segmentationAlignment')
        .append('canvas')
        .style('position', 'absolute')
        .attr('class', 'virtSegmentationCanvas')
        .attr('id', 'virtCanvas')
        .style('z-index', '101')
        .style('background-color', '#404040')
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
        .style('background-color', '#404040')
        .style('width', '70vw')
        .style('height', '90vh')
        .style('top', '30px')
        .style('z-index', '101')
        .style('left', '0px')
        .style('margin-left', '190px')
        .style('margin-right', '350px');
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
    margin-left:190px;
    margin-right: 350px;
    background-color:  #404040;;
  }

.virtSegmentationCanvas {
  position: absolute;
  top: 30px;
  left: 0px;
  margin-left:190px;
  margin-right: 350px;
  background-color:  #404040;;
}

</style>
