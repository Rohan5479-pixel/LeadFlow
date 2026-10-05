from django import forms
from .models import (
    Course,
    Counselor,
    Lead,
    Trainer,
    Batch,
    Student,
    Enrollment,
    Subject,
    Certification,
    Fee,
    PaymentHistory,
    Attendance,

)

import re


EMAIL_PATTERN = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'


class CourseForm(forms.ModelForm):

    class Meta:
        model = Course
        fields = [
            'course_name',
            'course_description',
        ]



class CounselorForm(forms.ModelForm):

    class Meta:
        model = Counselor
        fields = '__all__'


    def clean_email_id(self):

        email = self.cleaned_data['email_id']

        if not re.match(EMAIL_PATTERN,email):

            raise forms.ValidationError(
                'Enter a valid email. Example: rohan@gmail.com'
            )

        return email



class LeadForm(forms.ModelForm):

    class Meta:

        model = Lead

        exclude = [
            'created_at',
            'day'
        ]


        widgets = {

            'call_status': forms.Textarea(
                attrs={'rows':3}
            ),

            'call_status_date': forms.DateInput(
                attrs={'type':'date'}
            ),

            'next_follow_up': forms.DateInput(
                attrs={'type':'date'}
            ),
        }



    def clean_email_id(self):

        email = self.cleaned_data['email_id']

        if not re.match(EMAIL_PATTERN,email):

            raise forms.ValidationError(
                'Enter a valid email.'
            )

        return email



class TrainerForm(forms.ModelForm):

    class Meta:

        model = Trainer

        fields = '__all__'



class BatchForm(forms.ModelForm):

    class Meta:

        model = Batch

        fields = '__all__'


        widgets = {

            'batch_start_date': forms.DateInput(
                attrs={'type':'date'}
            ),

            'batch_timing': forms.TimeInput(
                attrs={'type':'time'}
            ),

            'batch_completion_date': forms.DateInput(
                attrs={'type':'date'}
            ),
        }



class LoginForm(forms.Form):

    email = forms.EmailField(

        widget=forms.EmailInput(
            attrs={
                'class':'form-control',
                'placeholder':'Enter Email'
            }
        )
    )


    password = forms.CharField(

        widget=forms.PasswordInput(
            attrs={
                'class':'form-control',
                'placeholder':'Enter Password'
            }
        )
    )



class ForgotPasswordForm(forms.Form):

    email = forms.EmailField(

        label="Enter Registered Email",

        widget=forms.EmailInput(
            attrs={
                'class':'form-control',
                'placeholder':'Enter your Email'
            }
        )
    )



class OTPForm(forms.Form):

    otp = forms.CharField(

        max_length=6,

        widget=forms.TextInput(
            attrs={
                'class':'form-control',
                'placeholder':'Enter OTP'
            }
        )
    )



class ResetPasswordForm(forms.Form):

    password = forms.CharField(

        widget=forms.PasswordInput(
            attrs={
                'class':'form-control',
                'placeholder':'New Password'
            }
        )
    )


    confirm_password = forms.CharField(

        widget=forms.PasswordInput(
            attrs={
                'class':'form-control',
                'placeholder':'Confirm Password'
            }
        )
    )



class StudentForm(forms.ModelForm):

    class Meta:
        model = Student
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['lead'].queryset = Lead.objects.filter(status='Closed')

class EnrollmentForm(forms.ModelForm):

    class Meta:
        model = Enrollment
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        enrolled_ids = Enrollment.objects.values_list(
            "student_id",
            flat=True
        )

        self.fields["student"].queryset = Student.objects.exclude(
            student_id__in=enrolled_ids
        )



class SubjectForm(forms.ModelForm):

    class Meta:

        model = Subject

        fields = '__all__'


class CertificationForm(forms.ModelForm):

    class Meta:
        model = Certification
        fields = [
            "student",
            "course",
            "issue_date",
            "status",
            "released_by",
            "certification_field",
        ]

        widgets = {
            "issue_date": forms.DateInput(attrs={"type": "date"}),
            "certification_field": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        paid_students = Student.objects.filter(
            fee__payment_status="Paid"
        ).distinct()

        self.fields["student"].queryset = paid_students
class FeeForm(forms.ModelForm):

    class Meta:

        model = Fee

        fields = [
            "student",
            "course",
            "total_fee_amount",
            "discount",
            "registration_fee",
            "payment_type",
            "number_of_installments",
        ]


        widgets = {


            "student": forms.Select(
                attrs={
                    "class":"form-control"
                }
            ),


            "course": forms.Select(
                attrs={
                    "class":"form-control"
                }
            ),


            "total_fee_amount": forms.NumberInput(
                attrs={
                    "class":"form-control",
                    "placeholder":"Enter Total Fee"
                }
            ),


            "discount": forms.NumberInput(
                attrs={
                    "class":"form-control",
                    "placeholder":"Enter Discount"
                }
            ),


            "registration_fee": forms.NumberInput(
                attrs={
                    "class":"form-control",
                    "placeholder":"Enter Registration Fee"
                }
            ),


            "payment_type": forms.Select(
                attrs={
                    "class":"form-control"
                }
            ),


            "number_of_installments": forms.NumberInput(
                attrs={
                    "class":"form-control",
                    "min":1,
                    "placeholder":"Number of EMI"
                }
            ),

        }



    def clean_student(self):

        student = self.cleaned_data["student"]


        if Fee.objects.filter(
            student=student,
            payment_status="Paid"
        ).exists():

            raise forms.ValidationError(
                "This student already completed payment."
            )


        return student




    def clean(self):

        cleaned_data = super().clean()


        payment_type = cleaned_data.get(
            "payment_type"
        )


        installments = cleaned_data.get(
            "number_of_installments"
        )


        if payment_type == "EMI" and not installments:

            raise forms.ValidationError(
                "Enter number of installments for EMI payment."
            )


        return cleaned_data




    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)



        self.fields["number_of_installments"].initial = 0


        enrolled_students = Student.objects.filter(
            enrollment__status="Enrolled"
        ).exclude(
            fee__payment_status="Paid"
        )


        self.fields["student"].queryset = enrolled_students

class PaymentHistoryForm(forms.ModelForm):

    class Meta:
        model = PaymentHistory
        fields = [
            "fee",
            "amount",
            "payment_mode",
            "transaction_ref",
            "received_by",
            "remark",
        ]

        widgets = {

            "fee": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "payment_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control"
                }
            ),

            "payment_mode": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "transaction_ref": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "received_by": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "remark": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows":3
                }
            ),
        }


    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["fee"].queryset = Fee.objects.exclude(
            payment_status="Paid"
        )

        self.fields["received_by"].queryset = Counselor.objects.all()

class AttendanceForm(forms.ModelForm):

    class Meta:

        model = Attendance

        fields = "__all__"

        widgets = {

            "attendance_date": forms.DateInput(
                attrs={
                    "type": "date"
                }
            ),
        }