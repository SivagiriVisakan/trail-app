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
          console.log(data);
          console.log(todayDateString);
          var todayData = data[todayDateString];
          $('#visitorsTodayText').html(todayData["total_visitors"]);

          var yesterdayDateString = getDateString(yesterdayDate);
          var yesterdayData = data[yesterdayDateString];

          var element = document.getElementById("visitorsYesterday");
          element.children[1].textContent = (todayData.total_visitors - yesterdayData.total_visitors).toString();
          if(yesterdayData.total_visitors <= todayData.total_visitors)
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
      }); 

}

