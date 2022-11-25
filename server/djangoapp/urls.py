from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'djangoapp'
urlpatterns = [
    # route is a string contains a URL pattern
    # view refers to the view function
    # name the URL

    # path for about view
    path('about/',view=views.about,name='about'),
    # path for contact us view
    path('contact/',view=views.contactus,name='contactinfo'),
    # path for registration
    path('registration_page/',view=views.registration_request,name='registration'),
    # path for login
    path('login/',view=views.login_request,name='login'),
    # path for logout
    path('logout/',view=views.logout_request,name='logout'),
    path(route='', view=views.get_dealerships, name='index'),
    path(route='dealer/<int:dealer_id>/',view=views.get_dealer_details,name='dealer_details'),
    path(route="dealer/<int:dealer_id>/submit",view=views.add_review,name='post_review')

    # path for dealer reviews view

    # path for add a review view

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)