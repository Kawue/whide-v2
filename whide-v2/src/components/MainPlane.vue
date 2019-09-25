<template>
  <div class="mainPlane">
    <p align="center">
      <canvas class="canvasToFill"></canvas>
    </p>
  </div>
</template>

<script>
export default {
  name: 'MainPlane.vue'
};

</script>

<style scoped lang="scss">
.mainPlane {
  position: absolute;
  top: 0px;
  left: 0px;
  right: 0px;
  bottom: 0px;
  background-color: whitesmoke;
  z-index: 100;
  color: white;
}
  .canvasToFill {
    position: relative;
    width: 70%;
    height: 400px;
    top: 30px;
    margin-left:190px;
    margin-right: 350px;
    background-color: #42b983;
  }
</style>
