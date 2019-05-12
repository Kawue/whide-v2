<template>
  <div class="sidebarWidget" v-bind:class="{ expanded: isExpanded }">
    <span class="trigger" v-on:click="toggleView()" v-bind:class="getExpandIconClass()">
      <v-icon name="arrow-right" v-if="showExpandRightIcon()"></v-icon>
      <v-icon name="arrow-left" v-if="showExpandLeftIcon()"></v-icon>
    </span>
    <div class="content">
      <slot></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SidebarWidget',
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
    getExpandIconClass: function () {
      return this.side === 'right' ? 'float-right' : 'float-left'
    },
    showExpandLeftIcon: function () {
      return this.side === 'right' ? !this.isExpanded : this.isExpanded
    },
    showExpandRightIcon: function () {
      return this.side === 'right' ? this.isExpanded : !this.isExpanded
    }
  },
  created () {
    console.log('SidebarWidget')
    console.log(this.initialExpanded)
  }
}

</script>

<style scoped lang="scss">
  .sidebarWidget {
    width: 20px;
    min-height: 100vh;
    max-height: 100vh;
    overflow: hidden;
    background-color: white;

    &.expanded {
      width: 200px;
      .content {
        display: block;
      }
    }
    .content {
      display: none;
    }
  }
  .trigger {
    vertical-align: middle;
  }
</style>
