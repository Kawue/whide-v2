<template>
  <TopbarWidget v-bind:side="side" v-bind:initialExpanded="initialExpanded">
    <div>Options</div>
  </TopbarWidget>
</template>

<script>
import TopbarWidget from './TopbarWidget'
export default {
  props: ['initialExpanded'],
  name: 'Options',
  extends: TopbarWidget,
  components: { TopbarWidget },
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
  .TopbarWidget {
    background-color: aqua;
  }
  .TobarWidget {
    &.expanded {
      width: 200px !important;
    }
  }
</style>
