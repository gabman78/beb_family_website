document.addEventListener("DOMContentLoaded", () => {

  const form = document.querySelector(".availability-form");
  if (!form) return;

  // Rileva la lingua dal tag <html lang="...">
  const lang = document.documentElement.lang || 'it';
  const isEn = lang.startsWith('en');

  const checkin = form.querySelector("input[name='checkin']");
  const checkout = form.querySelector("input[name='checkout']");
  const guests = form.querySelector("input[name='guests']");
  const msgDiv = form.querySelector(".availability-message");

  const maxGuests = parseInt(form.dataset.maxGuests) || 2;
  const ical = form.dataset.ical;

  // 🗓 Imposta il minimo check-out ogni volta che cambia il check-in
  checkin.addEventListener("change", () => {
    if (!checkin.value) return;

    const checkinDate = new Date(checkin.value);
    const nextDay = new Date(checkinDate.getTime() + 24*60*60*1000);
    const yyyy = nextDay.getFullYear();
    const mm = String(nextDay.getMonth() + 1).padStart(2, "0");
    const dd = String(nextDay.getDate()).padStart(2, "0");
    const minCheckout = `${yyyy}-${mm}-${dd}`;

    checkout.min = minCheckout;

    if (checkout.value && checkout.value < minCheckout) {
      checkout.value = minCheckout;
    }
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    // Pulisci messaggio precedente
    msgDiv.innerHTML = "";

    // Alert selezione date
    if (!checkin.value || !checkout.value) {
      const alertMsg = isEn ? "Please select check-in and check-out dates." : "Seleziona le date di check-in e check-out.";
      alert(alertMsg);
      return;
    }

    // Controllo numero ospiti
    if (parseInt(guests.value) > maxGuests) {
      const attnTitle = isEn ? "⚠️ Attention" : "⚠️ Attenzione";
      const attnMsg = isEn 
        ? `The property can accommodate a maximum of ${maxGuests} people.` 
        : `La struttura può ospitare al massimo ${maxGuests} persone.`;
      
      msgDiv.innerHTML = `
        <div class="p-4 bg-warning bg-opacity-10 rounded shadow text-center">
          <h4 class="fw-bold text-warning">${attnTitle}</h4>
          <p>${attnMsg}</p>
        </div>`;
      return;
    }


    try {
      const response = await fetch(
        `/check-availability/?checkin=${checkin.value}&checkout=${checkout.value}&ical=${encodeURIComponent(ical)}`
      );

      const data = await response.json();
      const disponibile = data.available;

      if (disponibile) {
        // Messaggi Disponibile
        const okTitle = isEn ? "Room Available!" : "Camera Disponibile!";
        const okMsg = isEn 
          ? "Contact us to receive more information or to proceed with the booking." 
          : "Contattaci per ricevere maggiori informazioni o per procedere con la prenotazione.";
        const callBtn = isEn ? "📞 Call now" : "📞 Chiama ora";
        const waBtn = isEn ? "💬 WhatsApp" : "💬 WhatsApp";

        msgDiv.innerHTML = `
          <div class="p-4 bg-success bg-opacity-10 rounded shadow-lg text-center">
            <h4 class="fw-bold text-success">${okTitle}</h4>
            <p class="mb-3">${okMsg}</p>
            <div class="d-flex justify-content-center gap-3 flex-wrap">
              <a href="tel:+393929093515" class="btn btn-success fw-bold text-white px-4 py-2 rounded-3">
                 ${callBtn}
              </a>
              <a href="https://wa.me/393929093515" target="_blank" class="btn btn-outline-success fw-bold px-4 py-2 rounded-3">
                 ${waBtn}
              </a>
            </div>
          </div>`;
      } else {
        // Messaggi Non Disponibile
        const noTitle = isEn ? "❌ Room not available" : "❌ Camera non disponibile";
        const noMsg = isEn 
          ? "We are sorry, but the room is already booked for the selected dates. Try changing rooms or dates!" 
          : "Siamo desolati, ma la camera è già prenotata per le date selezionate. Prova a cambiare camera o date!";

        msgDiv.innerHTML = `
          <div class="p-4 bg-danger bg-opacity-10 rounded shadow-lg text-center">
            <h4 class="fw-bold text-danger">${noTitle}</h4>
            <p>${noMsg}</p>
          </div>`;
      }

    } catch (err) {
      console.error("Errore:", err);
      const errTitle = isEn ? "❌ Error" : "❌ Errore";
      const errMsg = isEn 
        ? "An error occurred while checking availability." 
        : "Si è verificato un errore nel controllo disponibilità.";

      msgDiv.innerHTML = `
        <div class="p-4 bg-danger bg-opacity-10 rounded shadow text-center">
          <h4 class="fw-bold text-danger">${errTitle}</h4>
          <p>${errMsg}</p>
        </div>`;
    }
  });
});