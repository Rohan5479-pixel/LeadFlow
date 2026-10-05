# ===========================
# Imports
# ===========================

import random
from datetime import timedelta
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from django.db.models import Sum


from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from io import BytesIO
from reportlab.lib.colors import navy
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from .forms import (
    BatchForm,
    CertificationForm,
    CounselorForm,
    CourseForm,
    ForgotPasswordForm,
    LeadForm,
    LoginForm,
    OTPForm,
    PaymentHistoryForm,
    ResetPasswordForm,
    StudentForm,
    EnrollmentForm,
    SubjectForm,
    TrainerForm,
    FeeForm,
    AttendanceForm,
)

from .models import (
    Batch,
    Certification,
    Counselor,
    Course,
    Fee,
    Lead,
    PaymentHistory,
    Student,
    Enrollment,
    Subject,
    Trainer,
    InstallmentPlan,
    Attendance,
)


# ===========================
# Permission
# ===========================

def admin_only(user):
    return (
        user.is_authenticated and
        (
            user.is_superuser or
            user.groups.filter(name="Admin").exists()
        )
    )

def admin_or_counselor(user):
    return (
        user.is_superuser or
        Counselor.objects.filter(email_id=user.username).exists()
    )

# ===========================
# Dashboard
# ===========================

# ===========================
# Dashboard
# ===========================

@login_required(login_url="login")
def dashboard(request):

    today = timezone.localdate()

    # -------------------------
    # Daily Collection
    # -------------------------
    daily_collection = PaymentHistory.objects.filter(
        payment_date=today
    ).aggregate(
        total=Sum("amount")
    )["total"] or 0

    # -------------------------
    # Monthly Collection
    # -------------------------
    monthly_collection = PaymentHistory.objects.filter(
        payment_date__year=today.year,
        payment_date__month=today.month
    ).aggregate(
        total=Sum("amount")
    )["total"] or 0

    # -------------------------
    # Quarterly Collection
    # -------------------------
    quarter = (today.month - 1) // 3 + 1
    start_month = (quarter - 1) * 3 + 1

    quarterly_collection = PaymentHistory.objects.filter(
        payment_date__year=today.year,
        payment_date__month__gte=start_month,
        payment_date__month__lte=start_month + 2
    ).aggregate(
        total=Sum("amount")
    )["total"] or 0

    # -------------------------
    # Monthly Enrollment
    # -------------------------
    monthly_enrollment = Enrollment.objects.filter(
        enrollment_date__year=today.year,
        enrollment_date__month=today.month
    ).count()

    # -------------------------
    # Quarterly Enrollment
    # -------------------------
    quarterly_enrollment = Enrollment.objects.filter(
        enrollment_date__year=today.year,
        enrollment_date__month__gte=start_month,
        enrollment_date__month__lte=start_month + 2
    ).count()

    # -------------------------
    # Dashboard Context
    # -------------------------
    context = {
        "course_count": Course.objects.count(),
        "counselor_count": Counselor.objects.count(),
        "lead_count": Lead.objects.count(),
        "trainer_count": Trainer.objects.count(),
        "batch_count": Batch.objects.count(),
        "recent_leads": Lead.objects.order_by("-lead_id")[:5],

        "daily_collection": daily_collection,
        "monthly_collection": monthly_collection,
        "quarterly_collection": quarterly_collection,

        "monthly_enrollment": monthly_enrollment,
        "quarterly_enrollment": quarterly_enrollment,
    }

    return render(
        request,
        "dashboard.html",
        context
    )

# ===========================
# Course
# ===========================

@login_required(login_url="login")
def course_list(request):

    courses = Course.objects.all()

    return render(
        request,
        "course/course_list.html",
        {
            "courses": courses
        }
    )

@login_required(login_url="login")
@user_passes_test(admin_or_counselor)
def course_add(request):

    form = CourseForm(request.POST or None)

    if request.method == "POST":

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Course added successfully."
            )

            return redirect("course_list")

    return render(
        request,
        "course/course_form.html",
        {
            "form": form
        }
    )


# ===========================
# Counselor
# ===========================

@login_required(login_url="login")
def counselor_list(request):

    counselors = Counselor.objects.all()

    return render(
        request,
        "counselor/counselor_list.html",
        {
            "counselors": counselors
        }
    )


@login_required(login_url="login")
@user_passes_test(admin_only)
def counselor_add(request):

    form = CounselorForm(request.POST or None)

    if request.method == "POST":

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Counselor added successfully."
            )

            return redirect("counselor_list")

    return render(
        request,
        "counselor/counselor_form.html",
        {
            "form": form
        }
    )


