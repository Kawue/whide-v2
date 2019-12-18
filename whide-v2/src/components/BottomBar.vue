<template>
  <div class="bottombar">
    <div class="bottombarWidget">
      <div class="fixed-header-container">
        <div class="spacer"></div>
        <h2 class="h2">Bookmarks</h2>
        <div class="buttonContainer">
          <b-button id="lineBchart" v-if="horizontal" class="lineCharts" size="sm" v-on:click="lineChart">Line Chart </b-button>
          <b-button v-if="!horizontal" id="horizontalBcharts" class="horizonatlCharts" size="sm"
                    v-on:click="horizontalCharts">Horizontal Charts
          </b-button>
          <b-button v-else id="redoCharts" class="horizonatlCharts" size="sm" v-on:click="horizontalCharts">Vertical
            Charts
          </b-button>
          <b-button v-if="!showAnnotations" id="showAnnotation" class="annotionMzButton" size="sm"
                    v-on:click="showAnnotation">Show Annotations
          </b-button>
          <b-button v-else id="hideAnnotation" class="annotionMzButton" size="sm" v-on:click="showAnnotation">Hide
            Annotations
          </b-button>
          <b-button v-if="!showMzBoolean" id="showMz" class="showMzs" size="sm" v-on:click="showMz">Show MZ-Values
          </b-button>
          <b-button v-else id="hide" class="showMzs" size="sm" v-on:click="showMz">Hide MZ-Values</b-button>
          <b-button v-if="!fullscreen" class="fullScreenBookmarks" size="sm" v-on:click="bookmarkFullscreen">Fullscreen</b-button>
          <b-button v-else class="fullScreenBookmarks" size="sm" v-on:click="bookmarkFullscreen"> Standard Screen</b-button>
          <b-button id="deleteButton" class="clearBookmarks" variant="" size="sm" v-on:click="clearAllBookmarks()">Clear
            Bookmarks
          </b-button>
        </div>
      </div>
      <div id="bookmarkcontainer">
        <div id="bookmarkcontent" class="content-wrapper">
          <bchart v-for="(key) in bookmarkIds" ref="key" :key="key['id']" :prototypeid="key['id']">
          </bchart>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Bchart from './Bchart';
import interact from 'interactjs';
import store from '../store';
import * as d3 from 'd3';
import { mapGetters } from 'vuex';

export default {
  name: 'Bottom',
  data: function () {
    return {
      windowHeight: document.documentElement.clientHeight,
      horizontal: false,
      fullscreen: false,
      lineCharts: false

    };
  },
  components: { Bchart },
  computed: {
    ...mapGetters({
      showMzBoolean: 'getShowMzInBchart',
      showAnnotations: 'getShowAnnotationInBchart',
      ownHeight: 'getBottonBarHeight',
      bookmarkIds: 'getBookmarkIds'

    })
  },
  mounted () {
    store.subscribe(mutation => {
      if (mutation.type === 'SET_CHOOSED_BOOKMARK') {
        if (this.ownHeight === 50) {
          d3.select('.bottombarWidget')
            .style('height', '350px');
          d3.select('#bookmarkcontainer')
            .style('height', '300px');
          store.commit('SET_BOTTOMBAR_HEIGHT', 350);
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
          transform: `translate(0px, 0px)`
        });

        Object.assign(event.target.dataset, { x, y });
       
      }).on('resizeend', event => {
        Object.assign(event.target.style, {
          width: `${event.rect.width}px`,
          height: `${event.rect.height}px`,
          bottom: `0`,
          transform: `translate(0px, 0px)`
        });

        let height = event.target.style.height;
        const regex = /[0-9]*\.?[0-9]+?/i;
        let heightNumber = height.match(regex);
        if (parseInt(heightNumber[0]) >= 50) {
          const h = parseInt(heightNumber[0]);
          store.commit('SET_BOTTOMBAR_HEIGHT', h);
          d3.select('#bookmarkcontainer').style('height', (h - 40) + 'px');
        }
      });
  },
  methods: {
    clearAllBookmarks: function () {
      store.commit('DELETE_ALL_BOOKMARKS');
      d3.select('.bottombarWidget')
        .style('height', '50px');
      d3.select('#bookmarkcontainer').style('height', '0');
      store.commit('SET_BOTTOMBAR_HEIGHT', 50);
    },
    showMz: function () {
      store.commit('SET_SHOW_MZ_IN_BCHART');
    },
    showAnnotation: function () {
      store.commit('SET_SHOW_ANNOTATION_IN_BCHART');
    },
    horizontalCharts: function () {
      this.horizontal = !this.horizontal;
      if (this.horizontal) {
        d3.select('.bottombarWidget')
          .style('height', '500px');
        store.commit('SET_BOTTOMBAR_HEIGHT', 500);
        d3.select('#bookmarkcontent').style('flex-direction', 'column');
        d3.select('#bookmarkcontainer').style('flex-direction', 'column');
        d3.select('#bookmarkcontainer').style('height', '450px');
      } else {
        d3.select('.bottombarWidget')
          .style('height', '350px');
        store.commit('SET_BOTTOMBAR_HEIGHT', 350);
        d3.select('#bookmarkcontent').style('flex-direction', 'row');
        d3.select('#bookmarkcontainer').style('flex-direction', 'row');
        d3.select('#bookmarkcontainer').style('height', 350);
        this.fullscreen = false;
      }
      this.bookmarkIds.forEach(function (id) {
        d3.select('#' + id['id']).selectAll('*').remove();
      });
      store.commit('SET_BOOKMARKS_HORIZONTAL');
    },
    lineChart: function () {
      this.lineCharts = !this.lineCharts;
      this.bookmarkIds.forEach(function (id) {
        d3.select('#' + id['id']).selectAll('*').remove();
      });
      store.commit('SET_BOOKMARKS_LINECHART');
    },
    bookmarkFullscreen: function () {
      if (this.fullscreen) {
        d3.select('.bottombarWidget')
          .style('height', '350px');
        d3.select('#bookmarkcontainer').style('height', 300);

        store.commit('SET_BOTTOMBAR_HEIGHT', 350);
        this.fullscreen = false;
      } else {
        this.fullscreen = true;
        d3.select('.bottombarWidget')
          .style('height', '100%');
        d3.select('#bookmarkcontainer').style('height', '95%');

        store.commit('SET_BOTTOMBAR_HEIGHT', document.documentElement.clientHeight);
      }
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
    bottom: 0 !important;
    float: bottom;
    border-top-style: solid;
    border-top-color: orange;
    border-width: 1px;
    box-sizing: border-box;

  }
    .fixed-header-container {
      display: flex;
      flex-direction: row;
      justify-content: space-between;
      height: 40px;
      width: 100vw;
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
    .horizonatlCharts {
      color: #000000;
      background-color: orange;
    }
    .fullScreenBookmarks {
      color: #000000;
      background-color: orange;
    }
    #lineBchart{
      color: #000000;
      background-color: orange;
    }

  #bookmarkcontent {
    margin-right: 20px;
    margin-left: 20px;
    display: inline-flex;
    flex: 1;
    flex-direction: row;
  }

  #bookmarkcontainer {
    overflow: auto;
    display: flex;
    flex-direction: row;
    justify-content: flex-start;
    min-width: 100vw;
    width: 100vw;
  }

</style>
