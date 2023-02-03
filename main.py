import redis
import util
import validate
import json
from flask import Flask, Response, request, send_from_directory

db = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
app = Flask(__name__)

def main():
    app.run(host='0.0.0.0', port=9095)

@app.route("/")
def index():
    return send_from_directory("pages", "index.html")

@app.route("/getteams")
def getTeams():
    res = json.dumps(util.getTeamsFromDB(db))
    return Response(res, status=200, mimetype='application/json')

@app.route("/getteam")
def getTeam():
    teamId = request.args.get("teamid", "")
    if teamId == "":
        res = {
                "error": "Team name or membername was empty"
        }
        return Response(json.dumps(res), status=400, mimetype='application/json')
    
    print(f"get the team {teamId}")
    team = util.getTeam(db, teamId)
    if team == None:
        res = {
                "error": "Could not find teamId {teamId}"
        }
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
        res = {
            "error": "Team object was invalid"
        }
        return Response(json.dumps(res), status=400, mimetype='application/json')

@app.route("/addmember", methods=["POST"])
def addMember():
    teamId = request.args.get("teamid", "")
    memberName = request.args.get("membername", "")

    if teamId == "" or memberName == "":
        res = {
                "error": "Team name or membername was empty"
        }
        return Response(json.dumps(res), status=400, mimetype='application/json')
    
    if util.addMember(db, teamId, memberName) == False:
        res = {
                "error": f"Failed to add member {memberName} to team {teamId}"
        }
        return Response(json.dumps(res), status=400, mimetype='application/json')

    return Response(json.dumps(util.getTeam(db, teamId)), status=400, mimetype='application/json')

@app.route("/removemember", methods=["POST"])
def removeMember():
    teamId = request.args.get("teamid", "")
    memberName = request.args.get("membername", "")

    if teamId == "" or memberName == "":
        res = {
                "error": "Team name or membername was empty"
        }
        return Response(json.dumps(res), status=400, mimetype='application/json')

    if util.removeMember(db, teamId, memberName) == False:
        res = {
                "error": f"Failed to remove member {memberName} to team {teamId}"
        }
        return Response(json.dumps(res), status=400, mimetype='application/json')

    return Response(json.dumps(util.getTeam(db, teamId)), status=400, mimetype='application/json')

@app.route("/updatescore", methods=["POST"])
def updateScore():
    teamId = request.args.get("teamid", "")
    score = request.args.get("score", "")

    if teamId == "" or score == "" or validate.isInt(score) == False:
        res = {
                "error": "Team name or score was invalid"
        }
        return Response(json.dumps(res), status=400, mimetype='application/json')
    
    if util.updateScoreForTeam(db, teamId, score) == False:
        res = {
                "error": f"Failed to update score to {score} for team {teamId}"
        }
        return Response(json.dumps(res), status=400, mimetype='application/json')

    return Response(json.dumps(util.getTeam(db, teamId)), status=400, mimetype='application/json')

if __name__ == "__main__":
    main()