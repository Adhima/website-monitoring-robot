const btnStop = document.getElementById("btn-stop");
const btnStart = document.getElementById("btn-start");
const statusText = document.getElementById("status-text");
const actionButtons = document.querySelectorAll(".btn-f, .btn-g, .btn-h");
const btnData = document.querySelector(".btn-data");

let startActivated = false;

document.querySelector('.btn-data').addEventListener('click', () => {
  window.location.href = "/data";
});

// START ditekan
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
      btn.classList.remove("opacity-50");
    });

    // Aktifkan tombol arah
    btnForward.disabled = false;
    btnReverse.disabled = false;
    btnForward.classList.remove("opacity-50");
    btnReverse.classList.remove("opacity-50");
  }
});

// LEVEL
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

// STOP ditekan
btnStop.addEventListener("click", () => {
  startActivated = false;
  btnStart.classList.replace("bg-green-500", "bg-blue-500");
  statusText.textContent = "OFF";

  fetch("/motor", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ motor: false })
  }).then(() => {
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

  // Reset tombol arah
  btnForward.classList.remove("bg-green-500");
  btnReverse.classList.remove("bg-green-500");
  btnForward.disabled = true;
  btnReverse.disabled = true;
  btnForward.classList.add("opacity-50");
  btnReverse.classList.add("opacity-50");
});

// TOGGLE MANUAL
const manualBrakeBtn = document.getElementById("toggle-btn");
const brakeIndicator = document.getElementById("brake-indicator");

manualBrakeBtn.addEventListener("click", function () {
  const isBraking = manualBrakeBtn.classList.toggle("bg-green-500");
  manualBrakeBtn.classList.toggle("bg-blue-500", !isBraking);
  brakeIndicator.textContent = isBraking ? "Braking" : "Not Braking";
  fetch("/manual_brake", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ manual_brake: isBraking })
  });
});

// LOGOUT
document.getElementById("confirm-logout").addEventListener("click", function () {
  window.location.href = "/logout";
});

// TOGGLE LAMPU
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

function setCamera(type) {
  const videoStream = document.getElementById("video-stream");
  if (!videoStream) return;

  // Stop semua WebRTC sebelum ganti kamera
  stopWebRTCHuman && stopWebRTCHuman();
  stopWebRTCAnomali && stopWebRTCAnomali();

  switch (type) {
    case "human":
      startWebRTCHuman && startWebRTCHuman();
      break;
    case "vehicle":
      startWebRTCAnomali && startWebRTCAnomali();
      break;
    case "bantalan":
      videoStream.srcObject = null;
      videoStream.src = "https://luminolynx.my.id/bantalan";
      break;
    case "penambat":
      videoStream.srcObject = null;
      videoStream.src = "https://luminolynx.my.id/penambat";
      break;
    case "stop":
      videoStream.srcObject = null;
      videoStream.src = "";
      break;
  }
}


// === Kontrol Arah Motor ===
const btnForward = document.getElementById("btn-forward");
const btnReverse = document.getElementById("btn-reverse");

btnForward.addEventListener("click", () => {
  if (startActivated) {
    btnForward.classList.add("bg-green-500");
    btnReverse.classList.remove("bg-green-500");

    fetch("/motor_direction", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ direction: "forward" })
    });
  }
});

btnReverse.addEventListener("click", () => {
  if (startActivated) {
    btnReverse.classList.add("bg-green-500");
    btnForward.classList.remove("bg-green-500");

    fetch("/motor_direction", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ direction: "reverse" })
    });
  }
});