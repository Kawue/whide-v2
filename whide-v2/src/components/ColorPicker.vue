<template>
  <div>
    <div>
      <canvas id="colorwheelCanvas" width="310" height="310">
      </canvas>
    </div>
    <div class="colorwheelOptions">
      <div class="sliderOptions">
        <p style="color: white" v-if="!sliderDisabled">Set Granularity:</p>
        <p v-else>Clear Bookmarks to set Granularity!</p>
        <b-form-input v-model="ringGranularity" v-bind:type="'range'" :disabled="sliderDisabled" min="0" v-bind:max="lengthRings" class="slider" id="ringGranularity" @change="changePos"></b-form-input>
      </div>
      <div class="container">
        <div class="position-g">
          <div class="controlls">
            <div class="topControll">
              <b-button id="up"  size="sm">
                <v-icon name="arrow-up" style="color: orange"></v-icon>
              </b-button>
            </div>
            <div class="midControll">
              <b-button id="left"  size="sm" >
                <v-icon name="arrow-left" style="color: orange"></v-icon>
              </b-button>
              <b-button id="down"  size="sm">
                <v-icon name="arrow-down" style="color: orange"></v-icon>
              </b-button>
              <b-button id="right"  size="sm">
                <v-icon name="arrow-right" style="color: orange"></v-icon>
              </b-button>
            </div>
            <div class="bottomControll">
              <b-button id="default "  size="sm" v-on:click="setDefault()" >
                <v-icon name="backward" style="color: orange"></v-icon>
              </b-button>
            </div>
          </div>
        </div>
        <div  class="rotate">
          <div class="topControll">
          <b-button id="diskus" size="sm" >
            <v-icon name="redo" style="color: orange"></v-icon>
          </b-button>
          </div>
          <div class="bottomControll">
          <b-button id="diskusBack"  size="sm" v-on:click="spinDiskusBack">
            <v-icon name="backward" style="color: orange"></v-icon>
          </b-button>
          </div>
        </div>
          <div class="rotate">
            <div class="topControll">
            <b-button id="posSwitcher" size="sm" v-on:click="switchPos">
              <v-icon name="spinner" style="color: orange"></v-icon>
            </b-button>
            </div>
            <div class="bottomControll">
            <b-button id="'backPosSwitcher" size="sm" v-on:click="switchPosBack">
              <v-icon name="backward" style="color: orange"></v-icon>
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
      disabled: false,
      currentMarkedPrototypeColor: null,
      currentMarkedPrototype: null,
      rotations: 0,
      posSwitcher: 0,
      mousedownRotate: false
    };
  },
  computed: {
    ...mapGetters({
      prototypesPosition: 'getPrototypesPosition',
      numberOfRings: 'getNumberOfRings',
      sliderDisabled: 'getColorSlider',
      sagmentationScalor: 'getSegmentationScalor',
      highlightedPrototype: 'getCurrentHighlightedPrototype',
      coefficientsLoaded: 'getCoefficientLoad'

    })
  },

  created: function () {
    window.addEventListener('keydown', this.chooseMove);
  },
  mounted () {
    this.buttonEvent('diskus', this.rotatetDiskus);
    this.buttonEvent('up', this.moveUp);
    this.buttonEvent('left', this.moveLeft);
    this.buttonEvent('right', this.moveRight);
    this.buttonEvent('down', this.moveDown);
    this.setGranulaity();
    store.subscribe(mutation => {
      if (mutation.type === 'SET_MOEBIUS') {
        d3.select('#colorwheelContainer').remove();
        this.clearSegmentationMap();
        this.getPos();
      }
      if (mutation.type === 'SET_DEFAULT_POSITION') {
        d3.select('#colorwheelContainer').remove();
        this.clearSegmentationMap();
        this.getPos();
      }
      if (mutation.type === 'SET_FULL_DATA') {
        this.getPos();
      }
      if (mutation.type === 'SET_CURRENT_HIGHLIGHTED_PROTOTYPE') {
        if (this.highlightedPrototype !== null) {
          if (this.currentMarkedPrototype !== this.highlightedPrototype) {
            if (this.currentMarkedPrototype !== null) {
              d3.select('.' + this.currentMarkedPrototype)
                .style('fill', this.currentMarkedPrototypeColor);
              this.currentMarkedPrototypeColor = d3.select('.' + this.highlightedPrototype).style('fill');
              let markedColor = 'rgba(255,255,255,255)';
              d3.select('.' + this.highlightedPrototype)
                .style('fill', markedColor);
              this.currentMarkedPrototype = this.highlightedPrototype;
            } else {
              this.currentMarkedPrototypeColor = d3.select('.' + this.highlightedPrototype).style('fill');
              let markedColor = 'rgba(255,255,255,255)';
              d3.select('.' + this.highlightedPrototype)
                .style('fill', markedColor);
              this.currentMarkedPrototype = this.highlightedPrototype;
            }
          }
        } else {
          d3.select('.' + this.currentMarkedPrototype)
            .style('fill', this.currentMarkedPrototypeColor);
          this.currentMarkedPrototype = null;
          this.currentMarkedPrototypeColor = null;
        }
      }
    });
  },
  methods: {
    getPos: function () {
      cw.createColorWheel(this.prototypesPosition, this.rotations, this.posSwitcher, parseInt(this.ringGranularity));
    },
    setGranulaity: function () {
      this.lengthRings = this.numberOfRings - 1;
    },
    changePos: function () {
      d3.select('#colorwheelContainer').remove();
      this.clearSegmentationMap();
      let currentRing = 'ring' + this.ringGranularity.toString();
      store.commit('SET_RING_IDX', currentRing);
      store.commit('SET_PROTOTYPES_POSITION');
      store.dispatch('getRingCoefficients');
      store.commit('SET_COLORS_READY', false);
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
    },
    moveRight: function () {
      let right = { 'x': -1, 'y': 0 };
      store.commit('SET_MOEBIUS', right);
    },
    moveLeft: function () {
      let left = { 'x': 1, 'y': 0 };
      store.commit('SET_MOEBIUS', left);
    },
    moveDown: function () {
      let down = { 'x': 0, 'y': -1 };
      store.commit('SET_MOEBIUS', down);
    },
    setDefault: function () {
      this.rotations = 0;
      this.posSwitcher = 0;
      store.commit('SET_DEFAULT_POSITION');
    },
    clearAllBookmarks: function () {
      store.commit('CLEAR_ALL_BOOKMARKS');
    },
    clearSegmentationMap: function () {
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
    },
    rotatetDiskus: function () {
      this.rotations -= 0.1;
      d3.select('#colorwheelContainer').remove();
      this.clearSegmentationMap();
      this.getPos();
      store.commit('UPDATE_COLOR');
    },
    spinDiskusBack: function () {
      this.rotations = 0;
      d3.select('#colorwheelContainer').remove();
      this.clearSegmentationMap();
      this.getPos();
      store.commit('UPDATE_COLOR');
    },
    switchPos: function () {
      this.posSwitcher += 1;
      d3.select('#colorwheelContainer').remove();
      this.clearSegmentationMap();
      this.getPos();
      store.commit('UPDATE_COLOR');
    },
    switchPosBack: function () {
      this.posSwitcher = 0;
      d3.select('#colorwheelContainer').remove();
      this.clearSegmentationMap();
      this.getPos();
      store.commit('UPDATE_COLOR');
    },
    buttonEvent: function (id, func) {
      let timer;
      let object = document.getElementById(id);
      object.onmousedown = () => {
        timer = setInterval(() => {
          func();
        }, 50);
      };
      object.onmouseup = () => {
        clearInterval(timer);
      };
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
  .container {
    display: flex;
    flex-direction: row;
    justify-content: center;
  }
  .controlls {
    display: flex;
    flex-direction: column;
    b-button {
      display: inline-block;
    }
  }
  .postionClearAll {
    display: flex;
    height: 60px;
    justify-content: center;
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
    margin-top: 0.4vh;
  }
  .rotate {
    margin-left: 0.4vw;
    padding-left: 5px;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
  }

</style>
