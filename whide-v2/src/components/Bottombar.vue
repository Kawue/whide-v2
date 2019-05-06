<template>
    <Bookmarks>

    </Bookmarks>
</template>

<script>
import Bookmarks from './Bookmarks'
export default {
  name: 'SidebarBottom',
  components: { Bookmarks }
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
