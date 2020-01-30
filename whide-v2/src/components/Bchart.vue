<template>
  <div  v-bind:id="this.prototypeid + '-container'" class="chartContainer">
    <span class="delButton" v-on:click="deleteBookmark" v-b-tooltip.hover.top="'Delete Bookmark'">
      <v-icon class="deleteSymbol" name="window-close"/>
    </span>
    <canvas class="chart" v-bind:id="this.prototypeid"/>
  </div>
</template>

<script>
import * as d3 from 'd3';
import { mapGetters } from 'vuex';
import store from '../store';
import BookmarkService from '../services/BookmarkService';

export default {
  name: 'Bchart',
  data: function () {
    return {
      currentMarkedPrototype: null,
      bookmarkData: {},
      bookmarkColor: String,
      mzText: false,
      qdtree: {},
      chartData: {},
      bookmarkService: new BookmarkService(),
      mode: 'vertical'
    };
  },
  props: {
    prototypeid: {
      type: String
    }
  },
  computed: {
    ...mapGetters({
      highlightedPrototype: 'getCurrentHighlightedPrototype',
      height: 'getBottonBarHeight',
      showMzBoolean: 'getShowMzInBchart',
      showAnnotations: 'getShowAnnotationInBchart',
      bookmarkOrientation: 'getBookmarkOrientation',
      lineChart: 'getBookmarkLinechart'
    })
  },
  mounted () {
    this.qdtree = d3.quadtree();
    if (this.bookmarkOrientation) {
      d3.select('.bottombarWidget')
        .style('height', '500px');
      d3.select('#bookmarkcontainer').style('height', '450px');
      store.commit('SET_BOTTOMBAR_HEIGHT', 500);
    } else {
      d3.select('.bottombarWidget')
        .style('height', '350px');
      d3.select('#bookmarkcontainer').style('height', '300px');
      store.commit('SET_BOTTOMBAR_HEIGHT', 350);
    }
    this.bookmarkData = store.getters.getBookmarksData(this.prototypeid);
    if (this.height !== 0) {
      if (this.bookmarkOrientation) {
        if (this.lineChart) {
          this.buildLchart();
        } else {
          this.buildHchart();
        }
      } else {
        this.buildBchart(parseInt(this.height));
      }
    } else {
      if (this.bookmarkOrientation) {
        if (this.lineChart) {
          this.buildLchart();
        } else {
          this.buildHchart(300);
        }
      } else {
        this.buildBchart(300);
      }
    }
    this.unsubscribe = store.subscribe(mutation => {
      if (mutation.type === 'SET_MOEBIUS') {
        this.bookmarkColor = store.getters.getBookmarkColor(this.prototypeid);
        if (this.mode === 'vertical') {
          this.buildBchart(parseInt(this.height), this.bookmarkColor);
        } else if (this.mode === 'horizontal') {
          this.buildHchart(this.bookmarkColor);
        } else if (this.mode === 'line') {
          this.buildLchart(this.bookmarkColor);
        }
      } else if (mutation.type === 'SET_DEFAULT_POSITION') {
        this.bookmarkColor = store.getters.getBookmarkColor(this.prototypeid);
        if (this.mode === 'vertical') {
          this.buildBchart(parseInt(this.height), this.bookmarkColor);
        } else if (this.mode === 'horizontal') {
          this.buildHchart(this.bookmarkColor);
        } else if (this.mode === 'line') {
          this.buildLchart(this.bookmarkColor);
        }
      }
      if (mutation.type === 'UPDATE_COLOR') {
        this.bookmarkColor = store.getters.getBookmarkColor(this.prototypeid);
        if (this.mode === 'vertical') {
          this.buildBchart(parseInt(this.height), this.bookmarkColor);
        } else if (this.mode === 'horizontal') {
          this.buildHchart(this.bookmarkColor);
        } else if (this.mode === 'line') {
          this.buildLchart(this.bookmarkColor);
        }
      }
      if (mutation.type === 'SET_CURRENT_HIGHLIGHTED_PROTOTYPE') {
        if (this.highlightedPrototype === this.prototypeid) {
          let markedColor = 'rgba(255,255,255,255)';
          this.currentMarkedPrototype = this.prototypeid;
          d3.select('#' + this.bookmarkData['id'])
            .style('border-width', '3px')
            .style('border-color', markedColor);
        } else if (this.currentMarkedPrototype === this.prototypeid) {
          d3.select('#' + this.currentMarkedPrototype)
            .style('border-width', '1px')
            .style('border-color', 'black');
          this.currentMarkedPrototype = null;
        }
      }
      if (mutation.type === 'SET_BOTTOMBAR_HEIGHT') {
        d3.select('#' + this.prototypeid).selectAll('*').remove();
        if (this.bookmarkOrientation) {
          if (this.lineChart) {
            this.buildLchart();
          } else {
            this.buildHchart();
          }
        } else {
          this.buildBchart(parseInt(this.height));
        }
      }
      if (mutation.type === 'SET_SHOW_MZ_IN_BCHART') {
        d3.select('#' + this.prototypeid).selectAll('*').remove();
        if (this.height !== 0) {
          if (this.bookmarkOrientation) {
            if (this.lineChart) {
              this.buildLchart();
            } else {
              this.buildHchart();
            }
          } else {
            this.buildBchart(parseInt(this.height));
          }
        } else {
          if (this.bookmarkOrientation) {
            if (this.lineChart) {
              this.buildLchart();
            } else {
              this.buildHchart();
            }
          } else {
            this.buildBchart(300);
          }
        }
      }
      if (mutation.type === 'SET_SHOW_ANNOTATION_IN_BCHART') {
        d3.select('#' + this.prototypeid).selectAll('*').remove();
        if (this.height !== 0) {
          if (this.bookmarkOrientation) {
            if (this.lineChart) {
              this.buildLchart();
            } else {
              this.buildHchart();
            }
          } else {
            this.buildBchart(parseInt(this.height));
          }
        } else {
          if (this.bookmarkOrientation) {
            if (this.lineChart) {
              this.buildLchart();
            } else {
              this.buildHchart();
            }
          } else {
            this.buildBchart(300);
          }
        }
      }
      if (mutation.type === 'SET_BOOKMARKS_HORIZONTAL') {
        if (this.bookmarkOrientation) {
          if (this.lineChart) {
            this.buildLchart();
          } else {
            this.buildHchart();
          }
        } else {
          this.buildBchart(parseInt(this.height));
        }
      }
      if (mutation.type === 'SET_BOOKMARKS_LINECHART') {
        if (this.lineChart) {
          this.buildLchart();
        } else {
          this.buildHchart();
        }
      }
    });
  },
  beforeDestroy () {
    this.unsubscribe();
  },
  methods: {
    deleteBookmark: function () {
      store.commit('DELETE_BOOKMARK', this.bookmarkData['id']);
    },
    clearChart: function () {
      let canvas = document.querySelector('#' + this.bookmarkData['id']);
      let ctx = canvas.getContext('2d');
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    },
    createChartData: function (annotation) {
      this.qdtree.removeAll(this.chartData);
      this.qdtree = {};
      this.qdtree = d3.quadtree();
      let that = this;
      let mzItemList;
      if (annotation) {
        mzItemList = Object.values(this.bookmarkData['mzObject']);
      } else {
        mzItemList = Object.keys(this.bookmarkData['mzObject']);
      }
      this.chartData = mzItemList.map(function (x, i) {
        return { 'mz': x, 'coefficient': that.bookmarkData['data'][i] };
      });
    },
    buildBchart: function (h, color = null) {
      this.mode = 'vertical';
      d3.select('#' + this.prototypeid).remove();
      d3.select('#' + this.prototypeid + '-container')
        .append('canvas')
        .attr('class', 'chart')
        .attr('id', this.prototypeid)
        .style('position', 'absolute')
        .style('margin-right', '2px')
        .style('margin-bottom', '10px')
        .style('border-style', 'solid')
        .style('border-width', '1px');
      this.clearChart();
      this.qdtree.removeAll(this.chartData);
      this.createChartData(this.showAnnotations);
      if (color === null) {
        this.bookmarkService.createBchart(this.qdtree, this.chartData, h, this.showMzBoolean, this.showAnnotations, this.bookmarkData['id'], this.bookmarkData['color']);
      } else {
        this.bookmarkService.createBchart(this.qdtree, this.chartData, h, this.showMzBoolean, this.showAnnotations, this.bookmarkData['id'], color);
      }
    },
    buildHchart: function (color = null) {
      this.mode = 'horizontal';
      d3.select('#' + this.prototypeid).remove();
      d3.select('#' + this.prototypeid + '-container')
        .append('canvas')
        .attr('class', 'chart')
        .attr('id', this.prototypeid)
        .style('position', 'absolute')
        .style('margin-right', '2px')
        .style('margin-bottom', '10px')
        .style('border-style', 'solid')
        .style('border-width', '1px');
      this.clearChart();
      this.qdtree.removeAll(this.chartData);
      this.createChartData(this.showAnnotations);
      if (color === null) {
        this.bookmarkService.createHorizontalChart(this.qdtree, this.chartData, this.showMzBoolean, this.showAnnotations, this.bookmarkData['id'], this.bookmarkData['color']);
      } else {
        this.bookmarkService.createHorizontalChart(this.qdtree, this.chartData, this.showMzBoolean, this.showAnnotations, this.bookmarkData['id'], color);
      }
    },
    buildLchart: function (color = null) {
      this.mode = 'line';
      d3.select('#' + this.prototypeid).remove();
      d3.select('#' + this.prototypeid + '-container')
        .append('canvas')
        .attr('class', 'chart')
        .attr('id', this.prototypeid)
        .style('position', 'absolute')
        .style('margin-right', '2px')
        .style('margin-bottom', '10px')
        .style('border-style', 'solid')
        .style('border-width', '1px');
      this.clearChart();
      this.qdtree.removeAll(this.chartData);
      this.createChartData(this.showAnnotations);
      if (color === null) {
        this.bookmarkService.lineChart(this.qdtree, this.chartData, this.showMzBoolean, this.showAnnotations, this.bookmarkData['id'], this.bookmarkData['color']);
      } else {
        this.bookmarkService.lineChart(this.qdtree, this.chartData, this.showMzBoolean, this.showAnnotations, this.bookmarkData['id'], color);
      }
    }
  }

};
</script>

<style scoped lang="scss">
 .chart{
   position: absolute;
   margin-right: 2px;
   margin-bottom: 10px;
   border-style: solid;
   border-width: 1px;
 }
  .chartContainer {
    position: relative;
    height: 280px;
    width: 300px;

  }
 .delButton{
   position: absolute;
   top: 0;
   left: 3px;
   width: 30px;
   height: 30px;
   z-index: 102;
 }

  </style>
