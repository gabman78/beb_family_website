document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("form");
    
    // Rileva la lingua dal tag <html lang="...">
    const lang = document.documentElement.lang || 'it';
    const isEn = lang.startsWith('en');

    const icalVesuvio = form.dataset.icalVesuvio;
    const icalPlebiscito = form.dataset.icalPlebiscito;
    const icalCastello = form.dataset.icalCastello;
    const checkinInput = document.getElementById("checkin");
    const checkoutInput = document.getElementById("checkout");
    const guestsInput = document.getElementById("guests");

    const roomLinks = {
        "Camera Vesuvio": form.dataset.linkVesuvio,
        "Camera Piazza Plebiscito": form.dataset.linkPlebiscito,
        "Camera Castel dell'Ovo": form.dataset.linkCastello,
    };

    const msgDiv = document.createElement("div");
    msgDiv.style.marginTop = "20px";
    form.after(msgDiv);

    const maxGuests = 2;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const checkin = checkinInput.value;
        const checkout = checkoutInput.value;

        // Traduzione Alert iniziale
        if (!checkin || !checkout) {
            alert(isEn ? "Please select check-in and check-out dates" : "Seleziona check-in e check-out");
            return;
        }

        // Traduzione Errore Ospiti
        if (parseInt(guestsInput.value) > maxGuests) {
            msgDiv.innerHTML = `
                <div class="p-4 bg-warning bg-opacity-10 rounded shadow text-center">
                    <h4 class="fw-bold text-warning">⚠️ ${isEn ? 'Attention' : 'Attenzione'}</h4>
                    <p>${isEn ? `The room can accommodate a maximum of ${maxGuests} people.` : `La camera può ospitare al massimo ${maxGuests} persone.`}</p>
                </div>`;
            return;
        }

        const params = new URLSearchParams({
            checkin,
            checkout,
            ical_vesuvio: icalVesuvio,
            ical_plebiscito: icalPlebiscito,
            ical_castello: icalCastello,
        });

        const res = await fetch(`/check_availability_multiple/?${params.toString()}`);
        const data = await res.json();

        const availableCams = data.rooms.filter(r => r.available).map(r => r.name);

        if (availableCams.length > 0) {
            // Traduzione Messaggio Successo
            const title = isEn ? "Great news!" : "Ottime notizie!";
            const subtitle = isEn ? "The following rooms are available for your dates:" : "Le seguenti camere sono disponibili per le tue date:";
            const callBtn = isEn ? "📞 Call now" : "📞 Chiama ora";
            const waBtn = isEn ? "💬 WhatsApp" : "💬 WhatsApp";

            msgDiv.innerHTML = `
                <div class="p-4 bg-success bg-opacity-10 rounded shadow-lg text-center">
                    <h4 class="fw-bold text-success">${title}</h4>
                    <p>${subtitle}</p>
                    <ul style="list-style:none; padding:0; margin:10px 0;">
                        ${availableCams.map(c => `
                           <li>
                                ✅ <a href="${roomLinks[c]}" style="text-decoration:none; font-weight:600;" target="_blank">
                                    ${c}
                                </a>
                            </li>
                        `).join('')}
                    </ul>
                    <div class="d-flex justify-content-center gap-3 flex-wrap">
                        <a href="tel:+393929093515" class="btn btn-success fw-bold text-white px-4 py-2 rounded-3">
                            ${callBtn}
                        </a>
                        <a href="https://wa.me/393929093515" target="_blank" class="btn btn-outline-success fw-bold px-4 py-2 rounded-3">
                            ${waBtn}
                        </a>
                    </div>
                </div>
            `;
        } else {
            // Traduzione Messaggio Errore
            const errTitle = isEn ? "❌ No rooms available" : "❌ Nessuna camera disponibile";
            const errMsg = isEn 
                ? "We are sorry, but all rooms are already booked for the selected dates. Please try different dates!" 
                : "Siamo desolati, ma tutte le camere sono già prenotate per le date selezionate. Prova a cambiare date!";

            msgDiv.innerHTML = `
                <div class="p-4 bg-danger bg-opacity-10 rounded shadow-lg text-center">
                    <h4 class="fw-bold text-danger">${errTitle}</h4>
                    <p>${errMsg}</p>
                </div>
            `;
        }
    });
});