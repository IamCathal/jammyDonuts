def isValidTeam(team: dict) -> bool:
    teamNameIsValid = ("name" in team) and (team["name"] != None and team["name"] != "")
    membersAreValid = ("members" in team) and (type(team["members"]) == list)
    return teamNameIsValid and membersAreValid


def isValidListOfTeams(teams: list) -> bool:
    for team in teams:
        if isValidTeam(team) == False:
            return False
    return True
    

def isInt(intStr: str) -> bool:
    try:
        intVal = int(intStr)
        return True
    except ValueError as err:
        return False