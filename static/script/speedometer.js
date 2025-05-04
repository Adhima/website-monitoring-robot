// === Chart.js Setup ===
const chartCtx = document.getElementById("speedChart").getContext("2d");
const maxSpeed = 30;

const gaugeChart = new Chart(chartCtx, {
    type: "doughnut",
    data: {
        datasets: [{
            data: [0, maxSpeed],
            backgroundColor: ["#00C0FF", "#23272F"],
            borderWidth: 0
        }]
    },
    options: {
        circumference: 180,
        rotation: 270,
        cutout: "70%",
        responsive: false,
        animation: {
            animateRotate: true,
            duration: 800,
            easing: 'easeOutCubic'
        },
        plugins: {
            legend: { display: false },
            tooltip: { enabled: false }
        }
    }
});

// === Overlay for Panah dan Skala ===
const overlay = document.getElementById("overlay");
const ctx = overlay.getContext("2d");
const centerX = 150;
const centerY = 145;
const radius = 100;

let currentSpeed = 0;
let targetSpeed = 0;

function drawOverlay(speed) {
    ctx.clearRect(0, 0, overlay.width, overlay.height);

    // Skala angka
    ctx.fillStyle = "white";
    ctx.font = "16px Poppins";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    for (let i = 0; i <= maxSpeed; i += 5) {
        const angle = Math.PI + (Math.PI * i / maxSpeed);
        const x = centerX + (radius + 20) * Math.cos(angle);
        const y = centerY + (radius + 20) * Math.sin(angle);
        ctx.fillText(i.toString(), x, y);
    }

    // Panah
    const arrowLength = 90;
    const angle = Math.PI + (Math.PI * speed / maxSpeed);
    const arrowX = centerX + arrowLength * Math.cos(angle);
    const arrowY = centerY + arrowLength * Math.sin(angle);

    ctx.beginPath();
    ctx.moveTo(centerX, centerY);
    ctx.lineTo(arrowX, arrowY);
    ctx.lineWidth = 4;
    ctx.strokeStyle = "#ff4444";
    ctx.stroke();

    // Titik tengah
    ctx.beginPath();
    ctx.arc(centerX, centerY, 5, 0, 2 * Math.PI);
    ctx.fillStyle = "#ff4444";
    ctx.fill();
}

// === Update Speed Function ===
function updateSpeed(speed) {
    targetSpeed = Math.min(speed, maxSpeed);
    gaugeChart.data.datasets[0].data = [targetSpeed, maxSpeed - targetSpeed];
    gaugeChart.update();
    document.getElementById("speed").innerText = Math.round(targetSpeed) + " Km/h";
}

// === Animate Panah Smooth ===
function animate() {
    const easing = 0.1;
    const delta = targetSpeed - currentSpeed;

    if (Math.abs(delta) > 0.05) {
        currentSpeed += delta * easing;
    } else {
        currentSpeed = targetSpeed;
    }

    drawOverlay(currentSpeed);
    requestAnimationFrame(animate);
}
animate();

// === WebSocket Socket.IO ===
const socket = io(); // otomatis konek ke server Flask

socket.on("speed_update", (data) => {
    const speed = data.speed;
    updateSpeed(speed);
});