<template>
  <div class="bottombar">
      <div class="bottombarWidget">
        <div class="content">
          <Bookmarks side="up" ></Bookmarks>
        </div>
      </div>
  </div>
</template>

<script>
import Bookmarks from './Bookmarks';
import interact from 'interactjs';
import store from '../store';

export default {
  name: 'Bottom',
  components: { Bookmarks },
  mounted () {
    interact('.bottombarWidget')
      .resizable({
        edges: { top: true, bottom: false, left: false, right: false },
        modifiers: [
          interact.modifiers.restrictEdges({
            outer: 'parent',
            endOnly: true
          })
        ]
      }).on('resizemove', event => {
        let { x, y } = event.target.dataset;

        x = parseFloat(x) || 0;
        y = parseFloat(y) || 0;

        Object.assign(event.target.style, {
          width: `${event.rect.width}px`,
          height: `${event.rect.height}px`,
          transform: `translate(${event.deltaRect.left}px, ${event.deltaRect.top}px)`
        });

        Object.assign(event.target.dataset, { x, y });
        let height = event.target.style.height;
        const regex = /[0-9]*\.?[0-9]+?/i;
        let heightNumber = height.match(regex);
        store.commit('SET_BOTTOMBAR_HEIGHT', parseInt(heightNumber[0]));
      });
  }
};
</script>

<style scoped lang="scss">
  .bottombar{
    clear: both;
  }
  .bottombarWidget {
    position: absolute;
    height: 40px;
    min-width: 100vw;
    left: 0;
    z-index: 101;
    background-color: #4f5051;
    bottom: 0;
    float: bottom;
    border-style: solid;
    border-color: orange;
    box-sizing: border-box;

    .content {
      display: flex;
      overflow-x: scroll;

    }
  }

</style>
