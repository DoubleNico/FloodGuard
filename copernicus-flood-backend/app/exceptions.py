from __future__ import annotations


class AppError(Exception):
    status_code = 500
    error_code = "internal_error"

    def __init__(self, message: str, *, details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class MissingCredentialsError(AppError):
    status_code = 503
    error_code = "missing_copernicus_credentials"


class ExternalServiceError(AppError):
    status_code = 502
    error_code = "external_service_error"


class NoSceneFoundError(AppError):
    status_code = 404
    error_code = "no_scene_found"


class NoStatisticsError(AppError):
    status_code = 422
    error_code = "no_statistics"

