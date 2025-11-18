from enum import Enum

class Role(str, Enum):
    SUPER_ADMIN = "super_admin"
    SCHOOL_ADMIN = "school_admin"
    PRINCIPAL = "principal"
    SUPERVISOR = "supervisor"
    TEACHER = "teacher"
    ACCOUNTANT = "accountant"
    HR = "hr"
    LIBRARIAN = "librarian"
    NURSE = "nurse"
    TRANSPORT = "transport"
    PARENT = "parent"
    STUDENT = "student"
