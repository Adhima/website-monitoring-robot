let pc = null;

async function startWebRTCHuman() {
  const video = document.getElementById('video-stream');
  if (!video) return;

  pc = new RTCPeerConnection();
  pc.addTransceiver('video', { direction: 'recvonly' });

  pc.ontrack = function(event) {
    video.srcObject = event.streams[0];
  };

  const offer = await pc.createOffer();
  await pc.setLocalDescription(offer);

  while (!pc.localDescription || !pc.localDescription.sdp) {
    await new Promise(r => setTimeout(r, 10));
  }

  const response = await fetch('https://human.luminolynx.my.id/offer', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      sdp: pc.localDescription.sdp,
      type: pc.localDescription.type
    })
  });
  const answer = await response.json();
  if (answer.error) {
    alert("WebRTC error: " + answer.error);
    return;
  }
  await pc.setRemoteDescription(new RTCSessionDescription(answer));
}

function stopWebRTCHuman() {
  const video = document.getElementById('video-stream');
  if (video) video.srcObject = null;
  if (pc) {
    pc.getSenders().forEach(sender => pc.removeTrack(sender));
    pc.close();
    pc = null;
  }
}