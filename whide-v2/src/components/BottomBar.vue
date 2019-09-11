<template>
  <div class="bottombar">
  <div id="dragbar" onmousedown="darg()"></div>
  <div @mouseleave= "nothing" @mouseenter="nothing" class="bottombarWidget" v-bind:class="{ expanded: isExpanded }">
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
    toggleView: function () {
      this.isExpanded = !this.isExpanded;
    },
    getExpandUpIconClass: function () {
      return this.side === 'up' ? 'float-down' : 'float-up';
    },
    showExpandUpIcon: function () {
      return this.side === 'up' ? !this.isExpanded : this.isExpanded;
    },
    showExpandDownIcon: function () {
      return this.side === 'up' ? this.isExpanded : !this.isExpanded;
    },
    nothing: function () {
      return null;
    },
    drag: function () {
      this.dragging = true;
      let ghostbar = createElement('div',
        { id: 'ghostbar',
          css: {
            height: main.outerHeight(),
            top: main.offset().top,
            left: main.offset().left
          }
        }).appendTo('body');
    }
  }
};
</script>

<style scoped lang="scss">
  .bottombarWidget {
    position: absolute;
    height: 20px;
    width: 7vw;
    left: 43vw;
    min-width: 5vw;
    max-width: 80vw;
    z-index: 101;
    overflow: hidden;
    background-color: slategray;
    bottom: 0;
    float: bottom;
    border-style: solid;

    &.expanded {
      height: 45vh;
      min-width: 100vw;
      left:0;
      right:0;
      position: absolute;
      bottom: 0;
      .content {
        display: block;
      }
    }

    .content {
      display: none;
    }
  }
  #dragbar{
    background-color:black;
    height:100px;
    float: bottom;
    width: 100%;
    cursor: col-resize;
    z-index: 101;
  }

  #ghostbar{
    width:100%;
    background-color:#000;
    opacity:0.5;
    position:absolute;
    cursor: col-resize;
    z-index:999}

</style>
