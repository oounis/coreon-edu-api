from .org_core import (
    OrganizationType,
    ProductModule,
    SchoolModule,
    DepartmentType,
    Department,
)
from .school_core import School
from .rbac_core import (
    Permission,
    Role,
    RolePermission,
    UserRole,
)
from .workflow_core import (
    WorkflowDefinition,
    WorkflowStep,
    Request,
    RequestApproval,
)
from .audit_core import AuditLog
from .user_core import (
    User,
    StaffProfile,
    ParentProfile,
    StudentProfile,
)
from .academic_core import (
    AcademicYear,
    EducationalStage,
    Grade,
    Classroom,
    StudentParent,
)
from .nursery_core import (
    NurseryDailyReport,
    NurseryIncident,
)
from .transport_core import (
    Bus,
    Driver,
    Route,
    RouteStop,
    BusAssignment,
    TransportSubscription,
    BusAttendance,
)
from .health_core import (
    HealthProfile,
    MedicalVisit,
    MedicationRecord,
    HealthIncident,
)
from .counseling_core import (
    CounselingSession,
    BehaviorNote,
    CounselingReferral,
)
from .finance_core import (
    FeeStructure,
    StudentFee,
    Discount,
    StudentDiscount,
    Invoice,
    Payment,
)
from .hr_core import (
    StaffContract,
    StaffAttendance,
    LeaveRequest,
    StaffDocument,
)
from .purchasing_core import (
    Supplier,
    PurchaseItem,
    PurchaseOrder,
    PurchaseOrderItem,
    PurchaseRequest,
)
from .facilities_core import (
    FacilityRoom,
    Asset,
    MaintenanceRequest,
    MaintenanceAssignment,
)
from .activities_core import (
    ActivityClub,
    ClubEnrollment,
    ActivityEvent,
    Achievement,
)
from .security_core import SecurityPost
from .security_gate import GateAccessLog
from .security_visitors import Visitor, VisitorVisit
from .security_incidents import SecurityIncident
from .security_dismissal import StudentDismissalLog
from .security_vehicle import VehicleAccess, VehicleAccessLog
from .security_shifts import GuardShift
from .notification_core import (
    Notification,
    NotificationPreference,
    NotificationTemplate,
)

# Auto-added missing model imports
from .behavior_core import BehaviorIncident, BehaviorActionPlan
from .procurement_extra import Vendor, RFQ, Quotation
from .payroll_extra import PayrollBonus, PayrollDeduction
from .behavior_core import BehaviorIncident, BehaviorActionPlan
from .payroll_extra import PayrollBonus, PayrollDeduction
from .procurement_extra import Vendor, RFQ, Quotation
