<template>
  <div class="mainPlane">
    <p align="center">
      <canvas class="canvasToFill"></canvas>
    </p>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  name: 'MainPlane.vue',
  computed: {
    ...mapGetters({
      ids: 'getBookmarkIds'
    })
  }
};

</script>

<style scoped lang="scss">
.mainPlane {
  position: absolute;
  top: 0px;
  left: 0px;
  right: 0px;
  bottom: 0px;
  background-color: #404040;
  z-index: 100;
  color: white;
}
  .canvasToFill {
    position: relative;
    width: 70%;
    height: 700px;
    top: 30px;
    margin-left:190px;
    margin-right: 350px;
    background-color: #42b983;
  }

</style>
