<template>
  <div class="home">
    <MainPlane v-if="showPanels"/>
    <left v-if="showPanels" />
    <right v-if="showPanels" />
    <top v-if="showPanels" />
    <bottom v-if="showPanels" />
  </div>
</template>

<script>
// @ is an alias to /src
import Store from '@/store'
import MainPlane from '@/components/MainPlane'

import Left from '../components/Left'
import Right from '../components/Right'
import Top from '../components/Top'
import Bottom from '../components/Bottom'

export default {
  name: 'home',
  components: {
    Bottom,
    Top,
    Right,
    Left,
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
    this.showPanels = true
  }
}
</script>
