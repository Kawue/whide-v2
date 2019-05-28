<template>
    <SidebarWidget v-bind:side="side" v-bind:initialExpanded="initialExpanded">
      <div>MZs</div>
      <span
        style="float: left;margin-left: 15px; color: #dc3b9e"
        v-on:click="toggleShowAnnotation"
        v-b-tooltip.hover.top="'Show Annotations'"
      >
          <v-icon
            name="pencil-alt"
          ></v-icon>
        </span>
      <span
        v-on:click="toggleAsc(); sortMZ()"
        style="float: right; padding: 2px"
        v-b-tooltip.hover.top="'Sort'"
      >
        <v-icon
          v-bind:name="asc ? 'sort-amount-up' : 'sort-amount-down'"
        ></v-icon>
        </span>
      <select class="list" multiple>
        <option
          v-for="mzItem in mzs"
          v-bind:key="mzItem"
          v-bind:value="mzItem"
          v-on:dblclick="annotateMzItem(mzItem)"
            >
          {{showAnnotation ? mzItem : mzItem}} <!--first mzItem is the name-->
        </option>
      </select>

    </SidebarWidget>
</template>

<script>
import SidebarWidget from './SidebarWidget'
import { mapGetters } from 'vuex'
import store from '../store'

export default {
  props: ['initialExpanded'],
  extends: SidebarWidget,
  name: 'mzlist',
  components: {
    SidebarWidget
  },
  computed: {
    ...mapGetters({
      mzs: 'getMzValues',
      showAnnotation: 'mzShowAnnotation',
      asc: 'mzAsc'
    })
  },
  methods: {
    toggleAsc: function () {
      store.commit('MZLIST_TOOGLE_ASC')
    },
    sortMZ: function () {
      store.commit('MZLIST_SORT_MZ')
    },
    toggleShowAnnotation: function () {
      store.commit('MZLIST_SHOW_ANNOTATIONS')
    },
    annotateMzItem: function (mzItem) {

    }
  }

}

</script>
<style scoped lang="scss">

  .list {
    padding: 0;
    font-size: 0.9em;
    min-height: 93vh;
    width: 100%;
    text-align: center;
    margin-top: 8px;
  }
  .options {
    background-color: darkgray;
  }
</style>
