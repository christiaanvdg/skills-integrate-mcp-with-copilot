"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

try:
    from .storage import ActivityRepository
except ImportError:  # Allows running as `python app.py` from within `src/`
    from storage import ActivityRepository

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

repository = ActivityRepository(Path(__file__).with_name("activities.db"))


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return repository.list_activities()


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    try:
        repository.signup(activity_name, email)
    except KeyError:
        raise HTTPException(status_code=404, detail="Activity not found")
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    try:
        repository.unregister(activity_name, email)
    except KeyError:
        raise HTTPException(status_code=404, detail="Activity not found")
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )
    return {"message": f"Unregistered {email} from {activity_name}"}
