import json
from datetime import datetime
import uuid
import sys

JAM_DONUTS_PREFIX = "jamDonuts-"
TEAMS = "teams"
SCORE_UPDATES = "scoreUpdateLogs"
PROBLEMS = "problems"


def set(db, var: str, val: str):
    val = json.dumps(val)
    db.set(f"{JAM_DONUTS_PREFIX}{var}", val )


def getTeamsFromDB(db):
    teams = db.get(f"{JAM_DONUTS_PREFIX}{TEAMS}")
    if teams == "[]" or teams == None:
        return []
    return json.loads(teams)


def getTeam(db: dict, teamId: str) -> dict:
    teams = getTeamsFromDB(db)

    for team in teams:
        if team["id"] == teamId:
            return team
    return None


def doesTeamExist(db, teamId: str) -> dict:
    allTeams = getTeamsFromDB(db)
    for team in allTeams:
        if team["id"] == teamId:
            return True
    return False


def addTeam(db, team):
    set(db, TEAMS, json.dumps(team))


def addANewTeam(db, newTeam):
    newTeam["score"] = 0
    newTeam["id"] = str(uuid.uuid1())

    currTeams = getTeamsFromDB(db)

    for team in currTeams:
        if team["name"] == newTeam["name"]:
            return

    currTeams.append(newTeam)
    set(db, TEAMS, currTeams)
    db.publish('teamsUpdates', json.dumps(currTeams))


def updateTeam(db, teamToUpdate):
    if doesTeamExist(db, teamToUpdate["id"]) == False:
        return False
    
    allTeams = getTeamsFromDB(db)
    updatedAllTeams = []
    for team in allTeams:
        if team["id"] == teamToUpdate["id"]:
            updatedAllTeams.append(teamToUpdate)
        else:
            updatedAllTeams.append(team)

    set(db, TEAMS, updatedAllTeams)
    db.publish('teamsUpdates', json.dumps(updatedAllTeams))
    return True


def updateScoreForTeam(db, teamId: str, newScoreDiff: int):
    if doesTeamExist(db, teamId) == False:
        return
    
    allTeams = getTeamsFromDB(db)
    scoringTeam = ""

    for team in allTeams:
        if team["id"] == teamId:
            newScore = int(team["score"]) + newScoreDiff
            team["score"] = newScore
            scoringTeam = team["name"]

    set(db, TEAMS, allTeams)
    if newScoreDiff >= 1:
        scoreUpdateString = f"{scoringTeam} gained {newScoreDiff} points"
        db.publish("scoreUpdate", scoreUpdateString)
        db.publish('teamsUpdates', json.dumps(allTeams))


def addMember(db, teamId: str, memberName: str):
    if doesTeamExist(db, teamId) == False:
        return False

    allTeams = getTeamsFromDB(db)
    for team in allTeams:
        if team["id"] == teamId:
            team["members"].append(memberName)
            team["members"] = list(dict.fromkeys(team["members"]))

    set(db, TEAMS, allTeams)
    db.publish('teamsUpdates', json.dumps(allTeams))
    return True


def removeMember(db, teamId: str, memberName: str):
    if doesTeamExist(db, teamId) == False:
        return False

    allTeams = getTeamsFromDB(db)
    for team in allTeams:
        if team["id"] == teamId:
            if memberName in team["members"]:
                team["members"].remove(memberName)
            else:
                return False

    set(db, TEAMS, allTeams)
    db.publish("teamUpdates", allTeams)
    return True


def removeTeam(db, teamId: str) -> bool:
    if doesTeamExist(db, teamId) == False:
        return False

    allTeams = getTeamsFromDB(db)
    allTeamsWithoutRequestToBeDeletedTeam = []
    for team in allTeams:
        if team["id"] != teamId:
            allTeamsWithoutRequestToBeDeletedTeam.append(team)
            
    set(db, TEAMS, allTeamsWithoutRequestToBeDeletedTeam)
    db.publish("teamsUpdates", json.dumps(allTeamsWithoutRequestToBeDeletedTeam))
    return True


def getTeamName(db, teamId: str) -> str:
    if doesTeamExist(db, teamId) == False:
        return False
        
    return getTeam(db, teamId)["name"]


def getRecentScoreUpdates(db):
    scoreUpdates = db.get(f"{JAM_DONUTS_PREFIX}{SCORE_UPDATES}")
    if scoreUpdates == "[]" or scoreUpdates == None:
        return []
    return json.loads(scoreUpdates)


def addRecentScoreUpdate(db, newScoreUpdate):
    allScoreUpdates = getRecentScoreUpdates(db)
    allScoreUpdates.insert(0, newScoreUpdate)
    if len(allScoreUpdates) > 20:
        allScoreUpdates = allScoreUpdates[:20]
    set(db, SCORE_UPDATES, allScoreUpdates)