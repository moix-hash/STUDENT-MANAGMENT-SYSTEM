import re
from datetime import datetime
from enum import Enum

class Grade(Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"

class PerformanceStatus(Enum):
    EXCELLENT = "Excellent"
    GOOD = "Good"
    AVERAGE = "Average"
    NEEDS_IMPROVEMENT = "Needs Improvement"

class Student:
    def __init__(self, student_id, name, age, grade, email, performance, phone="", course="", department="", enrollment_date=None):
        self.student_id = student_id
        self.name = name
        self.age = age
        self.grade = grade
        self.email = email
        self.performance = performance
        self.phone = phone
        self.course = course
        self.department = department
        self.enrollment_date = enrollment_date or datetime.now().strftime("%Y-%m-%d")
        self.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self):
        return {
            'student_id': self.student_id,
            'name': self.name,
            'age': self.age,
            'grade': self.grade,
            'email': self.email,
            'performance': self.performance,
            'phone': self.phone,
            'course': self.course,
            'department': self.department,
            'enrollment_date': self.enrollment_date,
            'last_updated': self.last_updated
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            student_id=data['student_id'],
            name=data['name'],
            age=data['age'],
            grade=data['grade'],
            email=data['email'],
            performance=data['performance'],
            phone=data.get('phone', ''),
            course=data.get('course', ''),
            department=data.get('department', ''),
            enrollment_date=data.get('enrollment_date')
        )
    
    def calculate_status(self):
        if self.performance >= 90:
            return PerformanceStatus.EXCELLENT.value
        elif self.performance >= 75:
            return PerformanceStatus.GOOD.value
        elif self.performance >= 60:
            return PerformanceStatus.AVERAGE.value
        else:
            return PerformanceStatus.NEEDS_IMPROVEMENT.value
    
    def get_performance_color(self):
        status = self.calculate_status()
        colors = {
            PerformanceStatus.EXCELLENT.value: "#10B981",
            PerformanceStatus.GOOD.value: "#3B82F6", 
            PerformanceStatus.AVERAGE.value: "#F59E0B",
            PerformanceStatus.NEEDS_IMPROVEMENT.value: "#EF4444"
        }
        return colors.get(status, "#6B7280")

class StudentValidator:
    
    @staticmethod
    def validate_email(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone):
        pattern = r'^[\+]?[0-9\s\-\(\)]{10,}$'
        return re.match(pattern, phone) is not None if phone else True
    
    @staticmethod
    def validate_name(name):
        return len(name.strip()) >= 2 and all(c.isalpha() or c.isspace() for c in name)
    
    @staticmethod
    def validate_age(age):
        return 15 <= age <= 70
    
    @staticmethod
    def validate_grade(grade):
        return grade in [g.value for g in Grade]
    
    @staticmethod
    def validate_performance(performance):
        return 0 <= performance <= 100
    
    @staticmethod
    def validate_student_data(student_data):
        errors = []
        
        if not StudentValidator.validate_name(student_data.get('name', '')):
            errors.append("Full name must be at least 2 characters long and contain only letters and spaces")
        
        try:
            age = int(student_data.get('age', 0))
            if not StudentValidator.validate_age(age):
                errors.append("Age must be between 15 and 70 years")
        except ValueError:
            errors.append("Age must be a valid number")
        
        if not StudentValidator.validate_grade(student_data.get('grade', '')):
            errors.append("Grade must be one of: A, B, C, D, F")
        
        if not StudentValidator.validate_email(student_data.get('email', '')):
            errors.append("Please enter a valid email address format")
        
        try:
            performance = float(student_data.get('performance', 0))
            if not StudentValidator.validate_performance(performance):
                errors.append("Performance percentage must be between 0 and 100")
        except ValueError:
            errors.append("Performance must be a valid number")
        
        phone = student_data.get('phone', '')
        if phone and not StudentValidator.validate_phone(phone):
            errors.append("Please enter a valid phone number format")
        
        course = student_data.get('course', '')
        if not course or len(course.strip()) < 2:
            errors.append("Course name must be at least 2 characters long")
        
        return errors