
getAndRenderScoreboardData()


function getAndRenderScoreboardData() {
    getScoreboardData().then((teams) => {
        document.getElementById("teamsScoreboardRows").innerHTML = ""
        // TODO SANITISE THIS INPUT
        let output = ``
        let i = 1

        teams.forEach((team) => {
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