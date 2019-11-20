<template>
  <div class="sidebarRight" >
    <span class="trigger"  v-bind:class="getExpandIconClass()">
    </span>
    <div class="content">
      <ColorPicker side="float-right" ></ColorPicker>
    </div>
  </div>
</template>

<script>
import ColorPicker from './ColorPicker';
export default {
  name: 'Right',
  components: { ColorPicker },
  data: function () {
    return {
      isExpanded: true
    };
  },
  methods: {
    getExpandIconClass: function () {
      return this.side === 'right' ? 'float-right' : 'float-left';
    },
    showExpandLeftIcon: function () {
      return this.side === 'right' ? !this.isExpanded : this.isExpanded;
    },
    showExpandRightIcon: function () {
      return this.side === 'right' ? this.isExpanded : !this.isExpanded;
    }
  }
};
</script>

<style scoped lang="scss">
  .sidebarRight {
    background-color: #4f5051;
    position: absolute;
    top: 0;
    width: 350px;
    height: auto;
    z-index: 101;
    right: 0;
    overflow: hidden;
    border-left-style: solid;
    border-bottom-style: solid;
    border-color: orange;
    border-bottom-left-radius: 20px;
    vertical-align: middle;
  }

</style>
