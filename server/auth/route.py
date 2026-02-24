from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pymongo.errors import PyMongoError
import logging
from .model import TeacherUser, StudentUser
from server.config.db import users_collection
from .hash_utils import hash_password, verify_password

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBasic()


def authenticate(credentials: HTTPBasicCredentials=Depends(security)):
    user_record = users_collection.find_one({"username": credentials.username})

    if not user_record or not verify_password(credentials.password, user_record["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return {
        "username": user_record["username"],
        "fullname": user_record["fullname"],
        "email": user_record["email"]
    }



@router.post("/signup/student")
def signup_student(req: StudentUser):
    try:
        if users_collection.find_one({"username": req.username}):
            raise HTTPException(status_code=400, detail="Username already exists")

        # Hash the password before storing.
        hashed_password = hash_password(req.password)

        users_collection.insert_one(
            {
                "fullname": req.fullname,
                "email": req.email,
                "username": req.username,
                "password": hashed_password,
                "grade": req.grade,
                "school": req.school,
            }
        )
    except PyMongoError as exc:
        logger.exception("MongoDB error during student signup")
        raise HTTPException(
            status_code=503,
            detail=f"Database unavailable: {exc.__class__.__name__}: {exc}",
        )

    return {"message": "Student user created successfully"}


@router.post("/signup/teacher")
def signup_teacher(req: TeacherUser):
    try:
        if users_collection.find_one({"username": req.username}):
            raise HTTPException(status_code=400, detail="Username already exists")

        # Hash the password before storing.
        hashed_password = hash_password(req.password)

        users_collection.insert_one(
            {
                "fullname": req.fullname,
                "email": req.email,
                "username": req.username,
                "password": hashed_password,
                "school": req.school,
            }
        )
    except PyMongoError as exc:
        logger.exception("MongoDB error during student signup")
        raise HTTPException(
            status_code=503,
            detail=f"Database unavailable: {exc.__class__.__name__}: {exc}",
        )

    return {"message": "Teacher user created successfully"}


@router.get("/login")
def login(user=Depends(authenticate)):
    return {"message": f"Login successful, welcome {user}"}