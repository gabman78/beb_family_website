document.addEventListener("DOMContentLoaded", function() {
    console.log("✅ check_availability_beb.js caricato!");
    
    const form = document.getElementById("check-availability-form");
    
    if (!form) {
        console.error("❌ Form non trovato!");
        return;
    }
    
    const lang = document.documentElement.lang || 'it';
    const isEn = lang.startsWith('en');
    
    const checkinInput = document.getElementById("id_checkin");
    const checkoutInput = document.getElementById("id_checkout");
    const guestsInput = document.getElementById("id_guests");
    
    if (!checkinInput || !checkoutInput || !guestsInput) {
        console.error("❌ Input non trovati!");
        return;
    }
    
    // Trova il div messaggi
    const msgDiv = document.getElementById("availability-message");
    if (!msgDiv) {
        console.error("❌ #availability-message non trovato!");
        return;
    }
    
    const roomLinks = {
        "Camera Vesuvio": form.dataset.linkVesuvio,
        "Camera Piazza Plebiscito": form.dataset.linkPlebiscito,
        "Camera Castel dell'Ovo": form.dataset.linkCastello,
    };
    
    const maxGuests = 4;
    
    form.addEventListener("submit", async function(event) {
        event.preventDefault();
        console.log("🚀 Form inviato!");
        
        const checkin = checkinInput.value;
        const checkout = checkoutInput.value;
        const guests = parseInt(guestsInput.value) || 0;
        
        // Validazione
        if (!checkin || !checkout) {
            showMessage('warning', 
                isEn ? '⚠️ Attention' : '⚠️ Attenzione',
                isEn ? 'Please select check-in and check-out dates' : 'Seleziona check-in e check-out');
            return;
        }
        
        if (guests < 1 || guests > maxGuests) {
            showMessage('warning',
                isEn ? '⚠️ Attention' : '⚠️ Attenzione',
                isEn ? `Maximum ${maxGuests} guests allowed.` : `Massimo ${maxGuests} ospiti permessi.`);
            return;
        }
        
        // Mostra loader centrato
        msgDiv.innerHTML = `
            <div class="bg-white rounded-4 shadow-lg p-5 text-center" 
                 style="border: 2px solid #e6dccb;">
                <div class="spinner-border" role="status" style="color: #7a6652; width: 3rem; height: 3rem;">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-3 mb-0" style="color: #6c5b47; font-size: 1.1rem;">
                    ${isEn ? 'Checking availability...' : 'Verificando disponibilità...'}
                </p>
            </div>`;
        
        try {
            const params = new URLSearchParams({
                checkin: checkin,
                checkout: checkout,
                ical_vesuvio: form.dataset.icalVesuvio || '',
                ical_plebiscito: form.dataset.icalPlebiscito || '',
                ical_castello: form.dataset.icalCastello || '',
            });
            
            const url = `/check_availability_multiple/?${params.toString()}`;
            console.log("🌐 Chiamata a:", url);
            
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }
            
            const data = await response.json();
            console.log("📦 Dati ricevuti:", data);
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            const availableRooms = data.rooms ? data.rooms.filter(r => r.available) : [];
            
            if (availableRooms.length > 0) {
                // Mostra camere disponibili con stile uniforme
                let roomsHtml = availableRooms.map(room => {
                    const link = roomLinks[room.name] || '#';
                    return `
                        <div class="col-md-4 mb-3">
                            <a href="${link}" target="_blank" 
                               class="text-decoration-none">
                                <div class="card border-0 shadow-sm h-100" 
                                     style="background-color:#fff; transition: transform 0.2s;">
                                    <div class="card-body text-center">
                                        <div class="mb-2">
                                            <i class="fa-solid fa-circle-check fa-2x" style="color: #28a745;"></i>
                                        </div>
                                        <h5 class="fw-bold" style="color: #7a6652;">${room.name}</h5>
                                        <span class="badge px-3 py-2 mt-2" 
                                              style="background-color: #b59f84; font-size: 0.9rem;">
                                            ${isEn ? 'Available' : 'Disponibile'}
                                        </span>
                                    </div>
                                </div>
                            </a>
                        </div>`;
                }).join('');
                
                msgDiv.innerHTML = `
                    <div class="bg-white rounded-4 shadow-lg p-4 p-md-5" 
                         style="border: 2px solid #28a745; border-left: 6px solid #28a745;">
                        <div class="text-center mb-4">
                            <i class="fa-solid fa-circle-check fa-3x mb-3" style="color: #28a745;"></i>
                            <h4 class="fw-bold" style="color: #7a6652; font-family: 'Poppins', sans-serif;">
                                ${isEn ? 'Great news!' : 'Ottime notizie!'}
                            </h4>
                            <p style="color: #6c5b47; font-size: 1.1rem;">
                                ${isEn ? 'The following rooms are available for your dates:' : 'Le seguenti camere sono disponibili per le tue date:'}
                            </p>
                        </div>
                        
                        <div class="row justify-content-center g-3">
                            ${roomsHtml}
                        </div>
                        
                        <div class="text-center mt-4 pt-3 border-top" style="border-color: #e6dccb !important;">
                            <p class="mb-3" style="color: #6c5b47;">
                                ${isEn ? 'Book now or contact us:' : 'Prenota ora o contattaci:'}
                            </p>
                            <div class="d-flex justify-content-center gap-3 flex-wrap">
                                <a href="tel:+393929093515" 
                                   class="btn px-4 py-2 fw-bold text-white"
                                   style="background-color: #7a6652; border-radius: 30px;">
                                    <i class="fa-solid fa-phone me-2"></i>
                                    ${isEn ? 'Call now' : 'Chiama ora'}
                                </a>
                                <a href="https://wa.me/393929093515" target="_blank" 
                                   class="btn px-4 py-2 fw-bold"
                                   style="background-color: #25D366; color: white; border-radius: 30px;">
                                    <i class="fa-brands fa-whatsapp me-2"></i>
                                    WhatsApp
                                </a>
                            </div>
                        </div>
                    </div>`;
            } else {
                // Nessuna camera disponibile
                msgDiv.innerHTML = `
                    <div class="bg-white rounded-4 shadow-lg p-5 text-center" 
                         style="border: 2px solid #dc3545; border-left: 6px solid #dc3545;">
                        <i class="fa-solid fa-circle-xmark fa-3x mb-3" style="color: #dc3545;"></i>
                        <h4 class="fw-bold mb-3" style="color: #7a6652; font-family: 'Poppins', sans-serif;">
                            ${isEn ? 'No rooms available' : 'Nessuna camera disponibile'}
                        </h4>
                        <p style="color: #6c5b47; font-size: 1.1rem; max-width: 500px; margin: 0 auto;">
                            ${isEn 
                                ? 'We are sorry, but all rooms are already booked for the selected dates. Please try different dates or contact us for alternatives.'
                                : 'Siamo spiacenti, tutte le camere sono già prenotate per le date selezionate. Prova a cambiare date o contattaci per alternative.'
                            }
                        </p>
                        <div class="mt-4">
                            <a href="tel:+393929093515" 
                               class="btn px-4 py-2 fw-bold text-white"
                               style="background-color: #7a6652; border-radius: 30px;">
                                <i class="fa-solid fa-phone me-2"></i>
                                ${isEn ? 'Contact us' : 'Contattaci'}
                            </a>
                        </div>
                    </div>`;
            }
            
        } catch (error) {
            console.error("❌ Errore:", error);
            msgDiv.innerHTML = `
                <div class="bg-white rounded-4 shadow-lg p-5 text-center" 
                     style="border: 2px solid #ffc107; border-left: 6px solid #ffc107;">
                    <i class="fa-solid fa-triangle-exclamation fa-3x mb-3" style="color: #ffc107;"></i>
                    <h4 class="fw-bold mb-3" style="color: #7a6652;">
                        ${isEn ? 'Error' : 'Errore'}
                    </h4>
                    <p style="color: #6c5b47;">
                        ${isEn 
                            ? 'Unable to check availability. Please try again or contact us directly.'
                            : 'Impossibile verificare la disponibilità. Riprova o contattaci direttamente.'
                        }
                    </p>
                    <a href="tel:+393929093515" 
                       class="btn px-4 py-2 fw-bold text-white mt-3"
                       style="background-color: #7a6652; border-radius: 30px;">
                        <i class="fa-solid fa-phone me-2"></i>
                        392 9093515
                    </a>
                </div>`;
        }
    });
    
    console.log("✅ Form inizializzato con successo!");
});