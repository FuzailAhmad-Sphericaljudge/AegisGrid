from pydantic import BaseModel, Field, field_validator


class RegisterIn(BaseModel):
    email: str
    password: str = Field(min_length=8)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        email = value.strip().lower()
        if "@" not in email or email.count("@") != 1:
            raise ValueError("Email must contain exactly one @ symbol")
        local_part, domain = email.split("@", 1)
        if not local_part or not domain or "." not in domain and not domain.endswith(".local"):
            raise ValueError("Email must include a valid domain")
        return email


class LoginIn(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        email = value.strip().lower()
        if "@" not in email or email.count("@") != 1:
            raise ValueError("Email must contain exactly one @ symbol")
        local_part, domain = email.split("@", 1)
        if not local_part or not domain or "." not in domain and not domain.endswith(".local"):
            raise ValueError("Email must include a valid domain")
        return email


class ChatIn(BaseModel):
    message: str
    context: dict | None = None


class SimulateIn(BaseModel):
    threat_id: int
    action: str


class RecoveryUpdateIn(BaseModel):
    progress: int = Field(ge=0, le=100)
    status: str | None = None

class ThreatAnalysisIn(BaseModel):
    threat_id: int


class UpdateProfileIn(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    profile_bio: str | None = None
    profile_phone: str | None = None
    avatar: str | None = None  # base64 string
    two_factor_enabled: bool | None = None

class CompleteProfileIn(BaseModel):
    first_name: str
    last_name: str
    profile_bio: str = ""
    profile_phone: str = ""
    avatar: str = ""  # base64 string


class DeviceOut(BaseModel):
    id: int
    device_name: str
    device_type: str
    ip_address: str
    last_active: str
    is_trusted: bool
    
    class Config:
        from_attributes = True


class AuditLogOut(BaseModel):
    id: int
    action: str
    resource_type: str
    status: str
    ip_address: str
    details: str
    created_at: str
    
    class Config:
        from_attributes = True


class NotificationOut(BaseModel):
    id: int
    notification_type: str
    title: str
    message: str
    is_read: bool
    priority: str
    created_at: str
    
    class Config:
        from_attributes = True

