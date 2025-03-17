const btnStop = document.getElementById("btn-stop");
const btnStart = document.getElementById("btn-start");
const actionButtons = document.querySelectorAll(".btn-f, .btn-g, .btn-h");

let startActivated = false; // Status apakah START sudah ditekan

// Ketika tombol START ditekan
btnStart.addEventListener("click", () => {
    if (!startActivated) {
        startActivated = true;
        btnStart.classList.replace("bg-blue-500", "bg-green-500"); // START jadi hijau

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