# app/core/catalogs.py

from app.schemas import (
    ConfidenceLevel,
    IncidentCategory,
    IncidentPriority,
    ResponsibleArea,
    SourceChannel,
)

# These catalogs expose the controlled values accepted by the backend.
# They are useful for prompt construction, validation, documentation and tests.
ALLOWED_CATEGORIES = tuple(category.value for category in IncidentCategory)
ALLOWED_PRIORITIES = tuple(priority.value for priority in IncidentPriority)
ALLOWED_RESPONSIBLE_AREAS = tuple(area.value for area in ResponsibleArea)
ALLOWED_CONFIDENCE_LEVELS = tuple(level.value for level in ConfidenceLevel)
ALLOWED_SOURCE_CHANNELS = tuple(channel.value for channel in SourceChannel)


# Priority rules describe the operational meaning of each priority level.
# They will later be injected into the AI prompt so the model classifies
# incidents using consistent support triage criteria.
PRIORITY_RULES: dict[IncidentPriority, str] = {
    IncidentPriority.LOW: (
        "Minor issue with limited impact. The user can continue working "
        "or the incident has a clear workaround."
    ),
    IncidentPriority.MEDIUM: (
        "Issue affecting one user or a small scope. Work is partially blocked, "
        "but there is no confirmed production or security impact."
    ),
    IncidentPriority.HIGH: (
        "Issue blocking important work, affecting several users, or involving "
        "a business-critical application without a full outage."
    ),
    IncidentPriority.CRITICAL: (
        "Major outage, production impact, security risk, data access issue, "
        "or incident affecting many users or critical services."
    ),
}


# Ownership hints help keep the classifier aligned with realistic IT support
# responsibilities. These are not hard rules, but they guide both the mock
# classifier and the future Gemini prompt.
RESPONSIBLE_AREA_HINTS: dict[ResponsibleArea, str] = {
    ResponsibleArea.IT_SUPPORT: (
        "General user support, password resets, device assistance and basic "
        "first-level troubleshooting."
    ),
    ResponsibleArea.INFRASTRUCTURE: (
        "Network, VPN, servers, connectivity, identity infrastructure and "
        "platform availability issues."
    ),
    ResponsibleArea.SECURITY: (
        "Suspicious access, phishing, malware, MFA issues, account compromise "
        "or security policy incidents."
    ),
    ResponsibleArea.DATABASE: (
        "Database errors, query latency, connection failures, locks, backups "
        "or database availability problems."
    ),
    ResponsibleArea.APPLICATIONS: (
        "Application errors, HTTP errors, permissions inside business systems "
        "or feature-specific failures."
    ),
    ResponsibleArea.CLOUD: (
        "Cloud resources, storage buckets, IAM permissions, cloud deployments "
        "or managed service issues."
    ),
}


# Keyword hints are used only by the local mock classifier.
# The real AI integration will be added later, but these terms let us build
# and test the API contract before calling Gemini.
MOCK_CATEGORY_KEYWORDS: dict[IncidentCategory, tuple[str, ...]] = {
    IncidentCategory.VPN: ("vpn", "red privada", "túnel"),
    IncidentCategory.NETWORK: ("internet", "red", "wifi", "conectividad", "latencia"),
    IncidentCategory.ACCESS: ("contraseña", "password", "login", "inicio de sesión", "403", "permisos"),
    IncidentCategory.EMAIL: ("correo", "email", "outlook", "mail"),
    IncidentCategory.HARDWARE: ("laptop", "teclado", "mouse", "monitor", "impresora", "equipo"),
    IncidentCategory.OPERATING_SYSTEM: ("windows", "linux", "sistema operativo", "pantalla azul"),
    IncidentCategory.DATABASE: ("base de datos", "database", "sql", "query", "consulta", "postgres"),
    IncidentCategory.APPLICATIONS: ("aplicación", "sistema", "error 500", "panel", "módulo"),
    IncidentCategory.SECURITY: ("phishing", "malware", "sospechoso", "mfa", "seguridad"),
    IncidentCategory.CLOUD: ("cloud", "bucket", "bigquery", "cloud run", "iam", "gcp"),
}