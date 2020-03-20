import * as d3 from 'd3';
import store from '../store';

/*
Creates the colorwheel, and put the prototypes on it
@params:
  rotation is a value between 1 and 0 for the rotation of the farbscala
  posswitcher is a number from 0 to number of prototypes for the amount of switched positions in one way
  ringIndex is the index of the current ring for better visualisation on the wheel
 */
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

  // for better postioning of the prototypes on the wheel we set a multiplier
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

  let allPrototypeColors = {};
  const idList = Object.keys(protoId);
  const numberOfPrototypes = idList.length;
  /*
  for each prototype the will be calculated with respect to the number of posSwitcher
  */
  Object.keys(protoId).forEach(function (id) {
    let idNumber = parseInt(id.replace(/'/g, '').split(/(\d+)/).filter(Boolean)[1]);
    let newIdNumber;
    if (idNumber + (posSwitcher % numberOfPrototypes) >= numberOfPrototypes + firstIdx) {
      newIdNumber = idNumber + (posSwitcher % numberOfPrototypes) - (numberOfPrototypes);
    } else {
      newIdNumber = idNumber + (posSwitcher % numberOfPrototypes);
    }
    let newPrototypeString = 'prototyp' + newIdNumber;
    // calculate color for prototype
    let posColor = renderColorMarker((Object.values(protoId[newPrototypeString])), id);
    posDict[id] = {
      color: posColor,
      position: Object.values(protoId[id])
    };
    allPrototypeColors[id] = posColor;
  });
  store.commit('ADD_COLOR_TO_FULL_DATA', allPrototypeColors);
  store.commit('SET_POS_COLOR', posDict);
  store.commit('SET_COLORS_READY', true);
  return allPrototypeColors;

  /*
  puts prototype to his position on colorwheel
  @params:
  postion: position from prototype
  id: id from prototype
   */
  function renderColorMarker (position, id) {
    const markerRadius = 6;
    const x = position[0][0];
    const y = position[0][1];
    // i and j are the new coordinates on colorwheel
    const i = parseInt(x * multiplierForPosPosition + halfWidth);
    const j = parseInt(y * multiplierForPosPosition + halfHeight);
    let canvas = document.getElementById('colorwheelCanvas');
    let ctx = canvas.getContext('2d');
    let ctxData = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
    // number of colorchannels and the offestes in the imagedata object
    const NUM_CHANNELS = 4;
    const rowByteOffset = j * canvas.width * NUM_CHANNELS;
    const colByteOffset = i * NUM_CHANNELS;
    const pixelByteOffset = rowByteOffset + colByteOffset;
    const posColor = ctxData.slice(pixelByteOffset, pixelByteOffset + 4);

    let colorOfPos = 'rgba(' + posColor[0].toString() + ',' + posColor[1].toString() + ',' + posColor[2].toString() + ',' + posColor[3].toString() + ')';
    // draw a circle on the radius
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

  /*
  creates the colorwheel
  @params:
  image: empty imagedata object
   */
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

          // sets for every pixel the color of itself
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

  /*
  set the calculated color of the pixel in the imagedata object
  @params:
  image: imagedataObject
  x: postion x on the colorwheel
  y: postion y on the colorwheel
  color: color as an rgb value
  alpha: the alpha value of the color
   */
  function setPixelColor (image, x, y, color, alpha) {
    alpha = (alpha !== undefined ? alpha : 255);

    const NUM_CHANNELS = 4;
    const rowByteOffset = y * image.width * NUM_CHANNELS;
    const colByteOffset = x * NUM_CHANNELS;
    const pixelByteOffset = rowByteOffset + colByteOffset;

    image.data[pixelByteOffset] = color.r;
    image.data[pixelByteOffset + 1] = color.g;
    image.data[pixelByteOffset + 2] = color.b;
    image.data[pixelByteOffset + 3] = alpha;
  }
};
/*
function to apply the moebiustransformation the prototypes
@params:
allPrototyps: all prototyps and there postions
direction: the direction where the points should be transformed exp: (1,0) for right, (0,1) for up, (-1,-1) for left down
 */
var moebiustransformation = function (allPrototyps, direction) {
  const FOCUS_MOVE_SPEED = 0.06;
  let focus;

  /*
  move the focus from the midpoint to the direction
   */
  function moveFocus (x, y) {
    let defaultPoint = {
      'x': 0,
      'y': 0
    };

    let a = defaultPoint['x'] - x;
    let b = defaultPoint['y'] - y;
    let distance = Math.sqrt(a * a + b * b);

    if (distance <= 1) {
      focus = {
        'x': x,
        'y': y
      };
    }
  }

  /*
  moves the focus of the prototypes on the colorwheel with the speed
   */
  moveFocus(FOCUS_MOVE_SPEED * direction['x'], FOCUS_MOVE_SPEED * direction['y']);
  // focus coordinates
  let ar = focus['x'];
  let ai = focus['y'];

  let fA = Number; let fB = Number; let fC = Number; let fD = Number; let fQ = Number;
  let z0r = Number; let z0i = Number; let z1r = Number; let z1i = Number;

  let protoDict = {};
  Object.keys(allPrototyps).forEach(function (prototype) {
    z0r = allPrototyps[prototype]['currentPos'][0];
    z0i = allPrototyps[prototype]['currentPos'][1];

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

    /*
    new Position for each prototype after moebiusTransfromation
     */
    protoDict[prototype] = {
      'currentPos': [ z1r, z1i ],
      'startPos': allPrototyps[prototype]['startPos']
    };
  });

  return protoDict;
};
export { createColorWheel, moebiustransformation };
