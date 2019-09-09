import * as d3 from 'd3'
import store from '../store'

var createColorWheel = function (protoId) {
  'use strict'
  /* var pos = []
  Object.keys(protoId).forEach(function (id) {
    console.log(protoId[id]['currentPos'])
    pos.push(protoId[id]['currentPos'])
  })

   */
  var DEGREES_PER_RADIAN = 180 / Math.PI

  var canvas = document.getElementById('colorwheelCanvas')
  var context = canvas.getContext('2d')

  var bgImage = context.createImageData(canvas.width, canvas.height)

  var halfWidth = Math.floor(bgImage.width / 2)
  var halfHeight = Math.floor(bgImage.height / 2)

  var radius = Math.min(halfWidth, halfHeight)
  var radiusSquared = radius * radius

  renderColorWheel(bgImage)

  let posDict = {}

  context.clearRect(0, 0, canvas.width, canvas.height)
  context.putImageData(bgImage, 0, 0)

  Object.keys(protoId).forEach(function (id) {
    let posColor = null
    posColor = renderColorMarker((Object.values(protoId[id])), id)
    posDict[id] = {
      color: posColor,
      position: Object.values(protoId[id])
    }
  })
  // store.commit('SET_POS_COLOR', posDict)

  function renderColorMarker (position, id) {
    var markerRadius = 6
    var x = position[0][0]
    var y = position[0][1]
    var i = parseInt(x * 100 + halfWidth)
    var j = parseInt(y * 100 + halfHeight)
    let canvas = document.getElementById('colorwheelCanvas')
    let ctx = canvas.getContext('2d')
    let ctxData = ctx.getImageData(0, 0, canvas.width, canvas.height).data
    var NUM_CHANNELS = 4
    var rowByteOffset = j * canvas.width * NUM_CHANNELS
    var colByteOffset = i * NUM_CHANNELS
    var pixelByteOffset = rowByteOffset + colByteOffset
    var posColor = ctxData.slice(pixelByteOffset, pixelByteOffset + 4)

    var colorOfPos = 'rgba(' + posColor[0].toString() + ',' + posColor[1].toString() + ',' + posColor[2].toString() + ',' + posColor[3].toString() + ')'
    d3.select('#colorwheelContainer')
      .append('circle')
      .attr('cx', i)
      .attr('cy', j)
      .attr('r', markerRadius)
      .style('fill', colorOfPos)
      .on('click', function () {
        let dict = {}
        let protoDict = {}
        let pos = {
          startPos: position,
          currentPos: position
        }
        dict[colorOfPos] = pos
        protoDict[id] = dict
        protoId[id]['id'] = id
        protoId[id]['color'] = colorOfPos
        store.commit('SET_CHOOSED_BOOKMARKS', protoId[id])
      })
    return colorOfPos
  }

  function renderColorWheel (image) {
    var i, j
    for (j = 0; j < image.height; j++) {
      for (i = 0; i < image.width; i++) {
        var x = i - halfWidth
        var y = j - halfHeight

        var distanceFromOriginSquared = x * x + y * y
        var withinDisc = (distanceFromOriginSquared <= radiusSquared)
        if (withinDisc) {
          var angleInDegrees = DEGREES_PER_RADIAN * (Math.atan2(y, x) + Math.PI)
          var distanceFromOrigin = Math.sqrt(distanceFromOriginSquared)

          var color = d3.hsl(angleInDegrees, (distanceFromOrigin / radius), 0.5).rgb()
          setPixelColor(image, i, j, color, 200)
        }
      }
    }

    let colorwheelContainer = d3.select('#colorwheelCanvas').select(function () { return this.parentNode })
    let offset = parseInt(d3.select('#colorwheelCanvas').style('margin-left')) + parseInt(d3.select('.trigger').style('width'))
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
      .style('z-index', 101)

    return color
  }

  function setPixelColor (image, x, y, color, alpha) {
    alpha = (alpha !== undefined ? alpha : 255)

    var NUM_CHANNELS = 4
    var rowByteOffset = y * image.width * NUM_CHANNELS
    var colByteOffset = x * NUM_CHANNELS
    var pixelByteOffset = rowByteOffset + colByteOffset

    image.data[pixelByteOffset + 0] = color.r
    image.data[pixelByteOffset + 1] = color.g
    image.data[pixelByteOffset + 2] = color.b
    image.data[pixelByteOffset + 3] = alpha
    // console.log(image.data[pixelByteOffset + 0])
  }
}

var moebiustransformation = function (ringPos, direction) {
  let FOCUS_MOVE_SPEED = 0.05
  let protoDict = {}
  Object.keys(ringPos).forEach(function (prototype) {
    // console.log(ringPos[prototype]['currentPos'][1])
    // console.log(ringPos[prototype]['currentPos'][1])
    // console.log(ringPos[prototype]['currentPos'][1] + FOCUS_MOVE_SPEED * direction['x'])
    let newX = ringPos[prototype]['currentPos'][0] + FOCUS_MOVE_SPEED * direction['x']
    let newY = ringPos[prototype]['currentPos'][1] + FOCUS_MOVE_SPEED * direction['y']
    let proPos = {
      'currentPos': [newX, newY],
      'startPos': ringPos[prototype]['startPos']
    }
    protoDict[prototype] = proPos
    // console.log(newX)
    // console.log(newY)
  })
  return protoDict
}
export { createColorWheel, moebiustransformation }
