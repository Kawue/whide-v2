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
    let currentHighlightedMz;
    let bookM = document.querySelector('#' + bookmark['id']);
    bookM.removeEventListener('mousemove', addMouseMove);
    bookM.addEventListener('mousemove', addMouseMove, false);
    bookM.addEventListener('mouseenter', function () {
      store.commit('SET_CURRENT_HIGHLIGHTED_PROTOTYPE', bookmark['id']);
      store.commit('HIGHLIGHT_PROTOTYPE_OUTSIDE');
    });
    bookM.addEventListener('mouseout', function () {
      store.commit('SET_CURRENT_HIGHLIGHTED_PROTOTYPE', null);
      store.commit('HIGHLIGHT_PROTOTYPE_OUTSIDE');
    });
    let qdtree = d3.quadtree();
    const gHeight = givenHeight - 80;
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
      top: 20,
      right: 35,
      bottom: 20,
      left: 20
    };
    let width = 300 - margin.left - margin.right;
    let height = gHeight - margin.top - margin.bottom;
    let padding = 0.1; let outerPadding = 0.3;

    let dataMin = d3.min(data, function (d) { return d.coefficient; });
    let dataMax = d3.max(data, function (d) { return d.coefficient; });
    let barWidthMax = width;

    let canvas = document.querySelector('#' + bookmark['id']);
    canvas.width = width + 50;
    canvas.height = height;
    let ctx = canvas.getContext('2d');
    ctx.imageSmoothingEnabled = false;
    ctx.webkitImageSmoothingEnabled = false;
    ctx.fillStyle = backgroundColor;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.translate(margin.left, margin.top);

    let yScaleAxis = d3.scaleLinear()
      .range([0, height - 40]);

    let xScaleAxis = d3.scaleLinear()
      .domain([dataMin, dataMax])
      .range([0, barWidthMax + (barWidthMax * 0.05)], padding, outerPadding);

    // draw x axis
    ctx.strokeStyle = 'black';
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(xScaleAxis(dataMin), height - 39);
    ctx.lineTo(xScaleAxis(dataMax), height - 39);
    ctx.strokeStyle = 'black';
    ctx.stroke();

    // dataMin, dataMax / 2, dataMax]
    drawLine(dataMin);
    drawLine(dataMax / 2);
    drawLine(dataMax);

    // format the data
    data.forEach(function (d) {
      d.coefficient = +d.coefficient;
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
    ctx.fillStyle = 'white';
    data.forEach(function (d, i) {
      ctx.fillRect(0, yScaleAxis(offsetsAr[i]), xScaleAxis(d.coefficient), yScaleAxis(heights[i]));
      ctx.strokeStyle = 'black';
      ctx.lineWidth = 0.5;
      ctx.strokeRect(0, yScaleAxis(offsetsAr[i]), xScaleAxis(d.coefficient), yScaleAxis(heights[i]));
    });
    // TODO: schriftgroese gut aendern
    if (showMzBoolean) {
      data.forEach(function (d, i) {
        ctx.fillStyle = 'black';
        ctx.textAlign = 'left';
        ctx.textBaseline = 'left';
        ctx.font = yScaleAxis(heights[i]);
        ctx.fillText(d.mz, xScaleAxis(d.coefficient), yScaleAxis(offsetsAr[i]));
      });
    }
    qdtree
      .x(function (d) {
        return 0;
      })
      .y(function (d) {
        return yScaleAxis(offsetsAr[data.indexOf(d)]);
      })
      .extent([
        [0, 0],
        [canvas.width, canvas.height]
      ])
      .addAll(data);
    function drawLine (value) {
      ctx.fillStyle = 'black';
      ctx.font = '0.9em';
      ctx.textAlign = 'left';
      ctx.textBaseline = 'left';
      ctx.fillText(Math.round(value * 100) / 100, xScaleAxis(value) - 5, height - 25);
      ctx.beginPath(); ;
      ctx.moveTo(xScaleAxis(value), height - 39);
      ctx.lineTo(xScaleAxis(value), height - 35);
      ctx.strokeStyle = 'black';
      ctx.stroke();
    }
    function addMouseMove (event) {
      let x = event.offsetX;
      let y = event.offsetY;
      let nearest = qdtree.find(x - margin.left, y - margin.top);
      createAnnotation(nearest);
    }
    function createAnnotation (nearest) {
      const index = data.indexOf(nearest);
      if (currentHighlightedMz === undefined) {
        currentHighlightedMz = nearest;
        ctx.fillStyle = 'orange';
        ctx.fillRect(0, yScaleAxis(offsetsAr[index]), xScaleAxis(nearest.coefficient), yScaleAxis(heights[index]));
        ctx.strokeStyle = 'black';
        ctx.lineWidth = 0.5;
        ctx.strokeRect(0, yScaleAxis(offsetsAr[index]), xScaleAxis(nearest.coefficient), yScaleAxis(heights[index]));
      } else if (currentHighlightedMz !== nearest) {
        ctx.fillStyle = 'white';
        ctx.fillRect(0, yScaleAxis(offsetsAr[data.indexOf(currentHighlightedMz)]), xScaleAxis(currentHighlightedMz.coefficient), yScaleAxis(heights[data.indexOf(currentHighlightedMz)]));
        ctx.strokeStyle = 'black';
        ctx.lineWidth = 0.5;
        ctx.strokeRect(0, yScaleAxis(offsetsAr[data.indexOf(currentHighlightedMz)]), xScaleAxis(currentHighlightedMz.coefficient), yScaleAxis(heights[data.indexOf(currentHighlightedMz)]));
        ctx.fillStyle = 'orange';
        ctx.fillRect(0, yScaleAxis(offsetsAr[index]), xScaleAxis(nearest.coefficient), yScaleAxis(heights[index]));
        ctx.strokeStyle = 'black';
        ctx.lineWidth = 0.5;
        ctx.strokeRect(0, yScaleAxis(offsetsAr[index]), xScaleAxis(nearest.coefficient), yScaleAxis(heights[index]));
        currentHighlightedMz = nearest;
      }
      d3.select('.annotation-group').remove();

      const property = [{
        note: {
          label: currentHighlightedMz.mz
        },
        x: margin.left + xScaleAxis(currentHighlightedMz.coefficient),
        y: yScaleAxis(offsetsAr[index]) + 40,
        dy: -5 - yScaleAxis(offsetsAr[index]),
        dx: 210 - xScaleAxis(currentHighlightedMz.coefficient),
        color: 'black',
        type: d3annotate.annotationCalloutElbow
      }];
      let anno = d3.select('#' + bookmark['id']);
      anno
        .append('g')
        .attr('class', 'annotation-group')
        .call(d3annotate.annotation()
          .annotations(property));
    }
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

    let svg = d3.select('#' + bookmark['id'])
      .attr('width', width + margin.right + margin.left)
      .attr('height', height + margin.top + margin.bottom)
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
          dy: -10,
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

  lineChart (bookmark, showMzBoolean = false, mzAnnotations = false) {
    let backgroundColor = bookmark['color'].toString();
    let mzItemList = Object.keys(bookmark['mzObject']);
    let data = mzItemList.map(function (x, i) {
      return { 'mz': x, 'coefficient': bookmark['data'][i] };
    });
    let mzList = [];
    data.forEach(function (d) {
      mzList.push(d.mz);
    });
    const mzlistLength = mzList.length;

    let margin = {
      top: 25,
      right: 25,
      bottom: 40,
      left: 40
    };

    let width = document.documentElement.clientWidth - 50 - margin.left - margin.right;
    let height = 300 - margin.top - margin.bottom;
    data.forEach(function (d) {
      d.coefficient = +d.coefficient;
    });

    let dataMin = d3.min(data, function (d) {
      return d.coefficient;
    });
    let dataMax = d3.max(data, function (d) {
      return d.coefficient;
    });
    let mzMin = d3.min(data, function (d) {
      return parseFloat(d.mz);
    });
    let mzMax = d3.max(data, function (d) {
      return parseFloat(d.mz);
    });

    let yScaleAxis = d3.scaleLinear()
      .domain([dataMin, dataMax])
      .range([height, 0]);

    let xScaleAxis = d3.scaleLinear()
      .domain([mzMin, mzMax])
      .range([0, width]);

    let line = d3.line()
      .x(function (d, i) {
        return xScaleAxis(parseFloat(d.mz));
      })
      .y(function (d) {
        return yScaleAxis(d.coefficient);
      });

    let svg = d3.select('#' + bookmark['id'])
      .attr('width', width + margin.right + margin.left)
      .attr('height', height + margin.top + margin.bottom)
      .style('background-color', backgroundColor)
      .on('mouseenter', function () {
        d3.select(this)
          .append('g')
          .attr('class', 'annotation-group')
          .style('pointer-events', 'none');
      })
      .on('mouseleave', function () {
        d3.select(this).select('.annotation-group').remove();
      });

    svg.on('mouseover', function () {
      store.commit('SET_CURRENT_HIGHLIGHTED_PROTOTYPE', bookmark['id']);
      store.commit('HIGHLIGHT_PROTOTYPE_OUTSIDE');
    })
      .on('mouseout', function () {
        store.commit('SET_CURRENT_HIGHLIGHTED_PROTOTYPE', null);
        store.commit('HIGHLIGHT_PROTOTYPE_OUTSIDE');
      });

    svg.append('g')
      .attr('class', 'x axis')
      .attr('transform', 'translate(' + margin.left + ',' + (height + 40) + ')')
      .call(d3.axisBottom(xScaleAxis)
        .tickValues([mzList[0], mzList[parseInt(mzlistLength * 0.25)], mzList[parseInt(mzlistLength * 0.5)], mzList[parseInt(mzlistLength * 0.75)], mzList[mzlistLength - 1]])
        .tickFormat(d3.format('r')));

    svg.append('g')
      .attr('class', 'y_axis')
      .attr('transform', 'translate(' + margin.left + ',' + 40 + ')')
      .call(d3.axisLeft(yScaleAxis)
        .tickValues([dataMin, dataMax / 2, dataMax]));

    svg.append('path')
      .data([data])
      .attr('transform', 'translate(' + margin.left + ',' + 40 + ')')
      .attr('height', height + margin.top + margin.bottom)
      .attr('class', 'line')
      .attr('d', line)
      .style('fill', 'none')
      .style('stroke', 'black')
      .style('stroke-width', '0.2em');

    svg.selectAll('.dot')
      .data(data)
      .enter().append('circle')
      .attr('transform', 'translate(' + margin.left + ',' + 40 + ')')
      .attr('height', height + margin.top + margin.bottom)
      .attr('class', 'dot')
      .attr('cx', function (d) {
        return xScaleAxis(parseFloat(d.mz));
      })
      .attr('cy', function (d) {
        return yScaleAxis(d.coefficient);
      })
      .attr('r', 3.5)
      .style('fill', 'whitesmoke')
      .on('mouseenter', function () {
        d3.select(this)
          .attr('r', 6);
      })
      .on('mouseleave', function () {
        d3.select(this)
          .attr('r', 3.5);
      })
      .on('mouseover', function (d, i) {
        const property = [{
          note: {
            label: d.mz
          },
          x: margin.left + xScaleAxis(parseFloat(d.mz)),
          y: yScaleAxis(d.coefficient) + 40,
          dy: -10,
          dx: 10,
          color: 'whitesmoke',
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
  }
  alpha (values, width, padding, outerPadding) {
    let n = values.length;
    let total = d3.sum(values);
    return (width - (n - 1) * padding * width / n - 2 * outerPadding * width / n) / total;
  }
}
export default BookmarkService;
