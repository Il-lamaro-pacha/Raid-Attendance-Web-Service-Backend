from src.service.AuthService import AuthService

class AuthController:

    def __init__(self):
        self._auth_service = AuthService()

    def get_user_context(self, email):
        return self._auth_service.get_user_context(email = email)