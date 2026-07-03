# app/utils/api_errors.py

from fastapi import HTTPException, status


def incident_not_found_error() -> HTTPException:
    """Build the standard not-found error for incident lookup."""

    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error": "incident_not_found",
            "message": "No incident was found for the provided incident_id.",
        },
    )


def incident_history_unavailable_error() -> HTTPException:
    """Build the standard error used when BigQuery history cannot be queried."""

    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={
            "error": "incident_history_unavailable",
            "message": "Incident history is temporarily unavailable.",
        },
    )