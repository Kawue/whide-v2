<template>
  <div class="home">
    <SidebarLeft  v-if="showPanels" />
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
import Store from '@/store'

export default {
  name: 'home',
  components: {
    Topbar,
    SidebarRight,
    SidebarLeft,
    MainPlane,
    Bottombar
  },
  data: function () {
    return {
      showPanels: false
    }
  },
  mounted: function () {
    console.log('home component mounted')
    Store.dispatch('fetchData')
    this.showPanels = true
  }
}
</script>
