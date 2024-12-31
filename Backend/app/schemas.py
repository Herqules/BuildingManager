from pydantic import BaseModel, validator, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class TicketBase(BaseModel):
    description: str
    category: str
    subcategory: Optional[str]
    priority_level: int
    location_coordinates: Optional[str]
    images: Optional[List[str]]

class EmergencyTicketCreate(TicketBase):
    emergency_level: int
    immediate_response_needed: bool = False
    evacuation_required: bool = False
    safety_measures_taken: Optional[str]
    emergency_contacts_notified: Optional[Dict[str, Any]]

class TicketFieldsUpdate(BaseModel):
    fields: Dict[str, Any]
    notes: Optional[str]

    @validator('fields')
    def validate_fields(cls, v):
        allowed_fields = {
            'description', 'safety_measures_taken', 
            'emergency_level', 'location_coordinates'
        }
        if not all(k in allowed_fields for k in v.keys()):
            raise ValueError("Invalid field updates")
        return v

class StaffCreate(BaseModel):
    name: str
    department: str
    role: str
    skills: List[str]
    availability: Dict[str, Any]
    contact_info: Dict[str, str]
    emergency_contact: Optional[Dict[str, str]]

class StaffUpdate(BaseModel):
    department: Optional[str]
    role: Optional[str]
    skills: Optional[List[str]]
    availability: Optional[Dict[str, Any]]
    is_active: Optional[bool]

class LocationCreate(BaseModel):
    name: str
    type: str
    capacity: Optional[int]
    features: Dict[str, Any]
    status: str = "active"
    coordinates: Optional[Dict[str, float]]
    access_requirements: Optional[Dict[str, Any]]

class LocationUpdate(BaseModel):
    name: Optional[str]
    type: Optional[str]
    capacity: Optional[int]
    features: Optional[Dict[str, Any]]
    status: Optional[str]
    access_requirements: Optional[Dict[str, Any]]

class OrganizationBase(BaseModel):
    name: str
    type: str
    size: int
    address: str
    gps_coordinates: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None

class OrganizationCreate(OrganizationBase):
    pass

class Organization(BaseModel):
    organization_id: int
    name: str
    type: str
    size: int
    address: str
    gps_coordinates: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None  # Maps to JSONB in PostgreSQL
    created_at: datetime

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str
    organization_id: int
    identifier: Optional[str]
    contact_info: Dict[str, str]

class UserUpdate(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    role: Optional[str]
    identifier: Optional[str]
    contact_info: Optional[Dict[str, str]]
    is_active: Optional[bool]

class CommentCreate(BaseModel):
    content: str
    ticket_id: int
    user_id: int
    attachment_ids: Optional[List[int]]

class AttachmentCreate(BaseModel):
    file_name: str
    file_type: str
    file_size: int
    file_path: str
    ticket_id: int
    uploaded_by: int

class TicketResponse(BaseModel):
    ticket_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    assigned_to: Optional[Dict[str, Any]]
    location: Dict[str, Any]
    comments: List[Dict[str, Any]]
    attachments: List[Dict[str, Any]]

    class Config:
        orm_mode = True

class EmergencyTicketResponse(TicketResponse):
    emergency_level: int
    response_time: Optional[datetime]
    resolution_time: Optional[datetime]
    safety_measures: Dict[str, Any]

class TicketStats(BaseModel):
    total_tickets: int
    open_tickets: int
    resolution_rate: float
    average_response_time: Optional[float]
    emergency_distribution: Dict[str, int]

class FollowUpTaskCreate(BaseModel):
    ticket_id: int
    missing_fields: List[str]
    priority: str
    due_date: datetime
    assigned_to: Optional[int]

class StaffSkillCreate(BaseModel):
    staff_id: int
    category: str
    level: int
    certifications: Optional[List[str]]
    last_updated: datetime

class IncidentSeverityCreate(BaseModel):
    level: int
    description: str
    response_time_threshold: int
    escalation_required: bool
    notification_groups: List[str]

class OrganizationUpdate(OrganizationBase):
    name: Optional[str] = None
    type: Optional[str] = None
    size: Optional[int] = None
    address: Optional[str] = None
    gps_coordinates: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
