<template>
    <div class="bottombarWidget" v-bind:class="{ expanded: isExpanded }">
      <span v-on:click="toggleView()" v-bind:class="getExpandUpIconClass()">
        <v-icon name="arrow-up" v-if="showExpandUpIcon()"></v-icon>
        <v-icon name="arrow-down" v-if="showExpandDownIcon()"></v-icon>
      </span>
      <div class="content">
      <slot></slot>
    </div>
    </div>
</template>

<script>
export default {
  name: 'BottombarWidget',
  props: {
    side: {
      type: String,
      required: true
    },
    initialExpanded: {
      type: Boolean,
      required: false,
      default: true
    }
  },
  data: function () {
    return {
      isExpanded: this.initialExpanded
    }
  },
  methods: {
    toggleView: function () {
      this.isExpanded = !this.isExpanded
    },
    getExpandUpIconClass: function () {
      return this.side === 'up' ? 'float-up' : 'float-down'
    },
    showExpandUpIcon: function () {
      return this.side === 'up' ? this.isExpanded : this.isExpanded
    },
    showExpandDownIcon: function () {
      return this.side === 'up' ? this.isExpanded : !this.isExpanded
    }
  }
}
</script>

<style scoped lang="scss">
  .bottombarWidget {
    height: 20px;
    min-width: 100vh;
    max-width: 100vh;
    overflow: hidden;
    background-color: white;

  &.expanded {
     height: 200px;

  .content {
    display: block;
  }
  }

  .content {
    display: none;
  }
  }
</style>
