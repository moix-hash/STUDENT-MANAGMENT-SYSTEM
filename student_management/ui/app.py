import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import base64
import time
from enum import Enum
import io
import numpy as np


class PerformanceStatus(Enum):
    EXCELLENT = " Excellent"
    GOOD = " Good" 
    AVERAGE = " Average"
    NEEDS_IMPROVEMENT = " Needs Improvement"

class Grade(Enum):
    A = "A"
    B = "B"
    C = "C" 
    D = "D"
    F = "F"

class AttendanceStatus(Enum):
    EXCELLENT = " Excellent"
    GOOD = " Good"
    AVERAGE = " Average" 
    POOR = " Poor"

class Student:
    def __init__(self, student_id, name, age, grade, email, performance, phone="", course="", department="", enrollment_date="", attendance=95.0):
        self.student_id = student_id
        self.name = name
        self.age = age
        self.grade = grade
        self.email = email
        self.performance = performance
        self.phone = phone
        self.course = course
        self.department = department
        self.enrollment_date = enrollment_date
        self.attendance = attendance
        self.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.activities = []
    
    def calculate_status(self):
        if self.performance >= 90:
            return PerformanceStatus.EXCELLENT.value
        elif self.performance >= 75:
            return PerformanceStatus.GOOD.value
        elif self.performance >= 60:
            return PerformanceStatus.AVERAGE.value
        else:
            return PerformanceStatus.NEEDS_IMPROVEMENT.value
    
    def calculate_attendance_status(self):
        if self.attendance >= 95:
            return AttendanceStatus.EXCELLENT.value
        elif self.attendance >= 85:
            return AttendanceStatus.GOOD.value
        elif self.attendance >= 75:
            return AttendanceStatus.AVERAGE.value
        else:
            return AttendanceStatus.POOR.value
    
    def add_activity(self, activity_type, description, date=None):
        activity = {
            'type': activity_type,
            'description': description,
            'date': date or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'id': len(self.activities) + 1
        }
        self.activities.append(activity)
        return activity
    
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
            'attendance': self.attendance,
            'last_updated': self.last_updated,
            'activities': self.activities
        }

class StudentValidator:
    @staticmethod
    def validate_student_data(data):
        errors = []
        if not data.get('name') or len(data['name'].strip()) < 2:
            errors.append("Name must be at least 2 characters long")
        if not data.get('age') or data['age'] < 15 or data['age'] > 70:
            errors.append("Age must be between 15 and 70")
        if not data.get('email') or '@' not in data['email']:
            errors.append("Valid email address is required")
        if not data.get('performance') or data['performance'] < 0 or data['performance'] > 100:
            errors.append("Academic MentorDesk score must be between 0 and 100")
        if not data.get('course') or len(data['course'].strip()) < 2:
            errors.append("Course must be at least 2 characters long")
        if data.get('attendance') and (data['attendance'] < 0 or data['attendance'] > 100):
            errors.append("Attendance must be between 0 and 100")
        return errors

