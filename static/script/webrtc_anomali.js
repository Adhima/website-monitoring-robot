let pcAnomali = null;

async function startWebRTCAnomali() {
  const video = document.getElementById('video-stream');
  if (!video) return;

  pcAnomali = new RTCPeerConnection();
  pcAnomali.addTransceiver('video', { direction: 'recvonly' });

  pcAnomali.ontrack = function(event) {
    video.srcObject = event.streams[0];
  };

  const offer = await pcAnomali.createOffer();
  await pcAnomali.setLocalDescription(offer);

  while (!pcAnomali.localDescription || !pcAnomali.localDescription.sdp) {
    await new Promise(r => setTimeout(r, 10));
  }

  const response = await fetch('https://human.luminolynx.my.id:8082/offer_anomali', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      sdp: pcAnomali.localDescription.sdp,
      type: pcAnomali.localDescription.type
    })
  });
  const answer = await response.json();
  if (answer.error) {
    alert("WebRTC error: " + answer.error);
    return;
  }
  await pcAnomali.setRemoteDescription(new RTCSessionDescription(answer));
}

function stopWebRTCAnomali() {
  const video = document.getElementById('video-stream');
  if (video) video.srcObject = null;
  if (pcAnomali) {
    pcAnomali.getSenders().forEach(sender => pcAnomali.removeTrack(sender));
    pcAnomali.close();
    pcAnomali = null;
  }
}