class mzService {
  normalizeCoefficients (coefficients) {
    let max = Number.MIN_SAFE_INTEGER;
    let min = Number.MAX_SAFE_INTEGER;
    let newCoeff = {};
    /*
    coefficients.forEach(function (pro) {
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

     */

    for (let pro in coefficients) {
      let i;
      for (i = 0; i < coefficients[pro].length; i++) {
        if (coefficients[pro][i] < min) {
          min = coefficients[pro][i];
        }
        if (coefficients[pro][i] > max) {
          max = coefficients[pro][i];
        }
      }
    }
    /*
    coefficients.forEach(function (norPro) {
      let k;
      let newValues = [];
      for (k = 0; k < coefficients[norPro].length; k++) {
        let val = ((coefficients[norPro][k] - min) / (max - min));
        newValues.push(val);
      }
      newCoeff[norPro] = newValues;
    });

     */

    for (let norPro in coefficients) {
      let k;
      let newValues = [];
      for (k = 0; k < coefficients[norPro].length; k++) {
        let val = ((coefficients[norPro][k] - min) / (max - min));
        newValues.push(val);
      }
      newCoeff[norPro] = newValues;
    }
    return newCoeff;
  }
  roundMzValues (mzs) {
    let roundedMzs = [];
    mzs.forEach(function (mz) {
      roundedMzs.push(parseFloat(mz.toFixed(3)));
    });
    return roundedMzs;
  }
}
export default mzService;
