from .event_bus import event_bus
from .handlers.notification_handler import notification_handler
from .handlers.audit_handler import audit_handler
from .types import (
    WorkflowEvents,
    FinanceEvents,
    SecurityEvents,
    NurseryEvents,
    HREvents,
    TransportEvents,
    ActivityEvents,
    OrgEvents,
    UserEvents,
    StudentEvents,
    AcademicEvents,
)

# Workflow
event_bus.subscribe(WorkflowEvents.APPROVAL_PENDING, notification_handler)
event_bus.subscribe(WorkflowEvents.APPROVAL_DECISION, notification_handler)

# Finance
event_bus.subscribe(FinanceEvents.INVOICE_CREATED, notification_handler)
event_bus.subscribe(FinanceEvents.PAYMENT_RECEIVED, notification_handler)

# Security
event_bus.subscribe(SecurityEvents.INCIDENT_REPORTED, notification_handler)
event_bus.subscribe(SecurityEvents.GATE_ACCESS, audit_handler)

# Nursery
event_bus.subscribe(NurseryEvents.DAILY_REPORT_SUBMITTED, notification_handler)
event_bus.subscribe(NurseryEvents.INCIDENT_CREATED, notification_handler)

# HR
event_bus.subscribe(HREvents.LEAVE_REQUEST_CREATED, notification_handler)

# Transport
event_bus.subscribe(TransportEvents.BUS_ATTENDANCE, notification_handler)

# Activities
event_bus.subscribe(ActivityEvents.CLUB_EVENT_CREATED, notification_handler)

# Org
event_bus.subscribe(OrgEvents.SCHOOL_CREATED, notification_handler)
event_bus.subscribe(OrgEvents.DEPARTMENT_CREATED, notification_handler)

# Users
event_bus.subscribe(UserEvents.USER_CREATED, notification_handler)
event_bus.subscribe(UserEvents.ROLE_ASSIGNED, notification_handler)

# Students
event_bus.subscribe(StudentEvents.STUDENT_ENROLLED, notification_handler)
event_bus.subscribe(StudentEvents.STUDENT_PROMOTED, notification_handler)

# Academics
event_bus.subscribe(AcademicEvents.CLASSROOM_ASSIGNED, notification_handler)
event_bus.subscribe(AcademicEvents.YEAR_CREATED, notification_handler)
