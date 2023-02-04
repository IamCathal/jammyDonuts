getAndRenderTeamsData()
getAndRenderProblems()
initWsTeamUpdateListener()

function initWsTeamUpdateListener() {
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
                <div class="col-8" id="${team.id}-requestInfoBox">
                   
                </div>
                <div class="col-2">
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

    document.querySelectorAll(".deleteTeamButton").forEach(elem => {
        elem.addEventListener("click", (ev) => {
            // This is dirty and shameful but
            const teamID = ev.target.id.split("-deleteTeamButton")[0]; 
  
            removeTeam(teamID).then(res => {
                // getAndRenderTeamsData()
            }, err => {
                // document.getElementById(`${teamID}-requestInfoBox`).textContent = err
                console.error(err)
            })
        })
    })
}

document.getElementById("createTeam-createTeamButton").addEventListener("click", () => {
    const newTeamName = document.getElementById(`createTeam-name`).value
    const newTeamMembers = []
    document.querySelectorAll(`.teamMemberInput`).forEach(teamMemberBox => {
        if (teamMemberBox.id.startsWith("createTeam") && teamMemberBox.value != "") {
            newTeamMembers.push(teamMemberBox.value)
        }
    })
    const newTeamScore = document.getElementById(`createTeam-score`).value
    createTeam(newTeamName, newTeamMembers, newTeamScore).then(res => {
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
        document.getElementById(`createTeam-score`).value = ""
    })
}

function getAndRenderTeamsData() {
    getScoreboardData().then((teams) => {
        renderTeamEditRows(teams)
    }, (err) => {
        console.error(err)
    })
}

function getAndRenderProblems() {
    getProblems().then(problems => {
        renderProblems(problems)
    }, (err) => {
        console.error(err)
    })
}

function renderProblems(problems) {
    let output = ``

    problems.forEach(problem => {

        output += `
        
    <div class="row">
        <div class="col">
            <div class="row pt-1">
                <div class="col-9">
                    <textarea 
                        id="${problem.problemId}-problemText"
                        class="teamInput"
                        contenteditable="true"
                        style="width: 95%"
                    >
                    ${problem.problemText}
                    </textarea>
                </div>
                <div class="col-3 scoreboardLegendText">
                    <div class="row pb-1">
                        <div class="col">
                            <textarea 
                                id="${problem.problemId}-answer"
                                class="teamInput teamMemberInput"
                                contenteditable="true"
                                style="width: 95%"
                            >
                            ${problem.problemAnswer}
                            </textarea>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row pt-2 pb-3">
                <div class="col-2 text-center">
                    <button class="createProblemButton" id="createTeam-createTeamButton">
                        Update Problem
                    </button>
                </div>
                <div class="col" id="${problem.problemId}}-requestInfoBox">
                   
                </div>
            </div>
        </div>
    </div>
        `
    })
    document.getElementById("problemsEditRow").innerHTML = ""
    document.getElementById("problemsEditRow").innerHTML += output;
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

function getProblems() {
    return new Promise((resolve, reject) => {
        fetch(`/getproblems`, {
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