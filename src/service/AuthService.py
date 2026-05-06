from src.db.FirestoreAttendanceRepository import FirestoreAttendanceRepository
from src.schemas.UserContext import UserContext

class AuthService:

    def __init__(self):
        self._attendance_repository = FirestoreAttendanceRepository()

    def get_user_context(self, email):
        return self._attendance_repository.get_user_context(email)