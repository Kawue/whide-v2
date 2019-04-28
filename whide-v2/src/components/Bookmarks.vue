<template>
    <SidebarWidget v-bind:side="side" v-bind:initialExpanded="initialExpanded">
      <div>Bookmarks</div>
    </SidebarWidget>
</template>

<script>
import SidebarWidget from './SidebarWidget'
export default {
  name: 'Bookmarks',
  components: { SidebarWidget }
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
