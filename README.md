
# 🧠 Dynamic PDF Generator for Quiz Results

This project demonstrates how to dynamically generate personalized quiz reports in PDF format using Python and Flask. It’s designed for platforms like diagnostic quizzes or psychological assessments that return custom feedback, images, and user results — and send status updates via webhooks.

---

## 🚀 Features

* 📄 Generate PDF reports with:

  * User name
  * Quiz score
  * Archetype title & description
  * Optional image (based on archetype)
* 🔁 Retry logic for robust generation
* 📬 Webhook callback to notify backend of success/failure
* 📝 Logging of each generation attempt

---

## 📦 Tech Stack

* **Python**
* **Flask** – lightweight web server
* **ReportLab** – PDF generation
* **Requests** – webhook handling

---

## 📂 Project Structure

```
dynamic-pdf-generator/
│
├── app.py                  # Flask server & PDF logic
├── pdf_logs.log            # Logs for generation attempts
├── generated/              # Output folder for PDFs
├── static/archetypes/      # Archetype images
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## 🔧 Setup Instructions

1. **Clone the Repo**

   ```bash
   git clone https://github.com/your-username/dynamic-pdf-generator.git
   cd dynamic-pdf-generator
   ```

2. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Server**

   ```bash
   python app.py
   ```

4. **Test the API**
   Use [Postman](https://www.postman.com/) or curl:

   ```bash
   curl -X POST http://localhost:5000/generate-pdf \
     -H \"Content-Type: application/json\" \
     -d '{
       \"user_name\": \"Anagha\",
       \"score\": 87,
       \"archetype\": \"The Explorer\",
       \"description\": \"You thrive on adventure and love discovering new ideas.\",
       \"webhook_url\": \"http://localhost:5000/webhook-status\"
     }'
   ```

---

## 🧪 API Endpoints

### `POST /generate-pdf`

Generates a personalized quiz report based on provided data.

**Request Body:**

```json
{
  "user_name": "Anagha",
  "score": 87,
  "archetype": "The Explorer",
  "description": "You thrive on adventure and love discovering new ideas.",
  "webhook_url": "http://localhost:5000/webhook-status"
}
```

### `POST /webhook-status`

Receives webhook status updates (simulated callback for testing).

---

## 📸 Screenshots

> Add screenshots of the generated PDFs or Postman responses if you’d like

---

## 🏁 Next Improvements

* Convert to HTML template → PDF with `wkhtmltopdf` or `Puppeteer` for design fidelity
* Upload generated PDFs to cloud (S3, GCS)
* Add database logging
* Dockerize the app for production

---

## 👩‍💻 Author

**Anagha G.**
Backend Developer | PDF Automation | Flask | Django
\
[LinkedIn: www.linkedin.com/in/anagha-g-adiga-577567259] | \[GitHub:  GitHub: AnaghaGAdiga] 

---

Would you like me to:

* Zip this up for you as a downloadable GitHub-ready package?
* Help deploy it on **Render**, **Railway**, or **Heroku**?
* Help you write the GitHub repo description and tags?

Let me know what you want next!
