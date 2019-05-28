import data from '../../../python-scripts/data'

class ApiService {
  fetchData () {
    console.log('fetching data')
    return data
  }
}

export default ApiService
