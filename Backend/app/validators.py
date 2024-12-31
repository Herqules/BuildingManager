from typing import Dict, List
from datetime import datetime

class TicketValidator:
    @staticmethod
    def get_required_fields(ticket_type: str) -> Dict[str, bool]:
        base_fields = {
            "description": True,
            "category": True,
            "priority_level": True
        }
        
        if ticket_type == "emergency":
            base_fields.update({
                "emergency_level": True,
                "safety_measures_taken": True
            })
        elif ticket_type == "maintenance":
            base_fields.update({
                "scheduled_maintenance_date": True,
                "maintenance_type": True
            })
        
        return base_fields

    @staticmethod
    def validate_completion(ticket_data: dict, required_fields: Dict[str, bool]) -> Dict[str, bool]:
        completion_status = {}
        for field, required in required_fields.items():
            if required:
                completion_status[field] = bool(ticket_data.get(field))
        return completion_status

    @staticmethod
    def validate_ticket_update(current_status: str, new_status: str) -> bool:
        valid_transitions = {
            "draft": ["pending", "incomplete"],
            "incomplete": ["pending", "needs_info"],
            "pending": ["assigned", "needs_info"],
            "assigned": ["in_progress", "needs_info"],
            "in_progress": ["resolved", "needs_info"],
            "needs_info": ["pending", "incomplete"],
            "resolved": ["closed", "in_progress"],
        }
        return new_status in valid_transitions.get(current_status, []) 
