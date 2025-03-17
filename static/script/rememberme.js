
document.addEventListener("DOMContentLoaded", function () {
    // Cek apakah ada username/password yang tersimpan
    if (localStorage.getItem("rememberMe") === "true") {
        document.getElementById("username").value = localStorage.getItem("savedUsername");
        document.getElementById("password").value = localStorage.getItem("savedPassword");
        document.getElementById("rememberMe").checked = true;
    }

    // Simpan data saat form dikirim
    document.getElementById("loginForm").addEventListener("submit", function () {
        if (document.getElementById("rememberMe").checked) {
            localStorage.setItem("rememberMe", "true");
            localStorage.setItem("savedUsername", document.getElementById("username").value);
            localStorage.setItem("savedPassword", document.getElementById("password").value);
        } else {
            localStorage.removeItem("rememberMe");
            localStorage.removeItem("savedUsername");
            localStorage.removeItem("savedPassword");
        }
    });
});