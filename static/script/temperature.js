setInterval(() => {
    fetch("/temperature_data")
      .then(res => res.json())
      .then(data => {
        document.querySelector(".temperature-box .value").innerText = `${data.temperature}°`;
      });
  }, 2000);
  