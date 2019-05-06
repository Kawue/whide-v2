<template>
  <div class="home">
    <SidebarLeft />
    <SidebarRight />
    <Bottombar />
    <MainPlane />
  </div>
</template>

<script>
// @ is an alias to /src
import MainPlane from '@/components/MainPlane'
import SidebarLeft from '@/components/SidebarLeft'
import SidebarRight from '@/components/SidebarRight'
import Bottombar from '../components/Bottombar'

export default {
  name: 'home',
  components: {
    SidebarRight,
    SidebarLeft,
    MainPlane,
    Bottombar
  }
}
</script>
