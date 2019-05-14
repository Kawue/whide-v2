<template>
  <BottombarWidget v-bind:side="side" v-bind:initialExpanded="initialExpanded">
    <div>Options</div>
  </BottombarWidget>
</template>

<script>
import BottombarWidget from './BottombarWidget'
export default {
  props: ['initialExpanded'],
  name: 'Options',
  extends: BottombarWidget,
  components: { BottombarWidget },
  data () {
    return {
    }
  },

  created () {
    console.log('Options')
    console.log(this.initialExpanded)
  }
}
</script>

<style scoped lang="scss">
  .BottombarWidget {
    background-color: aqua;
  }
  .BottombarWidget {
    &.expanded {
      width: 200px !important;
    }
  }
</style>
