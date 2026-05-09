import os
import logging
import uvicorn
import firebase_admin
from firebase_admin import credentials

from src.logging.setup_logger import setup_logger

from dotenv import load_dotenv

from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.auth._check_token import verify_firebase_token

from src.schemas.RaidID import RaidID
from src.schemas.AttendanceResponse import AttendanceResponse
from src.schemas.AttendancePublishingList import AttendancePublishingList
from src.schemas.SoftresRequest import SoftresRequest
from src.schemas.AttendanceCreateRequest import AttendanceCreateRequest
from src.schemas.AttendancePreviewRequest import AttendancePreviewRequest
from src.schemas.AttendanceDeletionRequest import AttendanceDeletionRequest
from src.schemas.AttendanceUpdateRequest import AttendanceUpdateRequest
from src.schemas.UserContext import UserContext
from src.schemas.HistoryObject import HistoryObject
from src.schemas.ListRollbackItem import ListRollbackItem
from src.schemas.RegistrationUserCreate import RegistrationUserCreate

from src.controller.AttendanceController import AttendanceController
from src.controller.AuthController import AuthController

setup_logger()
logger = logging.getLogger(__name__)

load_dotenv()

cred = credentials.Certificate(os.path.join(os.getcwd(), "etc", "secrets", os.getenv("FIREBASE_SERVICE_ACCOUNT_FILE_NAME")))

router = APIRouter()
app = FastAPI()
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

def init_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(
            os.path.join(os.getcwd(), "etc", "secrets", os.getenv("FIREBASE_SERVICE_ACCOUNT_FILE_NAME"))
        )
        firebase_admin.initialize_app(cred)

init_firebase()

@router.get("/attendance_service", response_model=list[AttendanceResponse])
def get_attendance_list(raid_id: RaidID, raid_type: str, context: UserContext = Depends(get_user_context)):
    logging.info(f"[{context.username}]: Called 'get_attendance_list' endpoint - GET Request")
    return attendance_controller.get_attendance(raid_id=raid_id, 
                                                raid_type=raid_type, 
                                                context = context)

@router.post("/attendance_service")
def add_attendance(raid_id: RaidID, raid_type: str, attendance_list: AttendanceCreateRequest, context: UserContext = Depends(get_user_context)):
    logging.info(f"[{context.username}]: Called 'add_attendance' endpoint - POST Request")
    return attendance_controller.add_attendance(raid_id=raid_id, 
                                                raid_type=raid_type, 
                                                context=context, 
                                                attendance_list=attendance_list.attendance_list)

@router.delete("/attendance_service")
def remove_attendance(raid_id: RaidID, raid_type: str, deletion_request: AttendanceDeletionRequest, context: UserContext = Depends(get_user_context)):
    logging.info(f"[{context.username}]: Called 'remove_attendance' endpoint - DELETE Request")
    return attendance_controller.remove_attendance(raid_id=raid_id, 
                                                   raid_type=raid_type, 
                                                   player_names=deletion_request.player_names, 
                                                   context=context)

@router.patch("/attendance_service")
def update_attendance(raid_id: RaidID, raid_type: str, updates: AttendanceUpdateRequest, context: UserContext = Depends(get_user_context)):
    logging.info(f"[{context.username}]: Called 'update_attendance' endpoint - PATCH Request")
    return attendance_controller.update_attendance(raid_id=raid_id, 
                                                   raid_type=raid_type, 
                                                   attendances=updates.updates, 
                                                   context=context)

@router.get("/attendance_service/raid_types")
def get_raid_types(context: UserContext = Depends(get_user_context)):
    logging.info(f"[{context.username}]: Called 'get_raid_types' endpoint - GET Request")
    return attendance_controller.get_raid_types(context=context)

@router.post("/attendance_service/preview")
def preview_attendance(raid_id: RaidID, raid_type: str, payload: AttendancePreviewRequest, context: UserContext = Depends(get_user_context)):
    logging.info(f"[{context.username}]: Called 'preview_attendance' endpoint - POST Request")
    return attendance_controller.get_preview_attendance(raid_id=raid_id, 
                                                        raid_type=raid_type, 
                                                        new_attendances=payload.newAttendances, 
                                                        context=context)

@router.post("/softres_service/fetch_attendance")
def fetch_attendance(link: SoftresRequest, token: dict = Depends(verify_firebase_token)):
    logging.info(f"Called 'fetch_attendance' endpoint - POST Request")
    return attendance_controller.fetch_attendance(link=link)

@router.get("/attendance_service/history")
def get_history_list(raid_id: RaidID, raid_type: str, context: UserContext = Depends(get_user_context)):
    logging.info(f"[{context.username}]: Called 'get_history_list' endpoint - GET Request")
    return attendance_controller.get_history_list(raid_id=raid_id, 
                                                  raid_type=raid_type, 
                                                  context=context)

@router.post("/attendance_service/history/raid")
def get_raid_history(raid_type: str, raid_id: str, history: HistoryObject, context: UserContext = Depends(get_user_context)):
    logging.info(f"[{context.username}]: Called 'get_raid_history' endpoint - POST Request")
    return attendance_controller.get_raid_history(raid_type=raid_type, 
                                                  raid_id=raid_id, 
                                                  history=history, 
                                                  context=context)

@router.post("/attendance_service/list")
def create_new_list(raid_type: str, context: UserContext = Depends(get_user_context)):
    logging.info(f"[{context.username}]: Called 'create_new_list' endpoint - POST Request")
    return attendance_controller.create_new_list(raid_type=raid_type, 
                                                 context=context)

@router.patch("/attendance_service/history/raid")
def rollback_raid(raid_type: str, raid_id: str, rollbacks: ListRollbackItem, context: UserContext = Depends(get_user_context)):
    logging.info(f"[{context.username}]: Called 'rollback_raid' endpoint - PATCH Request")
    return attendance_controller.rollback_raid(raid_type=raid_type, 
                                               raid_id=raid_id, 
                                               rollbacks = rollbacks.rollback, 
                                               context=context)

@router.post("/attendance_service/publish_list")
def publish_list(raid_type: str, raid_id: str, attendance_list: AttendancePublishingList, context: UserContext = Depends(get_user_context)):
    logging.info(f"[{context.username}]: Called 'publish_list' endpoint - GET Request")
    return attendance_controller.publish_list(raid_type=raid_type, 
                                              raid_id=raid_id, 
                                              attendance_list=attendance_list.attendance_list, 
                                              context=context)

@router.get("/attendance_service/get_player_history")
def get_player_history(raid_type: str, raid_id: str, player_name: str, context: UserContext = Depends(get_user_context)):
    logging.info(f"[{context.username}]: Called 'get_player_history' endpoint - GET Request")
    return attendance_controller.get_player_history(raid_type=raid_type,
                                                    raid_id = raid_id,
                                                    player_name=player_name,
                                                    context=context)

@router.post("/attendance_service/registration")
def register_user(user: RegistrationUserCreate, token: dict = Depends(verify_firebase_token)):
    logging.info(f"Called 'register_user' endpoint - POST Request")
    return attendance_controller.register_user(user = user)

app.include_router(router) 