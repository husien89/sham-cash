// QR Code Generation
document.getElementById('btn-qr')?.addEventListener('click', () => {
    const canvas = document.getElementById('qr-canvas');
    const qrArea = document.getElementById('qr-area');
    
    // إنشاء QR بسيط يحتوي على معرف المستخدم
    const userId = auth.getCurrentUser()?.id || 'guest';
    const qrData = `shamcash://pay?user=${userId}`;
    
    // رسم QR كود بسيط (يمكن استخدام مكتبة QRCode.js هنا)
    const ctx = canvas.getContext('2d');
    canvas.width = 200;
    canvas.height = 200;
    
    // نمط QR بسيط
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0