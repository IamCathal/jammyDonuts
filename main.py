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

db = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
app = Flask(__name__)
sock = Sock(app)

def main():
    update = Thread(target=updateThread)
    # watch = Thread(target=watchMonitor)
    update.start()
    # watch.start()
    app.run(host='0.0.0.0', port=9095)

# def watchMonitor():
#     subscription = db.pubsub()
#     subscription.subscribe("teamsUpdates")
#     while True:
#         for message in subscription.listen():
#             print(f"message: {message['data']}\n\n\n\n")
#             if message is not None and validate.isValidTeam(message['data']):
#                 print(f"A NEW ONE: {message['data']}")

def updateThread():
    while True:
        util.updateScoreForTeam(db, "b95cd33e-a345-11ed-86e1-40167eaa9d32", random.randint(1, 1099))
        sleep(1.8)
        util.updateScoreForTeam(db, "2575f65c-a401-11ed-b810-40167eaa9d32", random.randint(1, 1099))
        sleep(1.2)
        util.updateScoreForTeam(db, "fd0980d4-a41a-11ed-93f1-40167eaa9d32", random.randint(1, 2300))
        sleep(1.7)
        util.updateScoreForTeam(db, "c5639962-a41a-11ed-affe-40167eaa9d32", random.randint(1, 1400))
        sleep(2.5)

@sock.route("/ws/teamupdates")
def teamUpdates(ws):
    subscription = db.pubsub()
    subscription.subscribe("teamsUpdates")
    while True:
        for message in subscription.listen():
            if message["data"] is not None and isinstance(message["data"], str):
                ws.send(message["data"])


@sock.route("/ws/scoreupdates")
def scoreUpdates(ws):
    subscription = db.pubsub()
    subscription.subscribe("scoreUpdate")
    lastTwentyUpdates = []
    while True:
        for message in subscription.listen():
            if message["data"] is not None and isinstance(message["data"], str):
                util.addRecentScoreUpdate(db, message["data"])
                ws.send(message["data"])

@app.route("/getrecentscoreupdates")
def getRecentScoreUpdates():
    res = json.dumps(util.getRecentScoreUpdates(db))
    return Response(res, status=200, mimetype='application/json')

@app.route("/")
def index():
    return send_from_directory("pages", "index.html")

@app.route("/dashboard")
def dashboard():
    password = request.args.get("password")
    if password != "V2hlbiBmb29kIGlzIHNjYXJjZSBhbmQgeW91ciBsYXJkZXIgYmFyZQpBbmQgbm8gcmFzaGVycyBncmVhc2UgeW91ciBwYW4sCldoZW4gaHVuZ2VyIGdyb3dzIGFzIHlvdXIgbWVhbHMgYXJlIHJhcmUg4oCTCkEgcGludCBvZiBwbGFpbiBpcyB5b3VyIG9ubHkgbWFuLgoKSW4gdGltZSBvZiB0cm91YmxlIGFuZCBsb3VzZXkgc3RyaWZlLApZb3UgaGF2ZSBzdGlsbCBnb3QgYSBkYXJsaW50IHBsYW4KWW91IHN0aWxsIGNhbiB0dXJuIHRvIGEgYnJpZ2h0ZXIgbGlmZSDigJMKQSBwaW50IG9mIHBsYWluIGlzIHlvdXIgb25seSBtYW4u":
        return send_from_directory("pages", "index.html")
    return send_from_directory("pages", "dashboard.html")

@app.route("/getteams")
def getTeams():
    res = json.dumps(util.getTeamsFromDB(db))
    return Response(res, status=200, mimetype='application/json')

@app.route("/getteam")
def getTeam():
    teamId = request.args.get("teamid", "")
    if teamId == "":
        res = {"error": "Team name or membername was empty"}
        return Response(json.dumps(res), status=400, mimetype='application/json')
    
    print(f"get the team {teamId}")
    team = util.getTeam(db, teamId)
    if team == None:
        res = {"error": "Could not find teamId {teamId}"}
        return Response(json.dumps(res), status=400, mimetype='application/json')

    return Response(json.dumps(team), status=200, mimetype='application/json')

@app.route("/addteam", methods=["POST"])
def addTeam():
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
    teamId = request.args.get("teamid", "")
    score = request.args.get("score", "")

    if teamId == "" or score == "" or validate.isInt(score) == False:
        res = {"error": "Team name or score was invalid"}
        return Response(json.dumps(res), status=400, mimetype='application/json')
    
    if util.updateScoreForTeam(db, teamId, score) == False:
        res = {"error": f"Failed to update score to {score} for team {teamId}"}
        return Response(json.dumps(res), status=400, mimetype='application/json')

    return Response(json.dumps(util.getTeam(db, teamId)), status=200, mimetype='application/json')

@app.route("/updateteam", methods=["POST"])
def updateTeam():
    teamToUpdate = request.get_json()
    if validate.isValidTeam(teamToUpdate) == False:
        res = {"error": f"Team {teamToUpdate['id']} was invalid"}
        return Response(json.dumps(res), status=400, mimetype='application/json')
    
    if util.updateTeam(db, teamToUpdate) == False:
        res = {"error": f"Failed to update team {teamToUpdate['id']}"}
        return Response(json.dumps(res), status=400, mimetype='application/json')

    return Response(json.dumps(util.getTeam(db, teamToUpdate["id"])), status=400, mimetype='application/json')

if __name__ == "__main__":
    main()