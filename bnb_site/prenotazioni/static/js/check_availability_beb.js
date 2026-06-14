// Attendere che il DOM sia completamente caricato
document.addEventListener("DOMContentLoaded", function() {
    console.log("✅ check_availability_beb.js caricato!");
    
    // Trova il form
    const form = document.getElementById("check-availability-form");
    
    if (!form) {
        console.error("❌ Form #check-availability-form non trovato!");
        return;
    }
    
    console.log("✅ Form trovato");
    
    // Verifica data attributes
    console.log("Data attributes:", {
        ical_vesuvio: form.dataset.icalVesuvio ? "presente" : "mancante",
        ical_plebiscito: form.dataset.icalPlebiscito ? "presente" : "mancante",
        ical_castello: form.dataset.icalCastello ? "presente" : "mancante"
    });
    
    // Rileva lingua
    const lang = document.documentElement.lang || 'it';
    const isEn = lang.startsWith('en');
    
    // Trova gli input
    const checkinInput = document.getElementById("id_checkin");
    const checkoutInput = document.getElementById("id_checkout");
    const guestsInput = document.getElementById("id_guests");
    
    if (!checkinInput || !checkoutInput || !guestsInput) {
        console.error("❌ Input non trovati!");
        return;
    }
    
    console.log("✅ Tutti gli input trovati");
    
    // Trova o crea il div per i messaggi
    let msgDiv = document.getElementById("availability-message");
    if (!msgDiv) {
        console.warn("⚠️ #availability-message non trovato, lo creo");
        msgDiv = document.createElement("div");
        msgDiv.id = "availability-message";
        msgDiv.style.marginTop = "20px";
        form.parentNode.insertBefore(msgDiv, form.nextSibling);
    }
    
    // Mappa dei link delle camere
    const roomLinks = {
        "Camera Vesuvio": form.dataset.linkVesuvio,
        "Camera Piazza Plebiscito": form.dataset.linkPlebiscito,
        "Camera Castel dell'Ovo": form.dataset.linkCastello,
    };
    
    const maxGuests = 4;
    
    // Gestione submit
    form.addEventListener("submit", async function(event) {
        event.preventDefault();
        console.log("🚀 Form inviato!");
        
        const checkin = checkinInput.value;
        const checkout = checkoutInput.value;
        const guests = parseInt(guestsInput.value) || 0;
        
        console.log("Valori:", { checkin, checkout, guests });
        
        // Validazione
        if (!checkin || !checkout) {
            alert(isEn ? "Please select check-in and check-out dates" : "Seleziona check-in e check-out");
            return;
        }
        
        if (guests < 1 || guests > maxGuests) {
            msgDiv.innerHTML = `
                <div class="alert alert-warning text-center">
                    <strong>⚠️ ${isEn ? 'Attention' : 'Attenzione'}</strong><br>
                    ${isEn ? `Maximum ${maxGuests} guests allowed.` : `Massimo ${maxGuests} ospiti.`}
                </div>`;
            return;
        }
        
        // Mostra loader
        msgDiv.innerHTML = `
            <div class="text-center p-4">
                <div class="spinner-border text-secondary" role="status"></div>
                <p class="mt-2">${isEn ? 'Checking availability...' : 'Verificando disponibilità...'}</p>
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
            console.log("📡 Status:", response.status);
            
            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }
            
            const data = await response.json();
            console.log("📦 Dati ricevuti:", data);
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Filtra camere disponibili
            const availableRooms = data.rooms ? data.rooms.filter(r => r.available) : [];
            console.log("✅ Camere disponibili:", availableRooms);
            
            if (availableRooms.length > 0) {
                let roomsHtml = availableRooms.map(room => {
                    const link = roomLinks[room.name] || '#';
                    return `
                        <li class="mb-2">
                            ✅ <a href="${link}" target="_blank" style="color:#7a6652; font-weight:600; text-decoration:none;">
                                ${room.name}
                            </a>
                        </li>`;
                }).join('');
                
                msgDiv.innerHTML = `
                    <div class="p-4 bg-success bg-opacity-10 rounded shadow text-center">
                        <h4 class="text-success fw-bold">
                            ${isEn ? 'Great news!' : 'Ottime notizie!'}
                        </h4>
                        <p>${isEn ? 'Available rooms:' : 'Camere disponibili:'}</p>
                        <ul style="list-style:none; padding:0;">${roomsHtml}</ul>
                        <div class="mt-3">
                            <a href="tel:+393929093515" class="btn btn-success me-2">
                                📞 ${isEn ? 'Call' : 'Chiama'}
                            </a>
                            <a href="https://wa.me/393929093515" target="_blank" class="btn btn-outline-success">
                                💬 WhatsApp
                            </a>
                        </div>
                    </div>`;
            } else {
                msgDiv.innerHTML = `
                    <div class="p-4 bg-danger bg-opacity-10 rounded shadow text-center">
                        <h4 class="text-danger fw-bold">
                            ${isEn ? 'No availability' : 'Nessuna disponibilità'}
                        </h4>
                        <p>${isEn 
                            ? 'All rooms are booked. Try different dates.'
                            : 'Tutte le camere sono prenotate. Prova altre date.'
                        }</p>
                    </div>`;
            }
            
        } catch (error) {
            console.error("❌ Errore:", error);
            msgDiv.innerHTML = `
                <div class="alert alert-danger text-center">
                    <strong>${isEn ? 'Error' : 'Errore'}</strong><br>
                    ${isEn ? 'Unable to check availability.' : 'Impossibile verificare la disponibilità.'}
                    <br><small class="text-muted">${error.message}</small>
                </div>`;
        }
    });
    
    console.log("✅ Event listener aggiunto al form!");
});