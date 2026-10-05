from django.core.mail import send_mail
from django.conf import settings
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from django.contrib.auth.models import User
import random
import string




phone_validator = RegexValidator(
    regex=r'^\d{10}$',
    message='Enter exactly 10 digits.'
)



class Course(models.Model):
    COURSE_CHOICES = [
        ('Python', 'Python'),
        ('Java', 'Java'),
        ('Data Analytics', 'Data Analytics'),
        ('Data Science', 'Data Science'),
        ('Full Stack React', 'Full Stack React'),
        ('Full Stack Java', 'Full Stack Java'),
        ('Full Stack Python', 'Full Stack Python'),
        ('Azure Data Engineering', 'Azure Data Engineering'),
        ('DevOps', 'DevOps'),
        ('AWS', 'AWS'),
    ]

    course_id = models.CharField(
        max_length=10,
        primary_key=True,
        editable=False
    )

    course_name = models.CharField(
        max_length=100,
        choices=COURSE_CHOICES
    )

    course_description = models.TextField()

    def save(self, *args, **kwargs):

        if not self.course_id:

            last = Course.objects.order_by('course_id').last()

            if last:
                number = int(last.course_id[2:]) + 1
            else:
                number = 1

            self.course_id = f"CR{number:03d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.course_name


class Counselor(models.Model):
    counselor_id = models.CharField(
        max_length=10,
        primary_key=True,
        editable=False
    )

    name = models.CharField(max_length=100)
    email_id = models.EmailField(unique=True)

    contact = models.CharField(
        max_length=10,
        validators=[phone_validator],
        unique=True
    )

    def save(self, *args, **kwargs):

        is_new = self._state.adding

        if not self.counselor_id:

            last = Counselor.objects.order_by("counselor_id").last()

            if last:
                number = int(last.counselor_id[1:]) + 1
            else:
                number = 1

            self.counselor_id = f"C{number:03d}"

        super().save(*args, **kwargs)

        if is_new:

            if not User.objects.filter(username=self.email_id).exists():

                User.objects.create_user(
                    username=self.email_id,
                    email=self.email_id,
                    password="Rohan@123"
                )

                send_mail(
                    subject="LeadFlow Login Credentials",
                    message=f"""
Hello {self.name},

Welcome to LeadFlow.

Your account has been created successfully.

Login Email: {self.email_id}

Password: Rohan@123

Regards,
LeadFlow Team
""",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[self.email_id],
                    fail_silently=False,
                )

    def __str__(self):
        return self.name



class Trainer(models.Model):
    trainer_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Batch(models.Model):
    TYPE_CHOICES = [
        ('Weekdays', 'Weekdays'),
        ('Weekends', 'Weekends'),
    ]

    batch_id = models.AutoField(primary_key=True)
    batch_name = models.CharField(max_length=150)
    batch_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    batch_start_date = models.DateField()
    batch_timing = models.TimeField()
    batch_completion_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.batch_name


class Lead(models.Model):
    SOURCE_CHOICES = [
        ('Google', 'Google'),
        ('Just Dial', 'Just Dial'),
        ('Website', 'Website'),
        ('Direct', 'Direct'),
        ('WhatsApp', 'WhatsApp'),
    ]

    BACKGROUND_CHOICES = [
        ('IT Working', 'IT Working'),
        ('Non-IT Working', 'Non-IT Working'),
        ('Fresher', 'Fresher'),
        ('Gap', 'Gap'),
    ]

    DOMAIN_CHOICES = [
        ('BTech', 'BTech'),
        ('BSC', 'BSC'),
        ('MSC', 'MSC'),
    ]

    FLAG_CHOICES = [
        ('Positive', 'Positive'),
        ('Negative', 'Negative'),
        ('Neutral', 'Neutral'),
        ('Join SE', 'Join SE'),
    ]

    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('Closed', 'Closed'),
    ]

    lead_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email_id = models.EmailField()
    location = models.CharField(max_length=100)

    contact_number = models.CharField(
        max_length=10,
        unique=True,
        validators=[phone_validator]
    )

    whatsapp_number = models.CharField(
        max_length=10,
        validators=[phone_validator]
    )

    created_at = models.DateTimeField(auto_now_add=True)
    day = models.CharField(max_length=15, editable=False)

    source = models.CharField(max_length=30, choices=SOURCE_CHOICES)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    background = models.CharField(max_length=30, choices=BACKGROUND_CHOICES)
    domain = models.CharField(max_length=20, choices=DOMAIN_CHOICES)
    counselor = models.ForeignKey(Counselor, on_delete=models.CASCADE)

    flag = models.CharField(max_length=20, choices=FLAG_CHOICES)
    call_status = models.TextField()
    call_status_date = models.DateField()
    next_follow_up = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Open')

    def save(self, *args, **kwargs):
        if not self.day:
            self.day = timezone.localtime(timezone.now()).strftime('%A')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Student(models.Model):
    student_id = models.AutoField(primary_key=True)

    lead = models.OneToOneField(
        Lead,
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=100)
    email_id = models.EmailField()

    contact_number = models.CharField(
        max_length=10,
        validators=[phone_validator]
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )

    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE
    )

    admission_date = models.DateField(auto_now_add=True)


    def __str__(self):
        return self.name

class Enrollment(models.Model):

    STATUS_CHOICES = [
        ("Enrolled", "Enrolled"),
        ("Completed", "Completed"),
        ("Dropped", "Dropped"),
    ]

    enrollment_id = models.AutoField(primary_key=True)

    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE
    )

    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE
    )

    enrollment_date = models.DateField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Enrolled"
    )

    def __str__(self):
        return self.student.name