# ===========================
# Lead
# ===========================

@login_required(login_url="login")
def lead_list(request):

    is_counselor = request.user.groups.filter(
        name="Counselor"
    ).exists()

    if is_counselor:

        leads = Lead.objects.filter(
            counselor__email_id=request.user.email
        )

    else:

        leads = Lead.objects.all()

    return render(
        request,
        "lead/lead_list.html",
        {
            "leads": leads.order_by("-lead_id")
        }
    )


@login_required(login_url="login")
def lead_add(request):

    form = LeadForm(request.POST or None)

    if request.method == "POST":

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Lead added successfully."
            )

            return redirect("lead_list")

    return render(
        request,
        "lead/lead_form.html",
        {
            "form": form
        }
    )


@login_required(login_url="login")
def lead_edit(request, lead_id):

    lead = get_object_or_404(
        Lead,
        lead_id=lead_id
    )

    is_admin = admin_only(request.user)

    is_counselor = request.user.groups.filter(
        name="Counselor"
    ).exists()

    if lead.status == "Closed" and not is_admin:

        raise PermissionDenied(
            "Closed lead can only be edited by Admin."
        )

    if not is_admin and not is_counselor:

        raise PermissionDenied(
            "Only Admin or Counselor can edit leads."
        )

    form = LeadForm(
        request.POST or None,
        instance=lead
    )

    if request.method == "POST":

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Lead updated successfully."
            )

            return redirect("lead_list")

    return render(
        request,
        "lead/lead_form.html",
        {
            "form": form
        }
    )


# ===========================
# Trainer
# ===========================

@login_required(login_url="login")
@user_passes_test(admin_only)
def trainer_list(request):

    trainers = Trainer.objects.all()

    return render(
        request,
        "trainer/trainer_list.html",
        {
            "trainers": trainers
        }
    )


@login_required(login_url="login")
@user_passes_test(admin_only)
def trainer_add(request):

    form = TrainerForm(request.POST or None)

    if request.method == "POST":

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Trainer added successfully."
            )

            return redirect("trainer_list")

    return render(
        request,
        "trainer/trainer_form.html",
        {
            "form": form
        }
    )


# ===========================
# Batch
# ===========================

@login_required(login_url="login")
@user_passes_test(admin_only)
def batch_list(request):

    batches = Batch.objects.all()

    return render(
        request,
        "batch/batch_list.html",
        {
            "batches": batches
        }
    )


@login_required(login_url="login")
@user_passes_test(admin_only)
def batch_add(request):

    form = BatchForm(request.POST or None)

    if request.method == "POST":

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Batch added successfully."
            )

            return redirect("batch_list")

    return render(
        request,
        "batch/batch_form.html",
        {
            "form": form
        }
    )


# ===========================
# Login
# ===========================

