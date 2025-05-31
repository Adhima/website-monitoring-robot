const btnStop = document.getElementById("btn-stop");
const btnStart = document.getElementById("btn-start");
const statusText = document.getElementById("status-text");
const actionButtons = document.querySelectorAll(".btn-f, .btn-g, .btn-h");
const btnData = document.querySelector(".btn-data");

let startActivated = false;

document.querySelector('.btn-data').addEventListener('click', () => {
  window.location.href = "/data";
});

// Tombol START ditekan
btnStart.addEventListener("click", () => {
  if (!startActivated) {
    startActivated = true;
    btnStart.classList.replace("bg-blue-500", "bg-green-500");
    statusText.textContent = "ON";

    fetch("/motor", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ motor: true })
    });

    actionButtons.forEach(btn => {
      btn.disabled = false;
      btn.classList.replace("cursor-not-allowed", "cursor-pointer");
    });
  }
});

// Tombol Level 1/2/3
actionButtons.forEach(btn => {
  btn.addEventListener("click", () => {
    if (!btn.disabled) {
      actionButtons.forEach(b => {
        b.classList.replace("bg-green-500", "bg-blue-900");
      });

      btn.classList.replace("bg-blue-900", "bg-green-500");

      const level = btn.innerText.trim();
      let targetSpeed = 0;
      if (level === "Level 1") targetSpeed = 2;
      else if (level === "Level 2") targetSpeed = 4;
      else if (level === "Level 3") targetSpeed = 6;

      fetch("/motor_speed", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ speed: targetSpeed })
      });
    }
  });
});

// Tombol STOP ditekan
btnStop.addEventListener("click", () => {
  startActivated = false;
  btnStart.classList.replace("bg-green-500", "bg-blue-500");
  statusText.textContent = "OFF";

  fetch("/motor", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ motor: false })
  }).then(() => {
    // Reset speed juga
    fetch("/motor_speed", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ speed: 0 })
    });
  });

  actionButtons.forEach(btn => {
    btn.disabled = true;
    btn.classList.replace("bg-green-500", "bg-blue-900");
    btn.classList.replace("cursor-pointer", "cursor-not-allowed");
  });
});

// Tombol Toggle Manual
const btn = document.getElementById("toggle-btn");
btn.addEventListener("click", () => {
  btn.classList.toggle("bg-blue-500");
  btn.classList.toggle("bg-green-500");
});

// Logout
document.getElementById("confirm-logout").addEventListener("click", function () {
  window.location.href = "/logout";
});

// Toggle Lampu
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

// Dropdown kamera
document.addEventListener("DOMContentLoaded", function () {
  const dropdown = document.getElementById("dropdown");
  const button = document.getElementById("camera-select-btn");

  button.addEventListener("click", function (e) {
    e.stopPropagation();
    dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
  });
});

function toggleDropdown() {
  const dropdown = document.getElementById("dropdown");
  dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
}

// Tutup dropdown jika klik di luar
document.addEventListener("click", function (event) {
  if (!button.contains(event.target) && !dropdown.contains(event.target)) {
    dropdown.style.display = "none";
  }
});

// Fungsi Set Kamera
let currentCamera = null;
function setCamera(type) {
  const dropdown = document.getElementById("dropdown");
  dropdown.style.display = "none";

  const videoStream = document.getElementById("video-stream");
  if (!videoStream) return;

  if (type === "stop") {
    videoStream.src = "";
    currentCamera = null;
  } else {
    const newSrc = "/video_feed/" + type;
    if (videoStream.src !== location.origin + newSrc) {
      videoStream.src = newSrc;
    }
    currentCamera = type;
  }
}
