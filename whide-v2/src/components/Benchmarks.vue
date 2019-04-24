<template>
    <SidebarGenerally v-bind:side="side" v-bind:initialExpanded="initialExpanded">
      <div>Benchmarks</div>
    </SidebarGenerally>
</template>

<script>
import SidebarGenerally from '@/components/SidebarGenerally'

export default {
  props: ["initialExpanded"],
  extends: SidebarGenerally,
  name: 'benchmarks',
  components: {
    SidebarGenerally
  },

  data () {
    return {
    }
  },
   
  created () {
    console.log("Benchmark")
    console.log(this.initialExpanded)
  }
}

</script>
<style scoped lang="scss">
  .sidebar-generally {
    background-color: aqua;
  }
  .sidebar-generally {
    &.expanded {
      width: 200px !important;
    }
  }
</style>
