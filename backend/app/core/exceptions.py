"""core/exceptions.py — Custom exception hierarchy."""


class AppException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class AuthError(AppException):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, 401)

class NotFoundError(AppException):
    def __init__(self, resource: str = "Resource"):
        super().__init__(f"{resource} not found", 404)

class ValidationError(AppException):
    def __init__(self, message: str):
        super().__init__(message, 422)

class LLMError(AppException):
    def __init__(self, message: str):
        super().__init__(f"AI service error: {message}", 503)

class FileError(AppException):
    def __init__(self, message: str):
        super().__init__(message, 400)

class PermissionError(AppException):
    def __init__(self):
        super().__init__("You don't have permission to access this resource", 403)
