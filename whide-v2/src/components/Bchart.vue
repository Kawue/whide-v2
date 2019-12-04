<template>
    <div id="graphic" class="chart">
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
      mzText: false
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
      bookmarkOrientation: 'getBookmarkOrientation'
    })
  },
  mounted () {
    let bookmarkService = new BookmarkService();
    if (this.bookmarkOrientation) {
      d3.select('.bottombarWidget')
        .style('height', '500px');
      store.commit('SET_BOTTOMBAR_HEIGHT', 500);
    } else {
      d3.select('.bottombarWidget')
        .style('height', '350px');
      store.commit('SET_BOTTOMBAR_HEIGHT', 350);
    }

    this.bookmarkData = store.getters.getBookmarksData(this.prototypeid);

    if (this.height !== 0) {
      if (this.bookmarkOrientation) {
        bookmarkService.createHorizontalChart(this.bookmarkData, parseInt(this.height), this.showMzBoolean, this.showAnnotations);
      } else {
        bookmarkService.createBchart(this.bookmarkData, parseInt(this.height), this.showMzBoolean, this.showAnnotations);
      }
    } else {
      if (this.bookmarkOrientation) {
        bookmarkService.createHorizontalChart(this.bookmarkData, 500, this.showMzBoolean, this.showAnnotations);
      } else {
        bookmarkService.createBchart(this.bookmarkData, 300, this.showMzBoolean, this.showAnnotations);
      }
    }
    this.unsubscribe = store.subscribe(mutation => {
      if (mutation.type === 'SET_MOEBIUS') {
        this.bookmarkColor = store.getters.getBookmarkColor(this.prototypeid);
        d3.select('#' + this.bookmarkData['id'])
          .style('background-color', this.bookmarkColor);
      } else if (mutation.type === 'SET_DEFAULT_POSITION') {
        this.bookmarkColor = store.getters.getBookmarkColor(this.prototypeid);
        d3.select('#' + this.bookmarkData['id'])
          .style('background-color', this.bookmarkColor);
      }
      if (mutation.type === 'UPDATE_COLOR') {
        this.bookmarkColor = store.getters.getBookmarkColor(this.prototypeid);
        d3.select('#' + this.bookmarkData['id'])
          .style('background-color', this.bookmarkColor);
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
        d3.select('#' + this.prototypeid).remove();
        if (this.bookmarkOrientation) {
          bookmarkService.createHorizontalChart(this.bookmarkData, parseInt(this.height), this.showMzBoolean, this.showAnnotations);
        } else {
          bookmarkService.createBchart(this.bookmarkData, parseInt(this.height), this.showMzBoolean, this.showAnnotations);
        }
      }
      if (mutation.type === 'SET_SHOW_MZ_IN_BCHART') {
        d3.select('#' + this.prototypeid).remove();
        if (this.height !== 0) {
          if (this.bookmarkOrientation) {
            bookmarkService.createHorizontalChart(this.bookmarkData, parseInt(this.height), this.showMzBoolean, this.showAnnotations);
          } else {
            bookmarkService.createBchart(this.bookmarkData, parseInt(this.height), this.showMzBoolean, this.showAnnotations);
          }
        } else {
          if (this.bookmarkOrientation) {
            bookmarkService.createHorizontalChart(this.bookmarkData, 500, this.showMzBoolean, this.showAnnotations);
          } else {
            bookmarkService.createBchart(this.bookmarkData, 300, this.showMzBoolean, this.showAnnotations);
          }
        }
      }
      if (mutation.type === 'SET_SHOW_ANNOTATION_IN_BCHART') {
        d3.select('#' + this.prototypeid).remove();
        if (this.height !== 0) {
          if (this.bookmarkOrientation) {
            bookmarkService.createHorizontalChart(this.bookmarkData, parseInt(this.height), this.showMzBoolean, this.showAnnotations);
          } else {
            bookmarkService.createBchart(this.bookmarkData, parseInt(this.height), this.showMzBoolean, this.showAnnotations);
          }
        } else {
          if (this.bookmarkOrientation) {
            bookmarkService.createHorizontalChart(this.bookmarkData, 500, this.showMzBoolean, this.showAnnotations);
          } else {
            bookmarkService.createBchart(this.bookmarkData, 300, this.showMzBoolean, this.showAnnotations);
          }
        }
      }
      if (mutation.type === 'SET_BOOKMARKS_HORIZONTAL') {
        if (this.bookmarkOrientation) {
          bookmarkService.createHorizontalChart(this.bookmarkData, parseInt(this.height), this.showMzBoolean, this.showAnnotations);
        } else {
          bookmarkService.createBchart(this.bookmarkData, parseInt(this.height), this.showMzBoolean, this.showAnnotations);
        }
      }
    });
  },
  beforeDestroy () {
    this.unsubscribe();
  }

};
</script>

<style scoped lang="scss">
  .chart{
    display: flex;
    flex-direction: row;
    overflow: auto;
    margin-right: 20px;
    margin-bottom: 20px;
    margin-left: 20px;
  }

  .tooltip {
    position: absolute;
    text-align: center;
    width: 60px;
    height: 28px;
    padding: 2px;
    font: 12px sans-serif;
    background: lightsteelblue;
    border-radius: 8px;
    pointer-events: none;
  }
  </style>
