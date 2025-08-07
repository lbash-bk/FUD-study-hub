from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from .models import Faculty, Department, Category, Level, Semester, Material
import tempfile
import os

User = get_user_model()

class BaseTestCase(TestCase):
    def setUp(self):
        # Create test data
        self.factory = RequestFactory()
        self.client = Client()
        
        self.faculty = Faculty.objects.create(name="Science", code="SCI")
        self.department = Department.objects.create(
            name="Computer Science", code="CSC", faculty=self.faculty
        )
        self.category = Category.objects.create(name="Lecture Notes", department=self.department)
        self.level = Level.objects.create(name="100L")
        self.semester = Semester.objects.create(name="First Semester")
        
        # Create users
        self.student = User.objects.create_user(
            email="student@test.com", 
            username="student", 
            password="testpass123",
            department=self.department
        )
        self.uploader = User.objects.create_user(
            email="uploader@test.com", 
            username="uploader", 
            password="testpass123",
            is_uploader=True,
            department=self.department
        )
        
        # Test file
        self.test_file = SimpleUploadedFile(
            "test.pdf", b"file_content", content_type="application/pdf"
        )

        # Create material for download tests
        self.material = Material.objects.create(
            title="Test Material",
            code="TEST101",
            file=self.test_file,
            session="2023/2024",
            department=self.department,
            level=self.level,
            uploaded_by=self.uploader,
            category=self.category,
            semester=self.semester
        )

class CustomUserModelTests(BaseTestCase):
    def test_user_creation(self):
        self.assertEqual(self.student.email, "student@test.com")
        self.assertFalse(self.student.is_uploader)
    
    def test_uploader_permission(self):
        self.assertTrue(self.uploader.is_uploader)
    
    def test_department_assignment(self):
        self.assertEqual(self.student.department.name, "Computer Science")

class FacultyModelTests(BaseTestCase):
    def test_slug_auto_generation(self):
        self.assertEqual(self.faculty.slug, "science")
    
    def test_str_representation(self):
        self.assertEqual(str(self.faculty), "Science (SCI)")

class DepartmentModelTests(BaseTestCase):
    def test_department_faculty_relationship(self):
        self.assertEqual(self.department.faculty.code, "SCI")
    
    def test_slug_generation(self):
        self.assertEqual(self.department.slug, "computer-science")

class MaterialModelTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.material = Material.objects.create(
            title="Intro to Python",
            code="CSC101",
            file=self.test_file,
            session="2023/2024",
            department=self.department,
            level=self.level,
            uploaded_by=self.uploader
        )
    
    def test_material_creation(self):
        self.assertEqual(self.material.download_count, 0)
    
    def test_is_accessible_to(self):
        # Test access rules
        self.assertTrue(self.material.is_accessible_to(self.uploader))  # Uploader
        self.assertFalse(self.material.is_accessible_to(self.student))  # Student
    
    def test_get_download_filename(self):
        self.assertEqual(
            self.material.get_download_filename(), 
            "CSC101_Intro to Python.pdf"
        )

class LoginViewTests(BaseTestCase):
    def test_login_success(self):
        response = self.client.post(reverse('login'), {
            'username': 'student@test.com', 
            'password': 'testpass123'
        })
        self.assertRedirects(response, reverse('department_list'))
    
    def test_uploader_role_check(self):
        response = self.client.post(
        reverse('login') + '?role=admin',
        {
            'username': 'student@test.com',
            'password': 'testpass123'
        },
        follow=True  # Follow the redirect
        )
        # Check if the error message appears in any page of the redirect chain
        messages = list(response.context['messages'])
        self.assertTrue(any("You don't have uploader privileges" in str(m) for m in messages))

class SignUpViewTests(BaseTestCase):
    def test_signup_flow(self):
        response = self.client.post(reverse('signup'), {
            'email': 'new@test.com',
            'username': 'newuser',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'department': self.department.id
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(User.objects.filter(email='new@test.com').exists())

class MaterialUploadTests(BaseTestCase):
    def test_upload_requires_login(self):
        response = self.client.get(reverse('materials_upload'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('materials_upload')}")
    
def test_upload_as_uploader(self):
    self.client.login(email='uploader@test.com', password='testpass123')
    with open('test.txt', 'w') as f:
        f.write("test content")
    with open('test.txt', 'rb') as f:
        response = self.client.post(reverse('materials_upload'), {
            'title': 'Test Material',
            'code': 'CSC102',
            'file': f,
            'session': '2023/2024',
            'level': self.level.id,
            'department': self.department.id,
            'category': self.category.id,
            'semester': self.semester.id
        })
    self.assertRedirects(response, reverse('admin_dashboard'))

class DownloadTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.material = Material.objects.create(
            title="Test Material",
            code="TEST101",
            file=self.test_file,
            session="2023/2024",
            department=self.department,
            level=self.level,
            uploaded_by=self.uploader
        )

class AjaxLoadTests(BaseTestCase):
    def test_load_departments(self):
        response = self.client.get(
            reverse('ajax_load_departments'), 
            {'faculty_id': self.faculty.id}
        )
        self.assertJSONEqual(
            response.content, 
            [{'id': self.department.id, 'name': 'Computer Science'}]
        )
        self.assertEqual(response.status_code, 200)

def test_empty_file_upload(self):
    self.client.login(email='uploader@test.com', password='testpass123')
    response = self.client.post(reverse('materials_upload'), {
        'title': 'Empty File',
        'code': 'CSC103',
        'file': '',
        'session': '2023/2024'
    })
    # Check for error in context instead
    self.assertContains(response, "This field is required", status_code=200)
    
    def test_nonexistent_download(self):
        response = self.client.get(reverse('track_download', args=[999]))
        self.assertEqual(response.status_code, 404)
