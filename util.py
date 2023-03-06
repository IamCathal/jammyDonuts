import json
from datetime import datetime
import uuid
import math
import time

JAM_DONUTS_PREFIX = "jamDonuts-"
TEAMS = "teams"
SHOW_SCOREBOARD = "showScoreboard"

SCORE_UPDATES = "scoreUpdates"
TEAM_UPDATES = "teamsUpdates"


def set(db, var: str, val: str):
    val = json.dumps(val)
    db.set(f"{JAM_DONUTS_PREFIX}{var}", val )


def getTeamsFromDB(db):
    teams = db.get(f"{JAM_DONUTS_PREFIX}{TEAMS}")
    if teams == "[]" or teams == None:
        return []
    return json.loads(teams)

def getShouldScoreScoreboardFromDB(db):
    if db.get(f"{JAM_DONUTS_PREFIX}{SHOW_SCOREBOARD}") == None:
        set(db, SHOW_SCOREBOARD, 0)
        return getShouldScoreScoreboardFromDB(db)

    shouldHide = db.get(f"{JAM_DONUTS_PREFIX}{SHOW_SCOREBOARD}")
    if shouldHide == "0":
        return False
    else:
        return True

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
    db.publish(TEAM_UPDATES, json.dumps(currTeams))


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
    db.publish(TEAM_UPDATES, json.dumps(updatedAllTeams))
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

    scoreUpdateString = ""
    if newScoreDiff >= 1:
        scoreUpdateString = f"{scoringTeam} gained {newScoreDiff} points"
    else:
        # When a score has been lowered do not broadcast
        # this in the scoreboard feed
        scoreUpdateString = ""
    
    publishScoreUpdate(db, scoreUpdateString)


def addMember(db, teamId: str, memberName: str):
    if doesTeamExist(db, teamId) == False:
        return False

    allTeams = getTeamsFromDB(db)
    for team in allTeams:
        if team["id"] == teamId:
            team["members"].append(memberName)
            team["members"] = list(dict.fromkeys(team["members"]))

    set(db, TEAMS, allTeams)
    db.publish(TEAM_UPDATES, json.dumps(allTeams))
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
    db.publish(TEAM_UPDATES, allTeams)
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
    db.publish(TEAM_UPDATES, json.dumps(allTeamsWithoutRequestToBeDeletedTeam))
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


def publishScoreUpdate(db, scoreUpdateMessage):
    scoreObj = {
        "time": math.floor(time.time()),
        "message": scoreUpdateMessage
    }
    addRecentScoreUpdate(db, scoreObj)
    db.publish(SCORE_UPDATES, json.dumps(scoreObj))
    db.publish(TEAM_UPDATES, json.dumps(getTeamsFromDB(db)))


def showScoreboard(db):
    set(db, SHOW_SCOREBOARD, 0)

def hideScoreboard(db):
    set(db, SHOW_SCOREBOARD, 1)

def shouldBlockRequest(db, requestHeaders, dashboardPass):
    if getShouldScoreScoreboardFromDB(db) == "True":
        return True
    if requestHeaders.get('Referer') == None:
        return True
    if dashboardPass not in requestHeaders.get('Referer'):
        return True
    return False

def shouldShowScoreboard(db):
    if getShouldScoreScoreboardFromDB(db) == 0:
        return False
    return True

def isAdminRequest(db, requestHeaders, dashboardPass):
    if requestHeaders.get('Referer') == None:
        return False
    if dashboardPass not in requestHeaders.get('Referer'):
        return False
    return True