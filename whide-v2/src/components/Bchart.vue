<template>
    <div id="graphic" class="chart">
      <!--<b-button pill variant="danger" class="deleteButton">X</b-button>-->
    </div>
</template>

<script>
import * as d3 from 'd3'
import * as d3annotate from '../../../node_modules/d3-svg-annotation'
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
        right: 10,
        bottom: 20,
        left: 10
      }
      let width = 200 // - margin.left - margin.right
      let height = 290 // - margin.top - margin.bottom

      var y = d3.scaleBand()
        .range([height, 0])
        .padding(0.1)

      let min = d3.min(data, function (d) { return d.coefficient })
      let max = d3.max(data, function (d) { return d.coefficient })

      var x = d3.scaleLinear()
        .domain([min, max])
        .range([min, width])

      // append the svg object to the body of the page
      // append a 'group' element to 'svg'
      // moves the 'group' element to the top left margin
      var svg = d3.select('#graphic').append('svg')
        .attr('width', 20 + 'vw') //  margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .style('background-color', backgroundColor)
        .append('g')
        // .attr('transform',
        //  'translate(' + margin.left + ',' + margin.top + ')')

      // format the data
      data.forEach(function (d) {
        d.cefficients = +d.cefficients
      })

      // Scale the range of the data in the domains
      y.domain(data.map(function (d) { return d.mz }))
      // y.domain([0, d3.max(data, function(d) { return d.sales; })]);

      const tooltipType = d3annotate.annotationCallout
      const annotationProtperties = [{
        note: {
          label: 'wut'
        },
        dx: 200,
        dy: 200
      }]
      const makeAnnotations = d3annotate.annotation()
        .type(tooltipType)
        .annotations(annotationProtperties)

      // append the rectangles for the bar chart

      svg.selectAll('.bar')
        .data(data)
        .enter().append('rect')
        .attr('class', 'bar')
        .style('fill', 'green')
        // .attr("x", function(d) { return x(d.sales); })
        .attr('width', function (d) { return x(d.coefficient) })
        .attr('y', function (d) { return y(d.mz) })
        .attr('height', function (d) { return x(0.03 * d.coefficient) }) // scale bar size
        .append('g')
        .attr('class', 'annotation-group')
        .call(makeAnnotations)

      // add the x Axis
      svg.append('g')
        .attr('transform', 'translate(0,' + height + ')')
        .call(d3.axisBottom(x).tickValues([0.2, 0.4, 0.6, 0.8]))

      // add the y Axis
      // svg.append('g').call(d3.axisLeft(y))

      svg.append('foreignObject')
        .attr('width', 350)
        .attr('height', 30)
        .attr('right', 0)
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
  }
  .deleteButton {
    border-radius: 8px;
    background-color: red;
  }
  .div.tooltip {
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
