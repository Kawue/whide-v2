<template>
  <div class="home">
    <MainPlane v-if="showPanels"/>
    <sidebarLeft v-if="showPanels" />
    <sidebarRight v-if="showPanels" />
    <bottomBar v-if="showPanels" />
  </div>
</template>

<script>
// @ is an alias to /src
import Store from '@/store';
import MainPlane from '@/components/MainPlane';
import SidebarLeft from '../components/SidebarLeft';
import SidebarRight from '../components/SidebarRight';
import BottomBar from '../components/BottomBar';

export default {
  name: 'home',
  components: {
    BottomBar,
    SidebarRight,
    SidebarLeft,
    MainPlane

  },
  data: function () {
    return {
      showPanels: false
    };
  },
  mounted: function () {
    Store.dispatch('getDimensions');
    Store.dispatch('getRingCoefficients');
    Store.dispatch('fetchData');
    //Store.dispatch('getBrightfieldImage');
    this.showPanels = true;
  }
};
</script>
