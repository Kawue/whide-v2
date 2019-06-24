<template>
  <div class="sidebarRight" v-bind:class="{ expanded: isExpanded }">
    <span class="trigger" v-on:click="toggleView()" v-bind:class="getExpandIconClass()">
      <v-icon name="arrow-right" v-if="showExpandRightIcon()"></v-icon>
      <v-icon name="arrow-left" v-if="showExpandLeftIcon()"></v-icon>
    </span>
    <div class="content">
      <ColorPicker side="left" v-if="isExpanded"></ColorPicker>
    </div>
  </div>
</template>

<script>
import ColorPicker from './ColorPicker'
export default {
  name: 'Right',
  components: { ColorPicker },
  data: function () {
    return {
      isExpanded: true
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
  .sidebarRight {
    background-color: slategray;
    position: absolute;
    width: 25px;
    top: 47.5vh;
    z-index: 101;
    height: 50px;
    right: 0;
    overflow: hidden;
  &.expanded {
     top:0;
     width: 35vw;
     height: 75vh;
   }
  }
  .trigger {
    vertical-align: middle;
  }
</style>
