function getCookie(cname) {
    var name = cname + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "null";
}

function setCookie(cname, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
    var expires = "expires=" + d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

var trailApp = { config: {} }
trailApp.init = function (apiKey) {
    trailApp.config.apiKey = apiKey;
    trailApp.signalEvent('pageview', {})
}

trailApp.config.BASE_TRAIL_APP_URL = "http://127.0.0.1:5000/api/v1/";



trailApp.getSessionId = function () {
    let sessionId = JSON.parse(getCookie('trailApp_session'));
    return sessionId || null;
}

trailApp.setSessionId = function (id) {
    setCookie("trailApp_session", JSON.stringify(id))
}

trailApp.signalEvent = function (eventType, customData) {
    console.log(eventType);
    console.log(customData);
    const payload = {
        "event_type": eventType,
        "api_key": this.config.apiKey,
        "page_url": window.location.href,
        "session_id": this.getSessionId(),
        "custom_params": customData || {}
    };
    req = new XMLHttpRequest();
    req.open("POST", trailApp.config.BASE_TRAIL_APP_URL + 'register-new', true);
    req.setRequestHeader("Content-type", "application/json");
    req.send(JSON.stringify(payload));
    console.log("sending request", payload);
    req.onreadystatechange = function () {
        if (this.readyState == 4) {
            console.log(this.responseText)
            console.log(JSON.parse(this.responseText).session_id)
            if(this.status == 200) {
                trailApp.setSessionId(JSON.parse(this.responseText).session_id)
            }

        }
    };
}

