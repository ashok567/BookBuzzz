from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import datetime, sys
from .models import BookInstance, Author, Genre, Book

class RenewBookForm(ModelForm):
    #renewal_date = forms.DateField(help_text="Enter a date between now and 4 weeks (default 3).")
    class Meta:
        model=BookInstance
        fields=['due_back',]
        labels={'due_back': _('Renewal date'),}
        help_texts={'due_back': _('Enter a date between now and 4 weeks (default 3).')}

    def clean_renewal_date(self):
        data = self.cleaned_data['due_back']

        #Check date is not in past.
        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        #Check date is in range librarian allowed to change (+4 weeks).
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

        # Remember to always return the cleaned data.
        return data

class NewBookForm(forms.Form):
    title = forms.CharField(max_length=200, help_text="Enter the title of Book")
    author = forms.ModelChoiceField(queryset=Author.objects.all())
    summary = forms.CharField(widget=forms.Textarea, help_text="Enter a brief description of the book")
    isbn = forms.CharField(max_length=200)
    genre = forms.MultipleChoiceField(choices=[(genre.pk, genre) for genre in Genre.objects.all()])


class SignupForm(forms.Form):
    username = forms.CharField()
    password= forms.CharField(widget=forms.PasswordInput)
    email=  forms.EmailField()

class PasswordResetForm(forms.Form):
    email= forms.EmailField()
    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            raise ValidationError("There is no user registered with the specified email address!")
        return email


class BorrowReturnForm(forms.Form):
    book = forms.ModelChoiceField(queryset=Book.objects.all())
    due_back = forms.DateField()



