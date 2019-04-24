<template>
  <div class="sidebar">
    <div class="row">
      <div class="col-sm">
        <Benchmarks side="left" v-bind:initialExpanded="false"></Benchmarks>
      </div>
    </div>
  </div>
</template>

<script>
import Benchmarks from '@/components/Benchmarks'
export default {
  name: 'sidebarLeft',
  components: {
    Benchmarks
  },
  data () {
    return {
    }
  },
   
  created () {
    console.log("SidebarLeft")
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