def login_view(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    form = LoginForm()

    if request.method == "POST":

        form = LoginForm(request.POST)

        if form.is_valid():

            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = authenticate(
                request,
                username=email,
                password=password
            )

            if user:

                login(request, user)

                messages.success(
                    request,
                    "Login Successful."
                )

                return redirect("dashboard")

            messages.error(
                request,
                "Invalid Email or Password."
            )

    return render(
        request,
        "login.html",
        {
            "form": form
        }
    )


# ===========================
# Logout
# ===========================

@login_required(login_url="login")
def logout_view(request):

    logout(request)

    messages.success(
        request,
        "Logged out successfully."
    )

    return redirect("login")
# ===========================
# Forgot Password
# ===========================

def forgot_password(request):

    form = ForgotPasswordForm()

    if request.method == "POST":

        form = ForgotPasswordForm(request.POST)

        if form.is_valid():

            email = form.cleaned_data["email"]

            if User.objects.filter(email=email).exists():

                otp = random.randint(100000, 999999)

                request.session["otp"] = str(otp)
                request.session["email"] = email
                request.session["otp_time"] = timezone.now().isoformat()

                send_mail(
                    subject="Password Reset OTP",
                    message=f"Your OTP is {otp}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )

                messages.success(
                    request,
                    "OTP sent successfully."
                )

                return redirect("verify_otp")

            else:

                messages.error(
                    request,
                    "Email not found."
                )

    return render(
        request,
        "forgot_password.html",
        {
            "form": form
        }
    )


# ===========================
# Verify OTP
# ===========================

def verify_otp(request):

    form = OTPForm()

    if request.method == "POST":

        form = OTPForm(request.POST)

        if form.is_valid():

            entered_otp = form.cleaned_data["otp"]

            saved_otp = request.session.get("otp")
            otp_time = request.session.get("otp_time")

            if not saved_otp or not otp_time:

                messages.error(
                    request,
                    "OTP not found. Please request a new OTP."
                )

                return redirect("forgot_password")

            otp_datetime = parse_datetime(otp_time)

            if timezone.now() > otp_datetime + timedelta(minutes=5):

                messages.error(
                    request,
                    "OTP expired. Please request a new OTP."
                )

                return redirect("forgot_password")

            if entered_otp == saved_otp:

                return redirect("reset_password")

            messages.error(
                request,
                "Invalid OTP."
            )

    return render(
        request,
        "verify_otp.html",
        {
            "form": form
        }
    )


# ===========================
# Reset Password
# ===========================

def reset_password(request):

    form = ResetPasswordForm()

    if request.method == "POST":

        form = ResetPasswordForm(request.POST)

        if form.is_valid():

            password = form.cleaned_data["password"]
            confirm_password = form.cleaned_data["confirm_password"]

            if password != confirm_password:

                messages.error(
                    request,
                    "Passwords do not match."
                )

                return render(
                    request,
                    "reset_password.html",
                    {
                        "form": form
                    }
                )

            email = request.session.get("email")

            user = User.objects.get(username=email)

            user.set_password(password)
            user.save()

            request.session.pop("otp", None)
            request.session.pop("otp_time", None)
            request.session.pop("email", None)

            messages.success(
                request,
                "Password changed successfully."
            )

            return redirect("login")

    return render(
        request,
        "reset_password.html",
        {
            "form": form
        }
    )


# ===========================
# Student
# ===========================

@login_required(login_url="login")
def student_list(request):

    students = Student.objects.all()

    return render(
        request,
        "student/student_list.html",
        {
            "students": students
        }
    )



@login_required(login_url="login")
def student_add(request):

    form = StudentForm(request.POST or None)

    if request.method == "POST":

        if form.is_valid():

            student = form.save(commit=False)

            student.name = student.lead.name
            student.email_id = student.lead.email_id
            student.contact_number = student.lead.contact_number
            student.course = student.lead.course

            student.save()

            messages.success(
                request,
                "Student added successfully."
            )

            return redirect("student_list")

    return render(
        request,
        "student/student_form.html",
        {
            "form": form
        }
    )

# ==============================
# Enrollment Views
# ==============================

@login_required
def enrollment_list(request):
    enrollments = Enrollment.objects.select_related(
        "student",
        "batch"
    )

    return render(
        request,
        "enrollment/enrollment_list.html",
        {"enrollments": enrollments}
    )


@login_required
def enrollment_add(request):

    if request.method == "POST":
        form = EnrollmentForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("enrollment_list")

    else:
        form = EnrollmentForm()

    return render(
        request,
        "enrollment/enrollment_form.html",
        {"form": form}
    )




# ===========================
# Subject
# ===========================

@login_required(login_url="login")
def subject_list(request):

    subjects = Subject.objects.all()

    return render(
        request,
        "subject/subject_list.html",
        {
            "subjects": subjects
        }
    )


@login_required(login_url="login")
def subject_add(request):

    form = SubjectForm(request.POST or None)

    if request.method == "POST":

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Subject added successfully."
            )

            return redirect("subject_list")

    return render(
        request,
        "subject/subject_form.html",
        {
            "form": form
        }
    )


# ===========================
# Certification
# ===========================

@login_required(login_url="login")
def certification_list(request):

    certifications = Certification.objects.all()

    return render(
        request,
        "certification/certification_list.html",
        {
            "certifications": certifications
        }
    )
def download_certificate(request, certificate_id):

    certificate = get_object_or_404(
        Certification,
        pk=certificate_id
    )

    response = HttpResponse(content_type="application/pdf")

    response["Content-Disposition"] = (
        f'attachment; filename="Certificate_{certificate.student.name}.pdf"'
    )

    p = canvas.Canvas(response)

    # Title
    p.setFont("Helvetica-Bold", 24)
    p.setFillColor(navy)
    p.drawCentredString(300, 780, "Certificate of Completion")

    p.setFont("Helvetica", 14)
    p.setFillColorRGB(0, 0, 0)

    p.drawCentredString(
        300,
        730,
        "This certificate is proudly presented to"
    )

    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(
        300,
        690,
        certificate.student.name
    )

    p.setFont("Helvetica", 14)
    p.drawCentredString(
        300,
        650,
        "For successfully completing"
    )

    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(
        300,
        620,
        certificate.course.course_name
    )

    p.setFont("Helvetica", 12)

    p.drawString(
        80,
        560,
        f"Certificate Number : {certificate.certification_number}"
    )

    p.drawString(
        80,
        535,
        f"Issue Date : {certificate.issue_date}"
    )

    p.line(80, 120, 220, 120)
    p.drawString(100, 100, "Authorized Signature")

    p.showPage()
    p.save()

    return response

@login_required(login_url="login")
def send_certificate(request, certificate_id):

    certificate = get_object_or_404(
        Certification,
        certificate_id=certificate_id
    )

    buffer = BytesIO()

    p = canvas.Canvas(buffer)

    p.setFont("Helvetica-Bold", 24)
    p.setFillColor(navy)
    p.drawCentredString(300, 780, "Certificate of Completion")

    p.setFont("Helvetica", 14)
    p.setFillColorRGB(0,0,0)

    p.drawCentredString(
        300,
        730,
        "This certificate is proudly presented to"
    )

    p.setFont("Helvetica-Bold",20)
    p.drawCentredString(
        300,
        690,
        certificate.student.name
    )

    p.setFont("Helvetica",14)
    p.drawCentredString(
        300,
        650,
        "For successfully completing"
    )

    p.setFont("Helvetica-Bold",18)
    p.drawCentredString(
        300,
        620,
        certificate.course.course_name
    )

    p.drawString(
        80,
        560,
        f"Certificate Number : {certificate.certification_number}"
    )

    p.drawString(
        80,
        535,
        f"Issue Date : {certificate.issue_date}"
    )

    p.line(80,120,220,120)
    p.drawString(95,100,"Authorized Signature")

    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()

    email = EmailMessage(
        subject="Course Completion Certificate",
        body=f"""
Hello {certificate.student.name},

Congratulations!

Your course completion certificate is attached.

Regards,
LeadFlow
""",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[certificate.student.email_id],
    )

    email.attach(
        "Certificate.pdf",
        pdf,
        "application/pdf"
    )

    email.send()

    messages.success(
        request,
        "Certificate sent successfully."
    )

    return redirect(
        "certification_list"
    )


@login_required(login_url="login")
def certification_add(request):

    form = CertificationForm(request.POST or None)

    if request.method == "POST":

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Certification added successfully."
            )

            return redirect("certification_list")

    return render(
        request,
        "certification/certification_form.html",
        {
            "form": form
        }
    )


