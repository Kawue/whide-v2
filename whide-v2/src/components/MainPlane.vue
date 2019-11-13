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

export default {
  name: 'MainPlane.vue',
  computed: {
    ...mapGetters({
      dim: 'getSegmentationDim',
      colorsReady: 'getIfColorsReady',
      outsideHighlight: 'getHighlightedPrototypeOutside'
    })
  },
  mounted () {
    this.unsubscribe = store.subscribe(mutation => {
      if (mutation.type === 'SET_COLORS_READY') {
        this.drawSegmentation();
      }
      if (mutation.type === 'HIGHLIGHT_PROTOTYPE_OUTSIDE') {
        this.drawSegmentation(this.outsideHighlight['outside'], this.outsideHighlight['id']);
      }
    });
  },
  beforeDestroy () {
    this.unsubscribe();
  },
  methods: {
    drawSegmentation: function (outside = false, prototype = '') {
      if (this.colorsReady) {
        sm.drawSegmentationMap(this.dim, outside, prototype);
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
