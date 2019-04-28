<template>
  <div class="sidebar">
  <div class="row">
    <div class="col-sm">
      <ColorPicker side="right" v-bind:initialExpanded="false">
      </ColorPicker>
    </div>
  </div>
  </div>
</template>

<script>
import ColorPicker from './ColorPicker'
export default {
  name: 'SidebarRight',
  components: { ColorPicker },
  data () {
    return {
    }
  },
  created () {
    console.log('SidebarRight')
  }
}
</script>

<style scoped lang="scss">
  .sidebar {
    position: absolute;
    right: 0;
    top: 0;
    bottom: 0;
    z-index: 101;
    background-color: violet;
    .row {
      padding: 0;
      margin: 0;
      .col-sm {
        padding: 0;
        margin: 0;
      }
    }
  }
</style>
