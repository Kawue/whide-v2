<template>
    <div id="graphic" class="chart">
      <!--<b-button pill variant="danger" class="deleteButton">X</b-button>-->
    </div>
</template>

<script>
import * as d3 from 'd3'
import * as d3annotate from 'd3-svg-annotation'
import { mapGetters } from 'vuex'
import store from '../store'

export default {
  name: 'Bchart',
  props: {
    prototypeid: String
  },
  computed: {
    ...mapGetters({
      bookmarks: 'getBookmarks'
    })
  },
  mounted () {
    let givenPrototypId = this.prototypeid
    for (const entry of this.bookmarks) {
      let id = entry['id'].toString()
      if (id === givenPrototypId) {
        this.createChart(entry)
      }
    }
  },
  methods: {
    createChart: function (bookmark) {
      let backgroundColor = bookmark['color'].toString()
      let data = bookmark['mzs'].map(function (x, i) {
        return { 'mz': x, 'coefficient': bookmark['data'][i] }
      })

      let margin = {
        top: 20,
        right: 25,
        bottom: 2,
        left: 25
      }
      let width = 300 - margin.left - margin.right
      let height = 385 - margin.top - margin.bottom

      let yScalAxis = d3.scaleBand()
        .range([height, 40])
        // .padding(0.1)

      let dataMin = d3.min(data, function (d) { return d.coefficient })
      let dataMax = d3.max(data, function (d) { return d.coefficient })
      // let barWidthMin = 10
      let barWidthMax = width

      let xScaleAxis = d3.scaleLinear()
        .domain([dataMin, dataMax])
        .range([0, barWidthMax + (barWidthMax * 0.05)])

      // let barHeightMin = 1
      let barHeightMax = height / data.map((d) => d.coefficient).reduce((a, b) => a + b, 0)

      let svg = d3.select('#graphic').append('svg')
        .attr('width', 20 + 'vw') //  margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .style('background-color', backgroundColor)
        .on('mouseenter', function () {
          d3.select(this)
            .append('g')
            .attr('class', 'annotation-group')
            .style('pointer-events', 'none')
        })
        .on('mouseleave', function (d) { d3.select(this).select('.annotation-group').remove() })

      // format the data
      data.forEach(function (d) {
        d.cefficients = +d.cefficients
      })

      // Scale the range of the data in the domains
      yScalAxis.domain(data.map(function (d) { return d.mz }))
      // y.domain([0, d3.max(data, function(d) { return d.sales; })]);

      svg
        .append('g')
        .attr('transform', 'translate(' + margin.left + ',0)')
        .attr('class', 'hist-rects')
        .style('padding-left', '1')
        .selectAll('.bar')
        .data(data)
        .enter().append('rect')
        .attr('class', 'bar')
        .style('fill', 'grey')
        .style('stroke', 'black')
        .style('stroke-width', '1')
        .attr('width', function (d) { return xScaleAxis(d.coefficient) })
        .attr('y', function (d) { return yScalAxis(d.mz) })
        .attr('height', function (d) { return d.coefficient * barHeightMax })
        .attr('height', function (d) { return 2 }) // scale bar size
      // scale bar size
        .on('mouseover', function (d) {
          const property = [{
            note: {
              label: d.mz
            },
            x: margin.left + xScaleAxis(d.coefficient),
            y: yScalAxis(d.mz),
            dy: 30 - yScalAxis(d.mz),
            dx: 240 - xScaleAxis(d.coefficient),
            color: 'black',
            type: d3annotate.annotationCalloutElbow
          }]
          svg
            .select('.annotation-group')
            .call(d3annotate.annotation()
              .annotations(property))
        })
        .on('mouseout', () => {
          svg
            .select('.annotations')
            .remove()
        })

      // add the x Axis
      svg.append('g')
        .attr('class', 'x_axis')
        .attr('transform', 'translate(' + margin.left + ',' + height + ')')
        .call(d3.axisBottom(xScaleAxis)
          .tickValues([dataMin, dataMax / 2, dataMax]))

      // add the y Axis
      svg.append('g')
        .attr('class', 'y_axis')
        .attr('transform', 'translate(' + margin.left + ',0)')
        .call(d3.axisLeft(yScalAxis))
        .selectAll('text').remove()

      svg.append('foreignObject')
        .attr('width', 30)
        .attr('height', 30)
        .append('xhtml:div')
        .append('xhtml:button')
        .attr('class', 'btn btn-info btn-sm')
        .html('x')
        .on('click', function () {
          store.commit('DELETE_CHOOSED_BOOKMARK', bookmark['id'].toString())
        })
    }
  }

}
</script>

<style scoped lang="scss">
  .chart{
    // position: absolute;
    display: flex;
    align-content: flex-end;
    align-items: flex-end;
    width: 100vw;
    bottom: 0;
    margin-left: 0.5vw;
  }

  .tooltip {
    position: absolute;
    text-align: center;
    width: 60px;
    height: 28px;
    padding: 2px;
    font: 12px sans-serif;
    background: lightsteelblue;
    border: 0px;
    border-radius: 8px;
    pointer-events: none;
  }
  </style>
