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


import os
from django.conf import settings

def home(request):
    # Leggi tutti i file dalla cartella hero
    hero_folder = os.path.join(settings.MEDIA_ROOT, 'hero')
    
    images = []
    videos = []
    
    image_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.gif')
    video_extensions = ('.mp4', '.webm', '.mov', '.avi')
    
    if os.path.exists(hero_folder):
        for filename in sorted(os.listdir(hero_folder)):
            file_lower = filename.lower()
            
            if file_lower.endswith(image_extensions):
                images.append({
                    'type': 'image',
                    'url': f"{settings.MEDIA_URL}hero/{filename}",
                    'alt': filename.split('.')[0].replace('_', ' ')
                })
            elif file_lower.endswith(video_extensions):
                videos.append({
                    'type': 'video',
                    'url': f"{settings.MEDIA_URL}hero/{filename}",
                    'alt': filename.split('.')[0].replace('_', ' ')
                })
    
    # Crea la sequenza: 2 immagini, 1 video, 2 immagini, 1 video, ecc.
    hero_media = []
    images_per_group = 2
    
    # Calcola quante sequenze complete possiamo fare
    max_sequences = max(len(images) // images_per_group, 1)
    
    for seq in range(max_sequences):
        # Aggiungi gruppo di immagini
        start_idx = seq * images_per_group
        end_idx = start_idx + images_per_group
        if start_idx < len(images):
            group_images = images[start_idx:end_idx]
            hero_media.extend(group_images)
        
        # Aggiungi video (ciclico: quando finiscono i video, ricomincia dal primo)
        if videos:
            video_idx = seq % len(videos)
            hero_media.append(videos[video_idx])
    
    # Aggiungi eventuali immagini rimanenti
    remaining_images = images[len(hero_media)//2 * images_per_group:]
    hero_media.extend(remaining_images)
    
    # Se non ci sono file, usa quelli di default
    if not hero_media:
        hero_media = [
            {'type': 'image', 'url': '/media/foto_portici/IMG_1721.jpg', 'alt': 'Family Room Portici'},
            {'type': 'image', 'url': '/media/generali/prima.jpg', 'alt': 'Family Room Portici 2'},
        ]
    
    # Immagine per mobile
    mobile_image = '/media/foto_portici/IMG_1721.jpg'
    for media in hero_media:
        if media['type'] == 'image':
            mobile_image = media['url']
            break
    
    context = base_context()
    context.update({
        'hero_media': hero_media,
        'mobile_image': mobile_image,
    })
    
    return render(request, 'home.html', context)

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
            ics_url = None

            if "vesuvio" in nome:
                ics_url = ICAL_LINKS["vesuvio"]
            elif "plebiscito" in nome:
                ics_url = ICAL_LINKS["plebiscito"]
            elif "ovo" in nome:
                ics_url = ICAL_LINKS["ovo"]
            elif "casa" in nome or "home" in nome:
                ics_url = ICAL_LINKS["casa"]

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
        'ricerca_effettuata': ricerca_effettuata,
        # ⬇️ AGGIUNTI PER IL JAVASCRIPT
        'ical_vesuvio': ICAL_LINKS.get("vesuvio", ""),
        'ical_plebiscito': ICAL_LINKS.get("plebiscito", ""),
        'ical_castello': ICAL_LINKS.get("ovo", ""),
        'today': today,
        'guests': persone if persone else 2,
    })

    return render(request, 'prenotazioni.html', context)

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
    
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from icalendar import Calendar
from datetime import datetime, timedelta
import traceback
import sys

