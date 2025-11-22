import json
import os
import csv
from datetime import datetime, timedelta
from models.student import Student, StudentValidator, PerformanceStatus, Grade

class StudentManager:
    def __init__(self, data_file='data/students.json'):
        self.data_file = data_file
        self.students = []
        self.load_students()
    
    def load_students(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as file:
                    data = json.load(file)
                    self.students = [Student.from_dict(student_data) for student_data in data]
            else:
                os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
                self.students = []
        except (json.JSONDecodeError, FileNotFoundError):
            self.students = []
    
    def save_students(self):
        try:
            with open(self.data_file, 'w') as file:
                json.dump([student.to_dict() for student in self.students], file, indent=2)
            return True
        except Exception as e:
            return False
    
    def export_to_csv(self, filename='data/students_export.csv'):
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                if self.students:
                    fieldnames = self.students[0].to_dict().keys()
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writeheader()
                    for student in self.students:
                        writer.writerow(student.to_dict())
            return True, f"Data exported successfully to {filename}"
        except Exception as e:
            return False, f"Error exporting data: {e}"
    
    def import_from_csv(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                imported_count = 0
                errors = []
                
                for i, row in enumerate(reader, 2):
                    validation_errors = StudentValidator.validate_student_data(row)
                    if validation_errors:
                        errors.append(f"Row {i}: {', '.join(validation_errors)}")
                        continue
                    
                    student = Student.from_dict(row)
                    if not any(s.student_id == student.student_id for s in self.students):
                        self.students.append(student)
                        imported_count += 1
                
                if self.save_students():
                    message = f"Successfully imported {imported_count} students"
                    if errors:
                        message += f". {len(errors)} rows had errors"
                    return True, message, errors
                else:
                    return False, "Failed to save imported data", errors
        except Exception as e:
            return False, f"Error importing data: {e}", []
    
    def add_student(self, student):
        if any(s.student_id == student.student_id for s in self.students):
            return False, "Student ID already exists"
        
        self.students.append(student)
        if self.save_students():
            return True, "Student added successfully"
        else:
            self.students.pop()
            return False, "Failed to save student data"
    
    def update_student(self, student_id, **kwargs):
        for student in self.students:
            if student.student_id == student_id:
                for key, value in kwargs.items():
                    if hasattr(student, key):
                        setattr(student, key, value)
                student.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if self.save_students():
                    return True, "Student updated successfully"
                else:
                    return False, "Failed to save updated data"
        return False, "Student not found"
    
    def delete_student(self, student_id):
        for i, student in enumerate(self.students):
            if student.student_id == student_id:
                del self.students[i]
                if self.save_students():
                    return True, "Student deleted successfully"
                else:
                    return False, "Failed to save after deletion"
        return False, "Student not found"
    
    def get_student(self, student_id):
        for student in self.students:
            if student.student_id == student_id:
                return student
        return None
    
    def get_all_students(self):
        return self.students
    
    def search_students(self, query):
        query = query.lower()
        return [student for student in self.students 
                if (query in student.name.lower() or 
                    query in student.email.lower() or
                    query in student.course.lower() or
                    query in student.department.lower() or
                    query in student.phone)]
    
    def filter_by_grade(self, grade):
        return [student for student in self.students if student.grade == grade]
    
    def filter_by_age_range(self, min_age, max_age):
        return [student for student in self.students 
                if min_age <= student.age <= max_age]
    
    def filter_by_performance(self, min_performance, max_performance=100):
        return [student for student in self.students 
                if min_performance <= student.performance <= max_performance]
    
    def filter_by_status(self, status):
        return [student for student in self.students if student.calculate_status() == status]
    
    def filter_by_course(self, course):
        return [student for student in self.students 
                if course.lower() in student.course.lower()]
    
    def filter_by_department(self, department):
        return [student for student in self.students 
                if department.lower() in student.department.lower()]
    
    def filter_recently_added(self, days=7):
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        return [student for student in self.students 
                if student.enrollment_date >= cutoff_date]
    
    def get_statistics(self):
        if not self.students:
            return {}
        
        total_students = len(self.students)
        avg_age = sum(s.age for s in self.students) / total_students
        avg_performance = sum(s.performance for s in self.students) / total_students
        
        grade_distribution = {}
        for grade in [g.value for g in Grade]:
            grade_distribution[grade] = sum(1 for s in self.students if s.grade == grade)
        
        status_distribution = {}
        for status in [s.value for s in PerformanceStatus]:
            status_distribution[status] = len(self.filter_by_status(status))
        
        course_distribution = {}
        department_distribution = {}
        performance_trend = []
        
        for student in self.students:
            course = student.course or "Undeclared"
            department = student.department or "Undeclared"
            
            course_distribution[course] = course_distribution.get(course, 0) + 1
            department_distribution[department] = department_distribution.get(department, 0) + 1
        
        recent_students = self.filter_recently_added(30)
        if recent_students:
            recent_avg = sum(s.performance for s in recent_students) / len(recent_students)
            performance_trend = ["improving" if recent_avg > avg_performance else "declining" if recent_avg < avg_performance else "stable"]
        
        return {
            'total_students': total_students,
            'average_age': round(avg_age, 1),
            'average_performance': round(avg_performance, 1),
            'grade_distribution': grade_distribution,
            'status_distribution': status_distribution,
            'course_distribution': course_distribution,
            'department_distribution': department_distribution,
            'performance_trend': performance_trend,
            'top_performer': max(self.students, key=lambda x: x.performance) if self.students else None,
            'recent_additions': len(recent_students)
        }
    
    def get_next_student_id(self):
        if not self.students:
            return "STU001"
        
        numbers = []
        for student in self.students:
            try:
                num = int(student.student_id[3:])
                numbers.append(num)
            except ValueError:
                continue
        
        next_num = max(numbers) + 1 if numbers else 1
        return f"STU{next_num:03d}"
    
    def bulk_delete_students(self, student_ids):
        initial_count = len(self.students)
        self.students = [s for s in self.students if s.student_id not in student_ids]
        deleted_count = initial_count - len(self.students)
        
        if self.save_students():
            return True, f"Successfully deleted {deleted_count} students"
        else:
            return False, "Failed to save after bulk deletion"
    
    def get_performance_analysis(self):
        if not self.students:
            return {}
        
        performances = [s.performance for s in self.students]
        return {
            'max_performance': max(performances),
            'min_performance': min(performances),
            'median_performance': sorted(performances)[len(performances)//2],
            'pass_rate': (sum(1 for s in self.students if s.performance >= 60) / len(self.students)) * 100
        }