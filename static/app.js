// ShamCash demo application
const ShamCashApp = {
  showQR() {
    const modal = document.getElementById('qr-modal');
    const canvas = document.getElementById('qr-canvas');
    const label = document.getElementById('qr-username');
    if (!modal || !canvas || !label) return;

    const username = auth?.getCurrentUser?.()?.username || 'guest';
    const data = `shamcash://demo?user=${encodeURIComponent(username)} `;

    modal.style.display = 'flex';
    label.textContent = `وضع تجريبي — ${username}`;

    if (window.QRCode) {
      canvas.style.display = 'none';
      let image = canvas.nextElementSibling;
      if (!image || image.tagName !== 'IMG') {
        image = document.createElement('img');
        canvas.insertAdjacentElement('afterend', image);
      }
      QRCode.toDataURL(data, { width: 200, margin: 1 }, (error, url) => {
        if (!error) image.src = url;
      });
    }
  }
};

window.app = ShamCashApp;
