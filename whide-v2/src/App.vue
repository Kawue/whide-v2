<template>
  <div id="app">
    <router-view/>
  </div>
</template>

<script>
export default {
  data: function () {
    return {
      easterEggFlag1: false,
      easterEggFlag2: false,
      easterEggFlag3: false,
      easterEggFlag4: false,
      easterEggFlag5: false,
      easterEggFlag6: false
    };
  },
  methods: {
    easterEgg (evt) {
      switch (evt.keyCode) {
        case 87:
          this.easterEggFlag1 = true;
          break;
        case 72:
          if (this.easterEggFlag1) {
            this.easterEggFlag2 = true;
          } else {
            document.getElementById('virtCanvas').style['z-index'] = 101;
            document.getElementById('segMap').style['z-index'] = 102;
          }
          break;
        case 73:
          if (this.easterEggFlag2) {
            this.easterEggFlag3 = true;
          } else {
            document.getElementById('virtCanvas').style['z-index'] = 101;
            document.getElementById('segMap').style['z-index'] = 102;
          }
          break;
        case 68:
          if (this.easterEggFlag3) {
            this.easterEggFlag4 = true;
          } else {
            document.getElementById('virtCanvas').style['z-index'] = 101;
            document.getElementById('segMap').style['z-index'] = 102;
          }
          break;
        case 69:
          if (this.easterEggFlag4) {
            this.easterEggFlag5 = true;
          } else {
            document.getElementById('virtCanvas').style['z-index'] = 101;
            document.getElementById('segMap').style['z-index'] = 102;
          }
          break;
        case 82:
          if (this.easterEggFlag5) {
            document.getElementById('virtCanvas').style['z-index'] = 102;
            document.getElementById('segMap').style['z-index'] = 101;
            this.easterEggFlag1 = false;
            this.easterEggFlag2 = false;
            this.easterEggFlag3 = false;
            this.easterEggFlag4 = false;
            this.easterEggFlag5 = false;
          } else {
            document.getElementById('virtCanvas').style['z-index'] = 101;
            document.getElementById('segMap').style['z-index'] = 102;
          }
          break;
        default:
          this.easterEggFlag1 = false;
          this.easterEggFlag2 = false;
          this.easterEggFlag3 = false;
          this.easterEggFlag4 = false;
          this.easterEggFlag5 = false;
          document.getElementById('virtCanvas').style['z-index'] = 101;
          document.getElementById('segMap').style['z-index'] = 102;
      }
    }
  },
  mounted () {
    window.addEventListener('keyup', event => {
      this.easterEgg(event);
    });
  }
};
</script>

<style lang="scss">
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}
#nav {
  padding: 30px;
  a {
    font-weight: bold;
    color: #2c3e50;
    &.router-link-exact-active {
      color: #42b983;
    }
  }
}
body {
  overflow: hidden;
}
</style>
