<template>
  <div  class="sidebarLeft">
    <div class="content">
      <Mzlist side="left" ></Mzlist>
    </div>
  </div>
</template>

<script>
import Mzlist from './MzList';
export default {
  name: 'Left',
  components: { Mzlist }
};
</script>

<style scoped lang="scss">
  .sidebarLeft {
    background-color: #4f5051;
    position: absolute;
    width: 10vw;
    z-index: 101;
    overflow: hidden;
    border-right-style: solid;
    border-bottom-style: solid;
    border-right-color:orange;
  }

</style>
