function updateNetworkStatus() {
  fetch("/esp_status")
    .then(res => res.json())
    .then(data => {
      const netStatus = document.querySelector(".network-box span[style*='font-size: 16px']");
      if (data.connected) {
        netStatus.textContent = "CONNECTED";
        netStatus.style.color = "#22c55e";
      } else {
        netStatus.textContent = "DISCONNECT";
        netStatus.style.color = "#ef4444";
      }
    });
}
setInterval(updateNetworkStatus, 2000);
updateNetworkStatus();

function updateLatency() {
  const start = performance.now();
  fetch("/ping")
    .then(() => {
      const latency = Math.round(performance.now() - start);
      document.querySelector('.latency-box .value').textContent = latency;
    })
    .catch(() => {
      document.querySelector('.latency-box .value').textContent = "-";
    });
}
setInterval(updateLatency, 2000);
updateLatency();