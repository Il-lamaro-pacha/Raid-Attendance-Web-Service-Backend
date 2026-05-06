import os
import logging
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv

from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.auth._check_token import verify_firebase_token

from src.schemas.RaidID import RaidID
from src.schemas.AttendanceResponse import AttendanceResponse
from src.schemas.SoftresRequest import SoftresRequest
from src.schemas.AttendanceCreateRequest import AttendanceCreateRequest
from src.schemas.AttendancePreviewRequest import AttendancePreviewRequest
from src.schemas.AttendanceDeletionRequest import AttendanceDeletionRequest
from src.schemas.AttendanceUpdateRequest import AttendanceUpdateRequest
from src.schemas.UserContext import UserContext
from src.schemas.HistoryObject import HistoryObject
from src.schemas.ListRollbackItem import ListRollbackItem

from src.controller.AttendanceController import AttendanceController
from src.controller.AuthController import AuthController

import firebase_admin
from firebase_admin import credentials, auth

logging.basicConfig(level=logging.DEBUG)

load_dotenv()

cred = credentials.Certificate(os.path.join(os.getcwd(), "keys", os.getenv("FIREBASE_SERVICE_ACCOUNT_FILE_NAME")))
firebase_admin.initialize_app(cred)

router = APIRouter()
app = FastAPI()
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

attendance_controller = AttendanceController()
auth_controller = AuthController()

def get_user_context(
        token: dict = Depends(verify_firebase_token)
    ) -> UserContext:

    email = token.get("email")

    response = auth_controller.get_user_context(email=email)

    return UserContext(username = response["username"], guild_id = response["guild_id"], server = response["server"], email=email)

@router.get("/attendance_service", response_model=list[AttendanceResponse])
def get_attendance_list(raid_id: RaidID, raid_type: str, context: UserContext = Depends(get_user_context)):
    return attendance_controller.get_attendance(raid_id=raid_id, raid_type=raid_type, context = context)

@router.post("/attendance_service")
def add_attendance(raid_id: RaidID, raid_type: str, attendance_list: AttendanceCreateRequest, context: UserContext = Depends(get_user_context)):
    return attendance_controller.add_attendance(raid_id=raid_id, raid_type=raid_type, context=context, attendance_list=attendance_list.attendance_list)

@router.delete("/attendance_service")
def remove_attendance(raid_id: RaidID, raid_type: str, deletion_request: AttendanceDeletionRequest, context: UserContext = Depends(get_user_context)):
    return attendance_controller.remove_attendance(raid_id=raid_id, raid_type=raid_type, player_names=deletion_request.player_names, context=context)

@router.patch("/attendance_service")
def update_attendance(raid_id: RaidID, raid_type: str, updates: AttendanceUpdateRequest, context: UserContext = Depends(get_user_context)):
    return attendance_controller.update_attendance(raid_id=raid_id, raid_type=raid_type, attendances=updates.updates, context=context)

@router.get("/attendance_service/raid_types")
def get_raid_types(context: UserContext = Depends(get_user_context)):
    return attendance_controller.get_raid_types(context=context)

@router.post("/attendance_service/preview")
def preview_attendance(raid_id: RaidID, raid_type: str, payload: AttendancePreviewRequest, context: UserContext = Depends(get_user_context)):
    return attendance_controller.get_preview_attendance(raid_id=raid_id, raid_type=raid_type, new_attendances=payload.newAttendances, context=context)

@router.post("/softres_service/fetch_attendance")
def fetch_attendance(link: SoftresRequest, token: dict = Depends(verify_firebase_token)):
    return attendance_controller.fetch_attendance(link=link)

@router.get("/attendance_service/history")
def get_history_list(raid_id: RaidID, raid_type: str, context: UserContext = Depends(get_user_context)):
    return attendance_controller.get_history_list(raid_id=raid_id, raid_type=raid_type, context=context)

@router.post("/attendance_service/history/raid")
def get_raid_history(raid_type: str, raid_id: str, history: HistoryObject, context: UserContext = Depends(get_user_context)):
    return attendance_controller.get_raid_history(raid_type=raid_type, raid_id=raid_id, history=history, context=context)

@router.post("/attendance_service/list")
def create_new_list(raid_type: str, context: UserContext = Depends(get_user_context)):
    return attendance_controller.create_new_list(raid_type=raid_type, context=context)

@router.patch("/attendance_service/history/raid")
def rollback_raid(raid_type: str, raid_id: str, rollbacks: ListRollbackItem, context: UserContext = Depends(get_user_context)):
    return attendance_controller.rollback_raid(raid_type=raid_type, raid_id=raid_id, rollbacks = rollbacks.rollback, context=context)

app.include_router(router) 
