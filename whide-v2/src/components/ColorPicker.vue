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
    <div class="position-g">
      <p>Change Position of the Wheel</p>
      <b-button id="up" variant="info" size="sm" onclick="moveUp()">Up</b-button>
      <b-button id="left" variant="info" size="sm" onclick="moveLeft()">Left</b-button>
      <b-button id="default " variant="info" size="sm" onclick="setDefault()">Default</b-button>
      <b-button id="right" variant="info" size="sm" onclick="moveRight()">Right</b-button>
      <b-button id="down" variant="info" size="sm" onclick="moveDown()">Down</b-button>
    </div>
  </div>
</template>

<script>
import * as cw from '../services/colorWheel'
import { mapGetters } from 'vuex'
import store from '../store'
import * as d3 from 'd3'

export default {
  name: 'ColorPicker',
  data: function () {
    return {
      lengthRings: null,
      midRings: null,
      ringGranularity: 0,
      focusMoveSpeed: 0.01
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
    store.commit('SET_RING_IDX', 'ring0')
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
      d3.select('#colorwheelContainer').remove()
      let currentRing = 'ring' + this.ringGranularity.toString()
      this.getPos(currentRing)
      store.commit('SET_RING_IDX', currentRing)
    },
    moveUp: function () {
      store.commit('MOEBIUS', (0, 1))
    },
    moveRight: function () {
      store.commit('MOEBIUS', (1, 0))
    },
    moveLeft: function () {
      store.commit('MOEBIUS', (-1, 0))
    },
    moveDown: function () {
      store.commit('MOEBIUS', (0, -1))
    },
    setDefault: function () {
      store.commit('SET_DEFAULT_POSITION')
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
  .position-g{
    height: 200px;
    width: 200px;
    margin-left: auto;
    margin-right: auto;
  }
  #up {
    margin-top: 0;
  }
  #down {
    margin-bottom: 0;
  }
  #default {
    text-align: center;
  }
  #left {
    margin-left: 0;
  }
  #right {
    margin-right: 0;
  }

</style>
