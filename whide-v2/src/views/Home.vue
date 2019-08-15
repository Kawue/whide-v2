<template>
  <div class="home">
    <MainPlane v-if="showPanels"/>
    <sidebarLeft v-if="showPanels" />
    <sidebarRight v-if="showPanels" />
    <topBar v-if="showPanels" />
    <bottomBar v-if="showPanels" />
  </div>
</template>

<script>
// @ is an alias to /src
import Store from '@/store'
import MainPlane from '@/components/MainPlane'
import SidebarLeft from '../components/SidebarLeft'
import SidebarRight from '../components/SidebarRight'
import TopBar from '../components/TopBar'
import BottomBar from '../components/BottomBar'

export default {
  name: 'home',
  components: {
    BottomBar,
    TopBar,
    SidebarRight,
    SidebarLeft,
    MainPlane

  },
  data: function () {
    return {
      showPanels: false
    }
  },
  mounted: function () {
    console.log('home component mounted')
    Store.dispatch('fetchData')
    Store.dispatch('simpleHelloWorld')
    this.showPanels = true
  }
}
</script>
