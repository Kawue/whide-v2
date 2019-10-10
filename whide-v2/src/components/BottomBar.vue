<template>
  <div class="bottombar">
      <div class="bottombarWidget" v-bind:class="{ expanded: isExpanded }">
      <span v-on:click="toggleView()" v-bind:class="getExpandUpIconClass()">
        <v-icon name="arrow-down" v-if="showExpandUpIcon()"></v-icon>
        <v-icon name="arrow-up" v-if="showExpandDownIcon()"></v-icon>
      </span>
        <div class="content">
          <Bookmarks side="up" v-if="isExpanded"></Bookmarks>
        </div>
      </div>
  </div>
</template>

<script>
import Bookmarks from './Bookmarks';
import * as d3 from 'd3';

export default {
  name: 'Bottom',
  components: { Bookmarks },
  data: function () {
    return {
      isExpanded: false,
      dragging: false
    };
  },
  methods: {
    handleResize () {
      console.log('resized');
    },
    toggleView: function () {
      this.isExpanded = !this.isExpanded;
      try {
        if (this.isExpanded) {
          // d3.select('.mzComp').attr('height', '20vh important!');
          document.getElementById('mzComponent').setAttribute('style', 'height:50vh');
          document.getElementById('mzlistid').setAttribute('style', 'height:85%');
        } else {
          document.getElementById('mzComponent').setAttribute('style', 'height:100vh');
          document.getElementById('mzlistid').setAttribute('style', 'height:93%');

          // d3.select('.mzComp').attr('height', '100vh');
        }
      } catch (e) {
        return null;
      }
    },
    getExpandUpIconClass: function () {
      return this.side === 'up' ? 'float-down' : 'float-up';
    },
    showExpandUpIcon: function () {
      return this.side === 'up' ? !this.isExpanded : this.isExpanded;
    },
    showExpandDownIcon: function () {
      return this.side === 'up' ? this.isExpanded : !this.isExpanded;
    }
  }
};
</script>

<style scoped lang="scss">
  .bottombar{
    clear: both;
  }
  .bottombarWidget {
    position: absolute;
    height: 40px;
    width: 7vw;
    left: 43vw;
    min-width: 5vw;
    max-width: 80vw;
    z-index: 101;
    background-color: #4f5051;
    bottom: 0;
    float: bottom;
    border-style: solid;
    border-color: orange;


    &.expanded {
      height: 45vh;
      min-width: 100vw;
      left:0;
      right:0;
      position: absolute;
      bottom: 0;
      .content {
        display: flex;
        overflow-x: scroll;
      }
    }

    .content {
      display: none;
      overflow-x: scroll;

    }
  }

</style>