class AdvancedStudentManager:
    def __init__(self):
        self.students = []
        self.analytics_data = {}
        self.cache_stats = None
        self.cache_time = None
        self.load_sample_data()
    
    def load_sample_data(self):
        
        sample_students = [
            Student("ST001", "Aarav Sharma", 20, Grade.A.value, "aarav.sharma@university.edu", 92.0, "+91 9876543210", 
                   "Computer Science", "Engineering", "2023-09-01", 96.5),
            Student("ST002", "Priya Patel", 22, Grade.B.value, "priya.patel@university.edu", 78.5, "+91 9876543211", 
                   "Data Science", "Computer Science", "2023-09-01", 88.2),
            Student("ST003", "Rohan Kumar", 21, Grade.A.value, "rohan.kumar@university.edu", 88.0, "+91 9876543212", 
                   "Artificial Intelligence", "Computer Science", "2023-09-01", 94.7),
            Student("ST004", "Ananya Singh", 19, Grade.C.value, "ananya.singh@university.edu", 65.5, "+91 9876543213", 
                   "Biology", "Life Sciences", "2023-09-01", 92.1),
            Student("ST005", "Vikram Joshi", 23, Grade.B.value, "vikram.joshi@university.edu", 72.0, "+91 9876543214", 
                   "Mechanical Engineering", "Engineering", "2023-09-01", 85.4),
            Student("ST006", "Neha Gupta", 20, Grade.A.value, "neha.gupta@university.edu", 95.0, "+91 9876543215", 
                   "Business Administration", "Business", "2023-09-01", 98.2),
            Student("ST007", "Arun Mishra", 22, Grade.C.value, "arun.mishra@university.edu", 62.0, "+91 9876543216", 
                   "Chemistry", "Science", "2023-09-01", 76.8),
            Student("ST008", "Pooja Reddy", 21, Grade.B.value, "pooja.reddy@university.edu", 79.0, "+91 9876543217", 
                   "Psychology", "Social Sciences", "2023-09-01", 89.3),
            Student("ST009", "Sanjay Verma", 24, Grade.A.value, "sanjay.verma@university.edu", 91.5, "+91 9876543218",
                   "Electrical Engineering", "Engineering", "2023-09-01", 93.7),
            Student("ST010", "Divya Malhotra", 19, Grade.B.value, "divya.malhotra@university.edu", 81.0, "+91 9876543219",
                   "Mathematics", "Science", "2023-09-01", 87.9),
        ]
        
        
        sample_students[0].add_activity("Assignment", "Completed Advanced Algorithms assignment")
        sample_students[1].add_activity("Project", "Submitted Data Visualization project")
        sample_students[2].add_activity("Exam", "Scored 95% in AI Midterm")
        
        self.students = sample_students
    
    def get_next_student_id(self):
        if not self.students:
            return "ST001"
        max_id = max(int(s.student_id[2:]) for s in self.students)
        return f"ST{max_id + 1:03d}"
    
    def add_student(self, student):
        try:
            self.students.append(student)
            self.clear_cache()
            return True, "Student added successfully"
        except Exception as e:
            return False, f"Error adding student: {str(e)}"
    
    def get_all_students(self):
        return self.students
    
    def get_student(self, student_id):
        for student in self.students:
            if student.student_id == student_id:
                return student
        return None
    
    def update_student(self, student_id, **kwargs):
        student = self.get_student(student_id)
        if not student:
            return False, "Student not found"
        
        try:
            for key, value in kwargs.items():
                if hasattr(student, key):
                    setattr(student, key, value)
            student.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.clear_cache()
            return True, "Student updated successfully"
        except Exception as e:
            return False, f"Error updating student: {str(e)}"
    
    def delete_student(self, student_id):
        student = self.get_student(student_id)
        if not student:
            return False, "Student not found"
        
        try:
            self.students = [s for s in self.students if s.student_id != student_id]
            self.clear_cache()
            return True, "Student deleted successfully"
        except Exception as e:
            return False, f"Error deleting student: {str(e)}"
    
    def clear_cache(self):
        self.cache_stats = None
        self.cache_time = None
    
    def search_students(self, query):
        if not query:
            return self.students
        
        query = query.lower()
        results = []
        for student in self.students:
            if (query in student.name.lower() or 
                query in student.email.lower() or 
                query in student.course.lower() or 
                query in student.department.lower() or 
                query in student.phone.lower() or
                query in student.student_id.lower()):
                results.append(student)
        return results
    
    def get_statistics(self):
        
        current_time = time.time()
        if self.cache_stats and self.cache_time and (current_time - self.cache_time) < 30:
            return self.cache_stats
        
        if not self.students:
            stats = {}
        else:
            total_students = len(self.students)
            average_performance = sum(s.performance for s in self.students) / total_students
            average_age = sum(s.age for s in self.students) / total_students
            average_attendance = sum(s.attendance for s in self.students) / total_students
            
            status_distribution = {status.value: 0 for status in PerformanceStatus}
            grade_distribution = {grade.value: 0 for grade in Grade}
            attendance_distribution = {status.value: 0 for status in AttendanceStatus}
            course_distribution = {}
            department_distribution = {}
            
            for student in self.students:
                status = student.calculate_status()
                attendance_status = student.calculate_attendance_status()
                
                status_distribution[status] = status_distribution.get(status, 0) + 1
                grade_distribution[student.grade] = grade_distribution.get(student.grade, 0) + 1
                attendance_distribution[attendance_status] = attendance_distribution.get(attendance_status, 0) + 1
                course_distribution[student.course] = course_distribution.get(student.course, 0) + 1
                department_distribution[student.department] = department_distribution.get(student.department, 0) + 1
            
            
            performances = [s.performance for s in self.students]
            performance_trend = "Stable"
            if len(performances) >= 2:
                if performances[-1] > performances[0]:
                    performance_trend = "Improving"
                elif performances[-1] < performances[0]:
                    performance_trend = "Declining"
            
            stats = {
                'total_students': total_students,
                'average_performance': round(average_performance, 1),
                'average_age': round(average_age, 1),
                'average_attendance': round(average_attendance, 1),
                'status_distribution': status_distribution,
                'grade_distribution': grade_distribution,
                'attendance_distribution': attendance_distribution,
                'course_distribution': course_distribution,
                'department_distribution': department_distribution,
                'performance_trend': performance_trend,
                'top_performer': max(self.students, key=lambda x: x.performance).name if self.students else "N/A",
                'most_attended': max(self.students, key=lambda x: x.attendance).name if self.students else "N/A"
            }
        
        self.cache_stats = stats
        self.cache_time = current_time
        return stats
    
    def get_performance_analysis(self):
        if not self.students:
            return {}
        
        performances = [s.performance for s in self.students]
        attendances = [s.attendance for s in self.students]
        
        return {
            'max_performance': max(performances),
            'min_performance': min(performances),
            'median_performance': np.median(performances),
            'pass_rate': (sum(1 for s in self.students if s.performance >= 60) / len(self.students)) * 100,
            'excellence_rate': (sum(1 for s in self.students if s.performance >= 90) / len(self.students)) * 100,
            'avg_attendance': sum(attendances) / len(attendances),
            'correlation': np.corrcoef(performances, attendances)[0,1] if len(performances) > 1 else 0
        }
    
    def bulk_delete_students(self, student_ids):
        try:
            initial_count = len(self.students)
            self.students = [s for s in self.students if s.student_id not in student_ids]
            deleted_count = initial_count - len(self.students)
            self.clear_cache()
            return True, f"Successfully deleted {deleted_count} students"
        except Exception as e:
            return False, f"Error during bulk deletion: {str(e)}"
    
    def export_to_csv(self):
        try:
            data = []
            for student in self.students:
                data.append({
                    'student_id': student.student_id,
                    'name': student.name,
                    'age': student.age,
                    'grade': student.grade,
                    'email': student.email,
                    'performance': student.performance,
                    'phone': student.phone,
                    'course': student.course,
                    'department': student.department,
                    'enrollment_date': student.enrollment_date,
                    'attendance': student.attendance,
                    'last_updated': student.last_updated
                })
            
            df = pd.DataFrame(data)
            csv = df.to_csv(index=False)
            return True, "Data exported successfully", csv
        except Exception as e:
            return False, f"Export failed: {str(e)}", None
    
    def import_from_csv(self, file_content):
        try:
            df = pd.read_csv(io.StringIO(file_content))
            imported_count = 0
            errors = []
            
            for _, row in df.iterrows():
                try:
                    student_data = {
                        'name': str(row.get('name', '')),
                        'age': int(row.get('age', 18)),
                        'grade': str(row.get('grade', Grade.B.value)),
                        'email': str(row.get('email', '')),
                        'performance': float(row.get('performance', 75)),
                        'phone': str(row.get('phone', '')),
                        'course': str(row.get('course', '')),
                        'department': str(row.get('department', 'General')),
                        'attendance': float(row.get('attendance', 95.0))
                    }
                    
                    validation_errors = StudentValidator.validate_student_data(student_data)
                    if validation_errors:
                        errors.append(f"Row {_ + 1}: {', '.join(validation_errors)}")
                        continue
                    
                    student_id = self.get_next_student_id()
                    new_student = Student(
                        student_id=student_id,
                        name=student_data['name'],
                        age=student_data['age'],
                        grade=student_data['grade'],
                        email=student_data['email'],
                        performance=student_data['performance'],
                        phone=student_data['phone'],
                        course=student_data['course'],
                        department=student_data['department'],
                        enrollment_date=datetime.now().strftime("%Y-%m-%d"),
                        attendance=student_data['attendance']
                    )
                    
                    self.students.append(new_student)
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f"Row {_ + 1}: Error processing - {str(e)}")
            
            self.clear_cache()
            return True, f"Successfully imported {imported_count} students", errors
            
        except Exception as e:
            return False, f"Import failed: {str(e)}", []

