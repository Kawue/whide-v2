<template>
  <div class="home">
    <SidebarLeft />
    <SidebarRight />
    <Topbar />
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
import Topbar from '../components/Topbar'

export default {
  name: 'home',
  components: {
    Topbar,
    SidebarRight,
    SidebarLeft,
    MainPlane,
    Bottombar
  }
}
</script>
