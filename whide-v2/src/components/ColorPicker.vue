<template>
    <SidebarWidget v-bind:side="side" v-bind:initialExpanded="initialExpanded">
      <div>
        <canvas id="colorwheelCanvas" width="512" height="512">
        </canvas>
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
  created () {},
  components: {
    SidebarWidget
  },
  computed: {
    ...mapGetters({
      rings: 'getRings'
    })
  },
  mounted () {
    cw.createColorWheel()
    //  this.getPos('ring0')
  },
  methods: {
    getPos: function (ring) {
      console.log(this.rings['ring0'])
      // for (let prototyp of Object.keys(this.rings['ring0'])) {
      // console.log(this.rings['ring0'][prototyp]['pos'])
      // }
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
