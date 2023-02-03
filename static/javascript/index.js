
getAndRenderScoreboardData()
initWsListener()

function initWsListener() {
    const socket = new WebSocket(`ws://${window.location.host}/ws/teamupdates`);
      socket.addEventListener('message', ev => {
        const newTeams = JSON.parse(ev.data)
        renderScoreboard(newTeams)
      });
}

function renderScoreboard(teamsData) {
    document.getElementById("teamsScoreboardRows").innerHTML = ""
    // TODO SANITISE THIS INPUT
    let output = ``
    let i = 1

    teamsData.sort(function(a, b) {
        return a.score - b.score
    })

    teamsData.forEach((team) => {
        output += `
<div class="row pt-1">
    <div class="col-1 mt-0 text-center">
        <p class="scoreboardRegularText mb-1">
            ${i}
        </p>
    </div>
    <div class="col-8 mt-0 text-center">
        <p class="scoreboardRegularText mb-1">
            ${team.name}
        </p>
    </div>
    <div class="col text-center">
        <p class="scoreboardRegularText mb-1">
            ${team.score}
        </p>
    </div>
</div>
`
        i++
    })

    document.getElementById("teamsScoreboardRows").innerHTML = output
}

function getAndRenderScoreboardData() {
    getScoreboardData().then((teams) => {
        renderScoreboard(teams)
    }, (error) => {
        console.error(error)
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