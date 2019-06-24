<template>
  <div>
      <div>
        <canvas id="colorwheelCanvas" width="300" height="300">
        </canvas>
      </div>
      <div>
        <p>Set Granularity:</p>
         <b-form-input v-model="ringGranularity" v-bind:type="'range'" min="0" v-bind:max="lengthRings" class="slider" id="ringGranularity" @change="changePos"></b-form-input>
      </div>
      <p>{{ringGranularity}}</p>
  </div>
</template>

<script>
import * as cw from '../services/colorWheel'
import { mapGetters } from 'vuex'

export default {
  name: 'ColorPicker',
  data: function () {
    return {
      lengthRings: null,
      midRings: null,
      ringGranularity: 0
    }
  },
  created () {
  },
  computed: {
    ...mapGetters({
      rings: 'getRings'
    })
  },
  mounted () {
    this.getPos('ring0')
    this.setGranulaity()
  },
  methods: {
    getPos: function (r) {
      var pos = []
      var ring = this.rings[r]
      Object.keys(ring).forEach(function (p) {
        var proto = Object.values(ring[p])
        pos.push(proto[0])
      })
      // console.log(pos)
      cw.createColorWheel(pos)
    },
    setGranulaity: function () {
      this.lengthRings = Object.keys(this.rings).length - 1
    },
    changePos: function () {
      this.getPos('ring' + this.ringGranularity.toString())
    }
  }
}
</script>

<style scoped lang="scss">
  #colorwheelCanvas {
    margin-left: auto;
    margin-right: auto;
    margin-bottom: 1em;
    display: block;
    top: 5px;
  }
  .colorDiv {
    font-family: monospace;
    padding: 1em;
    width: 256px;
    margin-left: auto;
    margin-right: auto;
    margin-bottom: 1em;
    border-radius: 2px;
  }
  .slider{
    width: 200px;
  }

</style>