class Subject(models.Model):

    SUBJECT_CHOICES = [
        ('Full Stack', 'Full Stack'),
        ('Software Testing', 'Software Testing'),
    ]


    subject_id = models.AutoField(
        primary_key=True
    )

    subject_name = models.CharField(
        max_length=100,
        choices=SUBJECT_CHOICES
    )


    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )


    trainer = models.ForeignKey(
        Trainer,
        on_delete=models.CASCADE
    )


    def __str__(self):
        return self.subject_name

class Certification(models.Model):

    STATUS_CHOICES = [

        ('Pending','Pending'),

        ('Released','Released'),

        ('Held - fees due','Held - fees due'),

    ]


    certificate_id = models.AutoField(
        primary_key=True
    )


    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE
    )


    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )


    certification_number = models.CharField(
        max_length=7,
        unique=True,
        editable=False
    )


    issue_date = models.DateField()


    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    released_by = models.ForeignKey(
        Counselor,
        on_delete=models.SET_NULL,
        null=True
    )


    certification_field = models.TextField(
        default="Name, Certification Number, Course, Signature, Release Date"
    )



    def save(self,*args,**kwargs):

        if not self.certification_number:

            number = ''.join(
                random.choices(
                    string.ascii_uppercase +
                    string.digits,
                    k=7
                )
            )

            self.certification_number = number


        super().save(*args,**kwargs)



    def __str__(self):
        return self.certification_number


class Fee(models.Model):

    PAYMENT_STATUS = [
        ('Not Started', 'Not Started'),
        ('Partial', 'Partial'),
        ('Paid', 'Paid'),
        ('Over Due', 'Over Due'),
    ]

    fee_id = models.AutoField(primary_key=True)

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )

    total_fee_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    registration_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    PAYMENT_TYPE = [
        ('Full Payment', 'Full Payment'),
        ('EMI', 'EMI'),
    ]

    payment_type = models.CharField(
        max_length=20,
        choices=PAYMENT_TYPE,
        default='Full Payment'
    )

    number_of_installments = models.PositiveIntegerField(
        default=0
    )

    net_payable_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False
    )



    payment_type = models.CharField(
        max_length=20,
        choices=PAYMENT_TYPE,
        default='Full Payment'
    )


    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    due_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default='Not Started'
    )

    last_payment_date = models.DateField(
        blank=True,
        null=True
    )

    created_date = models.DateField(
        auto_now_add=True
    )

    def save(self, *args, **kwargs):

        self.net_payable_amount = (
                self.total_fee_amount
                - self.discount
                + self.registration_fee
        )

        self.due_amount = (
                self.net_payable_amount
                - self.amount_paid
        )

        if self.amount_paid == 0:
            self.payment_status = "Not Started"

        elif self.amount_paid < self.net_payable_amount:
            self.payment_status = "Partial"

        else:
            self.payment_status = "Paid"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.name} - {self.course.course_name} - ₹{self.due_amount} Due"

class PaymentHistory(models.Model):

    PAYMENT_MODE = [
        ('Cash', 'Cash'),
        ('UPI', 'UPI'),
        ('Bank Transfer', 'Bank Transfer'),
        ('Cheque', 'Cheque'),
    ]

    payment_id = models.AutoField(
        primary_key=True
    )

    fee = models.ForeignKey(
        Fee,
        on_delete=models.CASCADE
    )



    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_date = models.DateField(
        auto_now_add=True
    )

    payment_mode = models.CharField(
        max_length=20,
        choices=PAYMENT_MODE
    )

    transaction_ref = models.CharField(
        max_length=100,
        blank=True
    )

    received_by = models.ForeignKey(
        Counselor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True

    )

    remark = models.TextField(
        blank=True
    )

    def __str__(self):
        return str(self.payment_id)

class InstallmentPlan(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Partial', 'Partial'),
        ('Paid', 'Paid'),
        ('Over Due', 'Over Due'),
    ]


    installment_id = models.AutoField(
        primary_key=True
    )


    fee = models.ForeignKey(
        Fee,
        on_delete=models.CASCADE
    )


    installment_number = models.PositiveIntegerField()


    installment_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )


    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )


    due_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )


    due_date = models.DateField()


    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    def save(self, *args, **kwargs):

        self.due_amount = (
            self.installment_amount - self.paid_amount
        )


        if self.paid_amount == 0:

            self.status = "Pending"


        elif self.paid_amount < self.installment_amount:

            self.status = "Partial"


        else:

            self.status = "Paid"


        super().save(*args, **kwargs)



    def __str__(self):

        return f"{self.fee.student.name} - Installment {self.installment_number}"

class Attendance(models.Model):

    STATUS_CHOICES = [
        ("Present", "Present"),
        ("Absent", "Absent"),
        ("Leave", "Leave"),
    ]

    attendance_id = models.AutoField(
        primary_key=True
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE
    )

    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE
    )

    attendance_date = models.DateField()

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="Present"
    )

    def __str__(self):
        return f"{self.student.name} - {self.attendance_date}"

class Feedback(models.Model):

    RATING_CHOICES = [
        (1, "1 Star"),
        (2, "2 Star"),
        (3, "3 Star"),
        (4, "4 Star"),
        (5, "5 Star"),
    ]

    feedback_id = models.AutoField(
        primary_key=True
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE
    )

    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE
    )

    trainer = models.ForeignKey(
        Trainer,
        on_delete=models.CASCADE
    )

    rating = models.IntegerField(
        choices=RATING_CHOICES
    )

    comments = models.TextField(
        blank=True
    )

    submitted_date = models.DateField(
        auto_now_add=True
    )


    def __str__(self):
        return f"{self.student.name} - {self.rating} Star"



