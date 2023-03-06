from sre_constants import SUCCESS
import redis
import util
import validate
import json
from flask import Flask, Response, request, send_from_directory
from threading import Thread
from time import sleep
from flask_sock import Sock
import random

DASHBOARD_PASS = "V2hlbiBmb29kIGlzIHNjYXJjZSBhbmQgeW91ciBsYXJkZXIgYmFyZQpBbmQgbm8gcmFzaGVycyBncmVhc2UgeW91ciBwYW4sCldoZW4gaHVuZ2VyIGdyb3dzIGFzIHlvdXIgbWVhbHMgYXJlIHJhcmUg4oCTCkEgcGludCBvZiBwbGFpbiBpcyB5b3VyIG9ubHkgbWFuLgoKSW4gdGltZSBvZiB0cm91YmxlIGFuZCBsb3VzZXkgc3RyaWZlLApZb3UgaGF2ZSBzdGlsbCBnb3QgYSBkYXJsaW50IHBsYW4KWW91IHN0aWxsIGNhbiB0dXJuIHRvIGEgYnJpZ2h0ZXIgbGlmZSDigJMKQSBwaW50IG9mIHBsYWluIGlzIHlvdXIgb25seSBtYW4u"

db = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
app = Flask(__name__)
sock = Sock(app)

@sock.route("/ws/teamupdates")
def teamUpdates(ws):
    subscription = db.pubsub()
    subscription.subscribe(util.TEAM_UPDATES)
    while True:
        for message in subscription.listen():
            if message["data"] is not None and isinstance(message["data"], str):
                ws.send(message["data"])


@sock.route("/ws/scoreupdates")
def scoreUpdates(ws):
    subscription = db.pubsub()
    subscription.subscribe(util.SCORE_UPDATES)
    while True:
        for message in subscription.listen():
            if message["data"] is not None and isinstance(message["data"], str):
                ws.send(json.dumps(message["data"]))


@app.route("/")
def index():
    return send_from_directory("pages", "index.html")


@app.route("/dashboard")
def dashboard():
    password = request.args.get("password")
    if password != DASHBOARD_PASS:
        return send_from_directory("pages", "index.html")
    return send_from_directory("pages", "dashboard.html")


@app.route("/hidethescoreboard")
def hideScoreboard():
    if util.isAdminRequest(db, request.headers, DASHBOARD_PASS) == False:
        print("not admin for hide")
        res = {}
        return Response(json.dumps(res), status=200, mimetype='application/json')

    util.hideScoreboard(db)
    return "false"


@app.route("/showthescoreboard")
def showScoreboard():
    if util.isAdminRequest(db, request.headers, DASHBOARD_PASS) == False:
        res = {}
        return Response(json.dumps(res), status=200, mimetype='application/json')
        
    util.showScoreboard(db)
    return "true"


@app.route("/isscoreboardhidden")
def shouldShowScoreboard():
    jsonResponse = {
        "value": util.getShouldScoreScoreboardFromDB(db)
    }
    return Response(json.dumps(jsonResponse), status=200, mimetype='application/json')


@app.route("/getrecentscoreupdates")
def getRecentScoreUpdates():
    if util.shouldShowScoreboard(db):
        res = {}
        return Response(json.dumps(res), status=200, mimetype='application/json')

    res = json.dumps(util.getRecentScoreUpdates(db))
    return Response(res, status=200, mimetype='application/json')


@app.route("/getteams")
def getTeams():
    if util.isAdminRequest(db, request.headers, DASHBOARD_PASS):
        res = json.dumps(util.getTeamsFromDB(db))
        return Response(res, status=200, mimetype='application/json')

    if util.shouldShowScoreboard(db):
        res = {}
        return Response(json.dumps(res), status=200, mimetype='application/json')
    
    res = json.dumps(util.getTeamsFromDB(db))
    return Response(res, status=200, mimetype='application/json')


@app.route("/getteam")
def getTeam():
    teamId = request.args.get("teamid", "")
    if teamId == "":
        res = {"error": "Team name or membername was empty"}
        return Response(json.dumps(res), status=400, mimetype='application/json')
    
    team = util.getTeam(db, teamId)
    if team == None:
        res = {"error": "Could not find teamId {teamId}"}
        return Response(json.dumps(res), status=400, mimetype='application/json')

    return Response(json.dumps(team), status=200, mimetype='application/json')


