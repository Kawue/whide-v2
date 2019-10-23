import store from '../store';
import * as d3 from 'd3';

var drawSegmentationMap = function (dimensions) {
  'use strict';
  let ringData = store.state.currentRingData;
  const dimX = dimensions['x'] + 1;
  const dimY = dimensions['y'] + 1;
  let uInt8IndexSample = {};
  let offsetX = 0;
  let offsetY = 0;

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
  let defaultImageData = copyImageData(ctx, imageData);

  let scalor = 1;

  if (dimX >= dimY) {
    scalor = Math.floor(canvas.width / dimX);
  } else {
    scalor = Math.floor(canvas.height / dimY);
  }
  let first = true;
  let selectedPrototype;
  store.commit('SET_SCALOR', scalor);
  ctx.save();
  ctx.scale(scalor, scalor);
  offsetX = (canvas.width - (newCanvas.width * scalor)) / 4;
  offsetY = (canvas.height - (newCanvas.height * scalor)) / 4;
  ctx.drawImage(newCanvas, offsetX, offsetY);
  canvas.addEventListener('mousemove', highlightPrototype, false);
  ctx.restore();

  function indexAccess (i, j) {
    const NUM_CHANNELS = 4;
    return j * dimX * NUM_CHANNELS + i * NUM_CHANNELS;
  }

  function highlightPrototype (e) {
    let mousePos = getMousePos(canvas, e);
    let currentCTX = canvas.getContext('2d');
    // console.log(currentCTX);
    let posX = parseInt((mousePos.x - offsetX) / scalor);
    let posY = parseInt((mousePos.y - offsetY) / scalor);
    // let posX = parseInt(mousePos.x);
    // let posY = parseInt(mousePos.y);

    ctx.fillStyle = 'black';
    let posXY = [posX, posY];
    Object.keys(ringData).map((protoKey) => {
      ringData[protoKey].pixels.map((pixelXY) => {
        if (pixelXY[0] === posXY[0] && pixelXY[1] === posXY[1]) {
          let prototypeSample = uInt8IndexSample[protoKey]['indizes'];
          if (first) {
            selectedPrototype = protoKey;
            first = false;
            prototypeSample.forEach(function (index) {
              data[index] = 255;
              data[index + 1] = 255;
              data[index + 2] = 255;
              data[index + 3] = 255;
            });
            draw(imageData);
          }
          if (selectedPrototype !== protoKey) {
            selectedPrototype = protoKey;
            let newImageData = copyImageData(ctx, defaultImageData);
            let newdata = newImageData.data;
            prototypeSample.forEach(function (index) {
              newdata[index] = 255;
              newdata[index + 1] = 255;
              newdata[index + 2] = 255;
              newdata[index + 3] = 255;
            });
            draw(newImageData);
          }
          ctx.fillStyle = 'green';
        }
      });
    });
    ctx.fillRect(posX, posY, 1, 1);
  }

  function getMousePos (canvas, evt) {
    let x = evt.clientX;
    let y = evt.clientY;
    // let pixeldata = ctx.getImageData(x, y, 1, 1);
    // let col = pixeldata.data;
    // console.log(col);
    // let color = 'rgba(' +
    //  col[0] + ',' + col[1] + ',' +
    //   col[2] + ',' + col[3] + ')';
    let rect = canvas.getBoundingClientRect();
    return {
      x: (evt.clientX - rect.left) / (rect.right - rect.left) * canvas.width,
      y: (evt.clientY - rect.top) / (rect.bottom - rect.top) * canvas.height
      // col: color
    };
  }
  function draw (givenImagedata) {
    let newCanvas = document.createElement('canvas');
    newCanvas.width = givenImagedata.width;
    newCanvas.height = givenImagedata.height;
    newCanvas.getContext('2d').putImageData(givenImagedata, 0, 0);
    ctx.save();
    ctx.scale(scalor, scalor);
    offsetX = (canvas.width - (newCanvas.width * scalor)) / 4;
    offsetY = (canvas.height - (newCanvas.height * scalor)) / 4;
    ctx.drawImage(newCanvas, offsetX, offsetY);
    ctx.restore();
  }
  function copyImageData (ctx, src) {
    var dst = ctx.createImageData(src.width, src.height);
    dst.data.set(src.data);
    return dst;
  }
};

export { drawSegmentationMap };