# ===========================
# Certificate View
# ===========================

@login_required(login_url="login")
def certificate_view(request, certificate_id):

    certificate = get_object_or_404(
        Certification,
        certificate_id=certificate_id
    )

    return render(
        request,
        "certification/certificate.html",
        {
            "certificate": certificate
        }
    )


# ===========================
# AJAX - Lead Details
# ===========================

@login_required(login_url="login")
def get_lead_details(request):

    lead_id = request.GET.get("lead_id")

    try:

        lead = Lead.objects.get(lead_id=lead_id)

        return JsonResponse({

            "name": lead.name,
            "email": lead.email_id,
            "contact": lead.contact_number,
            "course": lead.course.course_name,

        })

    except Lead.DoesNotExist:

        return JsonResponse({})
# ===========================
# Fee Management
# ===========================

@login_required(login_url="login")
def fee_list(request):

    fees = Fee.objects.all()

    return render(
        request,
        "fee/fee_list.html",
        {
            "fees": fees
        }
    )

@login_required(login_url="login")
def fee_detail(request, fee_id):

    fee = get_object_or_404(
        Fee,
        pk=fee_id
    )

    payments = PaymentHistory.objects.filter(
        fee=fee
    )

    installments = InstallmentPlan.objects.filter(
        fee=fee
    ).order_by(
        "installment_number"
    )

    return render(
        request,
        "fee/fee_detail.html",
        {
            "fee": fee,
            "payments": payments,
            "installments": installments
        }
    )
