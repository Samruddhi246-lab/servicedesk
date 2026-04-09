from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Complaint
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from django.core.paginator import Paginator

@login_required(login_url='/login/')
def home(request):
    return render(request, 'home.html')

from django.db.models import Q
@login_required
def dashboard(request):
    complaints_list = Complaint.objects.all().order_by('-id')

    # SEARCH
    search_query = request.GET.get('search')

    if search_query:
        complaints_list = complaints_list.filter(
        Q(id__iexact=search_query) |
        Q(title__icontains=search_query) |
        Q(description__icontains=search_query) |
        Q(status__icontains=search_query) |
        Q(created_by__username__icontains=search_query) |
        Q(created_at__icontains=search_query)
    )

    # PAGINATION
    from django.core.paginator import Paginator
    paginator = Paginator(complaints_list, 5)
    page_number = request.GET.get('page')
    complaints = paginator.get_page(page_number)

    # COUNTS
    pending = Complaint.objects.filter(status="Pending").count()
    in_progress = Complaint.objects.filter(status="In Progress").count()
    resolved = Complaint.objects.filter(status="Resolved").count()

    # ✅ THIS IS WHAT YOU WERE MISSING
    return render(request, 'dashboard.html', {
        'complaints': complaints,
        'pending': pending,
        'in_progress': in_progress,
        'resolved': resolved
    })
    

from django.contrib import messages

@login_required
def submit_complaint(request):
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        
        if not title or not description:
            return render(request, 'submit.html', {
        'error': 'All fields are required'
    })

        Complaint.objects.create(
            title=title,
            description=description,
            created_by=request.user
        )

        return redirect('dashboard')   # ✅ FIXED

    return render(request, 'submit.html')

@login_required
def delete_complaint(request, id):

    complaint = Complaint.objects.get(id=id)
    complaint.delete()

    return redirect("dashboard")


@login_required
def update_status(request, id):

    complaint = Complaint.objects.get(id=id)

    if complaint.status == "Pending":
        complaint.status = "In Progress"

    elif complaint.status == "In Progress":
        complaint.status = "Resolved"

    complaint.save()

    return redirect("dashboard")


@login_required
def track_complaint(request):

    complaint = None
    error = None

    if request.method == "POST":
        cid = request.POST.get("complaint_id")

        try:
            complaint = Complaint.objects.get(id=cid)
        except:
            error = "Complaint not found"

    return render(request, "track.html", {
        "complaint": complaint,
        "error": error
    })


from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login

from django.contrib import messages

def user_login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password ❌")

    return render(request, "login.html")


def register(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # ✅ CHECK IF USERNAME EXISTS
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists ❌")
            return redirect("register")

        # ✅ CREATE USER
        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, "Account created successfully ✅")
        return redirect("login")

    return render(request, "register.html")


def user_logout(request):

    logout(request)

    return redirect("login")

from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from datetime import datetime

@login_required
def download_report(request, id):

    complaint = Complaint.objects.get(id=id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="complaint_{id}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Header
    p.setFont("Helvetica-Bold", 22)
    p.drawString(200, height - 80, "HelpDeskPro")

    p.setFont("Helvetica", 12)
    p.drawString(220, height - 100, "Complaint Report")

    # Line
    p.line(50, height - 110, width - 50, height - 110)

    y = height - 150

    # Complaint Info
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Complaint Details")

    y -= 30
    p.setFont("Helvetica", 12)

    p.drawString(70, y, f"Complaint ID:")
    p.drawString(200, y, str(complaint.id))

    y -= 25
    p.drawString(70, y, "Title:")
    p.drawString(200, y, complaint.title)

    y -= 25
    p.drawString(70, y, "Description:")
    p.drawString(200, y, complaint.description)

    y -= 25
    p.drawString(70, y, "Status:")
    p.drawString(200, y, complaint.status)

    y -= 25
    p.drawString(70, y, "Created By:")
    p.drawString(200, y, str(complaint.created_by))

    y -= 25
    p.drawString(70, y, "Generated On:")
    p.drawString(200, y, datetime.now().strftime("%d-%m-%Y %H:%M"))

    # Footer
    p.line(50, 100, width - 50, 100)
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(200, 80, "Generated by HelpDeskPro System")

    p.save()

    return response

@login_required
def pending_list(request):

    complaints = Complaint.objects.filter(status="Pending")

    return render(request, "pending.html", {"complaints": complaints})


@login_required
def progress_list(request):

    complaints = Complaint.objects.filter(status="In Progress")

    return render(request, "progress.html", {"complaints": complaints})


@login_required
def resolved_list(request):

    complaints = Complaint.objects.filter(status="Resolved")

    return render(request, "resolved.html", {"complaints": complaints})
