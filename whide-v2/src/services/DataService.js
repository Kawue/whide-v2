import store from '../store';

class DataService {
  setData (ringIdx, rings, coefficients, mzs) {
    let ringData = {};
    Object.keys(store.state.rings[store.state.ringIdx]).forEach(function (prototype) {
      let prototypeData = {};
      let pixelIds = [];
      Object.values(store.state.rings[store.state.ringIdx][prototype]['pixel']).forEach(function (pixelId) {
        pixelIds.push(pixelId);
      });
      let pixelPos = [];
      pixelIds.forEach(function (pixel) {
        pixelPos.push(store.state.pixels[pixel]['pos']);
      });
      prototypeData['pixels'] = pixelPos;
      prototypeData['currentPos'] = store.state.rings[store.state.ringIdx][prototype]['pos'];
      prototypeData['startPos'] = store.state.rings[store.state.ringIdx][prototype]['pos'];
      prototypeData['id'] = prototype;
      prototypeData['data'] = store.state.ringCoefficients[prototype];
      prototypeData['mz'] = store.state.mzList.mzItems;
      ringData[prototype] = prototypeData;
    });
    store.commit('SET_DATA_READY', true);
    return ringData;
  }
}
export default DataService;
