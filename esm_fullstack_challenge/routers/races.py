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

# Route to get race circuit tab
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

        # Lap length
        length_km = 5.793
        laps = 52
        race_distance_km = round(length_km * laps, 3)

        # Fastest lap overall in race
        cur.execute("""
            SELECT milliseconds, driver_id, lap
            FROM lap_times
            WHERE race_id = ?
            ORDER BY milliseconds ASC
            LIMIT 1
        """, (race_id,))
        fl = cur.fetchone()
        if fl:
            fastest_lap_time_ms, fastest_driver_id, fastest_lap_number = fl
            cur.execute("SELECT forename, surname FROM drivers WHERE id = ?", (fastest_driver_id,))
            d = cur.fetchone()
            fastest_driver_name = f"{d[0]} {d[1]}" if d else "Unknown"
        else:
            fastest_lap_time_ms = None
            fastest_driver_name = None
            fastest_lap_number = None
    
        # Fastest lap per driver
        cur.execute("""
            SELECT driver_id, MIN(milliseconds) as fastest
            FROM lap_times
            WHERE race_id = ?
            GROUP BY driver_id
            ORDER BY fastest ASC
        """, (race_id,))
        fastest_laps = cur.fetchall()
        fastest_laps_per_driver = []
        for driver_id, time_ms in fastest_laps:
            cur.execute("SELECT forename, surname FROM drivers WHERE id = ?", (driver_id,))
            d = cur.fetchone()
            name = f"{d[0]} {d[1]}" if d else "Unknown"
            fastest_laps_per_driver.append({
                "driver": name,
                "milliseconds": time_ms,
            })

        # Winner's position per lap
        cur.execute("""
            SELECT driver_id
            FROM results
            WHERE race_id = ?
            ORDER BY position ASC
            LIMIT 1
        """, (race_id,))
        winner = cur.fetchone()
        winner_id = winner[0] if winner else None

        winner_position_changes = []
        if winner_id:
            cur.execute("""
                SELECT lap, position
                FROM lap_times
                WHERE race_id = ? AND driver_id = ?
                ORDER BY lap
            """, (race_id, winner_id))
            winner_position_changes = [
                {"lap": lap, "position": pos} for lap, pos in cur.fetchall()
            ]

        # Fastest lap timeline (scatter of all drivers)
        cur.execute("""
            SELECT lap, milliseconds
            FROM lap_times
            WHERE race_id = ?
            ORDER BY lap
        """, (race_id,))
        fastest_lap_timeline = [
            {"lap": lap, "milliseconds": ms} for lap, ms in cur.fetchall()
        ]

        # Top fastest laps
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

        # Race pace candlesticks 
        cur.execute("""
            SELECT d.forename || ' ' || d.surname, 
                MIN(l.milliseconds), 
                AVG(l.milliseconds), 
                MAX(l.milliseconds)
            FROM lap_times l
            JOIN drivers d ON l.driver_id = d.id
            WHERE l.race_id = ?
            GROUP BY d.id
        """, (race_id,))
        pace_candlestick = [
            {
                "driver": row[0],
                "min": row[1],
                "avg": row[2],
                "max": row[3]
            }
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
 
    def format_ms(ms: int) -> str:
        if ms is None:
            return "N/A"
        minutes = ms // 60000
        seconds = (ms % 60000) / 1000
        return f"{minutes}:{seconds:06.3f}"

    return {
        "circuit_name": circuit_name,
        "location": location,
        "race_name": race_name,
        "year": year,
        "laps": laps,
        "length_km": length_km,
        "race_distance_km": race_distance_km,
        "fastest_lap": {
            "time": format_ms(fastest_lap_time_ms),
            "driver": fastest_driver_name,
            "lap": fastest_lap_number
        },
        "fastest_laps_per_driver": fastest_laps_per_driver,
        "winner_position_changes": winner_position_changes,
        "fastest_lap_timeline": fastest_lap_timeline,

        "top_fastest_laps": top_fastest_laps,
        "pace_evolution": pace_evolution,
        "pace_candlestick": pace_candlestick,

        "position_evolution": position_evolution
    }
