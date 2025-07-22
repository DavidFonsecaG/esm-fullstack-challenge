from typing import List

from fastapi import APIRouter, Depends, HTTPException

from esm_fullstack_challenge.models import AutoGenModels
from esm_fullstack_challenge.routers.utils import \
    get_route_list_function, get_route_id_function

from esm_fullstack_challenge.dependencies import get_db
from esm_fullstack_challenge.db import DB


races_router = APIRouter()

table_model = AutoGenModels['races']

# Route to get race by id
get_race = get_route_id_function('races', table_model)
races_router.add_api_route(
    '/{id}', get_race,
    methods=["GET"], response_model=table_model,
)

# Route to get a list of races
get_races = get_route_list_function('races', table_model)
races_router.add_api_route(
    '', get_races,
    methods=["GET"], response_model=List[table_model],
)

# Route to get race circuit tab data
@races_router.get("/race_circuit_summary/{race_id}")
def get_race_circuit_summary(race_id: int, db: DB = Depends(get_db)):
    with db.get_connection() as conn:
        cur = conn.cursor()

        # Get race + circuit metadata
        cur.execute("""
            SELECT r.name, r.year, c.name, c.location
            FROM races r
            JOIN circuits c ON r.circuit_id = c.id
            WHERE r.id = ?
        """, (race_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Race not found.")
        race_name, year, circuit_name, location = row

        # Top 20 fastest laps
        cur.execute("""
            SELECT d.surname, l.lap, l.milliseconds
            FROM lap_times l
            JOIN drivers d ON l.driver_id = d.id
            WHERE l.race_id = ?
            ORDER BY l.milliseconds ASC
            LIMIT 20
        """, (race_id,))
        top_fastest_laps = [
            {
                "position": idx + 1,
                "driver": row[0],
                "lap": row[1],
                "milliseconds": row[2]
            }
            for idx, row in enumerate(cur.fetchall())
        ]

        # Race pace evolution
        cur.execute("""
            SELECT d.forename || ' ' || d.surname as driver, l.lap, l.milliseconds
            FROM lap_times l
            JOIN drivers d ON l.driver_id = d.id
            WHERE l.race_id = ?
            ORDER BY driver, lap
        """, (race_id,))
        pace_evolution = [
            {"driver": row[0], "lap": row[1], "milliseconds": row[2]}
            for row in cur.fetchall()
        ]

        # Position Evolution for All Drivers
        cur.execute("""
            SELECT d.forename || ' ' || d.surname as driver, l.lap, l.position
            FROM lap_times l
            JOIN drivers d ON l.driver_id = d.id
            WHERE l.race_id = ?
            ORDER BY driver, lap
        """, (race_id,))
        position_evolution = [
            {"driver": row[0], "lap": row[1], "position": row[2]}
            for row in cur.fetchall()
        ]

    return {
        "circuit_name": circuit_name,
        "location": location,
        "race_name": race_name,
        "year": year,
        "top_fastest_laps": top_fastest_laps,
        "pace_evolution": pace_evolution,
        "position_evolution": position_evolution
    }

# Route to get drivers tab data
@races_router.get("/race_driver_summary/{race_id}")
def get_race_driver_summary(race_id: int, db: DB = Depends(get_db)):
    with db.get_connection() as conn:
        cur = conn.cursor()

        def get_driver_name(driver_id):
            cur.execute("SELECT forename, surname FROM drivers WHERE id = ?", (driver_id,))
            d = cur.fetchone()
            return f"{d[0]} {d[1]}" if d else "Unknown"

        def get_constructor_info(constructor_id):
            cur.execute("SELECT name FROM constructors WHERE id = ?", (constructor_id,))
            c = cur.fetchone()
            return {"name": c[0]} if c else {"name": "Unknown"}

        def safe_int(val):
            try:
                return int(val)
            except (ValueError, TypeError):
                return None

        def format_ms(ms: int):
            minutes = ms // 60000
            seconds = (ms % 60000) / 1000
            return f"{minutes}:{seconds:06.3f}"

        # Race Winner
        cur.execute("""
            SELECT driver_id, constructor_id, time, milliseconds
            FROM results
            WHERE race_id = ? AND position = 1
        """, (race_id,))
        winner = cur.fetchone()
        winner_data = None
        if winner:
            driver_id, constructor_id, time, _ = winner
            winner_data = {
                "driver": get_driver_name(driver_id),
                "team": get_constructor_info(constructor_id)["name"],
                "time": time,
            }

        # Pole Position
        cur.execute("""
            SELECT driver_id, constructor_id, q3
            FROM qualifying
            WHERE race_id = ? AND q3 IS NOT NULL
            ORDER BY q3 ASC
            LIMIT 1
        """, (race_id,))
        pole = cur.fetchone()
        pole_data = None
        if pole:
            driver_id, constructor_id, q3_time = pole
            pole_data = {
                "driver": get_driver_name(driver_id),
                "team": get_constructor_info(constructor_id)["name"],
                "time": q3_time,
            }

        # Fastest Lap
        cur.execute("""
            SELECT lt.driver_id, r.constructor_id, lt.lap, lt.milliseconds
            FROM lap_times lt
            JOIN results r ON lt.race_id = r.race_id AND lt.driver_id = r.driver_id
            WHERE lt.race_id = ?
            ORDER BY lt.milliseconds ASC
            LIMIT 1
        """, (race_id,))
        fl = cur.fetchone()
        fastest_lap_data = None
        if fl:
            driver_id, constructor_id, lap, ms = fl
            ms_int = safe_int(ms)
            fastest_lap_data = {
                "driver": get_driver_name(driver_id),
                "team": get_constructor_info(constructor_id)["name"],
                "lap": lap,
                "time": format_ms(ms_int) if ms_int is not None else "N/A",
            }

        # Race Results
        cur.execute("""
            SELECT r.position, d.forename, d.surname, c.name, r.time, r.milliseconds, r.points, r.laps
            FROM results r
            JOIN drivers d ON r.driver_id = d.id
            JOIN constructors c ON r.constructor_id = c.id
            WHERE r.race_id = ?
            ORDER BY r.milliseconds ASC
        """, (race_id,))
        rows = cur.fetchall()
        results = []
        leader_ms = safe_int(rows[0][5]) if rows else None
        interval_val = 0
        for row in rows:
            pos, forename, surname, team, time, ms, points, laps = row
            ms_val = safe_int(ms)
            gap = ""
            if leader_ms is not None and ms_val is not None:
                gap_val = round((ms_val - leader_ms) / 1000, 3)
                gap = f"+{gap_val}s" if gap_val > 0 else ""
                interval_val += gap_val
                interval = f"+{round(interval_val, 3)}s" if gap_val > 0 else ""

            results.append({
                "position": pos,
                "driver": f"{forename} {surname}",
                "team": team,
                "time": time,
                "gap": gap if pos > "1" else "",
                "interval": interval if pos > "1" else "",
                "points": points,
                "laps": laps,
            })

        return {
            "race_winner": winner_data,
            "pole_position": pole_data,
            "fastest_lap": fastest_lap_data,
            "results": results,
        }

# Route to get constructors tab data
@races_router.get("/race_constructor_summary/{race_id}")
def get_race_constructor_summary(race_id: int, db: DB = Depends(get_db)):
    with db.get_connection() as conn:
        cur = conn.cursor()

        # Best Finishing Constructor
        cur.execute("""
            SELECT c.name, MIN(r.position)
            FROM results r
            JOIN constructors c ON r.constructor_id = c.id
            WHERE r.race_id = ? AND r.position IS NOT NULL
            GROUP BY c.id
            ORDER BY MIN(r.position)
            LIMIT 1
        """, (race_id,))
        best_finisher = cur.fetchone()
        best_finisher_data = {"team": best_finisher[0], "position": best_finisher[1]} if best_finisher else None

        # Constructor with Most Points
        cur.execute("""
            SELECT c.name, SUM(r.points)
            FROM results r
            JOIN constructors c ON r.constructor_id = c.id
            WHERE r.race_id = ?
            GROUP BY c.id
            ORDER BY SUM(r.points) DESC
            LIMIT 1
        """, (race_id,))
        top_points = cur.fetchone()
        top_points_data = {"team": top_points[0], "points": top_points[1]} if top_points else None

        # Constructor Results
        cur.execute("""
            SELECT c.name, d.forename || ' ' || d.surname, r.position, r.points, r.laps
            FROM results r
            JOIN constructors c ON r.constructor_id = c.id
            JOIN drivers d ON r.driver_id = d.id
            WHERE r.race_id = ?
        """, (race_id,))
        grouped = {}
        for team, driver, position, points, laps in cur.fetchall():
            if team not in grouped:
                grouped[team] = {
                    "team": team,
                    "drivers": [],
                    "positions": [],
                    "points": 0,
                    "laps": 0,
                }
            grouped[team]["drivers"].append(driver)
            if position and position != "\\N":
                grouped[team]["positions"].append(int(position))
            grouped[team]["points"] += points or 0
            grouped[team]["laps"] += laps or 0

        constructor_results = []
        for val in grouped.values():
            positions = val["positions"]
            constructor_results.append({
                "team": val["team"],
                "drivers": ", ".join(val["drivers"]),
                "best_position": min(positions) if positions else None,
                "avg_position": round(sum(positions)/len(positions), 2) if positions else None,
                "total_points": val["points"],
                "laps_completed": val["laps"],
            })

        # Points per driver
        cur.execute("""
            SELECT c.name, d.forename || ' ' || d.surname, r.points
            FROM results r
            JOIN constructors c ON r.constructor_id = c.id
            JOIN drivers d ON r.driver_id = d.id
            WHERE r.race_id = ?
        """, (race_id,))
        driver_points = [
            {"constructor": row[0], "driver": row[1], "points": row[2] or 0}
            for row in cur.fetchall()
        ]

        # Position Evolution
        cur.execute("""
            SELECT l.lap, c.name, AVG(CAST(l.position AS INTEGER))
            FROM lap_times l
            JOIN results r ON l.race_id = r.race_id AND l.driver_id = r.driver_id
            JOIN constructors c ON r.constructor_id = c.id
            WHERE l.race_id = ? AND l.position != '\\N'
            GROUP BY l.lap, c.name
            ORDER BY l.lap, c.name
        """, (race_id,))
        position_evolution = [
            {"lap": lap, "team": team, "position": avg}
            for lap, team, avg in cur.fetchall()
        ]

    return {
        "best_finisher": best_finisher_data,
        "most_points": top_points_data,
        "results": constructor_results,
        "driver_points": driver_points,
        "position_evolution": position_evolution
    }
    