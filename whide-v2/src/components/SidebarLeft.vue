<template>
  <div class="sidebar">
        <MzList side="left" v-bind:initialExpanded="false">
        </MzList>
  </div>
</template>

<script>
import MzList from '@/components/MzList.vue'

export default {
  name: 'Sidebar',
  components: { MzList },
  data () {
    return {}
  },
  created () {
    console.log('SidebarLeft')
  }
}
</script>

<style scoped lang="scss">
  .sidebar {
    position: absolute;
    left: 0;
    z-index: 101;
    background-color: yellow;
  }
</style>
