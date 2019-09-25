<template>
  <div>
      <div>
        <canvas id="colorwheelCanvas" width="310" height="310">
        </canvas>
      </div>
    <div class="colorwheelOptions">
       <div class="sliderOptions">
        <p v-if="!sliderDisabled">Set Granularity:</p>
         <p v-else>Clear Bookmarks to set Granularity!</p>
         <b-form-input v-model="ringGranularity" v-bind:type="'range'" :disabled="sliderDisabled" min="0" v-bind:max="lengthRings" class="slider" id="ringGranularity" @change="changePos" ></b-form-input>
      </div>
      <div class="position-g">
        <div class="controlls">
          <div class="topControll">
            <b-button id="up" variant="outline-dark" size="sm" v-on:click="moveUp()">
              <v-icon name="arrow-up"></v-icon>
            </b-button>
          </div>
          <div class="midControll">
            <b-button id="left" variant="outline-dark" size="sm" v-on:click="moveLeft()" >
              <v-icon name="arrow-left"></v-icon>
            </b-button>
            <b-button id="default " variant="outline-dark" size="sm" v-on:click="setDefault()" >
              <v-icon name="redo"></v-icon>
            </b-button>
            <b-button id="right" variant="outline-dark" size="sm" v-on:click="moveRight()">
              <v-icon name="arrow-right"></v-icon>
            </b-button>
          </div>
          <div class="bottomControll">
            <b-button id="down" variant="outline-dark" size="sm" v-on:click="moveDown()">
              <v-icon name="arrow-down"></v-icon>
            </b-button>
         </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as cw from '../services/colorWheel';
import { mapGetters } from 'vuex';
import store from '../store';
import * as d3 from 'd3';

export default {
  name: 'ColorPicker',
  data: function () {
    return {
      lengthRings: null,
      midRings: null,
      ringGranularity: 0,
      disabled: false
    };
  },
  computed: {
    ...mapGetters({
      prototypesPosition: 'getPrototypesPosition',
      numberOfRings: 'getNumberOfRings',
      sliderDisabled: 'getColorSlider'
    })
  },

  created: function () {
    window.addEventListener('keydown', this.chooseMove);
  },
  mounted () {
    this.getPos('ring0');
    store.dispatch('getRingCoefficients', 'ring0');
    this.setGranulaity();
    store.subscribe(mutation => {
      if (mutation.type === 'SET_MOEBIUS') {
        d3.select('#colorwheelContainer').remove();
        this.getPos(this.prototypesPosition);
      }
      if (mutation.type === 'SET_DEFAULT_POSITION') {
        d3.select('#colorwheelContainer').remove();
        this.getPos(this.prototypesPosition);
      }
    });
  },
  methods: {
    getPos: function () {
      cw.createColorWheel(this.prototypesPosition);
    },
    setGranulaity: function () {
      this.lengthRings = this.numberOfRings - 1;
    },
    changePos: function () {
      d3.select('#colorwheelContainer').remove();
      let currentRing = 'ring' + this.ringGranularity.toString();
      store.commit('SET_RING_IDX', currentRing);
      store.commit('SET_PROTOTYPES_POSITION');
      store.commit('SET_FOCUS_DEFAULT');
      this.getPos();
      store.dispatch('getRingCoefficients', currentRing);
    },
    chooseMove: function () {
      if (event.keyCode === 38) {
        this.moveUp();
      } else if (event.keyCode === 37) {
        this.moveLeft();
      } else if (event.keyCode === 39) {
        this.moveRight();
      } else if (event.keyCode === 40) {
        this.moveDown();
      }
    },
    moveUp: function () {
      let up = { 'x': 0, 'y': 1 };
      store.commit('SET_MOEBIUS', up);
      store.commit('SET_FOCUS_DEFAULT');
    },
    moveRight: function () {
      let right = { 'x': -1, 'y': 0 };
      store.commit('SET_MOEBIUS', right);
      store.commit('SET_FOCUS_DEFAULT');
    },
    moveLeft: function () {
      let left = { 'x': 1, 'y': 0 };
      store.commit('SET_MOEBIUS', left);
      store.commit('SET_FOCUS_DEFAULT');
    },
    moveDown: function () {
      let down = { 'x': 0, 'y': -1 };
      store.commit('SET_MOEBIUS', down);
      store.commit('SET_FOCUS_DEFAULT');
    },
    setDefault: function () {
      store.commit('SET_DEFAULT_POSITION');
      store.commit('SET_FOCUS_DEFAULT');
    }
  }
};
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
  .colorwheelOptions{
    display: flex;
    flex-direction: column;
  }
  .slider{
    width: 200px;
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
