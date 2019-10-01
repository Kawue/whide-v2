<template>
  <div
    @mouseleave="toggleView"
    @mouseenter="toggleView"
    class="topbarWidget"
    v-bind:class="{ expanded: isExpanded }">
      <span v-on:click="toggleView()" v-bind:class="getExpandUpIconClass()">
        <v-icon name="arrow-up" v-if="showExpandUpIcon()"></v-icon>
        <v-icon name="arrow-down" v-if="showExpandDownIcon()"></v-icon>
      </span>
    <div class="content">
      <options
        side="top"
        v-if="isExpanded">
      </options>
    </div>
  </div>
</template>

<script>
import Options from './Options';
export default {
  name: 'Top',
  components: { Options },
  data: function () {
    return {
      isExpanded: false
    };
  },
  methods: {
    toggleView: function () {
      this.isExpanded = !this.isExpanded;
    },
    getExpandUpIconClass: function () {
      return this.side === 'up' ? 'float-up' : 'float-down';
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
  .topbarWidget {
    position: absolute;
    height: 20px;
    width: 7vw;
    left: 43vw;
    min-width: 5vw;
    max-width: 80vw;
    overflow: hidden;
    background-color: slategray;
    z-index: 101;
    border-radius: 0 0 10px 0;
    &.expanded {
     height: 200px;
     width: 30vw;
     left: 15vw;
     position: absolute;
      background-color: #3e3f40;
      border-right: 1px solid #737374;
      border-bottom: 1px solid #737374;
  .content {
    display: block;
  }
  }

  .content {
    display: none;
  }
  }
</style>
