<template>
    <div id="graphic" class="chart">
      <!--<b-button pill variant="danger" class="deleteButton">X</b-button>-->
    </div>
</template>

<script>
import * as d3 from 'd3';
import * as d3annotate from 'd3-svg-annotation';
import { mapGetters } from 'vuex';
import store from '../store';

export default {
  name: 'Bchart',
  props: {
    prototypeid: {
      type: String
    }
  },
  computed: {
    ...mapGetters({
      bookmarks: 'getBookmarks'
    })
  },
  mounted () {
    let givenPrototypId = this.prototypeid;
    this.createChart(this.bookmarks[givenPrototypId]);
    store.subscribe(mutation => {
      if (mutation.type === 'SET_MOEBIUS') {
        let backgroundColor = this.bookmarks[givenPrototypId]['color'];
        d3.select('#' + this.bookmarks[givenPrototypId]['id'])
          .style('background-color', backgroundColor);
      }
    });
  },
  methods: {
    createChart: function (bookmark) {
      let backgroundColor = bookmark['color'].toString();
      let data = bookmark['mzs'].map(function (x, i) {
        return { 'mz': x, 'coefficient': bookmark['data'][i] };
      });

      let margin = {
        top: 25,
        right: 25,
        bottom: 2,
        left: 25
      };
      let width = 300 - margin.left - margin.right;
      let height = 360 - margin.top - margin.bottom;
      let padding = 0.1; let outerPadding = 0.3;

      let dataMin = d3.min(data, function (d) { return d.coefficient; });
      let dataMax = d3.max(data, function (d) { return d.coefficient; });
      // let barWidthMin = 10
      let barWidthMax = width;
      // let barHeightMin = 1
      let barHeightMax = height / data.map((d) => d.coefficient).reduce((a, b) => a + b, 0);

      let yScalAxis = d3.scaleLinear()
        .range([0, height - 40]);
        // let yScalAxis = d3.scaleBand()
        //  .rangeRound([height, 0]);

      let xScaleAxis = d3.scaleLinear()
        .domain([dataMin, dataMax])
        .range([0, barWidthMax + (barWidthMax * 0.05)], padding, outerPadding);

      let svg = d3.select('#graphic').append('svg')
        .attr('id', bookmark['id'])
        .attr('width', barWidthMax + margin.left + margin.right) //  margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .style('margin-right', '2px')
        .style('border-style', 'solid')
        .style('background-color', backgroundColor)
        .on('mouseenter', function () {
          d3.select(this)
            .append('g')
            .attr('class', 'annotation-group')
            .style('pointer-events', 'none');
        })
        .on('mouseleave', function (d) { d3.select(this).select('.annotation-group').remove(); });

      let coefficientArray = [];
      data.forEach(function (e) {
        coefficientArray.push(e['coefficient']);
      });

      /* data.forEach(function (entry) {
          var a = alpha(coefficientArray); // scale factor between value and bar width
          let mid = midi(coefficientArray, a); // mid-point displacement of bar i
          let w = wi(coefficientArray, a); // width of bar i

         */
      let a = alpha(coefficientArray);
      let mid = midi(coefficientArray, a);

      let offset = 0;
      let offsetsAr = [];
      let tickvals = [];
      let heights = [];
      for (let val of data) {
        let height = a * (val.coefficient);
        // console.log(val.mz);
        // console.log(yScalAxis(height));
        heights.push(height);
        let tick = offset + height;
        // console.log(tick);
        // console.log(offset);
        offsetsAr.push(offset);
        offset += height;
        tickvals.push(tick);
      }

      yScalAxis.domain([offsetsAr[0], offsetsAr[offsetsAr.length - 1]]);

      for (let val of data) {
        let height = a * (val.coefficient);
        console.log(val.mz);
        console.log(height);
        console.log(yScalAxis(height));
      }
      svg
        .append('g')
        .attr('transform', 'translate(' + margin.left + ',' + 40 + ')')
        .attr('class', 'hist-rects')
        .style('padding-left', '1')
        .selectAll('.bar')
        .data(data)
        .enter().append('rect')
        .attr('class', 'bar')
        .attr('y', function (d, i) {
          // return yScalAxis(d.mz) - (a * d.coefficient) / 2;
          return yScalAxis(offsetsAr[i]);
        })
        .style('fill', 'white')
        .style('stroke', 'black')
        .style('stroke-width', '0.1')
        .on('mouseenter', function () {
          d3.select(this)
            .style('fill', 'orange'); // orange is the new black
        })
        .on('mouseleave', function () {
          d3.select(this)
            .style('fill', 'white');
        })
        .attr('width', function (d) { return xScaleAxis(d.coefficient); })

        .attr('height', function (d, i) {
          return yScalAxis(heights[i]); // scale bar size
        })
        .on('mouseover', function (d) {
          const property = [{
            note: {
              label: d.mz
            },
            x: margin.left + xScaleAxis(d.coefficient),
            y: yScalAxis(d.mz),
            dy: 30 - yScalAxis(d.mz),
            dx: 220 - xScaleAxis(d.coefficient),
            color: 'black',
            type: d3annotate.annotationCalloutElbow
          }];
          svg
            .select('.annotation-group')
            .call(d3annotate.annotation()
              .annotations(property));
        })
        .on('mouseout', () => {
          svg
            .select('.annotations')
            .remove();
        });

      // format the data
      data.forEach(function (d) {
        d.coefficient = +d.coefficient;
      });

      // Scale the range of the data in the domains
      yScalAxis.domain(data.map(function (d) { return d.mz; }));
      // y.domain([0, d3.max(data, function(d) { return d.sales; })]);

      // add the x Axis
      svg.append('g')
        .attr('class', 'x_axis')
        .attr('transform', 'translate(' + margin.left + ',' + height + ')')
        .call(d3.axisBottom(xScaleAxis)
          .tickValues([dataMin, dataMax / 2, dataMax]));

      // add the y Axis
      svg.append('g')
        .attr('class', 'y_axis')
        .attr('transform', 'translate(' + margin.left + ',0)')
        .call(d3.axisLeft(yScalAxis))
        .selectAll('text').remove();
      // });

      svg.append('foreignObject')
        .attr('width', 30)
        .attr('height', 35)
        .append('xhtml:div')
        .append('xhtml:button')
        .attr('class', 'btn btn-outline-dark btn-sm')
        .html('x')
        .on('click', function () {
          store.dispatch('deleteBookmarks', bookmark['id'].toString());
          store.commit('DELETE_CHOOSED_BOOKMARK', bookmark['id'].toString());
        });

      function alpha (values) {
        let n = values.length;
        let total = d3.sum(values);
        return (width - (n - 1) * padding * width / n - 2 * outerPadding * width / n) / total;
      }
      function wi (values, alpha) {
        return function (i) {
        };
      }
      function midi (values, alpha) {
        let w = wi(values, alpha);
        let n = values.length;
        return function (_, i) {
          var op = outerPadding * width / n; var p = padding * width / n;
          return op + d3.sum(values.slice(0, i)) * alpha + i * p + w(i) / 2;
        };
      }
    }
  }

};
</script>

<style scoped lang="scss">
  .chart{
    // position: absolute;
    display: flex;
    align-content: flex-end;
    align-items: flex-end;
    bottom: 0;
    margin-left: 0.5vw;
    overflow: auto;
    margin-right: 0.5vw;
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
