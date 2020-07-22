import store from '../store';
import * as d3 from 'd3';
import * as d3annotate from 'd3-svg-annotation';

class BookmarkService {
  /*
  Set the new color from the colorwheel for the bookmark infromation.
  @params: newColors is a dict where eacht key (prototype) holds his color, choosedbookmark is the dict of all choosed Bookmarks
   */
  changePrototypeColor (newColors, choosedBookmarks) {
    let choosedPrototypes = Object.keys(choosedBookmarks);
    choosedPrototypes.forEach(function (p) {
      choosedBookmarks[p]['color'] = newColors[p]['color'];
    });
    return choosedBookmarks;
  }
  /*
  creates a vertical bar chart
  @params:
    qdtree is the qdtree which is created in the bookmaerk.vue for this prototype
    data hold the informations about the mzs and the intensities
    given height holds the height of the component
    showMzBoolean is a boolean if the mz should be display on the bars
    mzAnnotations is the boolean if the annotations should be display not the real values
    id is the prototype id
    color is the color of the bookmark
   */
  createBchart (qdtree, data, givenHeight = 300, showMzBoolean = false, mzAnnotations = false, id, color) {
    let currentHighlightedMz;
    const gHeight = givenHeight - 30;
    let backgroundColor = color.toString();
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

    // add events on chart for interaction
    let canvas = document.querySelector('#' + id);
    canvas.addEventListener('mousemove', addMouseMove, false);
    canvas.addEventListener('mouseenter', mEnter, false);
    canvas.addEventListener('mouseout', mOut, false);
    canvas.addEventListener('click', addMzToAggregation, false);
    function mEnter () {
      if (!store.state.horizonatlCharts) {
        store.commit('SET_CURRENT_HIGHLIGHTED_PROTOTYPE', id);
        store.commit('HIGHLIGHT_PROTOTYPE_OUTSIDE');
      } else {
        d3.select('.annotation-group').remove();
        canvas.removeEventListener('mousemove', addMouseMove);
        canvas.removeEventListener('mouseenter', mEnter);
        canvas.removeEventListener('mouseout', mOut);
        canvas.removeEventListener('click', addMzToAggregation);
      }
    }
    function mOut () {
      if (!store.state.horizonatlCharts) {
        store.commit('SET_CURRENT_HIGHLIGHTED_PROTOTYPE', null);
        store.commit('HIGHLIGHT_PROTOTYPE_OUTSIDE');
        drawChart();
        d3.select('.annotation-group').remove();
      } else {
        d3.select('.annotation-group').remove();
        canvas.removeEventListener('mousemove', addMouseMove);
        canvas.removeEventListener('mouseenter', mEnter);
        canvas.removeEventListener('mouseout', mOut);
        canvas.removeEventListener('click', addMzToAggregation);
      }
    }

    canvas.width = width + 50;
    canvas.height = height;
    let ctx = canvas.getContext('2d');
    ctx.imageSmoothingEnabled = false;
    ctx.webkitImageSmoothingEnabled = false;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = backgroundColor;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.translate(margin.left, margin.top);

    // build scalors for d3 chart
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
    this.drawLine(dataMin, ctx, height, xScaleAxis);
    this.drawLine(dataMax / 2, ctx, height, xScaleAxis);
    this.drawLine(dataMax, ctx, height, xScaleAxis);

    // format the data
    data.forEach(function (d) {
      d.coefficient = +d.coefficient;
    });

    // function to calculate the thikness of the bars according to the height
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
    // apply the offset on the y-axes
    yScaleAxis.domain([offsetsAr[0], offsetsAr[offsetsAr.length - 1]]);
    drawChart();

    // function for finding the nearest bar with the qdtree
    function addMouseMove (event) {
      let x = event.offsetX;
      let y = event.offsetY;
      let nearest = qdtree.find(x - margin.left, y - margin.top);
      createAnnotation(nearest);
    }

    // function to draw the chart as a canvas
    function drawChart () {
      qdtree.removeAll(data);
      qdtree
        .x(function () {
          return 0;
        })
        .y(function (d) {
          return (yScaleAxis(offsetsAr[data.indexOf(d)]) + yScaleAxis(heights[data.indexOf(d)]) / 2);
        })
        .extent([
          [0, 0],
          [canvas.width, canvas.height]
        ])
        .addAll(data);
      ctx.fillStyle = 'white';
      data.forEach(function (d, i) {
        ctx.fillRect(0, yScaleAxis(offsetsAr[i]), xScaleAxis(d.coefficient), yScaleAxis(heights[i]));
        ctx.strokeStyle = 'black';
        ctx.lineWidth = 0.5;
        ctx.strokeRect(0, yScaleAxis(offsetsAr[i]), xScaleAxis(d.coefficient), yScaleAxis(heights[i]));
      });
      if (showMzBoolean) {
        data.forEach(function (d, i) {
          const c = parseFloat(d.mz).toFixed(3).toString();
          ctx.fillStyle = 'black';
          ctx.textAlign = 'left';
          ctx.textBaseline = 'bottom';
          ctx.font = yScaleAxis(heights[i]).toString() + 'px verdana';
          ctx.fillText(c, xScaleAxis(d.coefficient) - ctx.measureText(c).width, yScaleAxis(offsetsAr[i]) + yScaleAxis(heights[i]));
        });
      }
    }

    /*
      colors the nearest bar in the chart orange or white and back if it is not anymore the nearest
      also adds the annotation with d3-annotations
     */
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
        let currentIndex = data.indexOf(currentHighlightedMz);
        ctx.fillStyle = 'white';
        ctx.fillRect(0, yScaleAxis(offsetsAr[currentIndex]), xScaleAxis(currentHighlightedMz.coefficient), yScaleAxis(heights[currentIndex]));
        ctx.strokeStyle = 'black';
        ctx.lineWidth = 0.5;
        ctx.strokeRect(0, yScaleAxis(offsetsAr[currentIndex]), xScaleAxis(currentHighlightedMz.coefficient), yScaleAxis(heights[currentIndex]));

        const c = parseFloat(currentHighlightedMz.mz).toFixed(3).toString();
        ctx.fillStyle = 'black';
        ctx.textAlign = 'left';
        ctx.textBaseline = 'bottom';
        ctx.font = yScaleAxis(heights[currentIndex]).toString() + 'px verdana';
        ctx.fillText(c, xScaleAxis(currentHighlightedMz.coefficient) - ctx.measureText(c).width, yScaleAxis(offsetsAr[currentIndex]) + yScaleAxis(heights[currentIndex]));

        // draw next one orange
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
          label: parseFloat(currentHighlightedMz.mz).toFixed(3)
        },
        x: margin.left + xScaleAxis(currentHighlightedMz.coefficient),
        y: yScaleAxis(offsetsAr[index]) + 26,
        dy: -yScaleAxis(offsetsAr[index]),
        dx: 200 - xScaleAxis(currentHighlightedMz.coefficient) - margin.top,
        color: 'black',
        type: d3annotate.annotationCalloutElbow
      }];
      let anno = d3.select('#' + id + '-container');
      anno
        .append('svg')
        .attr('class', 'annotation-group')
        .style('position', 'absolute')
        .style('z-index', '102')
        .style('height', height + 'px')
        .style('pointer-events', 'none')
        .call(d3annotate.annotation()
          .annotations(property));
    }
    // Function for clicking on bar to add the mz-value to aggregation list
    function addMzToAggregation () {
      store.commit('SET_MZ_TO_AGGREGATIONLIST', currentHighlightedMz.mz.toString());
    }
  }
  /*
  creates a horizontal bar chart which uses the full width of the screen
  @params:
    qdtree is the qdtree which is created in the bookmaerk.vue for this prototype
    data hold the informations about the mzs and the intensities
    showMzBoolean is a boolean if the mz should be display on the bars
    mzAnnotations is the boolean if the annotations should be display not the real values
    id is the prototype id
    color is the color of the bookmark
   */
  createHorizontalChart (qdtree, data, showMzBoolean = false, mzAnnotations = false, id, color) {
    let currentHighlightedMz;
    let backgroundColor = color.toString();

    let margin = {
      top: 40,
      right: 25,
      bottom: 20,
      left: 40
    };

    let width = document.documentElement.clientWidth - 100 - margin.left - margin.right;
    let height = 265 - margin.top - margin.bottom;
    let padding = 0.1;
    let outerPadding = 0.3;

    data.forEach(function (d) {
      d.coefficient = +d.coefficient;
    });

    let dataMin = d3.min(data, function (d) { return d.coefficient; });
    let dataMax = d3.max(data, function (d) { return d.coefficient; });

    // add events on chart for interaction
    let canvas = document.querySelector('#' + id);
    canvas.addEventListener('mousemove', addMouseMove, false);
    canvas.addEventListener('mouseenter', mEnter, false);
    canvas.addEventListener('mouseout', mOut, false);
    canvas.addEventListener('click', addMzToAggregation, false);
    function mEnter () {
      if (store.state.horizonatlCharts) {
        store.commit('SET_CURRENT_HIGHLIGHTED_PROTOTYPE', id);
        store.commit('HIGHLIGHT_PROTOTYPE_OUTSIDE');
      } else {
        d3.select('.annotation-group').remove();
        canvas.removeEventListener('mousemove', addMouseMove);
        canvas.removeEventListener('mouseenter', mEnter);
        canvas.removeEventListener('mouseout', mOut);
        canvas.removeEventListener('click', addMzToAggregation);
      }
    }
    function mOut () {
      if (store.state.horizonatlCharts) {
        store.commit('SET_CURRENT_HIGHLIGHTED_PROTOTYPE', null);
        store.commit('HIGHLIGHT_PROTOTYPE_OUTSIDE');
        drawChart();
        d3.select('.annotation-group').remove();
      } else {
        d3.select('.annotation-group').remove();
        canvas.removeEventListener('mousemove', addMouseMove);
        canvas.removeEventListener('mouseenter', mEnter);
        canvas.removeEventListener('mouseout', mOut);
        canvas.removeEventListener('click', addMzToAggregation);
      }
    }
    canvas.width = width + 50;
    canvas.height = height + 50;
    let ctx = canvas.getContext('2d');
    ctx.imageSmoothingEnabled = false;
    ctx.webkitImageSmoothingEnabled = false;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = backgroundColor;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.translate(margin.left, margin.top);
    let yScaleAxis = d3.scaleLinear()
      .domain([dataMin, dataMax])
      .range([ height, 0 ]);

    let xScaleAxis = d3.scaleLinear()
      .range([ 0, width ]);

    // draw x axis
    ctx.strokeStyle = 'black';
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(-1, yScaleAxis(dataMin));
    ctx.lineTo(-1, yScaleAxis(dataMax));
    ctx.strokeStyle = 'black';
    ctx.stroke();

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
    let widths = [];
    for (let val of data) {
      let w = a * (val.coefficient);
      widths.push(w);
      offsetsAr.push(offset);
      offset += w;
    }

    // dataMin, dataMax / 2, dataMax]
    this.drawHorizontalLine(dataMin, ctx, height, yScaleAxis);
    this.drawHorizontalLine(dataMax / 2, ctx, height, yScaleAxis);
    this.drawHorizontalLine(dataMax, ctx, height, yScaleAxis);
    xScaleAxis.domain([offsetsAr[0], offsetsAr[offsetsAr.length - 1]]);
    drawChart();

    function drawChart () {
      qdtree.removeAll(data);
      qdtree
        .x(function (d) {
          return xScaleAxis(offsetsAr[data.indexOf(d)]) + xScaleAxis(widths[data.indexOf(d)]) / 2;
        })
        .y(function () {
          return height;
        })
        .extent([
          [0, 0],
          [canvas.width, canvas.height]
        ])
        .addAll(data);
      ctx.fillStyle = 'white';
      data.forEach(function (d, i) {
        ctx.fillRect(xScaleAxis(offsetsAr[i]), yScaleAxis(d.coefficient), xScaleAxis(widths[i]), height - yScaleAxis(d.coefficient));
        ctx.strokeStyle = 'black';
        ctx.lineWidth = 0.5;
        ctx.strokeRect(xScaleAxis(offsetsAr[i]), yScaleAxis(d.coefficient), xScaleAxis(widths[i]), height - yScaleAxis(d.coefficient));
      });
      if (showMzBoolean) {
        data.forEach(function (d, i) {
          const c = parseFloat(d.mz).toFixed(3).toString();
          ctx.fillStyle = 'black';
          ctx.textAlign = 'left';
          ctx.textBaseline = 'bottom';
          fitTextOnBar(ctx, c, 'verdana', xScaleAxis(widths[i]));
          // ctx.font = xScaleAxis(widths[i]).toString() + 'px verdana';
          ctx.fillText(c, xScaleAxis(offsetsAr[i]), yScaleAxis(d.coefficient));
        });
      }
    }

    /* function to find out how big the font needs to be to fit on the bar
    @ params:
      context is the canvas context of the bookmark
      text is the mz-value or his annotation
      fontface is the type of font
      w is the width of the bar
     */
    function fitTextOnBar (context, text, fontface, w) {
      // start with a large font size
      var fontsize = 30;

      // lower the font size until the text fits the canvas
      do {
        fontsize--;
        context.font = fontsize + 'px ' + fontface;
      } while (context.measureText(text).width > w);
    }

    function addMouseMove (event) {
      let x = event.offsetX;
      let y = event.offsetY;
      let nearest = qdtree.find(x - margin.left, y - margin.top);
      createAnnotation(nearest);
    }
    /*
          colors the nearest bar in the chart orange or white and back if it is not anymore the nearest
          also adds the annotation with d3-annotations
    */
    function createAnnotation (nearest) {
      const index = data.indexOf(nearest);
      if (currentHighlightedMz === undefined) {
        currentHighlightedMz = nearest;
        ctx.fillStyle = 'orange';
        ctx.fillRect(xScaleAxis(offsetsAr[index]), yScaleAxis(nearest.coefficient), xScaleAxis(widths[index]), height - yScaleAxis(nearest.coefficient));
        ctx.strokeStyle = 'black';
        ctx.lineWidth = 0.5;
        ctx.strokeRect(xScaleAxis(offsetsAr[index]), yScaleAxis(nearest.coefficient), xScaleAxis(widths[index]), height - yScaleAxis(nearest.coefficient));
      } else if (currentHighlightedMz !== nearest) {
        let currentIndex = data.indexOf(currentHighlightedMz);
        ctx.fillStyle = 'white';
        ctx.fillRect(xScaleAxis(offsetsAr[currentIndex]), yScaleAxis(currentHighlightedMz.coefficient), xScaleAxis(widths[currentIndex]), height - yScaleAxis(currentHighlightedMz.coefficient));
        ctx.strokeStyle = 'black';
        ctx.lineWidth = 0.5;
        ctx.strokeRect(xScaleAxis(offsetsAr[currentIndex]), yScaleAxis(currentHighlightedMz.coefficient), xScaleAxis(widths[currentIndex]), height - yScaleAxis(currentHighlightedMz.coefficient));

        const c = parseFloat(currentHighlightedMz.mz).toFixed(3).toString();
        ctx.fillStyle = 'black';
        ctx.textAlign = 'left';
        ctx.textBaseline = 'bottom';
        fitTextOnBar(ctx, c, 'verdana', xScaleAxis(widths[currentIndex]));
        // ctx.font = xScaleAxis(widths[i]).toString() + 'px verdana';
        ctx.fillText(c, xScaleAxis(offsetsAr[currentIndex]), yScaleAxis(currentHighlightedMz.coefficient));

        ctx.fillStyle = 'orange';
        ctx.fillRect(xScaleAxis(offsetsAr[index]), yScaleAxis(nearest.coefficient), xScaleAxis(widths[index]), height - yScaleAxis(nearest.coefficient));
        ctx.strokeStyle = 'black';
        ctx.lineWidth = 0.5;
        ctx.strokeRect(xScaleAxis(offsetsAr[index]), yScaleAxis(nearest.coefficient), xScaleAxis(widths[index]), height - yScaleAxis(nearest.coefficient));
        currentHighlightedMz = nearest;
      }

      d3.select('.annotation-group').remove();

      const property = [{
        note: {
          label: parseFloat(currentHighlightedMz.mz).toFixed(3)
        },
        x: margin.left + xScaleAxis(offsetsAr[index]) + 3,
        y: yScaleAxis(nearest.coefficient) + margin.top + 2,
        dy: -15,
        dx: 10,
        color: 'black',
        type: d3annotate.annotationCalloutElbow
      }];
      let anno = d3.select('#' + id + '-container');
      anno
        .append('svg')
        .attr('class', 'annotation-group')
        .style('position', 'absolute')
        .style('z-index', '103')
        .style('height', height + margin.top + 'px')
        .style('width', width + 'px')
        .style('pointer-events', 'none')
        .call(d3annotate.annotation()
          .annotations(property));
    }
    function addMzToAggregation () {
      store.commit('SET_MZ_TO_AGGREGATIONLIST', currentHighlightedMz.mz.toString());
    }
  }

  /*
  creates a horizonatl linechart
  @params:
    qdtree is the qdtree which is created in the bookmaerk.vue for this prototype
    data hold the informations about the mzs and the intensities
    showMzBoolean is a boolean if the mz should be display on the bars
    mzAnnotations is the boolean if the annotations should be display not the real values
    id is the prototype id
    color is the color of the bookmark
   */
  lineChart (qdtree, data, showMzBoolean = false, mzAnnotations = false, id, color) {
    let currentHighlightedMz;
    let margin = {
      top: 40,
      right: 25,
      bottom: 20,
      left: 40
    };

    let width = document.documentElement.clientWidth - 100 - margin.left - margin.right;
    let height = 265 - margin.top - margin.bottom;
    data.forEach(function (d) {
      d.coefficient = +d.coefficient;
    });

    let dataMin = d3.min(data, function (d) { return d.coefficient; });
    let dataMax = d3.max(data, function (d) { return d.coefficient; });

    let mzMin = d3.min(data, function (d) {
      return parseFloat(d.mz);
    });
    let mzMax = d3.max(data, function (d) {
      return parseFloat(d.mz);
    });

    // add events on chart for interaction
    let canvas = document.querySelector('#' + id);
    canvas.addEventListener('mousemove', addMouseMove, false);
    canvas.addEventListener('mouseenter', mEnter, false);
    canvas.addEventListener('mouseout', mOut, false);
    canvas.addEventListener('click', addMzToAggregation, false);
    function mEnter () {
      if (store.state.horizonatlCharts) {
        store.commit('SET_CURRENT_HIGHLIGHTED_PROTOTYPE', id);
        store.commit('HIGHLIGHT_PROTOTYPE_OUTSIDE');
      } else {
        d3.select('.annotation-group').remove();
        canvas.removeEventListener('mousemove', addMouseMove);
        canvas.removeEventListener('mouseenter', mEnter);
        canvas.removeEventListener('mouseout', mOut);
        canvas.removeEventListener('click', addMzToAggregation);
      }
    }
    function mOut () {
      if (store.state.horizonatlCharts) {
        store.commit('SET_CURRENT_HIGHLIGHTED_PROTOTYPE', null);
        store.commit('HIGHLIGHT_PROTOTYPE_OUTSIDE');
        drawLines();
        d3.select('.annotation-group').remove();
      } else {
        d3.select('.annotation-group').remove();
        canvas.removeEventListener('mousemove', addMouseMove);
        canvas.removeEventListener('mouseenter', mEnter);
        canvas.removeEventListener('mouseout', mOut);
        canvas.removeEventListener('click', addMzToAggregation);
      }
    }

    canvas.width = width + 50;
    canvas.height = height + 50;
    let ctx = canvas.getContext('2d');
    ctx.imageSmoothingEnabled = false;
    ctx.webkitImageSmoothingEnabled = false;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = color.toString();
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.translate(margin.left, margin.top);

    let yScaleAxis = d3.scaleLinear()
      .domain([dataMin, dataMax])
      .range([height, 0]);

    let xScaleAxis = d3.scaleLinear()
      .domain([mzMin - 2, mzMax + 2])
      .range([0, width]);
    // draw x axis
    ctx.strokeStyle = 'black';
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(-1, yScaleAxis(dataMin));
    ctx.lineTo(-1, yScaleAxis(dataMax));
    ctx.strokeStyle = 'black';
    ctx.stroke();

    // dataMin, dataMax / 2, dataMax]
    this.drawHorizontalLine(dataMin, ctx, height, yScaleAxis);
    this.drawHorizontalLine(dataMax / 2, ctx, height, yScaleAxis);
    this.drawHorizontalLine(dataMax, ctx, height, yScaleAxis);

    let line = d3.line()
      .x(function (d) {
        return xScaleAxis(parseFloat(d.mz));
      })
      .y(function (d) {
        return yScaleAxis(d.coefficient);
      })
      .context(ctx);

    drawLines();
    function drawLines () {
      qdtree.removeAll(data);
      qdtree
        .x(function (d) {
          return xScaleAxis(d.mz);
        })
        .y(function () {
          return height;
        })
        .extent([
          [0, 0],
          [canvas.width, canvas.height]
        ])
        .addAll(data);
      let spektrumData = [];
      data.forEach(function (p) {
        spektrumData.push({ 'mz': p.mz, 'coefficient': 0 });
        spektrumData.push(p);
        spektrumData.push({ 'mz': p.mz, 'coefficient': 0 });
      });
      const lastItem = spektrumData[spektrumData.length - 1];
      spektrumData.push({ 'mz': lastItem.mz, 'coefficient': 0 });

      ctx.beginPath();
      line(spektrumData);
      ctx.lineWidth = 1;
      ctx.strokeStyle = 'black';
      ctx.stroke();

      ctx.fillStyle = 'black';
      data.forEach(function (point) {
        ctx.beginPath();
        ctx.arc(xScaleAxis(point.mz), yScaleAxis(point.coefficient), 2, 0, 2 * Math.PI);
        ctx.fill();
      });
      if (showMzBoolean) {
        data.forEach(function (d) {
          const c = parseFloat(d.mz).toFixed(3).toString();
          ctx.fillStyle = 'black';
          ctx.textAlign = 'left';
          ctx.textBaseline = 'left';
          ctx.font = xScaleAxis(d.mz);
          ctx.fillText(c, xScaleAxis(d.mz), yScaleAxis(d.coefficient));
        });
      }
    }
    function addMouseMove (event) {
      let x = event.offsetX;
      let y = event.offsetY;
      let nearest = qdtree.find(x - margin.left, y - margin.top);
      createAnnotation(nearest);
    }
    function createAnnotation (nearest) {
      if (currentHighlightedMz === undefined) {
        currentHighlightedMz = nearest;
        ctx.beginPath();
        ctx.fillStyle = 'white';
        ctx.arc(xScaleAxis(nearest.mz), yScaleAxis(nearest.coefficient), 2, 0, 2 * Math.PI);
        ctx.fill();
      } else if (currentHighlightedMz !== nearest) {
        ctx.beginPath();
        ctx.fillStyle = 'black';
        ctx.arc(xScaleAxis(currentHighlightedMz.mz), yScaleAxis(currentHighlightedMz.coefficient), 2, 0, 2 * Math.PI);
        ctx.fill();
        ctx.beginPath();
        ctx.fillStyle = 'white';
        ctx.arc(xScaleAxis(nearest.mz), yScaleAxis(nearest.coefficient), 2, 0, 2 * Math.PI);
        ctx.fill();
        currentHighlightedMz = nearest;
      }

      d3.select('.annotation-group').remove();

      const property = [{
        note: {
          label: parseFloat(currentHighlightedMz.mz).toFixed(3)
        },
        x: margin.left + xScaleAxis(nearest.mz) + 3,
        y: yScaleAxis(nearest.coefficient) + margin.top + 2,
        dy: -15,
        dx: 10,
        color: 'black',
        type: d3annotate.annotationCalloutElbow
      }];
      let anno = d3.select('#' + id + '-container');
      anno
        .append('svg')
        .attr('class', 'annotation-group')
        .style('position', 'absolute')
        .style('z-index', '103')
        .style('height', height + margin.top + 'px')
        .style('width', width + 'px')
        .style('pointer-events', 'none')
        .call(d3annotate.annotation()
          .annotations(property));
    }
    function addMzToAggregation () {
      store.commit('SET_MZ_TO_AGGREGATIONLIST', currentHighlightedMz.mz.toString());
    }
  }
  alpha (values, width, padding, outerPadding) {
    let n = values.length;
    let total = d3.sum(values);
    return (width - (n - 1) * padding * width / n - 2 * outerPadding * width / n) / total;
  }
  drawLine (value, context, h, xScale) {
    context.fillStyle = 'black';
    context.font = '0.9em';
    context.textAlign = 'left';
    context.textBaseline = 'left';
    context.fillText(Math.round(value * 100) / 100, xScale(value) - 5, h - 25);
    context.beginPath();
    context.moveTo(xScale(value), h - 39);
    context.lineTo(xScale(value), h - 35);
    context.strokeStyle = 'black';
    context.stroke();
  }
  drawHorizontalLine (value, context, h, yScale) {
    context.fillStyle = 'black';
    context.font = '0.9em';
    context.textAlign = 'right';
    context.textBaseline = 'right';
    context.fillText(Math.round(value * 100) / 100, -5, yScale(value) + 5);
    context.beginPath();
    context.moveTo(-1, yScale(value));
    context.lineTo(-4, yScale(value));
    context.strokeStyle = 'black';
    context.stroke();
  }
}
export default BookmarkService;
