import store from '../store';
import * as d3 from 'd3';
import * as d3annotate from 'd3-svg-annotation';

class BookmarkService {
  normalizeCoefficients (coefficients) {
    let max = Number.MIN_SAFE_INTEGER;
    let min = Number.MAX_SAFE_INTEGER;
    let newCoeff = {};
    for (let pro in coefficients) {
      let i;
      for (i = 0; i < coefficients[pro].length; i++) {
        if (coefficients[pro][i] < min) {
          min = coefficients[pro][i];
        }
        if (coefficients[pro][i] > max) {
          max = coefficients[pro][i];
        }
      }
    }
    for (var norPro in coefficients) {
      let k;
      let newValues = [];
      for (k = 0; k < coefficients[norPro].length; k++) {
        let val = ((coefficients[norPro][k] - min) / (max - min));
        newValues.push(val);
      }
      newCoeff[norPro] = newValues;
    }
    return newCoeff;
  }
  changePrototypeColor (newColors, choosedBookmarks) {
    let choosedPrototypes = Object.keys(choosedBookmarks);
    choosedPrototypes.forEach(function (p) {
      choosedBookmarks[p]['color'] = newColors[p]['color'];
    });
    return choosedBookmarks;
  }
  createBchart (bookmark, givenHeight = 300, showMzBoolean = false, mzAnnotations = false) {
    const gHeight = givenHeight - 60;
    let backgroundColor = bookmark['color'].toString();
    let mzItemList;
    if (mzAnnotations) {
      mzItemList = Object.values(bookmark['mzObject']);
    } else {
      mzItemList = Object.keys(bookmark['mzObject']);
    }
    let data = mzItemList.map(function (x, i) {
      return { 'mz': x, 'coefficient': bookmark['data'][i] };
    });

    let margin = {
      top: 25,
      right: 35,
      bottom: 5,
      left: 20
    };
    let width = 300 - margin.left - margin.right;
    let height = gHeight - margin.top - margin.bottom;
    let padding = 0.1; let outerPadding = 0.3;

    let dataMin = d3.min(data, function (d) { return d.coefficient; });
    let dataMax = d3.max(data, function (d) { return d.coefficient; });
    let barWidthMax = width;

    let yScaleAxis = d3.scaleLinear()
      .range([0, height - 40]);

    let xScaleAxis = d3.scaleLinear()
      .domain([dataMin, dataMax])
      .range([0, barWidthMax + (barWidthMax * 0.05)], padding, outerPadding);

    let svg = d3.select('#bookmarkcontent').append('svg')
      .attr('id', bookmark['id'])
      .attr('width', barWidthMax + margin.left + margin.right) //  margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .style('margin-right', '2px')
      .style('margin-bottom', '10px')
      .style('border-style', 'solid')
      .style('border-width', '1px')
      .style('background-color', backgroundColor)
      .on('mouseenter', function () {
        d3.select(this)
          .append('g')
          .attr('class', 'annotation-group')
          .style('pointer-events', 'none');
      })
      .on('mouseleave', function () { d3.select(this).select('.annotation-group').remove(); });

    svg.on('mouseover', function () {
      store.commit('SET_CURRENT_HIGHLIGHTED_PROTOTYPE', bookmark['id']);
      store.commit('HIGHLIGHT_PROTOTYPE_OUTSIDE');
    })
      .on('mouseout', function () {
        store.commit('SET_CURRENT_HIGHLIGHTED_PROTOTYPE', null);
        store.commit('HIGHLIGHT_PROTOTYPE_OUTSIDE');
      });
    let coefficientArray = [];
    data.forEach(function (e) {
      coefficientArray.push(e['coefficient']);
    });

    let a = this.alpha(coefficientArray, width, padding, outerPadding);
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
      .enter()
      .append('g')
      .attr('class', 'barGroup' + bookmark['id'])
      .append('rect')
      .attr('class', 'barRect')
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
          dy: -5 - yScaleAxis(offsetsAr[i]),
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

    if (showMzBoolean) {
      d3.selectAll('.barGroup' + bookmark['id'])
        .insert('text', 'barRect')
        .data(data)

        .attr('class', 'barLabel')

        .attr('y', function (d, i) {
          return (yScaleAxis(offsetsAr[i]) + yScaleAxis(heights[i])) - (yScaleAxis(heights[i]) / 6);
        })
        .attr('font-size', function (d, i) {
          return yScaleAxis(heights[i]);
        })
        .attr('x', function (d) {
          return (xScaleAxis(d.coefficient)) / 4;
        })
        .style('fill', '#000000')
        .text(function (d) {
          return d.mz;
        });
    }

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
        store.commit('DELETE_BOOKMARK', bookmark['id']);
      });
  }

  // function to creat a bar chart of the spektrum from one prototype
  createHorizontalChart (bookmark, givenHeight = 300, showMzBoolean = false, mzAnnotations = false) {
    let backgroundColor = bookmark['color'].toString();
    let mzItemList;
    if (mzAnnotations) {
      mzItemList = Object.values(bookmark['mzObject']);
    } else {
      mzItemList = Object.keys(bookmark['mzObject']);
    }
    let data = mzItemList.map(function (x, i) {
      return { 'mz': x, 'coefficient': bookmark['data'][i] };
    });

    let margin = {
      top: 25,
      right: 25,
      bottom: 40,
      left: 40
    };

    let width = document.documentElement.clientWidth - 50 - margin.left - margin.right;
    let height = 300 - margin.top - margin.bottom;
    let padding = 0.1;
    let outerPadding = 0.3;

    data.forEach(function (d) {
      d.coefficient = +d.coefficient;
    });

    let dataMin = d3.min(data, function (d) { return d.coefficient; });
    let dataMax = d3.max(data, function (d) { return d.coefficient; });

    let yScaleAxis = d3.scaleLinear()
      .domain([dataMin, dataMax])
      .range([ height, 0 ]);

    let xScaleAxis = d3.scaleLinear()
      .range([ 0, width ]);

    let svg = d3.select('#bookmarkcontent').append('svg')
      .attr('id', bookmark['id'])
      .attr('width', width + margin.right + margin.left)
      .attr('height', height + margin.top + margin.bottom)
      .style('border-style', 'solid')
      .style('border-width', '1px')
      .style('background-color', backgroundColor)
      .on('mouseenter', function () {
        d3.select(this)
          .append('g')
          .attr('class', 'annotation-group')
          .style('pointer-events', 'none');
      })
      .on('mouseleave', function () { d3.select(this).select('.annotation-group').remove(); });

    svg.on('mouseover', function () {
      store.commit('SET_CURRENT_HIGHLIGHTED_PROTOTYPE', bookmark['id']);
      store.commit('HIGHLIGHT_PROTOTYPE_OUTSIDE');
    })
      .on('mouseout', function () {
        store.commit('SET_CURRENT_HIGHLIGHTED_PROTOTYPE', null);
        store.commit('HIGHLIGHT_PROTOTYPE_OUTSIDE');
      });

    let coefficientArray = [];
    data.forEach(function (e) {
      coefficientArray.push(e['coefficient']);
    });

    // create a widths array with the with of the bar  and an offset array inclusive the size of the bars before
    let a = this.alpha(coefficientArray, width, padding, outerPadding);
    let offset = 0;
    let offsetsAr = [];
    let widths = [];
    for (let val of data) {
      let w = a * (val.coefficient);
      widths.push(w);
      offsetsAr.push(offset);
      offset += w;
    }

    xScaleAxis.domain([offsetsAr[0], offsetsAr[offsetsAr.length - 1]]);
    svg
      .append('g')
      .attr('transform', 'translate(' + margin.left + ',' + 40 + ')')
      .attr('class', 'hist-rects')
      .selectAll('.bar')
      .data(data)
      .enter()
      .append('g')
      .attr('class', 'barGroup' + bookmark['id'])
      .append('rect')
      .attr('class', 'barRect')
      .attr('x', function (d, i) {
        return xScaleAxis(offsetsAr[i]);
      })
      .attr('y', function (d) {
        return yScaleAxis(d.coefficient);
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
      .attr('height', function (d) { return height - yScaleAxis(d.coefficient); })
      .attr('width', function (d, i) {
        return xScaleAxis(widths[i]); // scale bar size
      })
      .on('mouseover', function (d, i) {
        const property = [{
          note: {
            label: d.mz
          },
          x: margin.left + xScaleAxis(offsetsAr[i]),
          y: yScaleAxis(d.coefficient) + 40,
          dy: 10,
          dx: 10,
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

    // add the y Axis
    svg.append('g')
      .attr('class', 'y_axis')
      .attr('transform', 'translate(' + margin.left + ',' + 40 + ')')
      .call(d3.axisLeft(yScaleAxis)
        .tickValues([dataMin, dataMax / 2, dataMax]));

    // add the x Axis
    svg.append('g')
      .attr('class', 'x_axis')
      .attr('transform', 'translate(' + margin.left + ',' + (height + 40) + ')')
      .call(d3.axisBottom(xScaleAxis));

    if (showMzBoolean) {
      d3.selectAll('.barGroup' + bookmark['id'])
        .insert('text', 'barRect')
        .data(data)
        .attr('class', 'barLabel')
        .attr('y', function (d) {
          return (yScaleAxis(d.coefficient));
        })
        .attr('font-size', function (d, i) {
          return xScaleAxis(widths[i]) / 4;
        })
        .attr('x', function (d, i) {
          return (xScaleAxis(offsetsAr[i]));
        })
        .style('fill', '#000000')
        .text(function (d) {
          return d.mz;
        });
    }
    svg.append('foreignObject')
      .attr('width', 30)
      .attr('height', 35)
      .append('xhtml:div')
      .append('xhtml:button')
      .attr('class', 'btn btn-outline-dark btn-sm')
      .html('x')
      .on('click', function () {
        store.commit('DELETE_BOOKMARK', bookmark['id']);
      });
  }
  lineChart (bookmark, givenHeight = 300) {
    let backgroundColor = bookmark['color'].toString();
    let mzItemList = Object.keys(bookmark['mzObject']);
    let data = mzItemList.map(function (x, i) {
      return { 'mz': x, 'coefficient': bookmark['data'][i] };
    });

    let margin = {
      top: 25,
      right: 25,
      bottom: 40,
      left: 40
    };

    let width = document.documentElement.clientWidth - 50 - margin.left - margin.right;
    let height = 300 - margin.top - margin.bottom;
    let padding = 0.1;
    let outerPadding = 0.3;

    data.forEach(function (d) {
      d.coefficient = +d.coefficient;
    });

    let dataMin = d3.min(data, function (d) { return d.coefficient; });
    let dataMax = d3.max(data, function (d) { return d.coefficient; });

    let yScaleAxis = d3.scaleLinear()
      .domain([dataMin, dataMax])
      .range([ height, 0 ]);

    let xScaleAxis = d3.scaleLinear()
      .range([ 0, width ]);

    let svg = d3.select('#bookmarkcontent').append('svg')
      .attr('id', bookmark['id'])
      .attr('width', width + margin.right + margin.left)
      .attr('height', height + margin.top + margin.bottom)
      .style('border-style', 'solid')
      .style('border-width', '1px')
      .style('background-color', backgroundColor)
      .on('mouseenter', function () {
        d3.select(this)
          .append('g')
          .attr('class', 'annotation-group')
          .style('pointer-events', 'none');
      })
      .on('mouseleave', function () { d3.select(this).select('.annotation-group').remove(); });

    svg.on('mouseover', function () {
      store.commit('SET_CURRENT_HIGHLIGHTED_PROTOTYPE', bookmark['id']);
      store.commit('HIGHLIGHT_PROTOTYPE_OUTSIDE');
    })
      .on('mouseout', function () {
        store.commit('SET_CURRENT_HIGHLIGHTED_PROTOTYPE', null);
        store.commit('HIGHLIGHT_PROTOTYPE_OUTSIDE');
      });

  }
  alpha (values, width, padding, outerPadding) {
    let n = values.length;
    let total = d3.sum(values);
    return (width - (n - 1) * padding * width / n - 2 * outerPadding * width / n) / total;
  }
}
export default BookmarkService;
