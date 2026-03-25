from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from sqlmodel import Session, select
from models import engine, Batting, People, Teams

app = FastAPI()

@app.get("/years")
async def get_years():
    with Session(engine) as session:
        years = session.exec(select(Teams.yearID).distinct().order_by(Teams.yearID)).all()
    return years

@app.get("/teams")
async def get_teams(year: int):
    with Session(engine) as session:
        teams = session.exec(
            select(Teams.teamID, Teams.name, Teams.lgID, Teams.divID)
            .where(Teams.yearID == year)
            .order_by(Teams.name)
        ).all()
    return [{"teamID": tid, "name": name, "league": lg, "division": div} for tid, name, lg, div in teams]




@app.get("/roster")
async def get_roster(year: int, team: str):
    with Session(engine) as session:
        players = session.exec(
            select(People.playerID, People.nameFirst, People.nameLast)
            .join(Batting, Batting.playerID == People.playerID)
            .where(Batting.yearID == year, Batting.teamID == team)
            .distinct()
            .order_by(People.nameLast, People.nameFirst)
        ).all()
    return [
        {"playerID": pid, "first": first, "last": last}
        for pid, first, last in players
    ]


@app.get("/player")
async def get_player(playerID: str):
    with Session(engine) as session:
        person = session.get(People, playerID)
        if not person:
            return {"error": "Player not found"}

        batting_history = session.exec(
            select(
                Batting.yearID,
                Batting.teamID,
                Batting.AB,
                Batting.R,
                Batting.H,
                Batting.HR,
                Batting.RBI
            )
            .where(Batting.playerID == playerID)
            .order_by(Batting.yearID)
        ).all()

        return {
            "playerID": person.playerID,
            "nameGiven": person.nameGiven,
            "nameFirst": person.nameFirst,
            "nameLast": person.nameLast,
            "birthYear": person.birthYear,
            "birthMonth": person.birthMonth,
            "birthDay": person.birthDay,
            "birthCity": person.birthCity,
            "birthState": person.birthState,
            "birthCountry": person.birthCountry,
            "battingHistory": [
                {
                    "yearID": y,
                    "teamID": t,
                    "AB": ab,
                    "R": r,
                    "H": h,
                    "HR": hr,
                    "RBI": rbi,
                }
                for y, t, ab, r, h, hr, rbi in batting_history
            ],
        }


app.mount("/", StaticFiles(directory="static", html=True), name="static")