import store from '../store';

var drawSegmentationMap = function (dimensions) {
  'use strict';
  let ringData = store.state.currentRingData;
  let dimX = dimensions['x'];
  let dimY = dimensions['y'];
  let p = 5;
  const canvas = document.getElementById('segMap');
  let ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  let canWidth = canvas.width * 0.9;
  let canHeight = canvas.height * 0.9;
  let rectSize = 0;
  if (dimX >= dimY) {
    rectSize = canWidth / dimX;
  } else {
    rectSize = canHeight / dimY;
  }
  function drawMap () {
    for (let x = 0; x <= canWidth; x += rectSize) {
      ctx.moveTo(x + p, p);
      ctx.lineTo(x + p, canHeight + p);
    }
    for (let y = 0; y <= canHeight; y += rectSize) {
      ctx.moveTo(p, p + y);
      ctx.lineTo(canWidth + p, y + p);
    }

    ctx.strokeStyle = 'black';
    ctx.stroke();
  }
  drawMap();
};

export { drawSegmentationMap };
