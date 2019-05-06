<template>
    <BottombarWidget v-bind:side="side" v-bind:initialExpanded="initialExpanded">
      <div>Bookmarks</div>
    </BottombarWidget>
</template>

<script>
import BottombarWidget from './BottombarWidget'
export default {
  props: ['initialExpanded'],
  name: 'Bookmarks',
  components: { BottombarWidget },
  data () {
    return {
    }
  },

  created () {
    console.log('Bookmarks')
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
