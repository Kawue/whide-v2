<template>
  <div class="bottombar">
      <div class="bottombarWidget">
        <div class="headerContainer">
          <div class="spacer"></div>
          <h2 class ="h2">Bookmarks</h2>
          <b-button id="deleteButton" class="clearBookmarks" variant="" size="sm" v-on:click="clearAllBookmarks()">Clear Bookmarks</b-button>
        </div>
        <div class="content">
          <Bookmarks side="up" ></Bookmarks>
        </div>
      </div>
  </div>
</template>

<script>
import Bookmarks from './Bookmarks';
import interact from 'interactjs';
import store from '../store';

export default {
  name: 'Bottom',
  data: function () {
    return {
      windowHeight: document.documentElement.clientHeight

    };
  },
  components: { Bookmarks },
  mounted () {
    interact('.bottombarWidget')
      .resizable({
        edges: { top: true, bottom: false, left: false, right: false },
        invert: 'repostion',
        modifiers: [
          interact.modifiers.restrictEdges({
            outer: 'parent',
            endOnly: true
          })
        ]
      }).on('resizemove', event => {
        let { x, y } = event.target.dataset;

        x = parseFloat(x) || 0;
        y = parseFloat(y) || 0;

        Object.assign(event.target.style, {
          width: `${event.rect.width}px`,
          height: `${event.rect.height}px`,
          bottom: `0`,
          transform: `translate(${event.deltaRect.left}px, ${event.deltaRect.top}px)`
        });

        Object.assign(event.target.dataset, { x, y });
        let height = event.target.style.height;
        const regex = /[0-9]*\.?[0-9]+?/i;
        let heightNumber = height.match(regex);
        if (parseInt(heightNumber[0]) >= 50) {
          store.commit('SET_BOTTOMBAR_HEIGHT', parseInt(heightNumber[0]));
        }
      });
  },
  methods: {
    clearAllBookmarks: function () {
      store.commit('DELETE_ALL_BOOKMARKS');
    }
  }
};
</script>

<style scoped lang="scss">
  .bottombar{
    clear: both;
    bottom: 0;
  }
  .h2 {
    color: #eeeeee;
  }
  .bottombarWidget {
    position: absolute;
    min-height: 50px;
    min-width: 100vw;
    left: 0;
    z-index: 101;
    background-color: #4f5051;
    bottom: 0;
    float: bottom;
    border-top-style: solid;
    border-top-color: orange;
    box-sizing: border-box;

    .content {
      display: flex;
      overflow-x: scroll;
    }
    .headerContainer {
      display: flex;
      flex-direction: row;
      justify-content: space-between;
    }
    /*.clearBookmarks {
      margin-right: 0.2vw;
    }
    .spacer {
      margin-left: 0.2vw;
    }*/
    #deleteButton{
      color: #000000;
      background-color:orange;
    }
  }

</style>
