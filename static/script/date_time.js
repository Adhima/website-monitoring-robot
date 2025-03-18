function updateDateTime() {
    let now = new Date();

    // Format tanggal DD/MM/YYYY
    let date = now.getDate().toString().padStart(2, "0") + "/" +
               (now.getMonth() + 1).toString().padStart(2, "0") + "/" +
               now.getFullYear();

    // Format waktu HH:MM:SS
    let time = now.getHours().toString().padStart(2, "0") + ":" +
               now.getMinutes().toString().padStart(2, "0") + ":" +
               now.getSeconds().toString().padStart(2, "0");

    // Update elemen HTML
    document.getElementById("date").textContent = date;
    document.getElementById("time").textContent = time;
}

// Update setiap detik
setInterval(updateDateTime, 1000);
updateDateTime();
