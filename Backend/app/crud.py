from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from . import models, schemas
import logging
from .validators import TicketValidator
from fastapi import HTTPException, status, Depends
from .models import TicketStatus

logger = logging.getLogger(__name__)

# Generic error handling decorator
def db_operation_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IntegrityError as e:
            logger.error(f"Database integrity error in {func.__name__}: {str(e)}")
            raise HTTPException(status_code=400, detail="Database constraint violation")
        except SQLAlchemyError as e:
            logger.error(f"Database error in {func.__name__}: {str(e)}")
            raise HTTPException(status_code=500, detail="Database operation failed")
    return wrapper

# Staff Operations
@db_operation_handler
def create_staff(db: Session, staff: schemas.StaffCreate) -> models.Staff:
    db_staff = models.Staff(**staff.dict())
    db.add(db_staff)
    db.commit()
    db.refresh(db_staff)
    return db_staff

@db_operation_handler
def get_staff(db: Session, staff_id: int) -> Optional[models.Staff]:
    return db.query(models.Staff).filter(
        models.Staff.staff_id == staff_id,
        models.Staff.is_deleted == False
    ).first()

@db_operation_handler
def get_available_staff(db: Session, skill_category: Optional[str] = None) -> List[models.Staff]:
    query = db.query(models.Staff).filter(models.Staff.is_on_job == False)
    if skill_category:
        query = query.join(models.StaffSkill).filter(
            models.StaffSkill.category == skill_category
        )
    return query.all()

# Location Operations
@db_operation_handler
def create_location(db: Session, location: schemas.LocationCreate) -> models.Location:
    db_location = models.Location(**location.dict())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location

@db_operation_handler
def get_organization_locations(
    db: Session, 
    organization_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[models.Location]:
    return db.query(models.Location).filter(
        models.Location.organization_id == organization_id,
        models.Location.is_deleted == False
    ).offset(skip).limit(limit).all()

# Emergency Ticket Operations
@db_operation_handler
def create_emergency_ticket(
    db: Session, 
    ticket: schemas.EmergencyTicketCreate
) -> models.EmergencyTicket:
    db_ticket = models.EmergencyTicket(**ticket.dict())
    db_ticket.created_at = datetime.utcnow()
    
    # Create associated ticket log
    ticket_log = models.TicketLog(
        ticket_id=db_ticket.ticket_id,
        action="created",
        log_timestamp=datetime.utcnow()
    )
    
    db.add(db_ticket)
    db.add(ticket_log)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

@db_operation_handler
def assign_emergency_ticket(
    db: Session,
    ticket_id: int,
    staff_id: int,
    estimated_response_time: int
) -> models.EmergencyTicket:
    ticket = db.query(models.EmergencyTicket).filter(
        models.EmergencyTicket.ticket_id == ticket_id
    ).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    ticket.assigned_staff_id = staff_id
    ticket.estimated_response_time = estimated_response_time
    ticket.status = "assigned"
    
    # Update staff status
    staff = db.query(models.Staff).filter(models.Staff.staff_id == staff_id).first()
    if staff:
        staff.is_on_job = True
    
    # Log the assignment
    ticket_log = models.TicketLog(
        ticket_id=ticket_id,
        action="assigned",
        performed_by=staff_id,
        log_timestamp=datetime.utcnow()
    )
    
    db.add(ticket_log)
    db.commit()
    db.refresh(ticket)
    return ticket

# Enhanced Organization Operations
@db_operation_handler
def update_organization(
    db: Session,
    organization_id: int,
    updates: schemas.OrganizationUpdate
) -> Optional[models.Organization]:
    db_organization = get_organization(db, organization_id)
    if db_organization:
        update_data = updates.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_organization, key, value)
        db.commit()
        db.refresh(db_organization)
    return db_organization

