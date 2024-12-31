from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, Date, Time, JSON, TIMESTAMP, event, ARRAY, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship, declared_attr
from .database import Base
from datetime import datetime
from enum import Enum

# Enums first
class TicketStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    INCOMPLETE = "incomplete"
    CLOSED = "closed"

# Base tables with no foreign keys
class Organization(Base):
    __tablename__ = "organizations"

    organization_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)  # e.g., college, corporate, hotel
    size = Column(Integer, nullable=False)  # e.g., number of occupants
    address = Column(Text, nullable=False)
    gps_coordinates = Column(String(100))  # Latitude/Longitude
    attributes = Column(JSON)  # Flexible field for client-specific data
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)

    users = relationship("User", back_populates="organization")
    staff = relationship("Staff", back_populates="organization")
    locations = relationship("Location", back_populates="organization")

class Location(Base):
    __tablename__ = "locations"

    location_id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.organization_id"), nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)
    capacity = Column(Integer)
    features = Column(JSON)
    status = Column(String(50), default="active")
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)

    organization = relationship("Organization", back_populates="locations")
    tickets = relationship("Ticket", back_populates="location")

# User-related tables
class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.organization_id"), nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    identifier = Column(String(100))
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)

    organization = relationship("Organization", back_populates="users")
    created_tickets = relationship("Ticket", foreign_keys="[Ticket.created_by]", back_populates="creator")
    assigned_tickets = relationship("Ticket", foreign_keys="[Ticket.assigned_to]", back_populates="assignee")

class Staff(Base):
    __tablename__ = "staff"

    staff_id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.organization_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    department = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False)
    skills = Column(ARRAY(String))
    availability = Column(JSON)  # Schedule/availability data
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)

    organization = relationship("Organization", back_populates="staff")
    skills_rel = relationship("StaffSkill", back_populates="staff")

class StaffSkill(Base):
    __tablename__ = "staff_skills"

    skill_id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staff.staff_id"), nullable=False)
    category = Column(String(100), nullable=False)
    level = Column(Integer, nullable=False)
    certifications = Column(ARRAY(String))
    last_updated = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)

    staff = relationship("Staff", back_populates="skills_rel")

# Ticket-related tables
class TicketBase(Base):
    __abstract__ = True
    
    ticket_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(50), nullable=False)
    priority = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)

    # Foreign keys
    location_id = Column(Integer, ForeignKey("locations.location_id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.user_id"), nullable=True)

    # Convert relationships to @declared_attr
    @declared_attr
    def location(cls):
        return relationship("Location", back_populates="tickets")

    @declared_attr
    def creator(cls):
        return relationship("User", foreign_keys=[cls.created_by], back_populates="created_tickets")

    @declared_attr
    def assignee(cls):
        return relationship("User", foreign_keys=[cls.assigned_to], back_populates="assigned_tickets")

    @declared_attr
    def comments(cls):
        return relationship("Comment", back_populates="ticket")

    @declared_attr
    def attachments(cls):
        return relationship("Attachment", back_populates="ticket")

    @declared_attr
    def followup_tasks(cls):
        return relationship("FollowUpTask", back_populates="ticket")

class Ticket(TicketBase):
    __tablename__ = "tickets"
    
    ticket_type = Column(String(50), nullable=False)  # To differentiate between ticket types
    category = Column(String(100))
    subcategory = Column(String(100))

class EmergencyTicket(TicketBase):
    __tablename__ = "emergency_tickets"
    
    emergency_type = Column(String(100), nullable=False)
    response_time = Column(Time, nullable=True)
    resolution_time = Column(Time, nullable=True)

class MaintenanceTicket(TicketBase):
    __tablename__ = "maintenance_tickets"
    
    maintenance_type = Column(String(100), nullable=False)
    scheduled_date = Column(Date, nullable=True)
    completed_date = Column(Date, nullable=True)
    recurrence = Column(String(50))

# Supporting tables
class Comment(Base):
    __tablename__ = "comments"

    comment_id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.ticket_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)

    ticket = relationship("Ticket", back_populates="comments")
    user = relationship("User")

class Attachment(Base):
    __tablename__ = "attachments"

    attachment_id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.ticket_id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)
    uploaded_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    uploaded_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    ticket = relationship("Ticket", back_populates="attachments")
    user = relationship("User")

class FollowUpTask(Base):
    __tablename__ = "followup_tasks"

    task_id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.ticket_id"), nullable=False)
    missing_fields = Column(ARRAY(String))
    priority = Column(String(50), nullable=False)
    due_date = Column(TIMESTAMP, nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    completed_at = Column(TIMESTAMP, nullable=True)
    status = Column(String(50), default="pending")

    ticket = relationship("TicketBase", back_populates="followup_tasks")
    assignee = relationship("User", foreign_keys=[assigned_to])

class IncidentSeverity(Base):
    __tablename__ = "incident_severities"

    severity_id = Column(Integer, primary_key=True, index=True)
    level = Column(Integer, nullable=False)
    description = Column(String(200), nullable=False)
    response_time_threshold = Column(Integer, nullable=False)
    escalation_required = Column(Boolean, default=False)
    notification_groups = Column(ARRAY(String))
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
