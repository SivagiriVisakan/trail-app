const todayDate = new Date(); // Today's date, to get the metrics for today

const yesterdayDate = new Date(); // We get the metrics from yesterday also to compare and show 
yesterdayDate.setDate(yesterdayDate.getDate()-1);

// Get the timestamp without milliseconds
var yesterdayTimestamp = Math.floor(yesterdayDate.getTime() / 1000); 
var todayTimestamp = Math.floor(todayDate.getTime() / 1000);

function getDateString(date){
  function pad(n){return n<10 ? '0'+n : n}
  return date.getFullYear()+'-'
  + pad(date.getMonth()+1)+'-'
  + pad(date.getDate())
}

// A helper function for setting the styles of the cards at the top in the dashboard
// after comparing with the previous day's value. This depends in the element passed has the hierachy we assumed
function addStylesForDashboardCard(element, today, yesterday)
{
  element.children[1].textContent = (today - yesterday).toString();
  if(yesterday <= today)
  {
    element.classList.add("text-success");
    element.children[0].classList.add("fa-arrow-up");
  }
  else
  {
    element.classList.add("text-danger");
    element.children[0].classList.add("fa-arrow-down");
  }

}

window.onload = () => {
    $.ajax({
        url: '/events/api/v1/get-metrics/flizon/',
        data: {
          "start_time": yesterdayTimestamp,
          "end_time": todayTimestamp,
        },
        dataType: 'json',
        type: 'GET',
        success: function(data) {
          var todayDateString = getDateString(todayDate);
          var todayData = data[todayDateString];
          var yesterdayDateString = getDateString(yesterdayDate);
          var yesterdayData = data[yesterdayDateString];

          $('#visitorsTodayText').html(todayData["total_visitors"]);
          $('#pageviewsTodayText').html(todayData["pageviews"]);
          $('#eventsTodayText').html(todayData["total_events"]);

          var element = document.getElementById("visitorsYesterday");
          addStylesForDashboardCard(element, todayData["total_visitors"], yesterdayData["total_visitors"]);

          element = document.getElementById("pageviewsYesterday");
          addStylesForDashboardCard(element, todayData["pageviews"], yesterdayData["pageviews"]);

          element = document.getElementById("eventsYesterday");
          addStylesForDashboardCard(element, todayData["total_events"], yesterdayData["total_events"]);

        }
      }); 

}

