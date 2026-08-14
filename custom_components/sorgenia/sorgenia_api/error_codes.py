"""Error-code catalogue extracted from the decompiled Sorgenia app.

The server can introduce additional codes; unknown codes remain available on
``SorgeniaApiError.error_code`` and are never discarded.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ApiErrorInfo:
    """Describe a Sorgenia error code and where it can occur."""

    code: str
    name: str
    description: str
    areas: tuple[str, ...]


def _item(code: str, name: str, description: str, *areas: str) -> ApiErrorInfo:
    return ApiErrorInfo(code, name, description, areas)


ERROR_CODES: dict[str, ApiErrorInfo] = {
    "001": _item(
        "001",
        "INVALID_CREDENTIALS_OR_FIELD",
        "Password, client type, or mandatory field is invalid",
        "login",
        "password",
        "otp",
    ),
    "002": _item("002", "EXPIRED_PASSWORD", "Password expired", "login", "otp"),
    "009": _item("009", "USERNAME_NOT_VALID", "Username is not valid", "recovery", "reset-password"),
    "010": _item("010", "USERNAME_NOT_EXISTING", "Username does not exist", "login", "reset-password"),
    "022": _item("022", "UNKNOWN_EMAIL", "Email is unknown", "recovery"),
    "036": _item("036", "GENESYS_UNAVAILABLE", "Genesys service unavailable", "videocall"),
    "080": _item("080", "INVALID_MIGRATION_CODE", "Migration code is invalid", "fiber"),
    "083": _item("083", "INVALID_FIELDS", "One or more fields are invalid", "fiber"),
    "400": _item("400", "MANDATORY_FIELD", "Mandatory field is missing", "login", "otp", "videocall"),
    "405": _item("405", "USER_ALREADY_REGISTERED", "User is already registered", "registration"),
    "412": _item("412", "UNKNOWN_TAX_CODE", "Tax code is unknown", "recovery"),
    "1004": _item("1004", "LOGIN_LOCKED", "Login is locked", "login"),
    "1015": _item("1015", "ACCOUNT_NOT_READY", "Account is not ready", "login"),
    "1044": _item("1044", "MANDATORY_USERNAME", "Username is mandatory", "password"),
    "1075": _item("1075", "MISSING_TOKEN_ID", "Token ID is missing", "videocall"),
    "1077": _item("1077", "MISSING_DEVICE_TYPE", "Device type is missing", "videocall"),
    "1078": _item("1078", "WRONG_DEVICE_TYPE", "Device type is invalid", "videocall"),
    "1080": _item("1080", "MISSING_CLIENT_LIST", "Client list is missing", "videocall"),
    "1081": _item("1081", "MISSING_CLIENT_NAME", "Client name is missing", "videocall"),
    "1082": _item("1082", "MISSING_CLIENT_SURNAME", "Client surname is missing", "videocall"),
    "1083": _item("1083", "MISSING_JOURNEY", "Journey is missing", "videocall"),
    "1122": _item("1122", "MANDATORY_OLD_PASSWORD", "Old password is mandatory", "password"),
    "1123": _item("1123", "MANDATORY_NEW_PASSWORD", "New password is mandatory", "password"),
    "1126": _item("1126", "PASSWORD_MATCH", "New password must differ from old password", "password"),
    "1127": _item("1127", "USERNAME_NOT_FOUND", "Username was not found", "password"),
    "1168": _item("1168", "USER_ALREADY_EXISTING", "User already exists", "registration"),
    "1172": _item(
        "1172", "USERNAME_ALREADY_REGISTERED_NOT_VALID", "Username is already registered or invalid", "registration"
    ),
    "1173": _item("1173", "USERNAME_ALREADY_REGISTERED", "Username is already registered", "registration"),
    "1174": _item("1174", "FISCAL_CODE_OR_VAT_NOT_EXISTING", "Tax code or VAT number does not exist", "registration"),
    "1175": _item("1175", "CLIENT_CODE_NOT_EXISTING", "Client code does not exist", "registration"),
    "1176": _item(
        "1176",
        "CLIENT_CODE_FISCAL_CODE_MISMATCH",
        "Client code and tax code association does not exist",
        "registration",
    ),
    "1177": _item("1177", "OTP_WRONG", "OTP validation failed", "otp", "registration"),
    "1178": _item("1178", "FISCAL_CODE_NOT_VALID", "Tax code is not valid", "registration"),
    "1179": _item("1179", "VAT_NOT_VALID", "VAT number is not valid", "registration"),
    "1180": _item("1180", "USERNAME_NOT_VALID", "Username is not valid", "login"),
    "1181": _item("1181", "OTP_NUMBER_VALIDATION", "OTP number validation is required", "login", "refresh"),
    "1182": _item("1182", "PHONE_NOT_VALID", "Phone number is not valid", "otp"),
    "1183": _item("1183", "PHONE_ALREADY_USED", "Phone number is already used", "otp"),
    "1184": _item("1184", "PHONE_IN_BLACKLIST", "Phone number is blacklisted", "otp"),
    "1185": _item("1185", "OTP_BACKEND_ERROR", "OTP backend error", "otp"),
    "1186": _item("1186", "OTP_PROVIDER_ERROR", "OTP provider error", "otp"),
    "1187": _item("1187", "OTP_NOT_MOST_RECENT", "OTP is not the most recent one", "otp", "registration"),
    "1188": _item("1188", "PHONE_OTP_LOCKED", "OTP sending is locked for this phone", "otp"),
    "1189": _item("1189", "OTP_TOO_MANY_ATTEMPTS", "Too many OTP attempts", "otp", "registration"),
    "1191": _item("1191", "PHONE_NUMBER_MISMATCH", "Phone number does not match", "login", "refresh"),
    "1192": _item("1192", "OTP_VALIDATION_REQUIRED", "Phone OTP validation is required", "login"),
    "5001": _item("5001", "USERNAME_MANDATORY", "Username is mandatory", "reset-password"),
    "5002": _item("5002", "USERNAME_EMAIL_NOT_MATCHING", "Username and email do not match", "reset-password"),
    "5007": _item("5007", "EMAIL_NOT_VALID", "Email is not valid", "reset-password"),
    "5008": _item("5008", "EMAIL_MANDATORY", "Email is mandatory", "reset-password"),
    "invalid_token": _item("invalid_token", "INVALID_BIDGELY_TOKEN", "Bidgely access token is invalid", "bidgely"),
    "chat.error.notnull.createconversationrequest.provider": _item(
        "chat.error.notnull.createconversationrequest.provider",
        "MISSING_CHAT_PROVIDER",
        "Chat provider is mandatory",
        "videocall",
    ),
    "bad.credentials": _item("bad.credentials", "BAD_CHAT_CREDENTIALS", "Chat credentials are invalid", "videocall"),
    "missing.division.permission": _item(
        "missing.division.permission", "MISSING_DIVISION_PERMISSION", "Division permission is missing", "videocall"
    ),
    "not.found": _item("not.found", "RESOURCE_NOT_FOUND", "Requested resource was not found", "videocall"),
    "client.timeout": _item("client.timeout", "CLIENT_TIMEOUT", "Client request timed out", "videocall"),
    "request.entity.too.large": _item(
        "request.entity.too.large", "REQUEST_ENTITY_TOO_LARGE", "Request entity is too large", "videocall"
    ),
    "unsupported.media.type": _item(
        "unsupported.media.type", "UNSUPPORTED_MEDIA_TYPE", "Media type is unsupported", "videocall"
    ),
    "too.many.requests.retry.after": _item(
        "too.many.requests.retry.after", "TOO_MANY_REQUESTS", "Too many requests; retry later", "videocall"
    ),
    "internal.server.error": _item("internal.server.error", "REMOTE_SERVER_ERROR", "Remote server error", "videocall"),
    "service.unavailable": _item("service.unavailable", "SERVICE_UNAVAILABLE", "Service unavailable", "videocall"),
    "request.timeout": _item("request.timeout", "REQUEST_TIMEOUT", "Request timed out", "videocall"),
}

# Public, descriptive alias used by the package API.
API_ERROR_CODES = ERROR_CODES


def describe_error(code: str | None) -> ApiErrorInfo | None:
    """Return the catalogue entry for an error code, when known."""
    return ERROR_CODES.get(str(code)) if code is not None else None
