import * as d3 from 'd3';
import store from '../store';

var createColorWheel = function (protoId, rotation = 0, posSwitcher = 0, ringIndex = 0) {
  let firstIdx = store.state.lastPrototypeIndex;
  const DEGREES_PER_RADIAN = 180 / Math.PI;
  const canvas = document.getElementById('colorwheelCanvas');
  const context = canvas.getContext('2d');

  const bgImage = context.createImageData(canvas.width, canvas.height);

  const halfWidth = Math.floor(bgImage.width / 2);
  const halfHeight = Math.floor(bgImage.height / 2);

  const radius = Math.min(halfWidth, halfHeight);
  const radiusSquared = radius * radius;
  let multiplierForPosPosition;
  if (ringIndex === 0) {
    multiplierForPosPosition = 100;
  } else if (ringIndex === 1) {
    multiplierForPosPosition = 120;
  } else if (ringIndex >= 2) {
    multiplierForPosPosition = 140;
  }

  renderColorWheel(bgImage);

  let posDict = {};

  context.clearRect(0, 0, canvas.width, canvas.height);
  context.putImageData(bgImage, 0, 0);

  const idList = Object.keys(protoId);
  const numberOfPrototypes = idList.length;
  Object.keys(protoId).forEach(function (id) {
    let idNumber = parseInt(id.replace(/'/g, '').split(/(\d+)/).filter(Boolean)[1]);
    let newIdNumber;
    if (idNumber + (posSwitcher % numberOfPrototypes) >= numberOfPrototypes + firstIdx) {
      newIdNumber = idNumber + (posSwitcher % numberOfPrototypes) - (numberOfPrototypes);
    } else {
      newIdNumber = idNumber + (posSwitcher % numberOfPrototypes);
    }
    // let newIdNumber = (idNumber + posSwitcher) % (numberOfPrototypes);
    let newPrototypeString = 'prototyp' + newIdNumber;
    let posColor = renderColorMarker((Object.values(protoId[newPrototypeString])), id);
    posDict[id] = {
      color: posColor,
      position: Object.values(protoId[id])
    };
    let idWithColor = {};
    idWithColor[id] = posColor;
    store.commit('ADD_COLOR_TO_FULL_DATA', idWithColor);
  });

  store.commit('SET_POS_COLOR', posDict);
  store.commit('SET_COLORS_READY', true);

  function renderColorMarker (position, id) {
    const markerRadius = 6;
    const x = position[0][0];
    const y = position[0][1];
    const i = parseInt(x * multiplierForPosPosition + halfWidth);
    const j = parseInt(y * multiplierForPosPosition + halfHeight);
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
        store.commit('SET_CHOOSED_BOOKMARK', id);
      })
      .on('mouseover', function () {
        store.commit('SET_CURRENT_HIGHLIGHTED_PROTOTYPE', id);
        store.commit('HIGHLIGHT_PROTOTYPE_OUTSIDE');
      })
      .on('mouseout', function () {
        store.commit('SET_CURRENT_HIGHLIGHTED_PROTOTYPE', null);
        store.commit('HIGHLIGHT_PROTOTYPE_OUTSIDE');
      });
    return colorOfPos;
  }

  function renderColorWheel (image) {
    /* let angleScaler180 = d3.scaleLinear()
      .domain([0, 180])
      .range([0, 1]);
    let angeleScaler360 = d3.scaleLinear()
      .domain([180, 360])
      .range([1, 0]);

    */

    let i, j;
    for (j = 0; j < image.height; j++) {
      for (i = 0; i < image.width; i++) {
        const x = i - halfWidth;
        const y = j - halfHeight;

        const distanceFromOriginSquared = x * x + y * y;
        const withinDisc = (distanceFromOriginSquared <= radiusSquared);
        if (withinDisc) {
          const angleInDegrees = DEGREES_PER_RADIAN * (Math.atan2(y, x) + Math.PI + rotation);
          const distanceFromOrigin = Math.sqrt(distanceFromOriginSquared);

          /*
          let hsl = d3.hsl(angleInDegrees, (distanceFromOrigin / radius), 0.5);
          let rainbow = d3.scaleSequential(hsl);
          let colorString = {};
          if (angleInDegrees >= 180) {
            colorString = d3.color(d3.interpolateCool(angeleScaler360(angleInDegrees))).rgb();
          } else {
            colorString = d3.color(d3.interpolateCool(angleScaler180(angleInDegrees))).rgb();
          }

          var matchColors = /rgb\((\d{1,3}), (\d{1,3}), (\d{1,3})\)/;
          var match = matchColors.exec(colorString);
          let newColor = {
            r: match[1],
            g: match[2],
            b: match[3],
            opacity: 1
          };

 */

          // needs to be var with let color is not defined ....?
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

    image.data[pixelByteOffset] = color.r;
    image.data[pixelByteOffset + 1] = color.g;
    image.data[pixelByteOffset + 2] = color.b;
    image.data[pixelByteOffset + 3] = alpha;
    // console.log(image.data[pixelByteOffset + 0])
  }
};

var moebiustransformation = function (ringPos, direction) {
  const FOCUS_MOVE_SPEED = 0.06;
  const RECTIFICATION_FACTOR = 0.4;
  const RECTIFICATION_FACTOR_X_2 = RECTIFICATION_FACTOR * 2;
  const RECTIFICATION_FACTOR_X_4 = RECTIFICATION_FACTOR * RECTIFICATION_FACTOR * 4;
  // let canvas = document.getElementById('colorwheelCanvas');
  // let context = canvas.getContext('2d');

  // let bgImage = context.createImageData(canvas.width, canvas.height);

  // let halfWidth = Math.floor(bgImage.width / 2);
  // let halfHeight = Math.floor(bgImage.height / 2);

  let focus = { 'x': 0, 'y': 0 };

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
  /* let offsetCenter;
  if (halfWidth > halfHeight) {
    offsetCenter = halfHeight;
  } else {
    offsetCenter = halfWidth;
  }

   */
  // focus coordinates
  let ar = focus['x'];
  let ai = focus['y'];

  let fR = Number;
  let fS = Number;

  let fA = Number; let fB = Number; let fC = Number; let fD = Number; let fQ = Number;
  let z0r = Number; let z0i = Number; let z1r = Number; let z1i = Number;

  // let fScale = 0.99;
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
    fD = ai * z0r - ar * z0i;
    fQ = fB * fB + fD * fD;

    z1r = (fA * fB + fC * fD) / fQ;
    z1i = (fC * fB - fA * fD) / fQ;

    fR = z1r * z1r + z1i * z1i;

    if (fR === 0) { fS = 1.0; } else {
      fS = 1 / (RECTIFICATION_FACTOR_X_2 * fR) * (fR - 1 + Math.sqrt(fR * fR - 2 * fR + 1 + RECTIFICATION_FACTOR_X_4 * fR));
    }
    protoDict[prototype] = {
      'currentPos': [ z1r, z1i ],
      'startPos': ringPos[prototype]['startPos']
    };
  });

  return protoDict;
};
export { createColorWheel, moebiustransformation };
