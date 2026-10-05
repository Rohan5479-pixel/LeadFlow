from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Courses
    path('courses/', views.course_list, name='course_list'),
    path('courses/add/', views.course_add, name='course_add'),

    # Counselors
    path('counselors/', views.counselor_list, name='counselor_list'),
    path('counselors/add/', views.counselor_add, name='counselor_add'),

    # Leads
    path('leads/', views.lead_list, name='lead_list'),
    path('leads/add/', views.lead_add, name='lead_add'),
    path('leads/edit/<int:lead_id>/', views.lead_edit, name='lead_edit'),

    # Trainers
    path('trainers/', views.trainer_list, name='trainer_list'),
    path('trainers/add/', views.trainer_add, name='trainer_add'),

    # Batches
    path('batches/', views.batch_list, name='batch_list'),
    path('batches/add/', views.batch_add, name='batch_add'),

    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),

    # Students
    path('students/', views.student_list, name='student_list'),
    path('students/add/', views.student_add, name='student_add'),

    # Subjects
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/add/', views.subject_add, name='subject_add'),

    #enrollment
    path("enrollments/", views.enrollment_list, name="enrollment_list"),
    path("enrollments/add/", views.enrollment_add, name="enrollment_add"),

    # Certification
    path('certifications/', views.certification_list, name='certification_list'),
    path('certifications/add/', views.certification_add, name='certification_add'),
    path('certificate/<int:certificate_id>/', views.certificate_view, name='certificate_view'),
    path("certificate/<int:certificate_id>/download/",views.download_certificate,name="download_certificate",),
    path('certificate/send/<int:certificate_id>/',views.send_certificate,name='send_certificate'),

    # AJAX
    path('get-lead-details/', views.get_lead_details, name='get_lead_details'),
    path('get-fee-details/', views.get_fee_details, name='get_fee_details'),

    # Fees
    path("fees/", views.fee_list, name="fee_list"),
    path("fees/<int:fee_id>/",views.fee_detail, name="fee_detail"),
    path("fees/add/", views.fee_add, name="fee_add"),

    # Payment History
    path('payments/', views.payment_history_list, name='payment_history_list'),
    path('payments/add/', views.payment_add, name='payment_add'),

    # Installment
    path("installment/pay/<int:installment_id>/", views.installment_pay,name="installment_pay"),
    path("installment/edit/<int:installment_id>/", views.installment_edit,name="installment_edit"),

    #Attendance
    path("attendance/",views.attendance_list,name="attendance_list"),
    path("attendance/add/",views.attendance_add, name="attendance_add"),
]
