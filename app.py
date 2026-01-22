import qrcode
import io
import base64
from flask import Flask, render_template, request, jsonify, send_file
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    data = request.get_json()
    url = data.get('url', '')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    qr.add_data(url)
    qr.make(fit=True)
    image = qr.make_image(fill='black', back_color='white')
    
    # Convert to base64
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return jsonify({'qr_code': img_str})


@app.route('/download/<format>', methods=['POST'])
def download_qr(format):
    data = request.get_json()
    url = data.get('url', '')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    qr.add_data(url)
    qr.make(fit=True)
    image = qr.make_image(fill='black', back_color='white')
    
    if format == 'png':
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        buffered.seek(0)
        return send_file(buffered, mimetype='image/png', as_attachment=True, download_name='qrcode.png')
    
    elif format == 'jpeg':
        # Convert to RGB for JPEG
        rgb_image = image.convert('RGB')
        buffered = io.BytesIO()
        rgb_image.save(buffered, format="JPEG")
        buffered.seek(0)
        return send_file(buffered, mimetype='image/jpeg', as_attachment=True, download_name='qrcode.jpeg')
    
    elif format == 'pdf':
        # Save QR code as temporary image
        img_buffer = io.BytesIO()
        image.save(img_buffer, format="PNG")
        img_buffer.seek(0)
        
        # Create PDF
        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=letter)
        
        # Add QR code to PDF
        temp_img = io.BytesIO(img_buffer.getvalue())
        c.drawImage(Image.open(temp_img), 150, 400, width=300, height=300)
        c.drawString(100, 350, f"QR Code for: {url}")
        c.save()
        
        pdf_buffer.seek(0)
        return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True, download_name='qrcode.pdf')
    
    return jsonify({'error': 'Invalid format'}), 400


if __name__ == '__main__':
    app.run(debug=True)