getAndRenderTeamsData()
initWsListener()

function initWsListener() {
    const socket = new WebSocket(`ws://${window.location.host}/ws/teamupdates`);
      socket.addEventListener('message', ev => {
        const newTeams = JSON.parse(ev.data)
        renderTeamEditRows(newTeams)
      });
}

function renderTeamEditRows(teamsData) {
    document.getElementById("teamsEditRow").innerHTML = ""
    // TODO SANITISE THIS INPUT
    let output = ``
    let i = 1

    teamsData.forEach((team) => {
        output += `
    <div class="row mb-3 boxWithBorder lightBorder">
        <div class="col">
            <div class="row pt-1">
                <div class="col-5">
                    <input 
                        id="${team.id}-name"
                        class="teamInput"
                        value="${team.name}"
                    >
                </div>
                <div class="col-5 text-center scoreboardLegendText">
                    <div class="row pb-1">
                        <div class="col">
                            <input 
                                id="${team.id}-member-0"
                                class="teamInput teamMemberInput"
                                value="${team.members[0] == undefined ? "" : team.members[0]}"
                            >
                        </div>
                    </div>
                    <div class="row">
                        <div class="col">
                            <input 
                                id="${team.id}-member-1"
                                class="teamInput teamMemberInput"
                                value="${team.members[1] == undefined ? "" : team.members[1]}"
                            >
                        </div>
                    </div>
                    <div class="row pb-1">
                        <div class="col">
                            <input 
                                id="${team.id}-member-2"
                                class="teamInput teamMemberInput"
                                value="${team.members[2] == undefined ? "" : team.members[2]}"
                            >
                        </div>
                    </div>
                    <div class="row pb-1">
                        <div class="col">
                            <input 
                                id="${team.id}-member-3"
                                class="teamInput teamMemberInput"
                                value="${team.members[3] == undefined ? "" : team.members[3]}"
                            >
                        </div>
                    </div>
                </div>
                <div class="col-2 text-center scoreboardLegendText">
                    <input 
                        id="${team.id}-score"
                        class="teamInput"
                        value="${team.score}"
                        type="number"
                    >
                </div>
            </div>

            <div class="row pt-2 pb-3">
                <div class="col-2 text-center">
                    <button class="updateTeamButton" id="${team.id}-updateTeamButton">
                        Update team
                    </button>
                </div>
                <div class="col" id="${team.id}-requestInfoBox">
                   
                </div>
            </div>
        </div>
    </div>
`
        i++
    })

    document.getElementById("teamsEditRow").innerHTML = output

    document.querySelectorAll(".updateTeamButton").forEach(elem => {
        elem.addEventListener("click", (ev) => {
            // This is dirty and shameful but
            const teamID = ev.target.id.split("-updateTeamButton")[0]; 

            const updatedTeamName = document.getElementById(`${teamID}-name`).value
            const updatedMembers = []
            document.querySelectorAll(`.teamMemberInput`).forEach(teamMemberBox => {
                if (teamMemberBox.id.startsWith(teamID) && teamMemberBox.value != "") {
                    updatedMembers.push(teamMemberBox.value)
                }
            })
            const updatedScore = document.getElementById(`${teamID}-score`).value
  
            updateTeam(teamID, updatedTeamName, updatedMembers, updatedScore).then(res => {
                document.getElementById(`${teamID}-requestInfoBox`).textContent = res
                getAndRenderTeamsData()
            }, err => {
                document.getElementById(`${teamID}-requestInfoBox`).textContent = err
                console.error(err)
            })
        })
    })
}

function getAndRenderTeamsData() {
    getScoreboardData().then((teams) => {
        renderTeamEditRows(teams)
    }, (error) => {
        console.error(error)
    })
}

function updateTeam(teamID, updatedName, updatedMembers, updatedScore) {
    return new Promise((resolve, reject) => {
        fetch(`/updateteam`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify({
                "id": teamID,
                "name": updatedName,
                "members": updatedMembers,
                "score": updatedScore
            })
        }).then((res) => res.json())
        .then((res) => {
            resolve(res)
        }, (err) => {
            reject(err.json())
        });
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