class ModernStudentManagementUI:
    def __init__(self):
        self.manager = AdvancedStudentManager()
        self.setup_page()
    
    def setup_page(self):
        st.set_page_config(
            page_title="Academic MentorDesk",
            layout="wide",
            initial_sidebar_state="expanded",
            page_icon="🎓"
        )
        
        
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "dashboard"
        
        
        st.markdown("""
        <style>
        /* Main background - Light Theme */
        .main {
            background: linear-gradient(to bottom, #F8FAFC, #F1F5F9, #E2E8F0);
            color: #1E293B;
        }
        
        /* Headers */
        .main-header {
            font-size: 3rem;
            text-align: center;
            margin-bottom: 2rem;
            font-weight: 800;
            padding: 1.5rem;
            color: white !important;
            border-bottom: 3px solid #E2E8F0;
        }
        
        .section-header {
            font-size: 2rem;
            color: white !important;
            border-bottom: 2px solid #3B82F6;
            padding-bottom: 0.5rem;
            margin: 2rem 0 1.5rem 0;
            font-weight: 700;
        }
        
        /* Modern Card Design - Clean & Light */
        .modern-card {
            background: white;
            padding: 1.5rem;
            border-radius: 16px;
            border: 1px solid #E2E8F0;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            margin-bottom: 1.5rem;
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease;
        }
        
        .modern-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
            border-color: #3B82F6;
        }
        
        /* Enhanced Metric Cards */
        .metric-card {
            background: white;
            padding: 2rem 1.5rem;
            border-radius: 16px;
            border: 1px solid #E2E8F0;
            color: #1E293B;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease;
            margin: 0.5rem 0;
        }
        
        .metric-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
        }
        
        .metric-card-1 { border-left: 4px solid #3B82F6; }
        .metric-card-2 { border-left: 4px solid #10B981; }
        .metric-card-3 { border-left: 4px solid #F59E0B; }
        .metric-card-4 { border-left: 4px solid #EF4444; }
        .metric-card-5 { border-left: 4px solid #8B5CF6; }
        .metric-card-6 { border-left: 4px solid #EC4899; }
        
        /* Enhanced Form Elements */
        .stTextInput input, .stNumberInput input, .stSelectbox select, .stTextArea textarea {
            background: white !important;
            border: 2px solid #E2E8F0 !important;
            border-radius: 12px !important;
            padding: 12px 16px !important;
            font-size: 1rem !important;
            color: #1E293B !important;
            transition: all 0.3s ease !important;
        }
        
        .stTextInput input:focus, .stNumberInput input:focus, .stSelectbox select:focus, .stTextArea textarea:focus {
            border-color: #3B82F6 !important;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
            transform: translateY(-1px) !important;
        }
        
        .stTextInput input::placeholder, .stNumberInput input::placeholder {
            color: #64748B !important;
        }
        
        /* Enhanced Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background: white;
            padding: 12px;
            border-radius: 12px;
            margin-bottom: 2rem;
            border: 1px solid #E2E8F0;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            padding: 12px 20px;
            font-weight: 600;
            transition: all 0.3s ease;
            background: transparent;
            color: #64748B;
        }
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: #3B82F6;
            color: white;
            box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
        }
        
        /* Custom Messages */
        .success-message {
            background: #D1FAE5;
            color: #065F46;
            padding: 1rem 1rem 1rem 3.5rem;
            border-radius: 12px;
            border-left: 4px solid #10B981;
            margin: 1rem 0;
            position: relative;
            font-weight: 500;
        }
        
        .success-message::before {
            content: "✓";
            position: absolute;
            left: 1.5rem;
            top: 50%;
            transform: translateY(-50%);
            font-weight: bold;
            font-size: 1.2rem;
            color: #10B981;
        }
        
        .error-message {
            background: #FEE2E2;
            color: #991B1B;
            padding: 1rem 1rem 1rem 3.5rem;
            border-radius: 12px;
            border-left: 4px solid #EF4444;
            margin: 1rem 0;
            position: relative;
            font-weight: 500;
        }
        
        .error-message::before {
            content: "✗";
            position: absolute;
            left: 1.5rem;
            top: 50%;
            transform: translateY(-50%);
            font-weight: bold;
            font-size: 1.2rem;
            color: #EF4444;
        }
        
        .info-message {
            background: #DBEAFE;
            color: #1E40AF;
            padding: 1rem 1rem 1rem 3.5rem;
            border-radius: 12px;
            border-left: 4px solid #3B82F6;
            margin: 1rem 0;
            position: relative;
            font-weight: 500;
        }
        
        .info-message::before {
            content: "ℹ";
            position: absolute;
            left: 1.5rem;
            top: 50%;
            transform: translateY(-50%);
            font-weight: bold;
            font-size: 1.2rem;
            color: #3B82F6;
        }
        
        .warning-message {
            background: #FEF3C7;
            color: #92400E;
            padding: 1rem 1rem 1rem 3.5rem;
            border-radius: 12px;
            border-left: 4px solid #F59E0B;
            margin: 1rem 0;
            position: relative;
            font-weight: 500;
        }
        
        .warning-message::before {
            content: "⚠";
            position: absolute;
            left: 1.5rem;
            top: 50%;
            transform: translateY(-50%);
            font-weight: bold;
            font-size: 1.2rem;
            color: #F59E0B;
        }
        
        /* Status Badges */
        .status-badge {
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            display: inline-block;
        }
        
        .status-excellent { 
            background: #D1FAE5;
            color: #065F46;
            border: 1px solid #10B981;
        }
        .status-good { 
            background: #DBEAFE;
            color: #1E40AF;
            border: 1px solid #3B82F6;
        }
        .status-average { 
            background: #FEF3C7;
            color: #92400E;
            border: 1px solid #F59E0B;
        }
        .status-needs-improvement { 
            background: #FEE2E2;
            color: #991B1B;
            border: 1px solid #EF4444;
        }
        
        /* Sidebar Enhancements */
        .sidebar-title {
            color: white;
            font-size: 1.5rem;
            font-weight: 800;
            text-align: center;
            margin-bottom: 1.5rem;
            padding: 1rem;
        }
        
        /* Progress Bars */
        .stProgress > div > div {
            background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
        }
        
        /* Dataframe Styling */
        .dataframe {
            background: white !important;
            color: #1E293B !important;
            border: 1px solid #E2E8F0 !important;
        }
        
        .dataframe th {
            background: #3B82F6 !important;
            color: white !important;
        }
        
        .dataframe td {
            background: white !important;
            color: #1E293B !important;
            border-color: #E2E8F0 !important;
        }
        
        /* Animation for loading */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .fade-in {
            animation: fadeIn 0.6s ease-out;
        }
        
        /* Navigation buttons container */
        .nav-container {
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin: 1rem 0;
        }
        
        /* Beautiful sidebar buttons */
        .sidebar-btn {
            background: white;
            border: 2px solid #E2E8F0;
            border-radius: 12px;
            padding: 14px 18px;
            font-weight: 600;
            color: #475569;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            font-size: 0.95rem;
            margin: 4px 0;
            width: 100%;
            text-align: left;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .sidebar-btn:hover {
            transform: translateY(-2px);
            border-color: #3B82F6;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.15);
            color: #1E293B;
        }
        
        .sidebar-btn.active {
            background: #3B82F6;
            color: white;
            border-color: #3B82F6;
        }
        
        /* Hide default sidebar elements */
        [data-testid="stSidebarNav"] {
            display: none;
        }
        
        /* Custom sidebar toggle */
        .sidebar-toggle {
            position: fixed;
            top: 20px;
            left: 20px;
            z-index: 9999;
            background: white;
            border: 2px solid #E2E8F0;
            border-radius: 8px;
            padding: 8px;
            cursor: pointer;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        /* Make all text visible */
        .stMarkdown, .stText, .stTitle, .stHeader, .stSubheader {
            color: #1E293B !important;
        }
        
        /* Button styling */
        .stButton button {
            background: #3B82F6;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .stButton button:hover {
            background: #2563EB;
            transform: translateY(-1px);
        }
        
        /* Selectbox dropdown styling */
        .stSelectbox [data-baseweb="select"] {
            background: white !important;
            color: #1E293B !important;
        }
        
        .stSelectbox [data-baseweb="popover"] {
            background: white !important;
            border: 1px solid #E2E8F0 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<h1 class="main-header fade-in"> Academic MentorDesk - Student Management System</h1>', unsafe_allow_html=True)
    
    def show_sidebar_menu(self):
        st.sidebar.markdown('<div class="sidebar-title"> Academic MentorDesk</div>', unsafe_allow_html=True)
        st.sidebar.markdown("---")
        
        # Navigation buttons with meaningful names
        st.sidebar.markdown('<div class="nav-container">', unsafe_allow_html=True)
        
        pages = [
            (" Academic Dashboard", "dashboard"),
            (" Student Enrollment", "registration"),
            (" Student Directory", "directory"),
            (" Academic MentorDesk Analytics", "analytics"),
            (" Student Management", "management"),
            (" Data Operations", "data")
        ]
        
        for page_name, page_key in pages:
            is_active = st.session_state.current_page == page_key
            btn_class = "sidebar-btn active" if is_active else "sidebar-btn"
            
            if st.sidebar.button(
                page_name, 
                key=f"nav_{page_key}",
                use_container_width=True
            ):
                st.session_state.current_page = page_key
                st.rerun()
        
        st.sidebar.markdown('</div>', unsafe_allow_html=True)
        
        # System overview in sidebar
        st.sidebar.markdown("---")
        st.sidebar.markdown("###  Quick Stats")
        
        stats = self.manager.get_statistics()
        
        if stats:
            st.sidebar.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin: 0.5rem 0;">
                <span style="color: #64748B;">Total Students</span>
                <span style="font-weight: 700; color: #3B82F6;">{stats.get('total_students', 0)}</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.sidebar.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin: 0.5rem 0;">
                <span style="color: #64748B;">Avg Academic MentorDesk</span>
                <span style="font-weight: 700; color: #10B981;">{stats.get('average_performance', 0)}%</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.sidebar.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin: 0.5rem 0;">
                <span style="color: #64748B;">Avg Attendance</span>
                <span style="font-weight: 700; color: #F59E0B;">{stats.get('average_attendance', 0)}%</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("""
        <div style="text-align: center; color: #64748B; font-size: 0.8rem;">
            <strong>Academic MentorDesk v4.0</strong><br>
            Academic Management System
        </div>
        """, unsafe_allow_html=True)

    def show_dashboard(self):
        st.markdown('<h2 class="section-header"> Academic MentorDesk Dashboard</h2>', unsafe_allow_html=True)
        
        stats = self.manager.get_statistics()
        performance_analysis = self.manager.get_performance_analysis()
        
        if not stats:
            st.markdown("""
            <div class="info-message">
                No student data available. Start by adding students to see analytics.
            </div>
            """, unsafe_allow_html=True)
            return
        
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card metric-card-1" style="margin: 1rem 0;">
                <div style="font-size: 0.9rem; color: #1e293b; margin-bottom: 0.5rem;">TOTAL STUDENTS</div>
                <div style="font-size: 2.5rem; font-weight: 800; margin-bottom: 0.5rem; color: #1e293b;">{stats['total_students']}</div>
                <div style="font-size: 0.8rem; color: #1e293b;">Active Learners</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card metric-card-2" style="margin: 1rem 0;">
                <div style="font-size: 0.9rem; color: #1e293b; margin-bottom: 0.5rem;">AVG ACADEMIC MENTORDESK</div>
                <div style="font-size: 2.5rem; font-weight: 800; margin-bottom: 0.5rem; color: #1E293B;">{stats['average_performance']}%</div>
                <div style="font-size: 0.8rem; color: #1e293b;">{stats['performance_trend']} Trend</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card metric-card-3" style="margin: 1rem 0;">
                <div style="font-size: 0.9rem; color: #1e293b; margin-bottom: 0.5rem;">PASS RATE</div>
                <div style="font-size: 2.5rem; font-weight: 800; margin-bottom: 0.5rem; color: #1E293B;">{performance_analysis.get('pass_rate', 0):.1f}%</div>
                <div style="font-size: 0.8rem; color: #1e293b;">Overall Success</div>
            </div>
            """, unsafe_allow_html=True)
        
        
        col4, col5, col6 = st.columns(3)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card metric-card-4" style="margin: 1rem 0;">
                <div style="font-size: 0.9rem; color: #1e293b; margin-bottom: 0.5rem;">EXCELLENCE RATE</div>
                <div style="font-size: 2.5rem; font-weight: 800; margin-bottom: 0.5rem; color: #1E293B;">{performance_analysis.get('excellence_rate', 0):.1f}%</div>
                <div style="font-size: 0.8rem; color: #1e293b;">90%+ Performers</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            st.markdown(f"""
            <div class="metric-card metric-card-5" style="margin: 1rem 0;">
                <div style="font-size: 0.9rem; color: #1e293b; margin-bottom: 0.5rem;">AVG ATTENDANCE</div>
                <div style="font-size: 2.5rem; font-weight: 800; margin-bottom: 0.5rem; color: #1E293B;">{stats['average_attendance']}%</div>
                <div style="font-size: 0.8rem; color: #1e293b;">Class Participation</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col6:
            st.markdown(f"""
            <div class="metric-card metric-card-6" style="margin: 1rem 0;">
                <div style="font-size: 0.9rem; color: #1e293b; margin-bottom: 0.5rem;">TOP PERFORMER</div>
                <div style="font-size: 1.2rem; font-weight: 800; margin-bottom: 0.5rem; color: #1E293B; line-height: 1.2;">{stats['top_performer']}</div>
                <div style="font-size: 0.8rem; color: #1e293b;">Leading Student</div>
            </div>
            """, unsafe_allow_html=True)
        
        
        st.markdown("---")
        st.markdown('<h3 class="section-header"> Academic MentorDesk Analytics</h3>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            
            if any(stats['status_distribution'].values()):
                status_data = stats['status_distribution']
                colors = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444']
                
                fig_status = px.pie(
                    values=list(status_data.values()),
                    names=list(status_data.keys()),
                    title="Student Academic MentorDesk Distribution",
                    color_discrete_sequence=colors
                )
                fig_status.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    hoverinfo='label+percent+value',
                    marker=dict(line=dict(color='white', width=2))
                )
                fig_status.update_layout(
                    showlegend=True,
                    height=400,
                    plot_bgcolor='blue',
                    paper_bgcolor='blue',
                    font=dict(size=12, color="#1E293B")
                )
                st.plotly_chart(fig_status, use_container_width=True)
        
        with col2:

            if any(stats['grade_distribution'].values()):
                grade_data = stats['grade_distribution']
                colors = ['#10B981', '#3B82F6', '#F59E0B', '#F97316', '#EF4444']
                
                fig_grade = px.bar(
                    x=list(grade_data.keys()),
                    y=list(grade_data.values()),
                    title="Grade Distribution Analysis",
                    color=list(grade_data.keys()),
                    color_discrete_sequence=colors,
                    text=list(grade_data.values())
                )
                fig_grade.update_layout(
                    xaxis_title="Grade",
                    yaxis_title="Number of Students",
                    showlegend=False,
                    height=400,
                    plot_bgcolor='blue',
                    paper_bgcolor='blue',
                    font=dict(size=12, color="#1E293B")
                )
                fig_grade.update_traces(
                    marker_line_color='white',
                    marker_line_width=2,
                    opacity=0.9,
                    textposition='outside'
                )
                st.plotly_chart(fig_grade, use_container_width=True)

    def show_registration(self):
        st.markdown('<h2 class="section-header"> Student Enrollment</h2>', unsafe_allow_html=True)
        
        with st.form("student_registration_form", clear_on_submit=True):
            with st.container():
                st.markdown('<div class="modern-card">', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("###  Personal Information")
                    name = st.text_input("Full Name *", placeholder="Enter student's full name", key="reg_name")
                    age = st.number_input("Age *", min_value=15, max_value=70, value=18, key="reg_age")
                    email = st.text_input("Email Address *", placeholder="student@institution.edu", key="reg_email")
                    phone = st.text_input("Phone Number", placeholder="+91 9876543210", key="reg_phone")
                
                with col2:
                    st.markdown("###  Academic Information")
                    course = st.text_input("Course/Program *", placeholder="Computer Science", key="reg_course")
                    department = st.selectbox("Department *", [
                        "Computer Science", "Engineering", "Mathematics", "Physics", 
                        "Chemistry", "Biology", "Business", "Arts", "Social Sciences",
                        "Life Sciences", "Data Science", "Artificial Intelligence"
                    ], key="reg_department")
                    grade_options = [grade.value for grade in Grade]
                    grade = st.selectbox("Current Grade *", grade_options, key="reg_grade")
                    performance = st.slider("Academic MentorDesk Score (%) *", 0, 100, 75, key="reg_performance")
                    attendance = st.slider("Attendance Rate (%)", 0, 100, 95, key="reg_attendance")
                    enrollment_date = st.date_input("Enrollment Date", value=datetime.now(), key="reg_date")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("***Required fields**")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submitted = st.form_submit_button("🎓 Register Student", use_container_width=True)
            
            if submitted:
                with st.spinner("Registering student..."):
                    time.sleep(1)
                    
                    student_data = {
                        'name': name,
                        'age': age,
                        'grade': grade,
                        'email': email,
                        'performance': performance,
                        'phone': phone,
                        'course': course,
                        'department': department,
                        'attendance': attendance
                    }
                    
                    errors = StudentValidator.validate_student_data(student_data)
                    
                    if errors:
                        for error in errors:
                            st.markdown(f'<div class="error-message">{error}</div>', unsafe_allow_html=True)
                    else:
                        student_id = self.manager.get_next_student_id()
                        new_student = Student(
                            student_id=student_id,
                            name=name.strip(),
                            age=int(age),
                            grade=grade,
                            email=email.strip(),
                            performance=float(performance),
                            phone=phone.strip(),
                            course=course.strip(),
                            department=department,
                            enrollment_date=enrollment_date.strftime("%Y-%m-%d"),
                            attendance=float(attendance)
                        )
                        
                        success, message = self.manager.add_student(new_student)
                        if success:
                            st.markdown(f'<div class="success-message"> Student registered successfully! Student ID: {student_id}</div>', unsafe_allow_html=True)
                            st.balloons()
                            time.sleep(2)
                            st.session_state.current_page = "directory"
                            st.rerun()
                        else:
                            st.markdown(f'<div class="error-message"> {message}</div>', unsafe_allow_html=True)

    def show_directory(self):
        st.markdown('<h2 class="section-header"> Student Directory</h2>', unsafe_allow_html=True)
        

        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            search_query = st.text_input(" Search Students", placeholder="Search by name, email, course, department...")
        
        with col2:
            status_filter = st.selectbox(" Status", ["All"] + [status.value for status in PerformanceStatus])
        
        with col3:
            grade_filter = st.selectbox("🎓 Grade", ["All"] + [grade.value for grade in Grade])
        
        with col4:
            departments = ["All"] + sorted(list(set(s.department for s in self.manager.students)))
            department_filter = st.selectbox(" Department", departments)
        
       
        students = self.manager.get_all_students()
        
        if search_query:
            students = self.manager.search_students(search_query)
        
        if status_filter != "All":
            students = [s for s in students if s.calculate_status() == status_filter]
        
        if grade_filter != "All":
            students = [s for s in students if s.grade == grade_filter]
        
        if department_filter != "All":
            students = [s for s in students if s.department == department_filter]
        
        self._display_students_table(students, "Student Records")

    def _display_students_table(self, students, title):
        if not students:
            st.markdown("""
            <div class="info-message">
                No student records found matching the current criteria.
            </div>
            """, unsafe_allow_html=True)
            return
        

        data = []
        for student in students:
            status = student.calculate_status()
            attendance_status = student.calculate_attendance_status()
            
            data.append({
                'Student ID': student.student_id,
                'Name': student.name,
                'Age': student.age,
                'Grade': student.grade,
                'Email': student.email,
                'Academic MentorDesk': f"{student.performance}%",
                'Attendance': f"{student.attendance}%",
                'Status': status,
                'Attendance Status': attendance_status,
                'Course': student.course,
                'Department': student.department,
                'Phone': student.phone,
                'Enrollment Date': student.enrollment_date
            })
        
        df = pd.DataFrame(data)
        
        st.subheader(f"{title} ({len(students)} records)")
        
        
        for _, student in df.iterrows():
            with st.container():
                st.markdown('<div class="modern-card">', unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.markdown(f"**{student['Name']}** ({student['Student ID']})")
                    st.markdown(f" {student['Email']}")
                    st.markdown(f" {student['Phone'] if student['Phone'] else 'N/A'}")
                    st.markdown(f" {student['Course']} - {student['Department']}")
                
                with col2:
                    st.markdown(f" Enrolled: {student['Enrollment Date']}")
                    
                    
                    performance_pct = float(student['Academic MentorDesk'].replace('%', ''))
                    attendance_pct = float(student['Attendance'].replace('%', ''))
                    
                    st.markdown("**Academic MentorDesk:**")
                    st.progress(performance_pct / 100)
                    
                    st.markdown("**Attendance:**")
                    st.progress(attendance_pct / 100)
                
                with col3:
                    status_class = student['Status'].lower().replace(' ', '-').replace('⭐-', '').replace('👍-', '').replace('📊-', '').replace('🚨-', '')
                    st.markdown(f'<div class="status-badge status-{status_class}">{student["Status"]}</div>', unsafe_allow_html=True)
                    st.markdown(f"**Grade: {student['Grade']}**")
                    st.markdown(f"**Academic MentorDesk: {student['Academic MentorDesk']}**")
                    st.markdown(f"**Attendance: {student['Attendance']}**")
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        
        st.markdown("---")
        st.markdown('<h4> Summary Statistics</h4>', unsafe_allow_html=True)
        
        if students:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                avg_age = sum(s.age for s in students) / len(students)
                st.metric("Average Age", f"{avg_age:.1f} years")
            with col2:
                avg_perf = sum(s.performance for s in students) / len(students)
                st.metric("Average Academic MentorDesk", f"{avg_perf:.1f}%")
            with col3:
                avg_att = sum(s.attendance for s in students) / len(students)
                st.metric("Average Attendance", f"{avg_att:.1f}%")
            with col4:
                excellent_count = sum(1 for s in students if s.calculate_status() == PerformanceStatus.EXCELLENT.value)
                st.metric("Excellent Students", excellent_count)

    def show_analytics(self):
        st.markdown('<h2 class="section-header"> Academic MentorDesk Analytics</h2>', unsafe_allow_html=True)
        
        stats = self.manager.get_statistics()
        performance_analysis = self.manager.get_performance_analysis()
        
        if not stats:
            st.markdown("""
            <div class="info-message">
                No data available for analytics.
            </div>
            """, unsafe_allow_html=True)
            return
        
        
        st.markdown("###  Academic MentorDesk Insights")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            correlation = performance_analysis.get('correlation', 0)
            trend_label = "Strong positive" if correlation > 0.5 else "Weak correlation" if correlation > 0.2 else "No correlation"
            st.metric("Academic MentorDesk vs Attendance Correlation", 
                     f"{correlation:.2f}",
                     trend_label)
        
        with col2:
            st.metric("Median Academic MentorDesk", f"{performance_analysis.get('median_performance', 0):.1f}%")
        
        with col3:
            st.metric("Academic MentorDesk Range", 
                     f"{performance_analysis.get('min_performance', 0):.0f}-{performance_analysis.get('max_performance', 0):.0f}%")
        
        
        st.markdown("###  Detailed Distributions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            
            if any(stats['attendance_distribution'].values()):
                attendance_data = stats['attendance_distribution']
                fig_attendance = px.bar(
                    x=list(attendance_data.keys()),
                    y=list(attendance_data.values()),
                    title="Attendance Status Distribution",
                    color=list(attendance_data.keys()),
                    color_discrete_sequence=['#10B981', '#3B82F6', '#F59E0B', '#EF4444']
                )
                fig_attendance.update_layout(
                    xaxis_title="Attendance Status",
                    yaxis_title="Number of Students",
                    showlegend=False,
                    height=400,
                    plot_bgcolor='blue',
                    paper_bgcolor='blue',
                    font=dict(color="#E2EAF7")
                )
                fig_attendance.update_traces(
                    marker_line_color='white',
                    marker_line_width=2,
                    textposition='outside'
                )
                st.plotly_chart(fig_attendance, use_container_width=True)
        
        with col2:
            
            if stats['department_distribution']:
                dept_data = stats['department_distribution']
                fig_dept = px.pie(
                    values=list(dept_data.values()),
                    names=list(dept_data.keys()),
                    title="Department Distribution",
                    hole=0.4
                )
                fig_dept.update_layout(
                    height=400,
                    plot_bgcolor='blue',
                    paper_bgcolor='blue',
                    font=dict(color="#DCE1E9")
                )
                fig_dept.update_traces(
                    textposition='inside',
                    textinfo='percent+label'
                )
                st.plotly_chart(fig_dept, use_container_width=True)

    def show_management(self):
        st.markdown('<h2 class="section-header"> Student Management</h2>', unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs([" Update Records", " Delete Records", " Bulk Operations"])
        
        with tab1:
            self._show_update_student_tab()
        
        with tab2:
            self._show_delete_student_tab()
        
        with tab3:
            self._show_bulk_operations_tab()

    def _show_update_student_tab(self):
        st.subheader("✏️ Update Student Information")
        
        if not self.manager.students:
            st.markdown("""
            <div class="info-message">
                No students available for update.
            </div>
            """, unsafe_allow_html=True)
            return
        
        student_id = st.selectbox(
            "Select Student to Update",
            options=[s.student_id for s in self.manager.students],
            format_func=lambda x: f"{x} - {self.manager.get_student(x).name}",
            key="update_select"
        )
        
        if student_id:
            student = self.manager.get_student(student_id)
            
            with st.form("update_student_form"):
                st.markdown('<div class="modern-card">', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("###  Personal Information")
                    new_name = st.text_input("Full Name *", value=student.name)
                    new_age = st.number_input("Age *", min_value=15, max_value=70, value=student.age)
                    new_email = st.text_input("Email Address *", value=student.email)
                    new_phone = st.text_input("Phone Number", value=student.phone)
                
                with col2:
                    st.markdown("###  Academic Information")
                    new_course = st.text_input("Course/Program *", value=student.course)
                    
                    departments = [
                        "Computer Science", "Engineering", "Mathematics", "Physics", 
                        "Chemistry", "Biology", "Business", "Arts", "Social Sciences",
                        "Life Sciences", "Data Science", "Artificial Intelligence"
                    ]
                    current_dept_index = departments.index(student.department) if student.department in departments else 0
                    new_department = st.selectbox("Department *", departments, index=current_dept_index)
                    
                    grade_options = [grade.value for grade in Grade]
                    current_grade_index = grade_options.index(student.grade) if student.grade in grade_options else 0
                    new_grade = st.selectbox("Current Grade *", grade_options, index=current_grade_index)
                    
                    new_performance = st.slider("Academic MentorDesk Score (%) *", 0, 100, value=int(student.performance))
                    new_attendance = st.slider("Attendance Rate (%)", 0, 100, value=int(student.attendance))
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown("***Required fields**")
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    update_clicked = st.form_submit_button(" Update Student", use_container_width=True)
                
                if update_clicked:
                    update_data = {
                        'name': new_name,
                        'age': new_age,
                        'email': new_email,
                        'phone': new_phone,
                        'course': new_course,
                        'department': new_department,
                        'grade': new_grade,
                        'performance': new_performance,
                        'attendance': new_attendance
                    }
                    
                    errors = StudentValidator.validate_student_data(update_data)
                    if errors:
                        for error in errors:
                            st.markdown(f'<div class="error-message">{error}</div>', unsafe_allow_html=True)
                    else:
                        success, message = self.manager.update_student(student_id, **update_data)
                        if success:
                            st.markdown(f'<div class="success-message"> {message}</div>', unsafe_allow_html=True)
                            st.rerun()
                        else:
                            st.markdown(f'<div class="error-message"> {message}</div>', unsafe_allow_html=True)

    def _show_delete_student_tab(self):
        st.subheader(" Delete Student Record")
        
        if not self.manager.students:
            st.markdown("""
            <div class="info-message">
                No students available for deletion.
            </div>
            """, unsafe_allow_html=True)
            return
        
        student_id = st.selectbox(
            "Select Student to Delete",
            options=[s.student_id for s in self.manager.students],
            format_func=lambda x: f"{x} - {self.manager.get_student(x).name}",
            key="delete_select"
        )
        
        if student_id:
            student = self.manager.get_student(student_id)
            
            st.markdown(f"""
            <div class="modern-card">
                <h4>Student Details</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                    <div><strong>Name:</strong> {student.name}</div>
                    <div><strong>Email:</strong> {student.email}</div>
                    <div><strong>Course:</strong> {student.course}</div>
                    <div><strong>Department:</strong> {student.department}</div>
                    <div><strong>Academic MentorDesk:</strong> {student.performance}%</div>
                    <div><strong>Attendance:</strong> {student.attendance}%</div>
                    <div><strong>Status:</strong> {student.calculate_status()}</div>
                    <div><strong>Enrollment:</strong> {student.enrollment_date}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.warning(" This action cannot be undone. The student record will be permanently deleted.")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button(" Delete Student", use_container_width=True, type="primary"):
                    success, message = self.manager.delete_student(student_id)
                    if success:
                        st.markdown(f'<div class="success-message"> {message}</div>', unsafe_allow_html=True)
                        st.rerun()
                    else:
                        st.markdown(f'<div class="error-message"> {message}</div>', unsafe_allow_html=True)

    def _show_bulk_operations_tab(self):
        st.subheader(" Bulk Operations")
        
        st.markdown("""
        <div class="info-message">
            Select multiple students for bulk operations like deletion or batch updates.
        </div>
        """, unsafe_allow_html=True)
        
        if not self.manager.students:
            st.markdown("""
            <div class="info-message">
                No students available for bulk operations.
            </div>
            """, unsafe_allow_html=True)
            return
        
        
        student_options = {f"{s.student_id} - {s.name}": s.student_id for s in self.manager.students}
        selected_students = st.multiselect(
            "Select Students for Bulk Operation",
            options=list(student_options.keys()),
            placeholder="Choose students..."
        )
        
        if selected_students:
            selected_ids = [student_options[student] for student in selected_students]
            
            st.markdown(f"**Selected {len(selected_ids)} students for operation**")
            
            
            with st.expander(" View Selected Students"):
                for student_id in selected_ids:
                    student = self.manager.get_student(student_id)
                    if student:
                        st.write(f"**{student.name}** ({student_id}) - {student.course} - {student.performance}%")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button(" Delete Selected Students", use_container_width=True):
                    st.warning(f"Are you sure you want to delete {len(selected_ids)} students?")
                    confirm = st.checkbox("I confirm this bulk deletion")
                    
                    if confirm:
                        success, message = self.manager.bulk_delete_students(selected_ids)
                        if success:
                            st.markdown(f'<div class="success-message"> {message}</div>', unsafe_allow_html=True)
                            st.rerun()
                        else:
                            st.markdown(f'<div class="error-message"> {message}</div>', unsafe_allow_html=True)

    def show_data_operations(self):
        st.markdown('<h2 class="section-header"> Data Operations</h2>', unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs([" Export Data", " Import Data", " System Tools"])
        
        with tab1:
            st.subheader(" Export Student Data")
            st.markdown("""
            <div class="modern-card">
                Export all student records to CSV format for external analysis, reporting, or backup purposes.
                The exported file will include all student information including academic mentordesk metrics and attendance data.
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button(" Export to CSV", use_container_width=True):
                    with st.spinner("Generating export file..."):
                        success, message, csv_data = self.manager.export_to_csv()
                        
                        if success:
                            st.markdown(f'<div class="success-message"> {message}</div>', unsafe_allow_html=True)
                            
                            # Create download link
                            b64 = base64.b64encode(csv_data.encode()).decode()
                            href = f'<a href="data:file/csv;base64,{b64}" download="student_records_export.csv" style="display: inline-block; padding: 0.5rem 1rem; background: #10B981; color: white; text-decoration: none; border-radius: 8px; font-weight: 600;">📥 Download CSV File</a>'
                            st.markdown(href, unsafe_allow_html=True)
                            
                            # Show preview
                            st.subheader(" Data Preview")
                            df = pd.read_csv(io.StringIO(csv_data))
                            st.dataframe(df.head(10), use_container_width=True)
                        else:
                            st.markdown(f'<div class="error-message"> {message}</div>', unsafe_allow_html=True)
            
            with col2:
                st.metric("Total Records", len(self.manager.students))
                st.metric("Data Size", f"{(len(str(self.manager.students)) / 1024):.1f} KB")
        
        with tab2:
            st.subheader(" Import Student Data")
            st.markdown("""
            <div class="modern-card">
                Import student records from CSV file. Ensure your CSV file follows the required format with columns:
                name, age, grade, email, academic_mentordesk, phone, course, department, attendance
            </div>
            """, unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader("Choose CSV file", type=['csv'], key="import_uploader")
            
            if uploaded_file is not None:
              
                df_preview = pd.read_csv(uploaded_file)
                st.subheader(" Uploaded File Preview")
                st.dataframe(df_preview.head(5), use_container_width=True)
                
                if st.button(" Import Data", use_container_width=True):
                    with st.spinner("Importing student data..."):
                        
                        file_content = uploaded_file.getvalue().decode('utf-8')
                        success, message, errors = self.manager.import_from_csv(file_content)
                        
                        if success:
                            st.markdown(f'<div class="success-message"> {message}</div>', unsafe_allow_html=True)
                            if errors:
                                st.markdown("###  Import Warnings")
                                for error in errors[:10]:  
                                    st.markdown(f'<div class="warning-message">{error}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="error-message"> {message}</div>', unsafe_allow_html=True)
        
        with tab3:
            st.subheader(" System Tools")
            st.markdown("""
            <div class="modern-card">
                Advanced system utilities for data management and maintenance.
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button(" Clear Cache", use_container_width=True):
                    self.manager.clear_cache()
                    st.markdown('<div class="success-message"> Cache cleared successfully</div>', unsafe_allow_html=True)
                
                if st.button(" Refresh Statistics", use_container_width=True):
                    self.manager.clear_cache()
                    st.markdown('<div class="success-message"> Statistics refreshed</div>', unsafe_allow_html=True)
                    st.rerun()
            
            with col2:
                if st.button(" Data Integrity Check", use_container_width=True):
                    
                    valid_students = all(s.performance >= 0 and s.performance <= 100 for s in self.manager.students)
                    if valid_students:
                        st.markdown('<div class="success-message"> All data integrity checks passed</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="error-message"> Data integrity issues found</div>', unsafe_allow_html=True)

    def run(self):
        self.show_sidebar_menu()
        
        if st.session_state.current_page == "dashboard":
            self.show_dashboard()
        elif st.session_state.current_page == "registration":
            self.show_registration()
        elif st.session_state.current_page == "directory":
            self.show_directory()
        elif st.session_state.current_page == "analytics":
            self.show_analytics()
        elif st.session_state.current_page == "management":
            self.show_management()
        elif st.session_state.current_page == "data":
            self.show_data_operations()


if __name__ == "__main__":
    app = ModernStudentManagementUI()
    app.run()