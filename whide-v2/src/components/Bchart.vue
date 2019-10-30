<template>
    <div id="graphic" class="chart">
    </div>
</template>

<script>
import * as d3 from 'd3';
import * as d3annotate from 'd3-svg-annotation';
import { mapGetters } from 'vuex';
import store from '../store';

export default {
  name: 'Bchart',
  data: function () {
    return {
      currentMarkedPrototypeColor: null,
      currentMarkedPrototype: null
    };
  },
  props: {
    prototypeid: {
      type: String
    }
  },
  computed: {
    ...mapGetters({
      bookmarks: 'getBookmarks',
      highlightedPrototype: 'getCurrentHighlightedPrototype'
    })
  },
  mounted () {
    this.createChart(this.bookmarks[this.prototypeid]);
    this.unsubscribe = store.subscribe(mutation => {
      if (mutation.type === 'SET_MOEBIUS') {
        if (Object.keys(this.bookmarks).length !== 0) {
          let backgroundColor = this.bookmarks[this.prototypeid]['color'];
          d3.select('#' + this.bookmarks[this.prototypeid]['id'])
            .style('background-color', backgroundColor);
        }
      } else if (mutation.type === 'SET_DEFAULT_POSITION') {
        if (Object.keys(this.bookmarks).length !== 0) {
          let backgroundColor = this.bookmarks[this.prototypeid]['color'];
          d3.select('#' + this.bookmarks[this.prototypeid]['id'])
            .style('background-color', backgroundColor);
        }
      }
      if (mutation.type === 'SET_CURRENT_HIGHLIGHTED_PROTOTYPE') {
        if (this.highlightedPrototype !== null) {
          let markedColor = 'rgba(255,255,255,255)';
          if (this.highlightedPrototype in this.bookmarks) {
            if (this.currentMarkedPrototype !== null) {
              if (this.currentMarkedPrototype !== this.highlightedPrototype) {
                d3.select('#' + this.currentMarkedPrototype)
                  .style('background-color', this.currentMarkedPrototypeColor);
                d3.select('#' + this.bookmarks[this.highlightedPrototype]['id'])
                  .style('background-color', markedColor);
                this.currentMarkedPrototype = this.prototypeid;
                this.currentMarkedPrototypeColor = this.bookmarks[this.prototypeid]['color'];
              }
            } else {
              this.currentMarkedPrototype = this.prototypeid;
              this.currentMarkedPrototypeColor = this.bookmarks[this.prototypeid]['color'];
            }
          } else {
            d3.select('#' + this.currentMarkedPrototype)
              .style('background-color', this.currentMarkedPrototypeColor);
            this.currentMarkedPrototype = null;
            this.currentMarkedPrototypeColor = null;
          }
        } else {
          d3.select('#' + this.currentMarkedPrototype)
            .style('background-color', this.currentMarkedPrototypeColor);
          this.currentMarkedPrototype = null;
          this.currentMarkedPrototypeColor = null;
        }
      }
    });
  },
  beforeDestroy () {
    this.unsubscribe();
  },
  methods: {
    createChart: function (bookmark) {
      if (this.highlightedPrototype !== null) {
        if (bookmark['id'] === this.highlightedPrototype.toString()) {
          console.log('now');
        }
      }

      let backgroundColor = bookmark['color'].toString();
      let data = bookmark['mzs'].map(function (x, i) {
        return { 'mz': x, 'coefficient': bookmark['data'][i] };
      });

      let margin = {
        top: 25,
        right: 35,
        bottom: 2,
        left: 20
      };
      let width = 300 - margin.left - margin.right;
      let height = 360 - margin.top - margin.bottom;
      let padding = 0.1; let outerPadding = 0.3;

      let dataMin = d3.min(data, function (d) { return d.coefficient; });
      let dataMax = d3.max(data, function (d) { return d.coefficient; });
      let barWidthMax = width;

      let yScaleAxis = d3.scaleLinear()
        .range([0, height - 40]);

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
        .on('mouseleave', function () { d3.select(this).select('.annotation-group').remove(); });

      let coefficientArray = [];
      data.forEach(function (e) {
        coefficientArray.push(e['coefficient']);
      });

      let a = alpha(coefficientArray);
      let offset = 0;
      let offsetsAr = [];
      let heights = [];
      for (let val of data) {
        let height = a * (val.coefficient);
        heights.push(height);
        offsetsAr.push(offset);
        offset += height;
      }

      yScaleAxis.domain([offsetsAr[0], offsetsAr[offsetsAr.length - 1]]);

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
          return yScaleAxis(offsetsAr[i]);
        })
        .style('fill', 'white')
        .style('stroke', 'black')
        .style('stroke-width', '0.5')
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
          return yScaleAxis(heights[i]); // scale bar size
        })
        .on('mouseover', function (d, i) {
          const property = [{
            note: {
              label: d.mz
            },
            x: margin.left + xScaleAxis(d.coefficient),
            y: yScaleAxis(offsetsAr[i]) + 40,
            dy: 10 - yScaleAxis(offsetsAr[i]),
            dx: 210 - xScaleAxis(d.coefficient),
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

      // add the x Axis
      svg.append('g')
        .attr('class', 'x_axis')
        .attr('transform', 'translate(' + margin.left + ',' + height + ')')
        .call(d3.axisBottom(xScaleAxis)
          .tickValues([dataMin, dataMax / 2, dataMax]));

      // add the y Axis
      svg.append('g')
        .attr('class', 'y_axis')
        .attr('transform', 'translate(' + margin.left + ',' + 40 + ')')
        .call(d3.axisLeft(yScaleAxis))
        .selectAll('text').remove();

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
    }
  }

};
</script>

<style scoped lang="scss">
  .chart{
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
    border-radius: 8px;
    pointer-events: none;
  }
  </style>
