<template>
  <div>
    <table>
    <div  v-for="(chart,index) in charts" v-bind:key="index">
      <th class="column">
      <v-chart v-bind:options="getChartOption(chart)" class="echarts">
      </v-chart>
      </th>
    </div>
    </table>
  </div>
</template>
<script>
import Echarts from 'vue-echarts'
import 'echarts/lib/chart/bar'
import 'echarts/lib/component/tooltip'
import { mapGetters } from 'vuex'

export default {
  components: {
    'v-chart': Echarts
  },
  computed: {
    ...mapGetters({
      bookmarks: 'getBookmarks',
      charts: 'getBookmarkChart'
    })
  },
  name: 'Bookmarks',
  methods: {
    getChartOption: function (chart) {
      console.log(chart)
      return {
        bar: {
          backgroundColor: chart.bar.backgroundColor,
          title: {
            text: chart.bar.title
          },
          tooltip: {
            trigger: chart.bar.tooltip.trigger
          },
          legend: {
            data: chart.bar.legend.data
          },
          toolbox: {
            show: chart.bar.toolbox.show,
            feature: {
              mark: {show: chart.bar.toolbox.feature.mark},
              dataView: {
                show: chart.bar.toolbox.feature.dataView.show,
                readOnly: chart.bar.toolbox.feature.dataView.show
              },
              magicType: {
                show: chart.bar.toolbox.feature.magicType.show,
                type: chart.bar.toolbox.feature.magicType.type
              },
              restore: {show: chart.bar.toolbox.feature.restore.show},
              saveAsImage: {show: chart.bar.toolbox.feature.saveAsImage.show}
            }
          },
          calculable: chart.bar.calculable,
          xAxis: [
            {
              type: chart.bar.xAxis.type,
              boundaryGap: chart.bar.xAxis.boundaryGap
            }
          ],
          yAxis: [
            {
              type: chart.bar.yAxis.type,
              data: chart.bar.yAxis.data
            }
          ],
          series: [
            {
              name: chart.bar.series.name,
              type: chart.bar.series.type,
              data: chart.bar.series.data
            }
          ]
        }
      }
    }
  }
}

</script>

<style scoped lang="scss">
  .echarts {
    position: relative;
    height: 45vh;
    width: 10vw;
    z-index: 102;
    left: auto;
  }
  .column{
    border: darkslateblue;
    z-index: 102;
  }

</style>
