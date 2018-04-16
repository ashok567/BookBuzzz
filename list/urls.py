from django.conf.urls import url, include

from . import views
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^book/$', views.BookList.as_view(), name='books'),
    url(r'^book/(?P<pk>\d+)$', views.BookDetail.as_view(), name='book-detail'),
    url(r'^author/$', views.AuthorList.as_view(), name='author'),
    url(r'^author/(?P<pk>\d+)$', views.AuthorDetail.as_view(), name='author-detail'),
    url(r'^book/(?P<pk>[-\w]+)/renew/$', views.renew_book, name='renew-book'),
    url(r'^borrow/$', views.LoanedBooks.as_view(), name='borrow'),
    url(r'^return/(?P<pk>.+)$', views.return_book, name='return'),
    url(r'^borrow/form/$', views.borrow, name='borrow-form'),
    url('^author/create/$', views.AuthorCreate.as_view(), name='author_create'),
    url('^author/(?P<pk>\d+)/update/', views.AuthorUpdate.as_view(), name='author_update'),
    url('^author/(?P<pk>\d+)/delete/', views.AuthorDelete.as_view(), name='author_delete'),
    url('^book/create/', views.new_book, name='book_create'),
    url('^book/(?P<pk>\d+)/update/', views.update_book, name='book_update'),
    url('^book/(?P<pk>\d+)/delete/', views.BookDelete.as_view(), name='book_delete'),
    url('^book/(?P<pk>\d+)/download/$', views.pdf_generation, name='download'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
        views.activate, name='activate'),
    url(r'^accounts/password_reset/', views.reset, name='password_reset')

    ]