@csrf_exempt
def check_availability_multiple(request):
    """
    Controlla la disponibilità di tutte le camere
    """
    # FORZA print su stderr così appare nei log di Render
    print("=" * 50, file=sys.stderr)
    print("CHIAMATA A check_availability_multiple", file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    
    checkin = request.GET.get("checkin")
    checkout = request.GET.get("checkout")
    
    print(f"Check-in: {checkin}", file=sys.stderr)
    print(f"Check-out: {checkout}", file=sys.stderr)
    
    ical_vesuvio = request.GET.get("ical_vesuvio")
    ical_plebiscito = request.GET.get("ical_plebiscito")
    ical_castello = request.GET.get("ical_castello")
    
    print(f"URL Vesuvio: {ical_vesuvio}", file=sys.stderr)
    print(f"URL Plebiscito: {ical_plebiscito}", file=sys.stderr)
    print(f"URL Castello: {ical_castello}", file=sys.stderr)
    
    if not checkin or not checkout:
        print("ERRORE: Date mancanti", file=sys.stderr)
        return JsonResponse({"error": "Date mancanti"}, status=400)
    
    try:
        start_date = datetime.fromisoformat(checkin).date()
        end_date = datetime.fromisoformat(checkout).date()
        print(f"Date parsate: {start_date} - {end_date}", file=sys.stderr)
    except ValueError as e:
        print(f"ERRORE parsing date: {str(e)}", file=sys.stderr)
        return JsonResponse({"error": f"Formato data non valido: {str(e)}"}, status=400)
    
    cameras = [
        {"name": "Camera Vesuvio", "ical": ical_vesuvio},
        {"name": "Camera Piazza Plebiscito", "ical": ical_plebiscito},
        {"name": "Camera Castel dell'Ovo", "ical": ical_castello},
    ]
    
    results = []
    
    for camera in cameras:
        available = True
        print(f"\nControllo: {camera['name']}", file=sys.stderr)
        
        if camera["ical"]:
            try:
                print(f"Download iCal da: {camera['ical'][:100]}...", file=sys.stderr)
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (compatible; FamilyPortici/1.0)'
                }
                
                # Usa verify=False se hai problemi SSL
                response = requests.get(
                    camera["ical"], 
                    timeout=30, 
                    headers=headers,
                    verify=True  # Metti False se hai errori SSL
                )
                
                print(f"HTTP Status: {response.status_code}", file=sys.stderr)
                print(f"Content length: {len(response.content)} bytes", file=sys.stderr)
                
                # Stampa i primi 200 caratteri della risposta
                print(f"Primi 200 char: {response.text[:200]}", file=sys.stderr)
                
                response.raise_for_status()
                
                # Verifica che sia un file iCal valido
                if not response.text.strip().startswith('BEGIN:VCALENDAR'):
                    print("ERRORE: Il file non sembra essere un iCal valido", file=sys.stderr)
                    print(f"Contenuto ricevuto: {response.text[:500]}", file=sys.stderr)
                    available = False
                else:
                    cal = Calendar.from_ical(response.content)
                    events_count = 0
                    
                    for component in cal.walk("VEVENT"):
                        events_count += 1
                        try:
                            event_start = component.get("dtstart").dt
                            event_end = component.get("dtend").dt
                            
                            if isinstance(event_start, datetime):
                                event_start = event_start.date()
                            if isinstance(event_end, datetime):
                                event_end = event_end.date()
                            
                            print(f"  Evento {events_count}: {event_start} - {event_end}", file=sys.stderr)
                            
                            if start_date < event_end and end_date > event_start:
                                print(f"  >>> SOVRAPPOSIZIONE TROVATA! <<<", file=sys.stderr)
                                available = False
                                break
                        except Exception as e:
                            print(f"  Errore parsing evento: {str(e)}", file=sys.stderr)
                            continue
                    
                    print(f"Totale eventi: {events_count}", file=sys.stderr)
                    print(f"Disponibile: {available}", file=sys.stderr)
                        
            except requests.exceptions.SSLError as e:
                print(f"ERRORE SSL: {str(e)}", file=sys.stderr)
                available = False
            except requests.exceptions.Timeout:
                print(f"ERRORE: Timeout dopo 30 secondi", file=sys.stderr)
                available = False
            except requests.exceptions.ConnectionError as e:
                print(f"ERRORE Connessione: {str(e)}", file=sys.stderr)
                available = False
            except Exception as e:
                print(f"ERRORE generico: {str(e)}", file=sys.stderr)
                print(f"Traceback: {traceback.format_exc()}", file=sys.stderr)
                available = False
        else:
            print("Nessun URL iCal configurato", file=sys.stderr)
            available = False  # O True, dipende dalla tua logica
        
        results.append({
            "name": camera["name"],
            "available": available
        })
    
    print(f"\nRisultati finali: {results}", file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    
    return JsonResponse({"rooms": results})