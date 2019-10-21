import store from '../store';
import * as d3 from 'd3';

var drawSegmentationMap = function (dimensions) {
  'use strict';
  let ringData = store.state.currentRingData;
  const dimX = dimensions['x'] + 1;
  const dimY = dimensions['y'] + 1;
  let uInt8IndexSample = {};
  let offsetX = 0;
  let offSetY = 0;

  Object.keys(ringData).forEach(function (prototype) {
    let pixels = ringData[prototype]['pixels'];
    let colorString = ringData[prototype]['color'];
    let colorsOnly = colorString.substring(colorString.indexOf('(') + 1, colorString.lastIndexOf(')')).split(/,\s*/);
    let colors = [];
    colorsOnly.forEach(function (value) {
      colors.push(parseInt(value));
    });
    let indizes = [];
    pixels.forEach(function (pixel) {
      let indize = indexAccess(pixel[0], pixel[1]);
      indizes.push(indize);
      pixel.push(indize);
    });
    let dict = {};
    dict['indizes'] = indizes;
    dict['color'] = colors;
    uInt8IndexSample[prototype] = dict;
  });
  const canvas = document.getElementById('segMap');
  let ctx = canvas.getContext('2d');
  ctx.webkitImageSmoothingEnabled = false;
  ctx.mozImageSmoothingEnabled = false;
  ctx.imageSmoothingEnabled = false;

  let imageData = ctx.createImageData(dimX, dimY);
  let data = imageData.data;
  Object.keys(uInt8IndexSample).forEach(function (prototype) {
    let sample = uInt8IndexSample[prototype]['indizes'];
    let color = uInt8IndexSample[prototype]['color'];
    sample.forEach(function (index) {
      data[index] = color[0];
      data[index + 1] = color[1];
      data[index + 2] = color[2];
      data[index + 3] = 255;
    });
  });

  let newCanvas = document.createElement('canvas');
  newCanvas.width = imageData.width;
  newCanvas.height = imageData.height;
  newCanvas.getContext('2d').putImageData(imageData, 0, 0);

  let scalor = 2;

  if (dimX >= dimY) {
    scalor = Math.floor(canvas.width / dimX);
  } else {
    scalor = Math.floor(canvas.height / dimY);
  }
  store.commit('SET_SCALOR', scalor);
  ctx.save();
  ctx.scale(scalor, scalor);
  offsetX = (canvas.width - (newCanvas.width * scalor)) / 4;
  offSetY = (canvas.height - (newCanvas.height * scalor)) / 4;
  ctx.drawImage(newCanvas, offsetX, offSetY);
  console.log(ctx);
  ctx.restore();
  console.log(ctx);
  function indexAccess (i, j) {
    const NUM_CHANNELS = 4;
    return j * dimX * NUM_CHANNELS + i * NUM_CHANNELS;
  }

  function highlightPrototype (e) {
    let mousePos = getMousePos(canvas, e);
    let posX = mousePos.x;
    let posY = mousePos.y;
    //console.log(posX);
    //console.log(posY);
    //console.log(mousePos.col);
    ctx.fillStyle = 'black';
    // console.log(posX + ' ' + posY);
    ctx.fillRect(posX, posY, 1, 1);
  }
  canvas.addEventListener('mousemove', highlightPrototype, false);

  function getMousePos (canvas, evt) {
    let x = evt.clientX;
    let y = evt.clientY;
    //let pixeldata = ctx.getImageData(x, y, 1, 1);
    //let col = pixeldata.data;
    //console.log(col);
    // let color = 'rgba(' +
    //  col[0] + ',' + col[1] + ',' +
    //   col[2] + ',' + col[3] + ')';
    let rect = canvas.getBoundingClientRect();
    return {
      x: (evt.clientX - rect.left) / (rect.right - rect.left) * canvas.width,
      y: (evt.clientY - rect.top) / (rect.bottom - rect.top) * canvas.height,
      // col: color
    };
  }
};

export { drawSegmentationMap };
