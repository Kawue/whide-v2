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
      <div class="controlls">
        <div class="topControll">
          <b-button id="up" variant="info" size="sm" v-on:click="moveUp()">Up</b-button>
        </div>
        <div class="midControll">
          <b-button id="left" variant="info" size="sm" v-on:click="moveLeft()">Left</b-button>
          <b-button id="default " variant="info" size="sm" v-on:click="setDefault()">Default</b-button>
          <b-button id="right" variant="info" size="sm" v-on:click="moveRight()">Right</b-button>
        </div>
        <div class="bottomControll">
          <b-button id="down" variant="info" size="sm" v-on:click="moveDown()">Down</b-button>
        </div>
        </div>
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
      ringGranularity: 0
    }
  },
  computed: {
    ...mapGetters({
      prototypesPosition: 'getPrototypesPosition',
      numberOfRings: 'getNumberOfRings'
    })
  },
  mounted () {
    this.getPos('ring0')
    store.dispatch('getRingCoefficients', 'ring0')
    this.setGranulaity()
    store.subscribe(mutation => {
      if (mutation.type === 'SET_MOEBIUS') {
        d3.select('#colorwheelContainer').remove()
        this.getPos(this.prototypesPosition)
      }
      if (mutation.type === 'SET_DEFAULT_POSITION') {
        d3.select('#colorwheelContainer').remove()
        this.getPos(this.prototypesPosition)
      }
    })
  },
  methods: {
    getPos: function () {
      cw.createColorWheel(this.prototypesPosition)
    },
    setGranulaity: function () {
      this.lengthRings = this.numberOfRings - 1
    },
    changePos: function () {
      d3.select('#colorwheelContainer').remove()
      let currentRing = 'ring' + this.ringGranularity.toString()
      store.commit('SET_RING_IDX', currentRing)
      store.commit('SET_PROTOTYPES_POSITION')
      this.getPos()
      store.dispatch('getRingCoefficients', currentRing)
    },
    moveUp: function () {
      let up = { 'x': 0, 'y': -1 }
      store.commit('SET_MOEBIUS', up)
    },
    moveRight: function () {
      let right = { 'x': 1, 'y': 0 }
      store.commit('SET_MOEBIUS', right)
    },
    moveLeft: function () {
      let left = { 'x': -1, 'y': 0 }
      store.commit('SET_MOEBIUS', left)
    },
    moveDown: function () {
      let down = { 'x': 0, 'y': 1 }
      store.commit('SET_MOEBIUS', down)
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
  .controlls {
    display: flex;
    flex-direction: column;
    b-button {
      display: inline-block;
    }
  }
  .topControll {
    display: flex;
    justify-content: center;
  }
  .midControll {
    display: flex;
    justify-content: center;
  }
  .bottomControll {
    display: flex;
    justify-content: center;

  }

</style>
