<template>
  <div class="bottombar">
      <div class="bottombarWidget">
        <div class="headerContainer">
          <div class="spacer"></div>
          <h2 class ="h2">Bookmarks</h2>
          <div class="buttonContainer">
            <b-button v-if="!showAnnotations" id="showAnnotation" class="annotionMzButton" size="sm"  v-on:click="showAnnotation">Show Annotations</b-button>
            <b-button v-else id="hideAnnotation" class="annotionMzButton" size="sm"  v-on:click="showAnnotation">Hide Annotations</b-button>
            <b-button v-if="!showMzBoolean" id="showMz" class="showMzs" size="sm" v-on:click="showMz">Show MZ-Values</b-button>
            <b-button v-else id="hide" class="showMzs" size="sm" v-on:click="showMz">Hide MZ-Values</b-button>
            <b-button id="deleteButton" class="clearBookmarks" variant="" size="sm" v-on:click="clearAllBookmarks()">Clear Bookmarks</b-button>
          </div>
        </div>
        <div id="bookmarkcontent" class="content">
          <Bookmarks id="bookmarks" side="up" ></Bookmarks>
        </div>
      </div>
  </div>
</template>

<script>
import Bookmarks from './Bookmarks';
import interact from 'interactjs';
import store from '../store';
import * as d3 from 'd3';
import { mapGetters } from 'vuex';

export default {
  name: 'Bottom',
  data: function () {
    return {
      windowHeight: document.documentElement.clientHeight

    };
  },
  components: { Bookmarks },
  computed: {
    ...mapGetters({
      showMzBoolean: 'getShowMzInBchart',
      showAnnotations: 'getShowAnnotationInBchart',
      ownHeight: 'getBottonBarHeight'
    })
  },
  mounted () {
    store.subscribe(mutation => {
      if (mutation.type === 'SET_CHOOSED_BOOKMARK') {
        if (this.ownHeight === 50) {
          d3.select('.bottombarWidget')
            .style('height', '300px');
          store.commit('SET_BOTTOMBAR_HEIGHT', 300);
        }
      }
    });
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
      d3.select('.bottombarWidget')
        .style('height', '50px');
      store.commit('SET_BOTTOMBAR_HEIGHT', 50);
    },
    showMz: function () {
      store.commit('SET_SHOW_MZ_IN_BCHART');
    },
    showAnnotation: function () {
      store.commit('SET_SHOW_ANNOTATION_IN_BCHART');
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
    border-width: 1px;
    box-sizing: border-box;

    .content {
      display: flex;
      overflow-x: scroll;
    }
    .content::-webkit-scrollbar {
      width: 12px;
    }

    .content::-webkit-scrollbar-track {
      -webkit-box-shadow: inset 0 0 6px rgba(0,0,0,0.3);
      border-radius: 10px;
    }

    .content::-webkit-scrollbar-thumb {
      border-radius: 10px;
      -webkit-box-shadow: inset 0 0 6px rgba(0,0,0,0.5);
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
    .showMzs{
      color: #000000;
      background-color: orange;
    }
    .annotionMzButton {
      color: #000000;
      background-color: orange;
    }
  }

</style>
