import * as d3 from 'd3'

var createColorWheel = function () {
  'use strict'
  var DEGREES_PER_RADIAN = 180 / Math.PI
  var RADIANS_PER_DEGREE = Math.PI / 180
  var TWO_PI = 2 * Math.PI

  var canvas = document.getElementById('colorwheelCanvas')
  var context = canvas.getContext('2d')

  var bgImage = context.createImageData(canvas.width, canvas.height)

  var halfWidth = Math.floor(bgImage.width / 2)
  var halfHeight = Math.floor(bgImage.height / 2)

  var radius = Math.min(halfWidth, halfHeight)
  var radiusSquared = radius * radius

  renderColorWheel(bgImage)

  context.clearRect(0, 0, canvas.width, canvas.height)
  context.putImageData(bgImage, 0, 0)

  window.colors.forEach(function (it) {
    renderColorMarker(d3.rgb(it))
  })

  var identityFunction = function (d) { return d }
  var htmlFunction = function (d) {
    var hsl = d3.rgb(d).hsl()
    return d + ' : hsl(' + d3.format(hsl.h) + '&deg;, ' + d3.format(hsl.s * 100) + '%, ' + d3.format(hsl.l * 100) + '%)'
  }
  d3.select(document.body).selectAll('.colorDiv').data(window.colors).enter().append('div').attr('class', 'colorDiv').style('background-color', identityFunction).html(htmlFunction)

  function renderColorMarker (color) {
    var markerRadius = 6
    color = color.hsl()
    var hueInRadians = RADIANS_PER_DEGREE * color.h - Math.PI

    var x = Math.cos(hueInRadians) * (color.s) * radius
    var y = Math.sin(hueInRadians) * (color.s) * radius

    var i = x + halfWidth
    var j = y + halfHeight

    context.save()
    context.lineWidth = 1
    context.beginPath()
    context.arc(i, j, markerRadius + 0.5, 0, TWO_PI, false)
    context.strokeStyle = 'black'
    context.stroke()
    context.beginPath()
    context.arc(i, j, markerRadius - 0.5, 0, TWO_PI, false)
    context.strokeStyle = 'white'
    context.stroke()
    context.restore()
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
          setPixelColor(image, i, j, color)
        }
      }
    }
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
  }
}
export { createColorWheel }