@app.route("/addteam", methods=["POST"])
def addTeam():
    if util.isAdminRequest(db, request.headers, DASHBOARD_PASS) == False:
        res = {}
        return Response(json.dumps(res), status=200, mimetype='application/json')

    team = request.get_json()
    teamObj = team
    if validate.isValidTeam(teamObj) == True:
        util.addANewTeam(db, team)
        return Response(json.dumps(team), status=200, mimetype='application/json')
    else:
        res = {"error": "Team object was invalid"}
        return Response(json.dumps(res), status=400, mimetype='application/json')


@app.route("/removeteam", methods=["POST"])
def removeTeam():
    if util.isAdminRequest(db, request.headers, DASHBOARD_PASS) == False:
        res = {}
        return Response(json.dumps(res), status=200, mimetype='application/json')

    teamId = request.args.get("teamid", "")
    if teamId == "":
        res = {"error": "Team name or membername was empty"}
        return Response(json.dumps(res), status=400, mimetype='application/json')

    if util.removeTeam(db, teamId) == False:
        res = {"error": f"TeamId {teamId} does not exist"}
        return Response(json.dumps(res), status=400, mimetype='application/json')

    return Response(json.dumps(util.getTeamsFromDB(db)), status=200, mimetype='application/json')

    
@app.route("/addmember", methods=["POST"])
def addMember():
    if util.isAdminRequest(db, request.headers, DASHBOARD_PASS) == False:
        res = {}
        return Response(json.dumps(res), status=200, mimetype='application/json')

    teamId = request.args.get("teamid", "")
    memberName = request.args.get("membername", "")

    if teamId == "" or memberName == "":
        res = {"error": "Team name or membername was empty"}
        return Response(json.dumps(res), status=400, mimetype='application/json')
    
    if util.addMember(db, teamId, memberName) == False:
        res = {"error": f"Failed to add member {memberName} to team {teamId}"}
        return Response(json.dumps(res), status=400, mimetype='application/json')

    return Response(json.dumps(util.getTeam(db, teamId)), status=400, mimetype='application/json')


@app.route("/removemember", methods=["POST"])
def removeMember():
    if util.isAdminRequest(db, request.headers, DASHBOARD_PASS) == False:
        res = {}
        return Response(json.dumps(res), status=200, mimetype='application/json')

    teamId = request.args.get("teamid", "")
    memberName = request.args.get("membername", "")

    if teamId == "" or memberName == "":
        res = {"error": "Team name or membername was empty"}
        return Response(json.dumps(res), status=400, mimetype='application/json')

    if util.removeMember(db, teamId, memberName) == False:
        res = {"error": f"Failed to remove member {memberName} to team {teamId}"}
        return Response(json.dumps(res), status=400, mimetype='application/json')

    return Response(json.dumps(util.getTeam(db, teamId)), status=400, mimetype='application/json')


@app.route("/updatescore", methods=["POST"])
def updateScore():
    if util.isAdminRequest(db, request.headers, DASHBOARD_PASS) == False:
        res = {}
        return Response(json.dumps(res), status=200, mimetype='application/json')
        
    teamId = request.args.get("teamid", "")
    newScoreDiff = request.args.get("scorediff", "", type=int)

    if teamId == "":
        res = {"error": "Team name or score was invalid"}
        return Response(json.dumps(res), status=400, mimetype='application/json')
    
    if util.updateScoreForTeam(db, teamId, newScoreDiff) == False:
        res = {"error": f"Failed to update score to {newScoreDiff} for team {teamId}"}
        return Response(json.dumps(res), status=400, mimetype='application/json')

    return Response(json.dumps(util.getTeam(db, teamId)), status=200, mimetype='application/json')


@app.route("/updateteam", methods=["POST"])
def updateTeam():
    if util.isAdminRequest(db, request.headers, DASHBOARD_PASS) == False:
        res = {}
        return Response(json.dumps(res), status=200, mimetype='application/json')
        
    teamToUpdate = request.get_json()
    if validate.isValidTeam(teamToUpdate) == False:
        res = {"error": f"Team {teamToUpdate['id']} was invalid"}
        return Response(json.dumps(res), status=400, mimetype='application/json')
    
    if util.updateTeam(db, teamToUpdate) == False:
        res = {"error": f"Failed to update team {teamToUpdate['id']}"}
        return Response(json.dumps(res), status=400, mimetype='application/json')

    return Response(json.dumps(util.getTeam(db, teamToUpdate["id"])), status=200, mimetype='application/json')


def updateThread():
    teams = util.getTeamsFromDB(db)
    while True:
        for team in teams:
            util.updateScoreForTeam(db, team["id"], random.randint(1, 1099))
            sleep(random.randint(20, 70))


def main():
    app.run(host='0.0.0.0', port=9095)
    pass


if __name__ == "__main__":
    main()