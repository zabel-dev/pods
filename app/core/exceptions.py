class AppException(Exception):
    def __init__(self, message: str = "Internal server error", status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ValidationError(AppException):
    def __init__(self, message: str = "Validation error"):
        super().__init__(message, status_code=422)

class InvalidCredentialsError(AppException):
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message, status_code=401)


class UserAlreadyExistsError(AppException):
    def __init__(self, message: str = "Email already exists"):
        super().__init__(message, status_code=409)


class ExternalServiceError(AppException):
    def __init__(self, message: str = "External service error"):
        super().__init__(message, status_code=502)

