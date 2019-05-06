<template>
  <div class="bottombar">
    <Bookmarks side="down" v-bind:initialExpanded="false">
    BOOKMARKS
    </Bookmarks>
  </div>
</template>

<script>
import Bookmarks from './Bookmarks'
export default {
  name: 'SidebarBottom',
  components: { Bookmarks },
  data () {
    return {}
  },
  created () {
    console.log('Bottombar')
  }
}
</script>

<style scoped lang="scss">
  .bottombar {
    position: absolute;
    bottom: 0;
    z-index: 102;
    background-color: yellow;
  }
</style>