@db_operation_handler
def soft_delete_organization(
    db: Session,
    organization_id: int
) -> bool:
    db_organization = get_organization(db, organization_id)
    if db_organization:
        # Soft delete related entities
        db.query(models.User).filter(
            models.User.organization_id == organization_id
        ).update({"is_deleted": True})
        
        db.query(models.Location).filter(
            models.Location.organization_id == organization_id
        ).update({"is_deleted": True})
        
        # Mark organization as deleted
        db_organization.is_deleted = True
        db.commit()
        return True
    return False

# Ticket Statistics
@db_operation_handler
def get_organization_ticket_stats(
    db: Session,
    organization_id: int
) -> dict:
    total_tickets = db.query(models.EmergencyTicket).filter(
        models.EmergencyTicket.organization_id == organization_id
    ).count()
    
    open_tickets = db.query(models.EmergencyTicket).filter(
        models.EmergencyTicket.organization_id == organization_id,
        models.EmergencyTicket.status.in_(["pending", "assigned"])
    ).count()
    
    return {
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "resolution_rate": (total_tickets - open_tickets) / total_tickets if total_tickets > 0 else 0
    }

@db_operation_handler
def create_ticket(db: Session, ticket_data: dict) -> models.TicketBase:
    ticket_type = ticket_data.get("ticket_type", "emergency")
    
    # Validate required fields
    validator = TicketValidator()
    required_fields = validator.get_required_fields(ticket_type)
    completion_status = validator.validate_completion(ticket_data, required_fields)
    
    # Set initial status
    initial_status = (TicketStatus.PENDING 
                     if all(completion_status.values()) 
                     else TicketStatus.INCOMPLETE)
    
    # Create appropriate ticket type
    if ticket_type == "emergency":
        db_ticket = models.EmergencyTicket(
            **ticket_data,
            status=initial_status,
            required_fields_status=completion_status
        )
    else:
        db_ticket = models.MaintenanceTicket(
            **ticket_data,
            status=initial_status,
            required_fields_status=completion_status
        )
    
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    
    # Create follow-up task if incomplete
    if initial_status == TicketStatus.INCOMPLETE:
        missing_fields = [f for f, v in completion_status.items() if not v]
        create_followup_task(db, db_ticket.ticket_id, missing_fields)
    
    return db_ticket

def create_followup_task(db: Session, ticket_id: int, missing_fields: Dict[str, bool]):
    """Create a follow-up task for incomplete tickets"""
    missing = [field for field, complete in missing_fields.items() if not complete]
    task = models.FollowUpTask(
        ticket_id=ticket_id,
        missing_fields=missing,
        due_date=datetime.utcnow() + timedelta(days=1),
        priority="high" if "emergency_level" in missing else "medium"
    )
    db.add(task)
    db.commit()

# FollowUpTask Operations
@db_operation_handler
def create_followup_task(db: Session, task_data: dict) -> models.FollowUpTask:
    db_task = models.FollowUpTask(**task_data)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@db_operation_handler
def get_followup_tasks(db: Session, ticket_id: int) -> List[models.FollowUpTask]:
    return db.query(models.FollowUpTask).filter(
        models.FollowUpTask.ticket_id == ticket_id
    ).all()

# StaffSkill Operations
@db_operation_handler
def create_staff_skill(db: Session, skill_data: dict) -> models.StaffSkill:
    db_skill = models.StaffSkill(**skill_data)
    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)
    return db_skill

@db_operation_handler
def get_staff_skills(db: Session, staff_id: int) -> List[models.StaffSkill]:
    return db.query(models.StaffSkill).filter(
        models.StaffSkill.staff_id == staff_id
    ).all()

# IncidentSeverity Operations
@db_operation_handler
def create_incident_severity(db: Session, severity_data: dict) -> models.IncidentSeverity:
    db_severity = models.IncidentSeverity(**severity_data)
    db.add(db_severity)
    db.commit()
    db.refresh(db_severity)
    return db_severity

@db_operation_handler
def get_incident_severities(db: Session) -> List[models.IncidentSeverity]:
    return db.query(models.IncidentSeverity).all()

def get_organization(db: Session, organization_id: int):
    return db.query(models.Organization).filter(models.Organization.organization_id == organization_id).first()
