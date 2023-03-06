getAndRenderTeamsData()
initWsTeamUpdateListener()
getAndRenderScoreBoardVisibilityStatus()

function initWsTeamUpdateListener() {
    const socket = new WebSocket(`ws://${window.location.host}/ws/teamupdates`);
      socket.addEventListener('message', ev => {
        const newTeams = JSON.parse(ev.data)
        renderTeamEditRows(newTeams)
      });
}

function getAndRenderScoreBoardVisibilityStatus() {
    isScoreboardHidden().then(isHidden => {
        if (isHidden) {
            document.getElementById("scoreboardHiddenStatus").textContent = "Scoreboard is currently HIDDEN"
        } else {
            document.getElementById("scoreboardHiddenStatus").textContent = "Scoreboard is currently VISIBLE"
        }
    })
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
                <div class="col-3">
                    <input 
                        id="${team.id}-name"
                        class="teamInput"
                        value="${team.name}"
                    >
                </div>
                <div class="col text-center scoreboardLegendText">
                    <div class="row pb-1">
                        <div class="col">
                            <input 
                                id="${team.id}-member-name-0"
                                class="teamInput teamMemberInput"
                                value="${team.members[0].name == undefined ? "" : team.members[0].name}"
                            >
                        </div>
                    </div>
                    <div class="row">
                        <div class="col">
                            <input 
                                id="${team.id}-member-name-1"
                                class="teamInput teamMemberInput"
                                value="${team.members[1].name == undefined ? "" : team.members[1].name}"
                            >
                        </div>
                    </div>
                    <div class="row pb-1">
                        <div class="col">
                            <input 
                                id="${team.id}-member-name-2"
                                class="teamInput teamMemberInput"
                                value="${team.members[2].name == undefined ? "" : team.members[2].name}"
                            >
                        </div>
                    </div>
                    <div class="row pb-1">
                        <div class="col">
                            <input 
                                id="${team.id}-member-name-3"
                                class="teamInput teamMemberInput"
                                value="${team.members[3].name == undefined ? "" : team.members[3].name}"
                            >
                        </div>
                    </div>
                </div>
                <div class="col">
                    <div class="row justify-content-md-center">
                        <button class="addPointsButton changePointsButton" id="${team.id}-1">
                            +1
                        </button>
                        <button class="addPointsButton changePointsButton" id="${team.id}-2">
                            +2
                        </button>
                        <button class="addPointsButton changePointsButton" id="${team.id}-3">
                            +3
                        </button>
                        <button class="addPointsButton changePointsButton" id="${team.id}-5">
                            +5
                        </button>
                    </div>
                    <div class="row justify-content-md-center pt-2">
                        <button class="takeAwayPointsButton changePointsButton" id="${team.id}-minus1">
                            -1
                        </button>
                        <button class="takeAwayPointsButton changePointsButton" id="${team.id}-minus2">
                            -2
                        </button>
                        <button class="takeAwayPointsButton changePointsButton" id="${team.id}-minus3">
                            -3
                        </button>
                        <button class="takeAwayPointsButton changePointsButton" id="${team.id}-minus5">
                            -5
                        </button>
                    </div>
                    <div class="row pt-2 justify-content-md-center">
                        <div class="col-4 text-center scoreboardLegendText">
                            <input 
                                id="${team.id}-score"
                                class="teamInput"
                                value="${team.score}"
                                style="font-size: 1.1rem"
                            >
                        </div>
                    </div>
                </div>
            </div>

            <div class="row pt-2 pb-3">
                <div class="col-2 text-center">
                    <button class="updateTeamButton" id="${team.id}-updateTeamButton">
                        Update team
                    </button>
                </div>
                <div class="col-8" id="${team.id}-requestInfoBox">
                   
                </div>
                <div class="col-1">

                </div>
                <div class="col">
                    <button class="deleteTeamButton" id="${team.id}-deleteTeamButton">
                        Delete
                    </button>
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
            const updatedScore = parseInt(document.getElementById(`${teamID}-score`).value)
            updatedTeamMembers = getTeamMemberNamesForTeamId(teamID)
  
            updateTeam(teamID, updatedTeamName, updatedTeamMembers, updatedScore).then(res => {
                document.getElementById(`${teamID}-requestInfoBox`).textContent = res
                getAndRenderTeamsData()
            }, err => {
                document.getElementById(`${teamID}-requestInfoBox`).textContent = err
                console.error(err)
            })
        })
    })

    document.querySelectorAll(".deleteTeamButton").forEach(elem => {
        elem.addEventListener("click", (ev) => {
            // This is dirty and shameful but
            const teamID = ev.target.id.split("-deleteTeamButton")[0]; 
            removeTeam(teamID).then(res => {
                getAndRenderTeamsData()
            }, err => {
                console.error(err)
            })
        })
    })

    document.querySelectorAll(".changePointsButton").forEach(elem => {
        elem.addEventListener("click", (ev) => {
            // this is shameful but it is javascript
            const teamId = ev.target.id.split("-").slice(0, -1).join("-")
            const scoreDiff = ev.target.textContent.replace("+","").trim()
            sendScoreDiff(teamId, scoreDiff).then(res => {
                getAndRenderTeamsData()
            }, (err) => {
                console.error(err)
            })
        })
    })
}

