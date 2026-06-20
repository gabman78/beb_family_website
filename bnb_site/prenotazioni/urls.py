from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('beb/', views.beb, name='beb'),
    path('camera_vesuvio/', views.camera_vesuvio, name='camera_vesuvio'),
    path('camera_piazzaplebiscito/', views.camera_piazzaplebiscito, name='camera_piazzaplebiscito'),
    path('camera_casteldellovo/', views.camera_casteldellovo, name='camera_casteldellovo'),
    path('casavacanze/', views.casavacanze, name='casavacanze'),
    path('prenotazioni/', views.prenotazioni, name='prenotazioni'),
    path('camere/', views.camere, name='camere'),
    path('contatti/', views.contatti, name='contatti'),
    path('gallery/', views.gallery, name='gallery'),
    path('servizi/', views.servizi, name='servizi'),
    path("api/calendar/<str:room>/", views.booking_calendar, name="booking_calendar"),
    path("check-availability/", views.check_availability, name="check_availability"),
    path('cosafare/', views.cosafare, name='cosafare'),
    path('check_availability_multiple/', views.check_availability_multiple, name='check_availability_multiple'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('termini-e-condizioni/', views.termini_condizioni, name='termini_condizioni'),
    path('cookie-policy/', views.cookie_policy, name='cookie_policy'), 
    path('i18n/', include('django.conf.urls.i18n')),
    path('rosetta/', include('rosetta.urls'))
]
