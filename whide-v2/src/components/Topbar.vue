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
    console.log('Bottombar')
  }
}
</script>

<style scoped lang="scss">
  .topbar {
    position: absolute;
    top: 10px;
    z-index: 102;
    background-color: yellow;
    &.expanded {
      bottom: 0vh;
    }
  }

</style>
