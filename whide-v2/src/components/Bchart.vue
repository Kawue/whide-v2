<template>
    <div id="graphic" class="chart"></div>
</template>

<script>
import * as d3 from 'd3'
import { mapGetters } from 'vuex'

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
    this.createChart()
  },
  methods: {
    createChart: function () {
      let backgroundColor = String
      let givenPrototypId = this.prototypeid
      this.bookmarks.forEach(function (entry) {
        let id = Object.keys(entry).toString()
        if (id === givenPrototypId) {
          backgroundColor = Object.keys(entry[id]).toString()
        }
      })
      // console.log(Object.keys(this.bookmarks[0][this.prototypeid]).toString())
      let data = [{ 'salesperson': 'Bob', 'sales': 33 }, { 'salesperson': 'Robin', 'sales': 12 }, { 'salesperson': 'Anne', 'sales': 41 }, { 'salesperson': 'Mark', 'sales': 16 }, { 'salesperson': 'Joe', 'sales': 59 }, { 'salesperson': 'Eve', 'sales': 38 }, { 'salesperson': 'Karen', 'sales': 21 }, { 'salesperson': 'Kirsty', 'sales': 25 }, { 'salesperson': 'Chris', 'sales': 30 }, { 'salesperson': 'Lisa', 'sales': 47 }, { 'salesperson': 'Tom', 'sales': 5 }, { 'salesperson': 'Stacy', 'sales': 20 }, { 'salesperson': 'Charles', 'sales': 13 }, { 'salesperson': 'Mary', 'sales': 29 }]

      let margin = {
        top: 20,
        right: 1,
        bottom: 30,
        left: 50
      }
      let width = 350 - margin.left - margin.right
      let height = 290 - margin.top - margin.bottom
      var y = d3.scaleBand()
        .range([height, 0])
        .padding(0.1)

      var x = d3.scaleLinear()
        .range([0, width])

      // append the svg object to the body of the page
      // append a 'group' element to 'svg'
      // moves the 'group' element to the top left margin
      var svg = d3.select('#graphic').append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .style('background-color', backgroundColor)
        .append('g')
        .attr('transform',
          'translate(' + margin.left + ',' + margin.top + ')')

      // format the data
      data.forEach(function (d) {
        d.sales = +d.sales
      })

      // Scale the range of the data in the domains
      x.domain([0, d3.max(data, function (d) { return d.sales })])
      y.domain(data.map(function (d) { return d.salesperson }))
      // y.domain([0, d3.max(data, function(d) { return d.sales; })]);

      // append the rectangles for the bar chart
      svg.selectAll('.bar')
        .data(data)
        .enter().append('rect')
        .attr('class', 'bar')
        .style('fill', 'green')
        // .attr("x", function(d) { return x(d.sales); })
        .attr('width', function (d) { return x(d.sales) })
        .attr('y', function (d) { return y(d.salesperson) })
        .attr('height', y.bandwidth())

      // add the x Axis
      svg.append('g')
        .attr('transform', 'translate(0,' + height + ')')
        .call(d3.axisBottom(x))

      // add the y Axis
      svg.append('g')
        .call(d3.axisLeft(y))
    }
  }

}
</script>

<style scoped lang="scss">
  .chart{
    display: flex;
    width: 100%;
  }
</style>
