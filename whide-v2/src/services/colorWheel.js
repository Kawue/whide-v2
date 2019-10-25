import * as d3 from 'd3';
import store from '../store';

var createColorWheel = function (protoId) {
  'use strict';
  const DEGREES_PER_RADIAN = 180 / Math.PI;
  const canvas = document.getElementById('colorwheelCanvas');
  const context = canvas.getContext('2d');

  const bgImage = context.createImageData(canvas.width, canvas.height);

  const halfWidth = Math.floor(bgImage.width / 2);
  const halfHeight = Math.floor(bgImage.height / 2);

  const radius = Math.min(halfWidth, halfHeight);
  const radiusSquared = radius * radius;

  renderColorWheel(bgImage);

  let posDict = {};

  context.clearRect(0, 0, canvas.width, canvas.height);
  context.putImageData(bgImage, 0, 0);

  Object.keys(protoId).forEach(function (id) {
    let posColor = renderColorMarker((Object.values(protoId[id])), id);
    posDict[id] = {
      color: posColor,
      position: Object.values(protoId[id])
    };
    let idWithColor = {};
    idWithColor[id] = posColor;
    store.commit('SET_COMPLETE_FULL_DATA', idWithColor);
  });
  store.commit('SET_POS_COLOR', posDict);
  store.commit('SET_COLORS_READY', true);

  function renderColorMarker (position, id) {
    const markerRadius = 6;
    const x = position[0][0];
    const y = position[0][1];
    const i = parseInt(x * 100 + halfWidth);
    const j = parseInt(y * 100 + halfHeight);
    let canvas = document.getElementById('colorwheelCanvas');
    let ctx = canvas.getContext('2d');
    let ctxData = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
    const NUM_CHANNELS = 4;
    const rowByteOffset = j * canvas.width * NUM_CHANNELS;
    const colByteOffset = i * NUM_CHANNELS;
    const pixelByteOffset = rowByteOffset + colByteOffset;
    const posColor = ctxData.slice(pixelByteOffset, pixelByteOffset + 4);

    let colorOfPos = 'rgba(' + posColor[0].toString() + ',' + posColor[1].toString() + ',' + posColor[2].toString() + ',' + posColor[3].toString() + ')';
    d3.select('#colorwheelContainer')
      .append('circle')
      .attr('class', id)
      .attr('cx', i)
      .attr('cy', j)
      .attr('r', markerRadius)
      .style('fill', colorOfPos)
      .on('click', function () {
        let dict = {};
        let protoDict = {};
        let pos = {
          startPos: position,
          currentPos: position
        };
        dict[colorOfPos] = pos;
        protoDict[id] = dict;
        protoId[id]['id'] = id;
        protoId[id]['color'] = colorOfPos;
        store.commit('SET_CHOOSED_BOOKMARKS', protoId[id]);
      });
    return colorOfPos;
  }

  function renderColorWheel (image) {
    let i, j;
    for (j = 0; j < image.height; j++) {
      for (i = 0; i < image.width; i++) {
        const x = i - halfWidth;
        const y = j - halfHeight;

        const distanceFromOriginSquared = x * x + y * y;
        const withinDisc = (distanceFromOriginSquared <= radiusSquared);
        if (withinDisc) {
          const angleInDegrees = DEGREES_PER_RADIAN * (Math.atan2(y, x) + Math.PI);
          const distanceFromOrigin = Math.sqrt(distanceFromOriginSquared);

          var color = d3.hsl(angleInDegrees, (distanceFromOrigin / radius), 0.5).rgb();
          setPixelColor(image, i, j, color, 200);
        }
      }
    }

    let colorwheelContainer = d3.select('#colorwheelCanvas').select(function () { return this.parentNode; });
    let offset = parseInt(d3.select('#colorwheelCanvas').style('margin-left')) + parseInt(d3.select('.trigger').style('width'));
    colorwheelContainer.append('svg')
      .attr('id', 'colorwheelContainer')
      .attr('width', canvas.width + 'px')
      .attr('height', canvas.height + 'px')
      .attr('stroke', 'black')
      .attr('stroke-width', 1 + 'px')
      .style('position', 'absolute')
      .style('margin-left', 'auto')
      .style('left', offset + 'px')
      .style('top', 0)
      .style('z-index', 101);

    return color;
  }

  function setPixelColor (image, x, y, color, alpha) {
    alpha = (alpha !== undefined ? alpha : 255);

    var NUM_CHANNELS = 4;
    var rowByteOffset = y * image.width * NUM_CHANNELS;
    var colByteOffset = x * NUM_CHANNELS;
    var pixelByteOffset = rowByteOffset + colByteOffset;

    image.data[pixelByteOffset + 0] = color.r;
    image.data[pixelByteOffset + 1] = color.g;
    image.data[pixelByteOffset + 2] = color.b;
    image.data[pixelByteOffset + 3] = alpha;
    // console.log(image.data[pixelByteOffset + 0])
  }
};

var moebiustransformation = function (ringPos, direction, midPoint) {
  const FOCUS_MOVE_SPEED = 0.05;
  let canvas = document.getElementById('colorwheelCanvas');
  let context = canvas.getContext('2d');

  let bgImage = context.createImageData(canvas.width, canvas.height);

  let halfWidth = Math.floor(bgImage.width / 2);
  let halfHeight = Math.floor(bgImage.height / 2);

  let focus = midPoint;

  function moveFocus (x, y) {
    let defaultPoint = {
      'x': 0,
      'y': 0
    };
    let movedFocus = {
      'x': focus['x'] + x,
      'y': focus['y'] + y
    };

    let a = defaultPoint['x'] - movedFocus['x'];
    let b = defaultPoint['y'] - movedFocus['y'];
    let distance = Math.sqrt(a * a + b * b);

    if (distance <= 1) {
      focus = {
        'x': movedFocus['x'],
        'y': movedFocus['y']
      };
    }
  }

  moveFocus(FOCUS_MOVE_SPEED * direction['x'], FOCUS_MOVE_SPEED * direction['y']);

  // focus coordinates
  let ar = focus['x'];
  let ai = focus['y'];

  let fR = Number;
  let fS = Number;

  let fA = Number; let fB = Number; let fC = Number; let fD = Number; let fQ = Number;
  let z0r = Number; let z0i = Number; let z1r = Number; let z1i = Number;

  let fScale = 0.99;
  let protoDict = {};
  Object.keys(ringPos).forEach(function (prototype) {
    z0r = ringPos[prototype]['currentPos'][0];
    z0i = ringPos[prototype]['currentPos'][1];

    // distance between point.x and focus.x
    fA = z0r - ar;
    // 1 - (point.x * focus.x) - (point.y * focus.y)
    fB = 1 - ar * z0r - ai * z0i;
    // distance between point.y and focus.y
    fC = z0i - ai;
    // f.y * p.x - f.x * p.y
    fD = ai * z0r - ar * z0i;
    fQ = fB * fB + fD * fD;

    z1r = (fA * fB + fC * fD) / fQ;
    z1i = (fC * fB - fA * fD) / fQ;

    fR = z1r * z1r + z1i * z1i;

    if (fR === 0) { fS = 1.0; } else {
      fS = 1 / (2 * fScale * fR) * (fR - 1 + Math.sqrt(fR * fR - 2 * fR + 1 + 4 * fScale * fScale * fR));
    }
    protoDict[prototype] = {
      'currentPos': [ z1r * fS, z1i * fS ],
      'startPos': ringPos[prototype]['startPos']
    };
  });

  store.commit('SET_MOVED_FOCUS', focus);
  return protoDict;
};
export { createColorWheel, moebiustransformation };
