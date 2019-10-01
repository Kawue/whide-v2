<template>
  <div>
    <bchart class="chart" v-for="key in itemsDirect()" :key="key" :prototypeid="key">
    </bchart>
  </div>
</template>
<script>
import { mapGetters } from 'vuex';
import store from '../store';
import Bchart from './Bchart';

export default {
  name: 'Bookmarks',
  components: {
    Bchart
  },
  computed: {
    ...mapGetters({
      ids: 'getBookmarkIds'
    })
  },
  methods: {
    itemsDirect: function () {
      debugger;
      return store.state.choosedBookmarksIds;
    }
  }
  /*,
  mounted () {
    store.subscribe(mutation => {
      if (mutation.type === 'DELETE_CHOOSED_BOOKMARK') {
        this.ids = store.state.choosedBookmarksIds;
      }
    });
  }

   */
};
</script>

<style scoped lang="scss">
  .chart{
    overflow: auto;
  }
</style>
