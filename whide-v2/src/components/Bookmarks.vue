<template>
  <div>
    <div class="bookmarks" v-for="key in ids" v-bind:key="key.toString()">
      <div class="content">
        <bchart class="chart" v-bind:prototypeid="key.toString()"/>
      </div>
    </div>
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

  #dragbar{
    background-color:black;
    height:100%;
    float: bottom;
    width: 3px;
    cursor: col-resize;
  }

  #ghostbar{
    width:3px;
    background-color:#000;
    opacity:0.5;
    position:absolute;
    cursor: col-resize;
    z-index:999}
</style>
