class mzService {
  /*
  normalizes the intensities of all coeffictiens  in the ring between 0 and 1
  @params:
  coefficients: all coefficients to the mz value per prototype in the current ring
   */
  normalizeCoefficients (coefficients) {
    let max = Number.MIN_SAFE_INTEGER;
    let min = Number.MAX_SAFE_INTEGER;
    let newCoeff = {};
    // find min and max over all coefficients
    let currentPrototypes = Object.keys(coefficients);
    currentPrototypes.forEach(function (pro) {
      let i;

      for (i = 0; i < coefficients[pro].length; i++) {
        if (coefficients[pro][i] < min) {
          min = coefficients[pro][i];
        }
        if (coefficients[pro][i] > max) {
          max = coefficients[pro][i];
        }
      }
    });

    // normalize them between 0 and 1
    currentPrototypes.forEach(function (norPro) {
      let k;
      let newValues = [];
      for (k = 0; k < coefficients[norPro].length; k++) {
        let val = ((coefficients[norPro][k] - min) / (max - min));
        newValues.push(val);
      }
      newCoeff[norPro] = newValues;
    });

    return newCoeff;
  }
}
export default mzService;
