import store from '../store';
import * as d3 from 'd3';

var drawSegmentationMap = function (dimensions) {
  const ringData = store.state.currentRingData;
  const dimX = dimensions['x'] + 1;
  const dimY = dimensions['y'] + 1;
  let uInt8IndexSample = {};
  const backGroundcolor = [64, 64, 64, 255];
  const backGroundColorRGBA = 'rgba(64,64,64,255)';
  let scalor = 1;
  let defaultScalor;
  let transformX = 0;
  let transformY = 0;
  let selectedPrototype;
  let first = true;
  let outside = Boolean;
  let outsideOnce = false;

  let colorIndex = 1;
  let colorDataDict = {};

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
      const colorOfIndex = getColor(colorIndex);
      colorIndex += 1;
      const colorOfIndexRGB = colorOfIndex.substring(colorOfIndex.indexOf('(') + 1, colorOfIndex.lastIndexOf(')')).split(/,\s*/);
      colorDataDict[colorOfIndex] = {
        'id': prototype,
        'indize': indize,
        'rgb': colorOfIndexRGB
      };
    });
    let dict = {};
    dict['indizes'] = indizes;
    dict['color'] = colors;
    uInt8IndexSample[prototype] = dict;
  });
  const canvas = document.getElementById('segMap');
  const virtCanvas = document.getElementById('virtCanvas');
  const regex = /[0-9]*\.?[0-9]+(px|%)?/i;
  const w = canvas.style.width.match(regex);
  const h = canvas.style.height.match(regex);
  const computedWidth = (w[0] * document.documentElement.clientWidth) / 100;
  const computedHeight = (h[0] * document.documentElement.clientHeight) / 100;
  canvas.width = computedWidth;
  canvas.height = computedHeight;
  virtCanvas.width = computedWidth;
  virtCanvas.height = computedHeight;

  const ctx = canvas.getContext('2d');
  const virtCtx = virtCanvas.getContext('2d');
  ctx.webkitImageSmoothingEnabled = false;
  ctx.imageSmoothingEnabled = false;
  virtCtx.webkitImageSmoothingEnabled = false;
  virtCtx.imageSmoothingEnabled = false;

  let imageData = ctx.createImageData(dimX, dimY);
  let data = imageData.data;
  let virtImageData = virtCtx.createImageData(dimX, dimY);
  let virtData = virtImageData.data;

  // color every pixel of every prototype for View
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

  const defaultImageData = copyImageData(ctx, imageData);
  if (dimX >= dimY) {
    scalor = Math.floor(canvas.width / dimX);
    defaultScalor = scalor;
  } else {
    scalor = Math.floor(canvas.height / dimY);
    defaultScalor = scalor;
  }

  // draw virtCanvas
  Object.keys(colorDataDict).forEach(function (pixel) {
    const dict = colorDataDict[pixel];
    virtData[dict.indize] = dict.rgb[0];
    virtData[dict.indize + 1] = dict.rgb[1];
    virtData[dict.indize + 2] = dict.rgb[2];
    virtData[dict.indize + 3] = 255;
  });
  draw(virtImageData, virtCtx);

  console.log(Object.keys(colorDataDict));
  virtCanvas.addEventListener('mousemove', test, false);
  function test (e) {
    let mouse = getMousePos(virtCanvas, e);
    let r = mouse.col[0];
    let g = mouse.col[1];
    let b = mouse.col[2];
    let rgb = 'rgb(' + r + ', ' + g + ', ' + b + ')';
    if (rgb !== 'rgb(0,0,0)') {
      console.log(rgb);
      console.log(colorDataDict[rgb]);
    }
  }
  draw(imageData, ctx);
  // add highlight and zoom
  canvas.addEventListener('mousemove', highlightPrototype, false);
  d3.select(virtCanvas).call(d3.zoom()
    .scaleExtent([0.3, 2])
    .on('zoom', () => zoomed(d3.event.transform)));

  function zoomed (transform) {
    transformX = transform.x;
    transformY = transform.y;
    // scalor = defaultScalor;
    // scalor = scalor * transform.k;

    // viewingCanvas
    ctx.save();
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.translate(transform.x, transform.y);
    ctx.scale(transform.k, transform.k);
    draw(imageData, ctx);
    ctx.restore();

    // virtuellCanvas
    virtCtx.save();
    virtCtx.clearRect(0, 0, virtCanvas.width, virtCanvas.height);
    virtCtx.translate(transform.x, transform.y);
    virtCtx.scale(transform.k, transform.k);
    draw(virtImageData, virtCtx);
    virtCtx.restore();
  }

  zoomed(d3.zoomIdentity);

  function draw (givenImageData, context) {
    let newCanvas = document.createElement('canvas');
    newCanvas.width = givenImageData.width;
    newCanvas.height = givenImageData.height;
    newCanvas.getContext('2d').putImageData(givenImageData, 0, 0);
    context.save();
    context.scale(scalor, scalor);
    // context.fillStyle = backGroundColorRGBA;
    // context.fillRect(0, 0, canvas.width, canvas.height);
    context.drawImage(newCanvas, 0, 0);
    context.restore();
    newCanvas.remove();
  }

  function highlightPrototype (e) {
    // ctx.save();
    let mousePos = getMousePos(canvas, e);
    let posX = parseInt((mousePos.x / scalor));
    let posY = parseInt((mousePos.y / scalor));
    // console.log(posX);
    // console.log(posY);
    ctx.fillStyle = 'red';
    ctx.fillRect(posX, posY, 1, 1);

    let currentColor = mousePos.col;
    outside = currentColor[0] === backGroundcolor[0] && currentColor[1] === backGroundcolor[1] &&
      currentColor[2] === backGroundcolor[2] && currentColor[3] === backGroundcolor[3];
    if (outside) {
      if (!outsideOnce) {
        outsideOnce = true;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        store.commit('SET_CURRENT_HIGHLIGHTED_PROTOTYPE', null);
        draw(defaultImageData, ctx);
        ctx.restore();
      }
    } else {
      ctx.save();
      ctx.beginPath();
      ctx.rect(0, 0, 10, 10);
      ctx.fillStyle = 'blue';
      ctx.fill();
      ctx.restore();
      outsideOnce = false;
      // let posX = parseInt((mousePos.x / scalor) - transformX);
      // let posY = parseInt((mousePos.y / scalor) - transformY);
      let posXY = [posX, posY];
      Object.keys(ringData).map((protoKey) => {
        ringData[protoKey].pixels.map((pixelXY) => {
          if (pixelXY[0] === posXY[0] && pixelXY[1] === posXY[1]) {
            ctx.fillStyle = 'green';
            ctx.fillRect(posXY[0], posXY[1], 4, 4);
            /* let prototypeSample = uInt8IndexSample[protoKey]['indizes'];
            if (first) {
              selectedPrototype = protoKey;
              store.commit('SET_CURRENT_HIGHLIGHTED_PROTOTYPE', selectedPrototype);
              first = false;
              prototypeSample.forEach(function (index) {
                data[index] = 255;
                data[index + 1] = 255;
                data[index + 2] = 255;
                data[index + 3] = 255;
              });
              ctx.clearRect(0, 0, canvas.width, canvas.height);
              draw(defaultImageData, false);
              ctx.restore();
            }
            if (selectedPrototype !== protoKey) {
              selectedPrototype = protoKey;
              store.commit('SET_CURRENT_HIGHLIGHTED_PROTOTYPE', selectedPrototype);
              ctx.clearRect(0, 0, canvas.width, canvas.height);
              let newImageData = copyImageData(ctx, defaultImageData);
              let newdata = newImageData.data;
              prototypeSample.forEach(function (index) {
                newdata[index] = 255;
                newdata[index + 1] = 255;
                newdata[index + 2] = 255;
                newdata[index + 3] = 255;
              });
              draw(newImageData);
              ctx.restore();
            }

             */
          }
        });
      });
    }
  }

  function getMousePos (canvas, evt) {
    let rect = canvas.getBoundingClientRect();
    let xCord = (evt.clientX - rect.left) / (rect.right - rect.left) * canvas.width;
    let yCord = (evt.clientY - rect.top) / (rect.bottom - rect.top) * canvas.height;
    let pixeldata = ctx.getImageData(xCord, yCord, 1, 1);
    let col = pixeldata.data;
    return {
      x: xCord,
      y: yCord,
      col: col
    };
  }

  function indexAccess (i, j) {
    const NUM_CHANNELS = 4;
    return j * dimX * NUM_CHANNELS + i * NUM_CHANNELS;
  }

  function copyImageData (ctx, src) {
    let dst = ctx.createImageData(src.width, src.height);
    dst.data.set(src.data);
    return dst;
  }

  function colorToHex (col) {
    var hex = Number(col).toString(16);
    if (hex.length < 2) {
      hex = '0' + hex;
    }
    return hex;
  }

  function fullColorToHex (r, g, b) {
    let red = colorToHex(r);
    let green = colorToHex(g);
    let blue = colorToHex(b);
    return red + green + blue;
  }

  function getColor (index) {
    return d3.rgb(
      (index & 0b111111110000000000000000) >> 16,
      (index & 0b000000001111111100000000) >> 8,
      (index & 0b000000000000000011111111))
      .toString();
  }
};
export { drawSegmentationMap };
