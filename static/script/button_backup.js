const btnStop = document.getElementById("btn-stop");
const btnStart = document.getElementById("btn-start");
const statusText = document.getElementById("status-text");
const actionButtons = document.querySelectorAll(".btn-f, .btn-g, .btn-h");

let startActivated = false; // Status apakah START sudah ditekan

// Ketika tombol START ditekan
btnStart.addEventListener("click", () => {
    if (!startActivated) {
        startActivated = true;
        btnStart.classList.replace("bg-blue-500", "bg-green-500"); // START jadi hijau
        statusText.textContent = "ON";
        // Aktifkan tombol 1, 2, 3 (tetap biru gelap sebelum diklik)
        actionButtons.forEach(btn => {
            btn.disabled = false;
            btn.classList.replace("cursor-not-allowed", "cursor-pointer");
        });
    }
});

// Ketika salah satu tombol 1, 2, atau 3 ditekan
actionButtons.forEach(btn => {
    btn.addEventListener("click", () => {
        if (!btn.disabled) {
            // Reset semua tombol ke biru gelap
            actionButtons.forEach(b => {
                b.classList.replace("bg-green-500", "bg-blue-900");
            });

            // Ubah tombol yang diklik menjadi hijau
            btn.classList.replace("bg-blue-900", "bg-green-500");
        }
    });
});

// Ketika tombol STOP ditekan
btnStop.addEventListener("click", () => {
    startActivated = false;
    btnStart.classList.replace("bg-green-500", "bg-blue-500"); // START kembali biru
    statusText.textContent = "OFF";

    // Reset tombol 1, 2, 3 ke biru gelap dan nonaktifkan
    actionButtons.forEach(btn => {
        btn.disabled = true;
        btn.classList.replace("bg-green-500", "bg-blue-900");
        btn.classList.replace("cursor-pointer", "cursor-not-allowed");
    });
});

const btn = document.getElementById("toggle-btn");

btn.addEventListener("click", () => {
    btn.classList.toggle("bg-blue-500"); // Warna aktif (biru)
    btn.classList.toggle("bg-green-500"); // Warna non-aktif (abu)
});

// Tombol Log Out
  document.getElementById("confirm-logout").addEventListener("click", function() {
    window.location.href = "/logout"; // Redirect ke route logout Flask
  });


// Tombol Toggle Lampu
function toggleLamp() {
  let lampStatus = document.getElementById("lamp-status");
  let lampBtn = document.querySelector(".btn-e");

  let newStatus = (lampStatus.innerText === "OFF") ? "ON" : "OFF";
  lampStatus.innerText = newStatus;
  lampBtn.classList.toggle("active", newStatus === "ON");

  fetch("/lamp", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ lamp: newStatus === "ON" })
  });
}

document.addEventListener("DOMContentLoaded", function () {
  const dropdown = document.getElementById("dropdown");
  const button = document.getElementById("camera-select-btn");

  // Toggle dropdown saat tombol diklik
  button.addEventListener("click", function (e) {
    e.stopPropagation();
    dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
  });

  // Tutup dropdown saat klik di luar
  document.addEventListener("click", function (event) {
    if (!dropdown.contains(event.target) && event.target !== button) {
      dropdown.style.display = "none";
    }
  });
});

// Fungsi setCamera final
function setCamera(type) {
  // Tutup dropdown
  const dropdown = document.getElementById("dropdown");
  dropdown.style.display = "none";

  // Ganti source video stream
  const videoStream = document.getElementById("video-stream");
  if (videoStream) {
    videoStream.src = "/video_feed/" + type;
  }

  // Jangan ubah tombol. Biarkan tetap <img>.
}