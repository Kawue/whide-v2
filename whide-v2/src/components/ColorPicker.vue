<template>
    <SidebarWidget v-bind:side="side" v-bind:initialExpanded="initialExpanded">
      <div>
        <canvas id="colorwheelCanvas" width="256" height="256">
        </canvas>
      </div>
      <div>
        <p>Custom range slider:</p>
        <input type="range" min="1" v-bind:max="{lengthRings}" v-bind:value="2" class="slider" id="ringGranularity">
      </div>
    </SidebarWidget>
</template>

<script>
import SidebarWidget from './SidebarWidget'
import * as cw from '../services/colorWheel'
import { mapGetters } from 'vuex'

export default {
  extends: SidebarWidget,
  name: 'ColorPicker',
  props: {
    lengthRings: Number,
    midRings: Number,
    ringGranularity: String
  },
  created () {
  },
  components: {
    SidebarWidget
  },
  computed: {
    ...mapGetters({
      rings: 'getRings'
    })
  },
  mounted () {
    this.getPos('ring1')
    this.setGranulaity()
    console.log(this.lengthRings)
    console.log(this.midRings)
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
      this.lengthRings = this.rings.length
      this.midRings = Math.round(this.lengthRings / 2)
    }
  }
}
</script>

<style scoped lang="scss">
  .sidebarWidget {
    background-color: gold;
    &.expended {
      right:400px;
    }
  }
  #colorwheelCanvas {
    margin-left: auto;
    margin-right: auto;
    margin-bottom: 1em;
    display: block;
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


</style>
