const form = document.getElementById('downloadForm');
const filenameInput = document.getElementById('filename');
const status = document.getElementById('status');
const btn = document.getElementById('downloadBtn');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const filename = filenameInput.value.trim();
  if (!filename) return;

  btn.disabled = true;
  document.getElementById('clientStatus').textContent = 'Sending request...';
  document.getElementById('serverStatus').textContent = 'Waiting...';
  status.textContent = '';
  document.getElementById('progressFill').style.width = '0%';
  document.getElementById('progressText').textContent = '0%';

  try {
    const res = await fetch('/download', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filename }),
    });

    if (!res.ok) {
      const txt = await res.text();
      status.textContent = 'Server error: ' + txt;
      document.getElementById('clientStatus').textContent = 'Error';
      btn.disabled = false;
      return;
    }

    document.getElementById('clientStatus').textContent = 'Request sent';

    const contentLength = res.headers.get('Content-Length');
    const total = contentLength ? parseInt(contentLength, 10) : null;

    const reader = res.body.getReader();
    const chunks = [];
    let received = 0;
    let first = true;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      if (first) {
        first = false;
        document.getElementById('serverStatus').textContent = 'Receiving data';
      }
      chunks.push(value);
      received += value.length;

      if (total) {
        const pct = Math.floor((received / total) * 100);
        document.getElementById('progressFill').style.width = pct + '%';
        document.getElementById('progressText').textContent = pct + '%';
      } else {
        // indeterminate pulse
        document.getElementById('progressFill').style.width = '30%';
        document.getElementById('progressText').textContent = (received + ' bytes');
      }
    }

    // finalize
    const blob = new Blob(chunks);
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename.split('/').pop();
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);

    document.getElementById('serverStatus').textContent = 'Completed';
    document.getElementById('progressFill').style.width = '100%';
    document.getElementById('progressText').textContent = '100%';
    status.textContent = 'Download complete — saved as ' + a.download;
    status.className = 'success';
  } catch (err) {
    status.textContent = 'Error: ' + err.message;
    status.className = 'error';
    document.getElementById('serverStatus').textContent = 'Error';
    document.getElementById('clientStatus').textContent = 'Error';
  } finally {
    btn.disabled = false;
  }
});
