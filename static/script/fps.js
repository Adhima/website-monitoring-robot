  function toggleDropdown() {
    document.getElementById("dropdown-menu").classList.toggle("show");
  }

  // Fungsi untuk mengubah kamera dan memperbarui tombol dropdown
  function setCamera(cameraType, cameraText) {
    document.getElementById("video-stream").src = "/video_feed/" + cameraType;
    document.getElementById("camera-select-btn").innerHTML = cameraText + " ▼"; // Update teks tombol
    updateFPS(cameraType);
    closeDropdown();
  }

  // Fungsi untuk mendapatkan FPS dari server berdasarkan kamera yang dipilih
  function updateFPS(cameraType) {
    fetch("/get_fps/" + cameraType)
      .then(response => response.json())
      .then(data => {
        document.getElementById("fps-value").textContent = data.fps;
      })
      .catch(error => console.error("Error fetching FPS:", error));
  }

  // Update FPS setiap 1 detik
 // Update FPS setiap 1 detik
setInterval(() => {
  const videoStream = document.getElementById("video-stream");
  const src = videoStream?.src;

  if (
    !src ||
    src === "" ||
    (!src.includes("luminolynx.my.id/human") &&
      !src.includes("luminolynx.my.id/vehicle") &&
      !src.includes("luminolynx.my.id/bantalan") &&
      !src.includes("luminolynx.my.id/penambat"))
  ) {
    // Kamera dimatikan atau src kosong
    document.getElementById("fps-value").textContent = 0;
    return;
  }

  const currentCamera = src.includes("ipcam") ? "ipcam" : "webcam";
  updateFPS(currentCamera);
}, 1000);


