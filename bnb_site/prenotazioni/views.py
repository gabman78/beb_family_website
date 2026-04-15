from django.shortcuts import render
from django.conf import settings
from django.utils.dateparse import parse_date
from datetime import datetime, timedelta
from .models import Camera
from .utils.calendars import get_booking_events
import os
from django.http import JsonResponse
import requests
from icalendar import Calendar
# settings_private.py (nella stessa app)
import os
from dotenv import load_dotenv

# carica le variabili da link.env
env_path = os.path.join(os.path.dirname(__file__), '..', 'link.env')
load_dotenv(env_path)

ICAL_LINKS = {
    "vesuvio": os.getenv("VESUVIO"),
    "plebiscito": os.getenv("PLEBISCITO"),
    "ovo": os.getenv("OVO"),
    "casa": os.getenv("CASA"),
}

# CONTEXT BASE
def base_context():
    return {
        'brand_name': 'Family Room Portici',
        'telefono': '0810000000',
        'email': 'info@familyroomportici.it',
    }


# HOME
def home(request):
    return render(request, 'home.html', base_context())

def privacy_policy(request):
    return render(request, 'privacy_policy.html', base_context())

def termini_condizioni(request):
    return render(request, 'termini_condizioni.html', base_context())

def cookie_policy(request):
    return render(request, 'cookie_policy.html', base_context())

def contatti(request):
    context = base_context()
    context.update({
        'EMAILJS_USER_ID': os.getenv('EMAILJS_USER_ID'), # <-- CORRETTO QUI
        'EMAILJS_SERVICE_ID': os.getenv('EMAILJS_SERVICE_ID'),
        'EMAILJS_TEMPLATE_ID': os.getenv('EMAILJS_TEMPLATE_ID'),
    })
    return render(request, 'contatti.html', context)


def beb(request):
    context = base_context()
    context.update({
        "ical_vesuvio": ICAL_LINKS["vesuvio"],
        "ical_plebiscito": ICAL_LINKS["plebiscito"],
        "ical_castello": ICAL_LINKS["ovo"],
    })
    return render(request, 'beb.html', context)

# CASA VACANZE
def casavacanze(request):
    # Path delle foto
    folder_path = os.path.join(settings.MEDIA_ROOT, 'casa_vacanze')
    fotos = []

    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                fotos.append({'url': f"{settings.MEDIA_URL}casa_vacanze/{filename}"})

    context = base_context()
    context['fotos'] = fotos

    # Se vuoi anche il link iCal per la casa vacanze
    context['ical_link'] = ICAL_LINKS.get('casa')

    return render(request, 'casavacanze.html', context)


# CAMERE
def camere(request):

    camere = Camera.objects.all()

    context = base_context()
    context['camere'] = camere

    return render(request, 'camere.html', context)


# GALLERY
def gallery(request):
    return render(request, 'gallery.html', base_context())


# SERVIZI
def servizi(request):
    return render(request, 'servizi.html', base_context())



def cosafare(request):
    return render(request, 'cosafare.html')

def camera_vesuvio(request):
    context = base_context()
    context['ical_link'] = ICAL_LINKS['vesuvio']
    return render(request, 'camera_vesuvio.html', context)


def camera_piazzaplebiscito(request):
    context = base_context()
    context['ical_link'] = ICAL_LINKS['plebiscito']
    return render(request, 'camera_piazzaplebiscito.html', context)


def camera_casteldellovo(request):
    context = base_context()
    context['ical_link'] = ICAL_LINKS['ovo']  # supponendo che “ovo” corrisponda a Castello dell’Ovo
    return render(request, 'camera_casteldellovo.html', context)




