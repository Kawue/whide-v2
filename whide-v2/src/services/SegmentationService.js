import store from '../store';
import * as d3 from 'd3';

var drawSegmentationMap = function (dimensions) {
  const canvas = document.getElementById('segMap');
  const context = canvas.getContext('2d');
  const r = 15;
  console.log(canvas.width);
  console.log(canvas.height);
  console.log(dimensions);

  d3.select(canvas).call(d3.zoom()
    .scaleExtent([0.7, 2])
    .on('zoom', () => zoomed(d3.event.transform)));

  function zoomed (transform) {
    context.save();
    context.clearRect(0, 0, canvas.width, canvas.height);
    context.translate(transform.x, transform.y);
    context.scale(transform.k, transform.k);
    context.beginPath();
    context.moveTo(100 + r, 70);
    context.arc(100, 70, r, 0, 2 * Math.PI);
    context.fill();
    context.restore();
  }

  zoomed(d3.zoomIdentity);
};
export { drawSegmentationMap };
