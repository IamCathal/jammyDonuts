import json
import uuid

JAM_DONUTS_PREFIX = "jamDonuts-"
TEAMS = "teams"

def set(db, var: str, val: str):
    print(f"Set '{var}' as '{val}'")
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
    print("no found team")
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
    print(f"Curr teams are '{currTeams}' ({type(currTeams)}) ({len(currTeams)})")
    print(f"Curr team is '{newTeam}'")

    for team in currTeams:
        if team["name"] == newTeam["name"]:
            print("duplicate team insert")
            return

    currTeams.append(newTeam)
    print(f"update teams are '{currTeams}' ({type(currTeams)}) ({len(currTeams)})")
    set(db, TEAMS, currTeams)


def updateScoreForTeam(db, teamId: str, newScore: int):
    if doesTeamExist(db, teamId) == False:
        print(f"team {teamId} does not exist")
        return
    
    allTeams = getTeamsFromDB(db)
    for team in allTeams:
        if team["id"] == teamId:
            team["score"] = int(newScore)

    set(db, TEAMS, allTeams)

def addMember(db, teamId: str, memberName: str):
    if doesTeamExist(db, teamId) == False:
        print(f"team {teamId} does not exist")
        return False

    allTeams = getTeamsFromDB(db)
    for team in allTeams:
        if team["id"] == teamId:
            team["members"].append(memberName)
            team["members"] = list(dict.fromkeys(team["members"]))

    set(db, TEAMS, allTeams)
    return True

def removeMember(db, teamId: str, memberName: str):
    if doesTeamExist(db, teamId) == False:
        print(f"team {teamId} does not exist")
        return False

    allTeams = getTeamsFromDB(db)
    for team in allTeams:
        if team["id"] == teamId:
            if memberName in team["members"]:
                team["members"].remove(memberName)
            else:
                print(f"member {memberName} does not exist in team {teamId}")
                return False

    set(db, TEAMS, allTeams)
    return True
