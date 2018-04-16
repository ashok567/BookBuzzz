from django.contrib import admin
from django.shortcuts import render
from .models import Author, Genre, Book, BookInstance
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.urls import reverse, reverse_lazy
from django.contrib.auth.models import User
from django import forms
from weasyprint import HTML
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from .tokens import account_activation_token
from django.contrib.auth import login, authenticate



import datetime, base64

from .forms import RenewBookForm, NewBookForm, SignupForm, BorrowReturnForm
from .models import Author, Book


def index(request):
    no_books=Book.objects.all().count()
    no_instances=BookInstance.objects.all().count()
    no_instances_available=BookInstance.objects.filter(status__exact='a').count()
    no_authors=Author.objects.count()
    num_visits=request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits+1

    context= {'num_books':no_books,'num_instances':no_instances,
             'num_instances_available':no_instances_available,
             'num_authors':no_authors,'num_visits':num_visits}

    return render(request, 'list/index.html', context)


class BookList(generic.ListView):
    model=Book
    paginate_by=5

class AuthorList(generic.ListView):
    model=Author
    paginate_by=5

class BookDetail(generic.DetailView):
    model = Book

class AuthorDetail(generic.DetailView):
    model = Author


def renew_book(request, pk):
    book_inst=get_object_or_404(BookInstance, pk = pk)

    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_inst.due_back = form.cleaned_data['due_back']
            book_inst.save()

            return HttpResponseRedirect(reverse('books') )


    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'due_back': proposed_renewal_date,})

    return render(request, 'list/renw_book.html', {'form': form, 'bookinst':book_inst})


class LoanedBooks(LoginRequiredMixin,generic.ListView):
    model = BookInstance
    template_name ='list/borrowed_user.html'
    paginate_by = 5

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

class AuthorCreate(CreateView):
    model=Author
    fields='__all__'

class AuthorUpdate(UpdateView):
    model = Author
    fields=['first_name','last_name','date_of_birth','date_of_death']

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('author')


class BookCreate(CreateView):
    model = Book
    fields='__all__'

class BookUpdate(UpdateView):
    model = Book
    fields='__all__'

class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')


def new_book(request):

    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = NewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            new = Book()
            new.title=form.cleaned_data['title']
            new.author=form.cleaned_data['author']
            new.summary=form.cleaned_data['summary']
            new.isbn=form.cleaned_data['isbn']
            new.save()
            new.genre.set(form.cleaned_data['genre'])

            return HttpResponseRedirect(reverse('books'))


    else:
        form = NewBookForm()

    return render(request, 'list/new_book.html', {'form': form})


def update_book(request, pk):
    book=get_object_or_404(Book, pk = pk)

    if request.method == 'POST':
        form = NewBookForm(request.POST)

        if form.is_valid():

            book.title=form.cleaned_data['title']
            book.author=form.cleaned_data['author']
            book.summary=form.cleaned_data['summary']
            book.isbn=form.cleaned_data['isbn']
            book.save()
            #book.genre.set(form.cleaned_data['genre'])

            return HttpResponseRedirect(reverse('books'))

    else:
        form = NewBookForm(initial={'title': book.title, 'author': book.author, 'summary': book.summary, 'isbn': book.isbn, })

    return render(request, 'list/update_book.html', {'form': form, 'book': book})

def signup(request):
    if request.method== 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(username=form.cleaned_data['username'],                                          password=form.cleaned_data['password'],                                                                               email=form.cleaned_data['email'])

            #user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            uid = urlsafe_base64_encode(force_bytes(user.pk)).decode('utf8')
            mail_subject = 'Activate your LocalLibrary account'
            message = render_to_string('list/email.html', {
                'domain': current_site.domain,
                'uidb64': uid,
                'token': account_activation_token.make_token(user),
            })

            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                        mail_subject, message, to=[to_email])

            email.send()
            return HttpResponseRedirect('/accounts/login')

    else:

        form = SignupForm()
    return render(request, 'list/signup.html', {'form': form})



def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        #login(request, user)
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')

def pdf_generation(request, pk):
    #html_temp = get_template('list/book_detail.html')
    book = get_object_or_404(Book, pk = pk)
    html_temp = render_to_string('list/book_pdf.html', {'book': book})
    pdf_file = HTML(string=html_temp, base_url=request.build_absolute_uri()).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf;')
    response['Content-Disposition'] = 'filename='+book.title+'.pdf'

    return response


def reset(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        email = form.cleaned_data.get('email')
        if form.is_valid():
            mail_subject = 'Activate your LocalLibrary account'
            message = render_to_string('list/password_reset_email.html')
            to_email = email
            email = EmailMessage(
                mail_subject, message, to=[to_email])

            email.send()
            return HttpResponseRedirect('list/password_reset_done.html')

    else:
        form =PasswordResetForm()

    return render(request, 'templates/registration/password_reset_form.html', {'form': form})


def borrow(request):
    if request.method == 'POST':
        form = BorrowReturnForm(request.POST)
        if form.is_valid():
            book_inst = BookInstance()
            book_inst.book = form.cleaned_data.get('book')
            book_inst.imprint = 1
            book_inst.due_back = form.cleaned_data.get('due_back')
            book_inst.status = 'o'
            book_inst.borrower = request.user
            book_inst.save()
            return HttpResponseRedirect(reverse('borrow'))


    else:
        form = BorrowReturnForm()

    return render(request, 'list/borrow.html', {'form': form})



def return_book(request,pk):
    book_inst = BookInstance.objects.get(pk=pk)
    book_inst.delete()
    return HttpResponseRedirect(reverse('borrow'))
