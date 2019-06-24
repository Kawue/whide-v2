<template>
  <div class="sidebarLeft" v-bind:class="{ expanded: isExpanded }">
    <span class="trigger" v-on:click="toggleView()" v-bind:class="getExpandIconClass()">
      <v-icon name="arrow-right" v-if="showExpandRightIcon()"></v-icon>
      <v-icon name="arrow-left" v-if="showExpandLeftIcon()"></v-icon>
    </span>
    <div class="content">
      <Mzlist side="left" v-if="isExpanded"></Mzlist>
    </div>
  </div>
</template>

<script>
import Mzlist from './MzList'
export default {
  name: 'Left',
  components: { Mzlist },

  data: function () {
    return {
      isExpanded: false
    }
  },
  methods: {
    toggleView: function () {
      this.isExpanded = !this.isExpanded
    },
    getExpandIconClass: function () {
      return this.side === 'right' ? 'float-right' : 'float-left'
    },
    showExpandLeftIcon: function () {
      return this.side === 'right' ? !this.isExpanded : this.isExpanded
    },
    showExpandRightIcon: function () {
      return this.side === 'right' ? this.isExpanded : !this.isExpanded
    }
  }
}
</script>

<style scoped lang="scss">
  .sidebarLeft {
    background-color: slategray;
    position: absolute;
    width: 25px;
    top: 47.5vh;
    height: 50px;
    z-index: 101;
    overflow: hidden;
    &.expanded {
      top:0;
      width: 10vw;
      height: 100vh;
    }
  }
  .trigger {
    vertical-align: middle;
  }

</style>
