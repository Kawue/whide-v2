import data from '../../../backend/data';

class ApiService {
  async fetchData () {
    return data;
  }
}

export default ApiService;
