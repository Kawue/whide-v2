<template>
  <div>
    <bchart class="chart" v-for="(key, index) in ids"  ref="key" :key="index" :prototypeid="key['id']" >
    </bchart>
  </div>
</template>
<script>
import { mapGetters } from 'vuex';
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
  }
};
</script>

<style scoped lang="scss">
  .chart{
    overflow: auto;
  }
</style>
