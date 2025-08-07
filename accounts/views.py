from django.http import FileResponse, Http404
import os
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import EmailAuthenticationForm
from django.contrib.auth.decorators import user_passes_test 
from django.contrib.auth import login, authenticate, logout
from django.http import JsonResponse
from .forms import MaterialUploadForm, SignUpForm
from .models import Material, Category, Semester, Department, Faculty
from django.db.models import Q # for search
from django.core.mail import send_mail


def login_view(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Redirect based on user permissions
            if user.is_uploader:
                return redirect('materials_upload')
            return redirect('department_list')
        else:
            messages.error(request, "Invalid email or password")
    else:
        form = EmailAuthenticationForm()

    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'user was logged out!')
    return redirect('login')

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Create user with commit=False
            user = form.save(commit=False)
            
            # Set faculty based on department
            department = form.cleaned_data['department']
            user.faculty = department.faculty

            # Set additional fields
            user.first_name = form.cleaned_data.get('first_name', '')
            user.last_name = form.cleaned_data.get('last_name', '')
            user.set_password(form.cleaned_data['password1']) #ensure password is hashed
            
            # Save the user (this hashes the password)
            user.save()
            
            # Send welcome email
            subject = 'Welcome to study hub'
            message = f'Hi {user.username}, get access to your learning materials'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [user.email]  # Fixed: This should be a list
            
            send_mail(
                subject,
                message,
                from_email,
                recipient_list,
                fail_silently=False
            )
            
            # Authenticate and login
            login(request, user)
            messages.success(request, f'Account created successfully! Welcome, {user.username}!')
            return redirect('department_list')
            
    else:
        form = SignUpForm()
    
    return render(request, 'signup.html', {'form': form})

def load_departments(request):
    faculty_id = request.GET.get('faculty_id')
    departments = Department.objects.filter(faculty_id=faculty_id).order_by('name')
    departments_data = [{'id': dept.id, 'name': dept.name} for dept in departments]
    return JsonResponse(departments_data, safe=False)

def load_categories(request):
    categories = Category.objects.all().order_by('name')
    categories_data = [{'id': sem.id, 'name': sem.name} for sem in categories]
    return JsonResponse(categories_data, safe=False)

def load_semesters(request):
    semesters = Semester.objects.all().order_by('name')
    semesters_data = [{'id': sem.id, 'name': sem.name} for sem in semesters]
    return JsonResponse(semesters_data, safe=False)

def index(request):
    """
    Home page view that redirects authenticated users to appropriate dashboards
    and shows landing page for anonymous users.
    """
    if request.user.is_authenticated:
        if request.user.is_uploader:
            return redirect('materials_upload')
        return redirect('department_list')
    return render(request, 'index.html', {'show_signup': True})

def feedback_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # Send email
        subject = f"New Feedback from {name}"
        email_message = f"""
        Name: {name}
        Email: {email}
        Message: {message}
        """
        
        try:
            send_mail(
                subject,
                email_message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],  # Send to yourself
                fail_silently=False,
            )
            messages.success(request, 'Thank you for your feedback!')
            return redirect('home')
        except Exception as e:
            messages.error(request, 'error status=500')
            return redirect('home')
    messages.error(request, 'invalid request status=400')
    return redirect('home')

@login_required
def department_view(request):
    # Get all departments initially
    departments = Department.objects.all()
    
    # Get search query from request (using 'search' parameter)
    search_query = request.GET.get('search')
    
    # Apply search filter if query exists
    if search_query:
        departments = departments.filter(
            Q(name__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(faculty__name__icontains=search_query)
        )
    
    return render(request, 'department-list.html', {
        'departments': departments.order_by('name'),
        'search_query': search_query
    })

@login_required
def material_list_view(request, slug):
    # Get the department
    department = get_object_or_404(Department, slug=slug)
    
    # Get all materials for this department initially
    materials = Material.objects.filter(department=department)
    
    # Get filter parameters from request
    selected_level = request.GET.get('level')
    search_query = request.GET.get('search', '')
    
    # Apply level filter if selected
    if selected_level:
        materials = materials.filter(level=selected_level)
    
    # Apply search filter if query exists
    if search_query:
        materials = materials.filter(
            Q(title__icontains=search_query) | 
            Q(code__icontains=search_query)
        )
    
    # Get all available levels for dropdown
    levels = Material.objects.filter(department=department)\
                           .values_list('level', flat=True)\
                           .distinct()\
                           .order_by('level')
    
    return render(request, 'material-list.html', {
        'department': department,
        'materials': materials.order_by('title'),  # Sort by title by default
        'levels': levels,
        'selected_level': selected_level,
        'search_query': search_query,
    })

@login_required
@user_passes_test(lambda u: u.is_uploader, login_url='/')
def admin_dashboard(request):
    materials = Material.objects.filter(
        uploaded_by=request.user
    ).order_by('-upload_date')
    
    total_downloads = sum(m.download_count for m in materials)

    stats = {
        'total_uploads': materials.count(),
        'total_downloads': total_downloads,
        'last_upload': materials.first()
    }
    
    return render(request, 'admin_dashboard.html', {
        'materials': materials[:5],
        'stats': stats
    })

@login_required
@user_passes_test(lambda u: u.is_uploader, login_url='/')
def material_upload_view(request):
    if request.method == 'POST':
        form = MaterialUploadForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            material = form.save(commit=False)
            material.uploaded_by = request.user
            
            # Auto-set department for class reps
            if request.user.is_uploader:
                material.department = request.user.department
                
            material.save()
            messages.success(request, 'Material Uploaded sucessfully!')
            return redirect('admin_dashboard')
    else:
        form = MaterialUploadForm(user=request.user)
    
    return render(request, 'materials_upload.html', {'form': form})

@login_required
def track_download(request, pk):
    try:
        material = get_object_or_404(Material, pk=pk)
        material.download_count += 1
        material.save()

        file_path = material.file.path
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
    except Material.DoesNotExist:
        raise Http404("Material not found.")
    except Exception as e:
        print(f'Download error: {e}')
        raise Http404("File unavailable.")