import os
import io
import logging
import time
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
import requests
from utils import safe_filename, ensure_dirs

# Configuration
OUT_DIR = "generated"
ARCH_DIR = os.path.join("static", "archetypes")
LOG_FILE = "pdf_logs.log"
MAX_GENERATION_RETRIES = 3
WEBHOOK_RETRY = 3
WEBHOOK_BACKOFF = 2  # seconds

# Setup
ensure_dirs([OUT_DIR, ARCH_DIR])

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

app = Flask(__name__)


def generate_pdf_bytes(user_name, score, archetype, description, image_path=None):
    """Return bytes of generated PDF using ReportLab."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Header
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 80, f"Quiz Report — {user_name}")

    # Score & date
    c.setFont("Helvetica", 14)
    c.drawString(50, height - 120, f"Score: {score}")
    c.drawString(50, height - 140, f"Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")

    # Archetype title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 180, f"Archetype: {archetype}")

    # Archetype description (wrap text)
    c.setFont("Helvetica", 12)
    text_obj = c.beginText(50, height - 210)
    text_obj.setLeading(16)
    max_width = width - 100
    # naive wrapping
    for line in description.split("\n"):
        words = line.split()
        cur = ""
        for w in words:
            test = (cur + " " + w).strip()
            if c.stringWidth(test, "Helvetica", 12) <= max_width:
                cur = test
            else:
                text_obj.textLine(cur)
                cur = w
        if cur:
            text_obj.textLine(cur)
    c.drawText(text_obj)

    # optionally draw image
    if image_path and os.path.exists(image_path):
        try:
            img = ImageReader(image_path)
            iw, ih = img.getSize()
            max_w = 200
            max_h = 200
            ratio = min(max_w / iw, max_h / ih, 1)
            draw_w = iw * ratio
            draw_h = ih * ratio
            c.drawImage(img, width - draw_w - 50, height - draw_h - 100, draw_w, draw_h)
        except Exception as e:
            logging.warning(f"Could not draw image {image_path}: {e}")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()


@app.route("/generate-pdf", methods=["POST"])
def generate_pdf_endpoint():
    data = request.get_json(force=True)
    user_name = data.get("user_name")
    score = data.get("score")
    archetype = data.get("archetype")
    description = data.get("description", "")
    webhook_url = data.get("webhook_url")

    if not user_name or score is None or not archetype:
        return jsonify({"error": "user_name, score and archetype are required"}), 400

    safe_name = safe_filename(f"{user_name}_{archetype}_{int(time.time())}.pdf")
    out_path = os.path.join(OUT_DIR, safe_name)

    # optional image lookup
    image_candidate = os.path.join(ARCH_DIR, f"{archetype.lower().replace(' ', '_')}.png")
    image_path = image_candidate if os.path.exists(image_candidate) else None

    success = False
    last_err = None
    for attempt in range(1, MAX_GENERATION_RETRIES + 1):
        try:
            pdf_bytes = generate_pdf_bytes(user_name, score, archetype, description, image_path)
            with open(out_path, "wb") as f:
                f.write(pdf_bytes)
            success = True
            logging.info(f"PDF generated: {out_path} (attempt {attempt})")
            break
        except Exception as e:
            last_err = str(e)
            logging.exception(f"Generation attempt {attempt} failed: {e}")
            time.sleep(1 * attempt)

    # Prepare webhook payload
    payload = {
        "user_name": user_name,
        "file_path": out_path if success else None,
        "success": success,
        "error": last_err,
    }

    # call webhook with retry
    if webhook_url:
        for w_attempt in range(1, WEBHOOK_RETRY + 1):
            try:
                r = requests.post(webhook_url, json=payload, timeout=5)
                logging.info(f"Webhook call to {webhook_url} status {r.status_code} (attempt {w_attempt})")
                break
            except Exception as e:
                logging.warning(f"Webhook attempt {w_attempt} failed: {e}")
                time.sleep(WEBHOOK_BACKOFF * w_attempt)

    status_code = 200 if success else 500
    return jsonify(payload), status_code


@app.route("/webhook-status", methods=["POST"])
def webhook_receiver():
    # simple receiver to test webhook calls
    data = request.get_json(force=True)
    logging.info(f"Webhook received: {data}")
    return jsonify({"received": True}), 200


@app.route("/generated/<path:filename>")
def serve_generated(filename):
    return send_from_directory(OUT_DIR, filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)