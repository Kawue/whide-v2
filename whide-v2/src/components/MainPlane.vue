<template>
    <div class="mainPlane">
      <li class="witz" v-for="(item, index) in ids" :key="item.id" :item="item">
        {{index}}
      </li>
    </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  name: 'MainPlane.vue',
  computed: {
    ...mapGetters({
      ids: 'getBookmarkIds'
    })
  }
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
  .witz{ color: #42b983}
</style>