# PRENOTAZIONI
def prenotazioni(request):

    camere = Camera.objects.all()

    checkin = request.GET.get('checkin')
    checkout = request.GET.get('checkout')
    persone = request.GET.get('persone')

    today = datetime.today().date()

    if not checkin:
        checkin = today.strftime('%Y-%m-%d')

    if not checkout:
        checkout = (today + timedelta(days=1)).strftime('%Y-%m-%d')

    ricerca_effettuata = bool(persone)

    camere_disponibili = []

    if ricerca_effettuata:

        checkin_date = parse_date(checkin)
        checkout_date = parse_date(checkout)

 

        for camera in camere:

            nome = camera.nome.lower()

            # dentro la funzione
            ics_url = None
            nome = camera.nome.lower()

            if "vesuvio" in nome:
                ics_url = ICAL_LINKS["vesuvio"]
            elif "plebiscito" in nome:
                ics_url = ICAL_LINKS["plebiscito"]
            elif "ovo" in nome:
                ics_url = ICAL_LINKS["ovo"]
            elif "casa" in nome or "home" in nome:
                ics_url = ICAL_LINKS["casa"]

            else:
                ics_url = None

            disponibile = True

            if ics_url:

                events = get_booking_events(ics_url)

                for event in events:

                    start = event["start"]
                    end = event["end"]

                    if checkin_date < end and checkout_date > start:
                        disponibile = False
                        break

            if disponibile and (not persone or int(persone) <= getattr(camera, 'capienza', 10)):
                camere_disponibili.append(camera)

    context = base_context()

    context.update({
        'camere': camere_disponibili,
        'checkin': checkin,
        'checkout': checkout,
        'persone': persone,
        'ricerca_effettuata': ricerca_effettuata
    })

    return render(request, 'prenotazioni.html', context)


from django.http import JsonResponse
import requests
from icalendar import Calendar
from datetime import datetime



def booking_calendar(request, room):
    url = ICAL_LINKS.get(room)
    if not url:
        return JsonResponse({"error": "Calendario non trovato"}, status=404)

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        cal = Calendar.from_ical(response.content)
        events = []

        for event in cal.walk("VEVENT"):
            start = event.get("DTSTART").dt
            end = event.get("DTEND").dt

            if isinstance(start, datetime):
                start = start.date()
            if isinstance(end, datetime):
                end = end.date()

            events.append({
                "start": start.isoformat(),
                "end": end.isoformat()
            })

        return JsonResponse(events, safe=False)

    except Exception as e:
        print("Errore nel fetch del calendario:", e)
        return JsonResponse([], safe=False)
    

from django.http import JsonResponse
import requests
from icalendar import Calendar
from datetime import datetime

def check_availability(request):

    checkin = request.GET.get("checkin")
    checkout = request.GET.get("checkout")
    ical_url = request.GET.get("ical")

    if not checkin or not checkout or not ical_url:
        return JsonResponse({"available": False}, status=400)

    start = datetime.fromisoformat(checkin).date()
    end = datetime.fromisoformat(checkout).date()

    try:
        response = requests.get(ical_url, timeout=10)
        response.raise_for_status()

        cal = Calendar.from_ical(response.content)

        disponibile = True

        for component in cal.walk("VEVENT"):

            event_start = component.get("dtstart").dt
            event_end = component.get("dtend").dt

            # normalizza a date
            if isinstance(event_start, datetime):
                event_start = event_start.date()

            if isinstance(event_end, datetime):
                event_end = event_end.date()

            if start < event_end and end > event_start:
                disponibile = False
                break

        return JsonResponse({"available": disponibile})

    except Exception as e:
        print("Errore check availability:", e)
        return JsonResponse({"available": False}, status=500)
    
# views.py
from django.http import JsonResponse
import requests

def check_availability_multiple(request):
    """
    Controlla la disponibilità di tutte le camere passate tramite iCal.
    """
    checkin = request.GET.get("checkin")
    checkout = request.GET.get("checkout")

    # I link iCal vengono passati come GET parameters
    ical_vesuvio = request.GET.get("ical_vesuvio")
    ical_plebiscito = request.GET.get("ical_plebiscito")
    ical_castello = request.GET.get("ical_castello")

    calendars = [
        {"name": "Camera Vesuvio", "ical": ical_vesuvio},
        {"name": "Camera Piazza Plebiscito", "ical": ical_plebiscito},
        {"name": "Camera Castel dell'Ovo", "ical": ical_castello},
    ]

    results = []

    for cam in calendars:
        try:
            url = f"http://127.0.0.1:8000/check-availability/?ical={cam['ical']}&checkin={checkin}&checkout={checkout}"
            r = requests.get(url)
            r.raise_for_status()
            data = r.json()
            available = data.get("available", False)
        except Exception:
            available = False
        results.append({"name": cam["name"], "available": available})

    return JsonResponse({"rooms": results})