const endDate = new Date(endDateInput); // Today's date, to get the metrics for today


const startDate = new Date(startDateInput); // We get the metrics from the past week until today, which is used to plot the graph 

var metrics = {} // To store the fetched data

// Get the timestamp without milliseconds
var endTimestamp = Math.floor(endDate.getTime() / 1000);
var startDateTimestamp = Math.floor(startDate.getTime() / 1000);

$('.datepicker').on('changeDate', (event) => {
    // save checkout date
    startDateInput = document.getElementById('start-date-input').value;
    endDateInput = document.getElementById('end-date-input').value
});


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
            "end_time": endTimestamp,
        },
        dataType: 'json',
        type: 'GET',
        success: function (data) {
            console.log("Fetched data: ", data);
            var todayDateString = getDateString(endDate);
            var todayData = data[todayDateString];

            document.querySelectorAll("[role=status]").forEach((el) => {
                el.hidden = true;
            })

            $('#eventsTodayText').html(todayData["total_events"]);

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

            if (type !== null) {
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
            else {
                config.labels.push(d);
                config.data.push(element["total_events"]);

            }
        }
    }
    console.log("Final config", config)
    return config;
}

function handleRefreshClick() {
    let startDateTimestamp = Math.floor(new Date(startDateInput).getTime() / 1000);
    let endDateTimestamp = Math.floor(new Date(endDateInput).getTime() / 1000);

    let url = urlFormat.replace('START', startDateTimestamp.toString())
    url = url.replace('END', endDateTimestamp.toString())
    url = url.replace('EVENT_TYPE', eventType ? eventType.toString() : '')

    alert(url);
    window.location.href = url;
}

function handleEventSelectionChange() {
    let el = document.getElementById('event-type-select-input');
    eventType = el.value;
    if (eventType == 'All events') {
        eventType = null;
    }
}

function drawChart() {


    var ctx = document.getElementById('chart-page-views').getContext('2d');
    let gradient = ctx.createLinearGradient(0, 0, 0, 450);

    gradient.addColorStop(0, 'rgba(94, 114, 228, 0.5)');
    gradient.addColorStop(0.5, 'rgba(94, 114, 228, 0.25)');
    gradient.addColorStop(1, 'rgba(94, 114, 228, 0)');


    var pageviewData = extractEventDataForChart(metrics, eventType);
    pageviewData.labels.map((value, idx) => {
        var d = new Date(value);
        var options = { month: 'short', day: 'numeric' }
        pageviewData.labels[idx] = new Intl.DateTimeFormat('en-US', options).format(d);
    });
    var config = {
        type: 'line',
        data: {
            datasets: [{
                data: pageviewData.data, fill: "origin", lineTension: 0,
                backgroundColor: gradient,
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

    new Chart(ctx, config);
    console.log(config);
}