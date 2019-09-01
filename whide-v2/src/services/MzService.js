function getObjectKeysAlphabetical (data, asc) {
  var keys = []; var key
  for (key in data) {
    if (data.hasOwnProperty(key)) {
      keys.push(key)
    }
  }
  if (!asc) {
    keys.sort((a, b) => a - b)
  } else {
    keys.sort((a, b) => b - a)
  }
  return keys
}

class MzService {
  sortMzList (data, asc) {
    var keys = getObjectKeysAlphabetical(data, asc)
    var i = 0
    var key = null
    var val = null
    var dict = {}
    for (i = 0; i < keys.length; i++) {
      key = keys[i]
      val = data[key]
      dict[key] = val
    }
    return dict
  }
}
export default MzService
