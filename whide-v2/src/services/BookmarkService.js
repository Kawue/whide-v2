class BookmarkService {
  createBookmarkObject (color) {
    return {
      bar: {
        backgroundColor: color,
        title: 'kann Ich lesen',
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['2011年', '2012年']
        },
        toolbox: {
          show: true,
          feature: {
            mark: { show: true },
            dataView: { show: true, readOnly: false },
            magicType: { show: true, type: ['line', 'bar'] },
            restore: { show: true },
            saveAsImage: { show: true }
          }
        },
        calculable: true,
        xAxis: [
          {
            type: 'value',
            boundaryGap: [0, 0.5]
          }
        ],
        yAxis: [
          {
            type: 'category',
            data: ['1', '2', '3', '4', '5']
          }
        ],
        data: [5, 10, 20, 30, 40]
      }
    }
  }
}
export default BookmarkService
