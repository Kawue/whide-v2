<template>
  <div class="topbar">
    <Options side="up" v-bind:initialExpanded="false">
    </Options>
  </div>
</template>

<script>
import Options from './Options'
export default {
  name: 'Topbar',
  components: { Options },
  data () {
    return {}
  },
  created () {
    console.log('Topbar')
  }
}
</script>

<style scoped lang="scss">
  .topbar {
    position: absolute;
    top: 0;
    z-index: 102;
    background-color: yellow;
    &.expanded {
      bottom: 0vh;
    }
  }

</style>
