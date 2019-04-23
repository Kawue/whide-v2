<template>
  <div class="home">
    <SidebarLeft />
    <MainPlane />
  </div>
</template>

<script>
// @ is an alias to /src
import MainPlane from '@/components/MainPlane.vue'
import SidebarLeft from '../components/sidebarLeft'

export default {
  name: 'home',
  components: {
    SidebarLeft,
    MainPlane
  }
}
</script>
