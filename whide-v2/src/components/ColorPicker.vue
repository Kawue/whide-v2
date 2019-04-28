<template>
    <SidebarWidget v-bind:side="side" v-bind:initialExpanded="initialExpanded">
      <div>
        ColorPicker
      </div>
    </SidebarWidget>
</template>

<script>
import SidebarWidget from './SidebarWidget'
export default {
  extends: SidebarWidget,
  name: 'ColorPicker',
  components: {
    SidebarWidget
  }
}
</script>

<style scoped lang="scss">
  .sidebarWidget {
    background-color: gold;
  }
  .sidebarWidget {
    &.expanded {
      width: 200px !important;
    }
  }
</style>
