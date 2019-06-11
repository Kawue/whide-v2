<template>
  <div class="sidebar">
      <ColorPicker side="right" v-bind:initialExpanded="false"></ColorPicker>
  </div>
</template>

<script>
import ColorPicker from './ColorPicker.vue'

export default {
  name: 'Sidebar',
  components: { ColorPicker },
  data () {
    return {}
  },
  created () {
    console.log('SidebarRight')
  }
}
</script>

<style scoped lang="scss">
  .sidebar {
    position: absolute;
    right: 40px;
    z-index: 101;
    background-color: yellow;
  }
</style>
