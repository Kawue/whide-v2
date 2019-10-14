<template>
  <div class="mainPlane">
    <p align="center">
      <canvas id="segMap" class="segmentationCanvas"></canvas>
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
      dim: 'getSegmentationDim'
    })
  },
  mounted () {
    this.unsubscribe = store.subscribe(mutation => {
      if (mutation.type === 'SET_SEGMENTATION_DIM') {
        this.drawSegmentation();
      }
    });
  },
  beforeDestroy () {
    this.unsubscribe();
  },
  methods: {
    drawSegmentation: function () {
      sm.drawSegmentationMap(this.dim);
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
  color: white;
}
  .segmentationCanvas {
    position: relative;
    width: 70%;
    height: 700px;
    top: 30px;
    margin-left:190px;
    margin-right: 350px;
    background-color: #42b983;
  }

</style>
