<template>
    <SidebarGenerally v-bind:side="side" v-bind:initial-expended="initialExpended">
      <div>Benschmarks</div>
    </SidebarGenerally>
</template>

<script>
import SidebarGenerally from './SidebarGenerally'

export default {
  extends: SidebarGenerally,
  name: 'benchmarks',
  components: {
    SidebarGenerally
  }
}

</script>
<style scoped lang="scss">
  .sidebar-generally {
    background-color: aqua;
  }
  .sidebar-generally {
    &.expended {
      width: 200px !important;
    }
  }
</style>
