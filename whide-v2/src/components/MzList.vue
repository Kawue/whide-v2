<template>
    <SidebarWidget v-bind:side="side" v-bind:initialExpanded="initialExpanded">
      <div>MZs</div>
    </SidebarWidget>
</template>

<script>
import SidebarWidget from './SidebarWidget'

export default {
  props: ['initialExpanded'],
  extends: SidebarWidget,
  name: 'mzlist',
  components: {
    SidebarWidget
  },

  data () {
    return {
    }
  },
  created () {
    console.log('MzList')
    console.log(this.initialExpanded)
  }
}

</script>
<style scoped lang="scss">
  .sidebarWidget {
    background-color: aqua;
  }
  .sidebarWidget {
    &.expanded {
      width: 200px !important;
    }
  }
</style>
