const todayDate = new Date(); // Today's date, to get the metrics for today

const yesterdayDate = new Date(); // We get the metrics from yesterday also to compare and show 
yesterdayDate.setDate(yesterdayDate.getDate() - 1);

const startDate = new Date(); // We get the metrics from the past week until today, which is used to plot the graph 
startDate.setDate(startDate.getDate() - 6);

var metrics = {} // To store the fetched data

// Get the timestamp without milliseconds
var yesterdayTimestamp = Math.floor(yesterdayDate.getTime() / 1000);
var todayTimestamp = Math.floor(todayDate.getTime() / 1000);
var startDateTimestamp = Math.floor(startDate.getTime() / 1000);


function getDateString(date) {
  function pad(n) { return n < 10 ? '0' + n : n }
  return date.getFullYear() + '-'
    + pad(date.getMonth() + 1) + '-'
    + pad(date.getDate())
}

// A helper function for setting the styles of the cards at the top in the dashboard
// after comparing with the previous day's value. This depends in the element passed has the hierachy we assumed
function addStylesForDashboardCard(element, today, yesterday) {
  element.children[1].textContent = (today - yesterday).toString();
  if (yesterday <= today) {
    element.classList.add("text-success");
    element.children[0].classList.add("fa-arrow-up");
  }
  else {
    element.classList.add("text-danger");
    element.children[0].classList.add("fa-arrow-down");
  }

}

window.addEventListener('DOMContentLoaded', () => {
  $.ajax({
    url: '/api/v1/get-metrics/' + window.projectName,
    data: {
      "start_time": startDateTimestamp,
      "end_time": todayTimestamp,
    },
    dataType: 'json',
    type: 'GET',
    success: function (data) {
      console.log("Fetched data: ", data);
      var todayDateString = getDateString(todayDate);
      var todayData = data[todayDateString];
      var yesterdayDateString = getDateString(yesterdayDate);
      var yesterdayData = data[yesterdayDateString];

      document.querySelectorAll("[role=status]").forEach((el) => {
        el.hidden = true;
      })

      $('#visitorsTodayText').html(todayData["total_visitors"]);
      $('#pageviewsTodayText').html(todayData["pageviews"]);
      $('#eventsTodayText').html(todayData["total_events"]);

      var element = document.getElementById("visitorsYesterday");
      addStylesForDashboardCard(element, todayData["total_visitors"], yesterdayData["total_visitors"]);

      element = document.getElementById("pageviewsYesterday");
      addStylesForDashboardCard(element, todayData["pageviews"], yesterdayData["pageviews"]);

      element = document.getElementById("eventsYesterday");
      addStylesForDashboardCard(element, todayData["total_events"], yesterdayData["total_events"]);

      extractEventDataForChart(data, "pageview");
      metrics = data;
      drawChart();

      populateEventsTable(metrics[todayDateString]["category_wise"])
    }
  });
});

function populateEventsTable(eventsData) {
  window.aa = eventsData;
  let table = document.getElementById("top-events-table");
  for (let event in eventsData) {
    let row = table.insertRow();
    let cell = row.insertCell();
    let text = document.createTextNode(event);
    cell.appendChild(text);

    cell = row.insertCell();
    text = document.createTextNode(eventsData[event]);
    cell.appendChild(text);
  }
}

function extractEventDataForChart(data, type) {
  var config = {}
  config.labels = []
  config.data = []

  delete data.success;
  console.log("Data within extract: ", data);
  for (const d in data) {
    if (d === "success") continue;
    if (data.hasOwnProperty(d)) {
      const element = data[d];

      if (element.category_wise.hasOwnProperty(type)) {
        const value = element.category_wise[type];
        config.labels.push(d);
        config.data.push(value);
      }
      else {
        config.labels.push(d);
        config.data.push(0);
      }

    }
  }
  console.log("Final config", config)
  return config;
}

function drawChart() {


  var pageviewData = extractEventDataForChart(metrics, "pageview");
  pageviewData.labels.map((value, idx) => {
    var d = new Date(value);
    var options = { month: 'short', day: 'numeric' }
    pageviewData.labels[idx] = new Intl.DateTimeFormat('en-US', options).format(d);
  });
  var config = {
    type: 'line',
    data: {
      datasets: [{
        data: pageviewData.data, fill: false, lineTension: 0.1
      }],
      labels: pageviewData.labels
    },
    options: {
      responsive: true,
      title: {
        display: false, // We don't diplay it here because it is included as card header in HTML
      },
      tooltips: {
        mode: 'index',
        intersect: false,
      },
      hover: {
        mode: 'nearest',
        intersect: true
      },
      scales: {
        xAxes: [{
          display: true,
          scaleLabel: {
            display: true,
            labelString: 'Date'
          }
        }],
        yAxes: [{
          display: true,
          gridLines: {
            lineWidth: 1,
            color: Charts.colors.gray[900],
            zeroLineColor: Charts.colors.gray[900]
          },

          scaleLabel: {
            display: true,
            labelString: 'Views'
          }
        }]
      }
    }
  };

  var ctx = document.getElementById('chart-page-views').getContext('2d');
  new Chart(ctx, config);
  console.log(config);
}