@login_required(login_url="login")
def fee_add(request):

    form = FeeForm(request.POST or None)

    if request.method == "POST":

        if form.is_valid():

            fee = form.save(commit=False)

            fee.save()


            # ==========================
            # CREATE EMI INSTALLMENTS
            # ==========================

            if fee.payment_type == "EMI":

                installment_count = fee.number_of_installments


                if installment_count > 0:

                    installment_amount = (
                        fee.net_payable_amount /
                        installment_count
                    )


                    from datetime import date

                    for i in range(1, installment_count + 1):
                        InstallmentPlan.objects.create(

                            fee=fee,

                            installment_number=i,

                            installment_amount=installment_amount,

                            paid_amount=0,

                            due_amount=installment_amount,

                            due_date=date.today(),

                            status="Pending"

                        )



            messages.success(
                request,
                "Fee added successfully."
            )


            return redirect("fee_list")


    return render(
        request,
        "fee/fee_add.html",
        {
            "form": form
        }
    )



# ===========================
# Payment History
# ===========================

@login_required(login_url="login")
def payment_history_list(request):

    payments = PaymentHistory.objects.select_related(
        "fee",
        "received_by"
    ).all()

    return render(
        request,
        "fee/payment_history_list.html",
        {
            "payments": payments
        }
    )
@login_required(login_url="login")
def payment_add(request):

    form = PaymentHistoryForm(request.POST or None)

    if request.method == "POST":

        if form.is_valid():



            payment = form.save(commit=False)

            payment.save()

            fee = payment.fee

            fee.amount_paid += payment.amount

            fee.due_amount = fee.net_payable_amount - fee.amount_paid

            if fee.due_amount <= 0:
                fee.payment_status = "Paid"
            else:
                fee.payment_status = "Partial"

            fee.last_payment_date = payment.payment_date

            fee.save()

            messages.success(
                request,
                "Payment added successfully."
            )

            return redirect("payment_history_list")


        print(form.errors)


    return render(
        request,
        "fee/payment_add.html",
        {
            "form": form
        }
    )


# ===========================
# AJAX - Fee Details
# ===========================

@login_required(login_url="login")
def get_fee_details(request):

    fee_id = request.GET.get("fee_id")

    try:

        fee = Fee.objects.select_related(
            "student"
        ).get(pk=fee_id)

        return JsonResponse({

            "student_id": fee.student.student_id,
            "student_name": fee.student.name,

        })

    except Fee.DoesNotExist:

        return JsonResponse({})

# ===========================
# Pay Installment
# ===========================

@login_required(login_url="login")
def installment_pay(request, installment_id):

    installment = get_object_or_404(
        InstallmentPlan,
        installment_id=installment_id
    )


    if request.method == "POST":

        paid_amount = request.POST.get("paid_amount")


        if paid_amount:

            paid_amount = float(paid_amount)


            installment.due_amount -= paid_amount


            if installment.due_amount <= 0:

                installment.due_amount = 0
                installment.status = "Paid"

            else:

                installment.status = "Partial"


            installment.save()



            fee = installment.fee


            fee.amount_paid += paid_amount


            fee.due_amount = (
                fee.net_payable_amount -
                fee.amount_paid
            )


            if fee.due_amount <= 0:

                fee.payment_status = "Paid"

            else:

                fee.payment_status = "Partial"



            fee.save()



            messages.success(
                request,
                "Installment payment added successfully."
            )


            return redirect(
                "fee_detail",
                fee_id=fee.fee_id
            )



    return render(
        request,
        "fee/installment_pay.html",
        {
            "installment": installment
        }
    )





# ===========================
# Edit Installment
# ===========================

@login_required(login_url="login")
def installment_edit(request, installment_id):


    installment = get_object_or_404(
        InstallmentPlan,
        installment_id=installment_id
    )



    if request.method == "POST":


        installment.due_amount = request.POST.get(
            "amount"
        )


        installment.due_date = request.POST.get(
            "due_date"
        )


        installment.status = request.POST.get(
            "status"
        )


        installment.save()



        messages.success(
            request,
            "Installment updated successfully."
        )



        return redirect(
            "fee_detail",
            fee_id=installment.fee.fee_id
        )



    return render(
        request,
        "fee/installment_edit.html",
        {
            "installment": installment
        }
    )

@login_required(login_url="login")
def attendance_list(request):

    attendance = Attendance.objects.select_related(
        "student",
        "batch"
    )

    return render(
        request,
        "attendance/attendance_list.html",
        {
            "attendance": attendance
        }
    )

@login_required(login_url="login")
def attendance_add(request):

    form = AttendanceForm(request.POST or None)

    if request.method == "POST":

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Attendance added successfully."
            )

            return redirect("attendance_list")

    return render(
        request,
        "attendance/attendance_form.html",
        {
            "form": form
        }
    )