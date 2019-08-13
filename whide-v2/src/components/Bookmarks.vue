<template>
  <div>
  <div class="bookmarks" v-for="key in bookmarks" v-bind:key="Object.keys(key)[0]">
    <bchart v-bind:prototypeid="Object.keys(key)[0]"/>
  </div>
  </div>
</template>
<script>
import { mapGetters } from 'vuex'
import Bchart from './Bchart'

export default {
  components: {
    Bchart
  },
  computed: {
    ...mapGetters({
      bookmarks: 'getBookmarks'
    })
  },
  name: 'Bookmarks'
}

</script>

<style scoped lang="scss">

</style>
