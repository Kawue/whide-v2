<template>
  <div class="sidebar">
    <div class="row">
      <div class="col-sm">
        <MzList side="left" v-bind:initialExpanded="false">
        </MzList>
      </div>
    </div>
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
    top: 0;
    bottom: 0;
    z-index: 101;
    background-color: yellow;

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
