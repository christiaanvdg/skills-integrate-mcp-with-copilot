from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


DEFAULT_ACTIVITIES: dict[str, dict[str, Any]] = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"],
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"],
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"],
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"],
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"],
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"],
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"],
    },
}


class ActivityRepository:
    def __init__(self, database_path: Path):
        self.database_path = database_path
        self._initialize_database()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize_database(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS activities (
                    name TEXT PRIMARY KEY,
                    description TEXT NOT NULL,
                    schedule TEXT NOT NULL,
                    max_participants INTEGER NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS participants (
                    activity_name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    PRIMARY KEY (activity_name, email),
                    FOREIGN KEY (activity_name) REFERENCES activities(name) ON DELETE CASCADE
                )
                """
            )

            activity_count = connection.execute(
                "SELECT COUNT(*) FROM activities"
            ).fetchone()[0]
            if activity_count == 0:
                self._seed_activities(connection)

    def _seed_activities(self, connection: sqlite3.Connection) -> None:
        for activity_name, details in DEFAULT_ACTIVITIES.items():
            connection.execute(
                """
                INSERT INTO activities (name, description, schedule, max_participants)
                VALUES (?, ?, ?, ?)
                """,
                (
                    activity_name,
                    details["description"],
                    details["schedule"],
                    details["max_participants"],
                ),
            )
            for email in details["participants"]:
                connection.execute(
                    """
                    INSERT INTO participants (activity_name, email)
                    VALUES (?, ?)
                    """,
                    (activity_name, email),
                )

    def list_activities(self) -> dict[str, dict[str, Any]]:
        with self._connect() as connection:
            activities = connection.execute(
                """
                SELECT name, description, schedule, max_participants
                FROM activities
                ORDER BY name
                """
            ).fetchall()

            results: dict[str, dict[str, Any]] = {}
            for activity in activities:
                participants = connection.execute(
                    """
                    SELECT email
                    FROM participants
                    WHERE activity_name = ?
                    ORDER BY email
                    """,
                    (activity["name"],),
                ).fetchall()

                results[activity["name"]] = {
                    "description": activity["description"],
                    "schedule": activity["schedule"],
                    "max_participants": activity["max_participants"],
                    "participants": [participant["email"] for participant in participants],
                }

            return results

    def signup(self, activity_name: str, email: str) -> None:
        with self._connect() as connection:
            activity = connection.execute(
                """
                SELECT 1
                FROM activities
                WHERE name = ?
                """,
                (activity_name,),
            ).fetchone()
            if activity is None:
                raise KeyError("Activity not found")

            signed_up = connection.execute(
                """
                SELECT 1
                FROM participants
                WHERE activity_name = ? AND email = ?
                """,
                (activity_name, email),
            ).fetchone()
            if signed_up is not None:
                raise ValueError("Student is already signed up")

            connection.execute(
                """
                INSERT INTO participants (activity_name, email)
                VALUES (?, ?)
                """,
                (activity_name, email),
            )

    def unregister(self, activity_name: str, email: str) -> None:
        with self._connect() as connection:
            activity = connection.execute(
                """
                SELECT 1
                FROM activities
                WHERE name = ?
                """,
                (activity_name,),
            ).fetchone()
            if activity is None:
                raise KeyError("Activity not found")

            signed_up = connection.execute(
                """
                SELECT 1
                FROM participants
                WHERE activity_name = ? AND email = ?
                """,
                (activity_name, email),
            ).fetchone()
            if signed_up is None:
                raise ValueError("Student is not signed up for this activity")

            connection.execute(
                """
                DELETE FROM participants
                WHERE activity_name = ? AND email = ?
                """,
                (activity_name, email),
            )
