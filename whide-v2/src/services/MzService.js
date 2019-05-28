class MzService {
  sortMzList (data, asc) {
    if (asc) {
      return data.sort((a, b) => a - b)
    } else {
      return data.sort((a, b) => b - a)
    }
  }
}
export default MzService
