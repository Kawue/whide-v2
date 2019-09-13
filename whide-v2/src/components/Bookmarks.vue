<template>
  <div>
  <div class="bookmarks" v-for="key in bookmarks" v-bind:key="key['id'].toString()">
    <bchart v-bind:prototypeid="key['id'].toString()"/>
    {{updateBookmarks}}
  </div>
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
      bookmarks: 'getBookmarks'
    })

  },
  methods: {
    updateBookmarks: function () {
      let bookmarksNew = this.state.choosedBookmarks;
      return bookmarksNew;
    }
  }
};
</script>

<style scoped lang="scss">

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
