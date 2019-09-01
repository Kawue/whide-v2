<template>
  <div>
  <div class="bookmarks" v-for="key in bookmarks" v-bind:key="key['id'].toString()">
    <bchart v-bind:prototypeid="key['id'].toString()"/>
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
