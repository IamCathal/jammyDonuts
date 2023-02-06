let lastUpdatedTime = new Date();
let recentScoreUpdateLogs = []

const MAX_LENGTH_LOGS = 15
const LOG_BACKGROUND_COLORS = ["#211d21", "#292729"]
let backGroundColorPicker = 0

getAndRenderScoreboardData()
getAndRenderMostRecentScoreUpdates()
initWsTeamUpdateListener()
initWsScoreUpdateListener()

function initWsTeamUpdateListener() {
    const socket = new WebSocket(`ws://${window.location.host}/ws/teamupdates`);
      socket.addEventListener('message', ev => {
        const newTeams = JSON.parse(ev.data)
        // document.getElementById("lastUpdatedInfo").textContent = `Last updated ${timeSince(lastUpdatedTime)} ago`;
        lastUpdatedTime = new Date()
        renderScoreboard(newTeams)
      });
}

function initWsScoreUpdateListener() {
    const socket = new WebSocket(`ws://${window.location.host}/ws/scoreupdates`);
      socket.addEventListener('message', ev => {
        const newScoreText = ev.data

        const now = new Date();
        const currTimeString = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`
        const currFullLog = 
        `
        <div class="row teamScoreUpdateLogText pt-2 pb-2 pl-1 pr-1 mt-0 mb-0 ml-2" style="background-color: ${LOG_BACKGROUND_COLORS[backGroundColorPicker % LOG_BACKGROUND_COLORS.length]}">
            <div class="col-10">
                ${newScoreText}
            </div>
            <div class="col" style="color:#c0c0c0">
                ${currTimeString}
            </div>
        </div>
        `
        backGroundColorPicker++;
        recentScoreUpdateLogs.push(currFullLog)
        console.log(recentScoreUpdateLogs.length)
        if (recentScoreUpdateLogs.length > MAX_LENGTH_LOGS) {
            recentScoreUpdateLogs = recentScoreUpdateLogs.slice(1, MAX_LENGTH_LOGS+1)
        }

        document.getElementById("scoreUpdateLogCol").innerHTML = ""
        recentScoreUpdateLogs.forEach(log => {
            document.getElementById("scoreUpdateLogCol").innerHTML = log + document.getElementById("scoreUpdateLogCol").innerHTML;
        })
     
      });
}

function renderScoreboard(teamsData) {
    document.getElementById("teamsScoreboardRows").innerHTML = ""
    // TODO SANITISE THIS INPUT
    let output = ``
    let i = 1

    teamsData.sort(function(a, b) {
        return b.score - a.score
    })

    teamsData.forEach((team) => {
        output += `
<div class="row pt-1">
    <div class="col-1 mt-0 text-center">
        <p class="scoreboardRegularText mb-1">
            ${i}
        </p>
    </div>
    <div class="col-4 mt-0 text-center">
        <p class="scoreboardRegularText mb-1">
            ${team.name}
        </p>
    </div>
    <div class="col-4 mt-0 text-center">
        ${renderTeamNames(team.members)}
    </div>
    <div class="col text-center">
        <p class="scoreboardScoreText mb-1">
            ${team.score}
        </p>
    </div>
</div>
`
        i++
    })

    document.getElementById("teamsScoreboardRows").innerHTML = output
}

function renderTeamNames(members) {
    let output = `
    <p class="scoreboardRegularText mb-1">
`
    members.forEach(member => {
        if (member.name != "") {
            output += `
            <div class="lightBorder text-center teamMemberScoreboardText pt-1 pb-1 pl-1 pr-1 mt-0 mb-1 ml-2" style="border-radius: 0.2rem; display: inline-block">
                ${member.name}
            </div>
        `
        }
       
    })
    return output;
}

function getAndRenderScoreboardData() {
    getScoreboardData().then((teams) => {
        renderScoreboard(teams)
    }, (error) => {
        console.error(error)
    })
}

function getAndRenderMostRecentScoreUpdates() {
    getRecentScoreboardUpdates().then(recentUpdates => {
        document.getElementById("scoreUpdateLogCol").innerHTML = ""
        recentUpdates.forEach(recentUpdate => {
            const now = new Date()
            const currTimeString = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`
            const currFullLog = 
            `
            <div class="row teamScoreUpdateLogText pt-2 pb-2 pl-1 pr-1 mt-0 mb-0 ml-2" style="background-color: ${LOG_BACKGROUND_COLORS[backGroundColorPicker % LOG_BACKGROUND_COLORS.length]}">
                <div class="col-10">
                    ${recentUpdate}
                </div>
                <div class="col" style="color:#c0c0c0">
                    ${currTimeString}
                </div>
            </div>
            `
            recentScoreUpdateLogs.push(currFullLog)
            console.log(recentScoreUpdateLogs.length)
            if (recentScoreUpdateLogs.length > MAX_LENGTH_LOGS) {
                recentScoreUpdateLogs = recentScoreUpdateLogs.slice(1, MAX_LENGTH_LOGS+1)
            }


            backGroundColorPicker++;
            document.getElementById("scoreUpdateLogCol").innerHTML = currFullLog + document.getElementById("scoreUpdateLogCol").innerHTML;
        })
    }, (err) => {
        console.error(err)
    })
}


function getScoreboardData() {
    return new Promise((resolve, reject) => {
        fetch(`/getteams`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
        }).then((res) => res.json())
        .then((res) => {
            resolve(res)
        }, (err) => {
            reject(err)
        });
    })
}

function getRecentScoreboardUpdates() {
    return new Promise((resolve, reject) => {
        fetch(`/getrecentscoreupdates`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
        }).then((res) => res.json())
        .then((res) => {
            resolve(res)
        }, (err) => {
            reject(err)
        });
    })
}

function timeSince(targetDate) {
    let seconds = Math.floor((new Date() - targetDate) / 1000)
    let interval = seconds / 31536000 // years
    interval = seconds / 2592000; // months
    interval = seconds / 86400; // days
    if (interval > 1) {
        return Math.floor(interval) + "d";
    }
    interval = seconds / 3600;
    if (interval > 1) {
        return Math.floor(interval) + "h";
    }
    interval = seconds / 60;
    if (interval > 1) {
        return Math.floor(interval) + "m";
    }
    return Math.floor(seconds) + "s";
}