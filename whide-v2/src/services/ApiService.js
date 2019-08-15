import data from '../../../backend/data'

class ApiService {
  fetchData () {
    console.log('fetching data')
    return data
  }
}

export default ApiService