document.getElementById("hideScoreboardButton").addEventListener("click", (ev) => {
    hideScoreboard().then(nothing => {
        location.reload()
    })
})

document.getElementById("showScoreboardButton").addEventListener("click", (ev) => {
    showScoreboard().then(nothing => {
        location.reload()
    })
})


document.getElementById("createTeam-createTeamButton").addEventListener("click", () => {
    const newTeamName = document.getElementById(`createTeam-name`).value

    const newTeamMembers = getTeamMemberNamesForTeamId("createTeam")

    createTeam(newTeamName, newTeamMembers, 0).then(res => {
        document.getElementById(`createTeam-requestInfoBox`).textContent = "Successfully created new team"
        clearInputsForCreateTeam()
    }, (err) => {
        console.error(err)
        document.getElementById(`createTeam-requestInfoBox`).textContent = "Failed to create team. Check webpage console"
    })
});

function clearInputsForCreateTeam() {
    document.getElementById(`createTeam-name`).value = ""
    document.querySelectorAll(`.teamMemberInput`).forEach(teamMemberBox => {
        if (teamMemberBox.id.startsWith("createTeam") && teamMemberBox.value != "") {
            document.getElementById(teamMemberBox.id).value = ""
        }
    })
}

function getAndRenderTeamsData() {
    getScoreboardData().then((teams) => {
        renderTeamEditRows(teams)
    }, (err) => {
        console.error(err)
    })
}

function getTeamMemberNamesForTeamId(teamID) {
    let teamMembers = []

    let teamMemberNames = []

    document.querySelectorAll(`.teamMemberInput`).forEach(teamMemberBox => {
        if (teamMemberBox.id.startsWith(teamID)) {
            if (teamMemberBox.id.includes("-member-name-")) {
                teamMemberNames.push(teamMemberBox.value)
            }
        }
    })

    for (let i = 0; i < teamMemberNames.length; i++) {
        teamMembers.push({
            "name": teamMemberNames[i],
        })
    }
    return teamMembers
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

function removeTeam(teamId) {
    return new Promise((resolve, reject) => {
        fetch(`/removeteam?teamid=${teamId}`, {
            method: "POST",
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

function createTeam(teamName, teamMembers, newTeamScore) {
    return new Promise((resolve, reject) => {
        fetch(`/addteam`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify({
                "name": teamName,
                "members": teamMembers,
                "score": newTeamScore
            })
        })
        .then((res) => {
            if (res.status == 400) {
                console.error(res)
                reject(res)
            } else {
                resolve(res.json())
            }
        }, (err) => {
            reject(err.json())
        });
    })
}

function sendScoreDiff(teamId, scoreDiff) {
    return new Promise((resolve, reject) => {
        fetch(`/updatescore?teamid=${teamId}&scorediff=${scoreDiff}`, {
            method: "POST",
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

function hideScoreboard() {
    return new Promise((resolve, reject) => {
        fetch(`/hidethescoreboard`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
        }).then((res) => res.json())
        .then((res) => {
            resolve()
        }, (err) => {
            reject(err)
        });
    })
}

function showScoreboard() {
    return new Promise((resolve, reject) => {
        fetch(`/showthescoreboard`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
        }).then((res) => res.json())
        .then((res) => {
            resolve()
        }, (err) => {
            reject(err)
        });
    })
}

function isScoreboardHidden() {
    return new Promise((resolve, reject) => {
        fetch(`/isscoreboardhidden`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
        }).then((res) => res.json())
        .then((res) => {
            if (res.value == false) {
                resolve(false);
            } else {
                resolve(true)
            }
        }, (err) => {
            reject(err)
        });
    })
}