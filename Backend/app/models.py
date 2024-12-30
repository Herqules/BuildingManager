from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, Date, Time, JSON, TIMESTAMP
from sqlalchemy.orm import relationship
from .database import Base

# Organizations Table
class Organization(Base):
    __tablename__ = "organizations"

    organization_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)  # e.g., college, corporate, hotel
    size = Column(Integer, nullable=False)  # e.g., number of occupants
    address = Column(Text, nullable=False)
    gps_coordinates = Column(String(100))  # Latitude/Longitude
    attributes = Column(JSON)  # Flexible field for client-specific data
    created_at = Column(TIMESTAMP, nullable=False)

    users = relationship("User", back_populates="organization")
    staff = relationship("Staff", back_populates="organization")
    locations = relationship("Location", back_populates="organization")

# Users Table
class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.organization_id"), nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # e.g., student, staff, admin
    identifier = Column(String(100))  # Student ID, employee ID, room number, etc.
    created_at = Column(TIMESTAMP, nullable=False)
    is_deleted = Column(Boolean, default=False)

    organization = relationship("Organization", back_populates="users")

# Locations Table
class Location(Base):
    __tablename__ = "locations"

    location_id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.organization_id"), nullable=False)
    name = Column(String(100), nullable=False)  # e.g., "Dorm A" or "Building 3"
    type = Column(String(50), nullable=False)  # e.g., dorm, office, classroom
    gps_coordinates = Column(String(100))  # Latitude/Longitude for mapping
    floor_number = Column(Integer)  # Optional for multi-floor buildings
    room_number = Column(String(50))  # Optional for specific rooms
    address = Column(Text, nullable=False)
    is_deleted = Column(Boolean, default=False)

    organization = relationship("Organization", back_populates="locations")

# Staff Table
class Staff(Base):
    __tablename__ = "staff"

    staff_id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.organization_id"), nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20))  # Optional contact field
    office_location = Column(Text)  # Normal base or office location
    is_on_job = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, nullable=False)

    organization = relationship("Organization", back_populates="staff")

# Staff Skills Table
class StaffSkill(Base):
    __tablename__ = "staff_skills"

    skill_id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staff.staff_id", ondelete="CASCADE"), nullable=False)
    category = Column(String(50), nullable=False)  # e.g., plumbing, IT support
    subcategory = Column(String(50))  # Optional subcategory
    skill_level = Column(String(20), nullable=False)  # e.g., beginner, intermediate, expert

# Tickets Table
class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    location_id = Column(Integer, ForeignKey("locations.location_id"), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="open")
    urgency_score = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=False)
    is_deleted = Column(Boolean, default=False)

# Emergency Tickets Table
class EmergencyTicket(Base):
    __tablename__ = "emergency_tickets"

    ticket_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.organization_id", ondelete="CASCADE"), nullable=False)
    user_input_location = Column(Text, nullable=False)
    matched_location = Column(Text)
    location_type = Column(String(50))
    location_details = Column(Text)
    description = Column(String(400), nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    created_date = Column(TIMESTAMP, nullable=False)
    user_name = Column(String(100), nullable=False)
    user_contact = Column(String(100), nullable=False)
    identifier = Column(String(100))
    severity_id = Column(Integer, ForeignKey("incident_severity.severity_id"))
    assigned_staff_id = Column(Integer, ForeignKey("staff.staff_id", ondelete="SET NULL"))
    estimated_response_time = Column(Integer)
    created_at = Column(TIMESTAMP, nullable=False)
    is_deleted = Column(Boolean, default=False)

# Incident Severity Table
class IncidentSeverity(Base):
    __tablename__ = "incident_severity"

    severity_id = Column(Integer, primary_key=True, index=True)
    level = Column(String(50), nullable=False)  # e.g., low, medium, high, critical
    response_time = Column(Integer, nullable=False)  # Expected response time in minutes
    description = Column(Text)
    color_code = Column(String(7))  # For UI indication
    priority_level = Column(Integer)

# Ticket Logs Table
class TicketLog(Base):
    __tablename__ = "ticket_logs"

    log_id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("emergency_tickets.ticket_id", ondelete="CASCADE"), nullable=False)
    action = Column(String(50), nullable=False)  # e.g., created, updated, resolved
    performed_by = Column(Integer, ForeignKey("staff.staff_id"))
    log_timestamp = Column(TIMESTAMP, nullable=False)
