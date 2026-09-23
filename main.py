import os
import shutil
import smtplib
from email.message import EmailMessage
from typing import List
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Junk Car Buying Backend API")

# Enable CORS so browser apps can connect smoothly
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Folder where car submission photos are saved
UPLOAD_DIR = "uploaded_car_photos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# OPTIONAL: Configure your email credentials to get instant alerts on your phone
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your_email@gmail.com"      # <-- Your email address
SENDER_PASSWORD = "your_app_password"      # <-- App Password generated from Google
NOTIFICATION_RECEIVER = "your_email@gmail.com"

def send_email_alert(car_info: str, condition: str, has_converter: str, zipcode: str, phone: str, photo_count: int):
    """Sends an automated email notification when a seller submits a car."""
    try:
        msg = EmailMessage()
        msg['Subject'] = f"🚨 NEW CAR LEAD: {car_info} ({zipcode})"
        msg['From'] = SENDER_EMAIL
        msg['To'] = NOTIFICATION_RECEIVER

        body = f"""
        NEW CAR SUBMISSION RECEIVED!
        ------------------------------------
        Vehicle: {car_info}
        Condition: {condition}
        Catalytic Converter: {has_converter}
        Location/Zip Code: {zipcode}
        Seller Phone: {phone}
        Uploaded Photos: {photo_count} file(s)
        ------------------------------------
        Photos are stored in your server's uploaded_car_photos folder.
        """
        msg.set_content(body)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print("Notification email sent successfully!")
    except Exception as e:
        print(f"Server notification log (Email skipped or unconfigured): {e}")


@app.get("/")
def home():
    return {"status": "Active", "message": "Car Buying Platform API is running!"}


@app.post("/submit-car/")
async def submit_car(
    car_info: str = Form(...),
    condition: str = Form(...),
    has_converter: str = Form(...),
    zipcode: str = Form(...),
    phone: str = Form(...),
    photos: List[UploadFile] = File(...)
):
    saved_photos = []

    # Store uploaded photos with the seller's phone number in the filename
    for photo in photos:
        clean_phone = phone.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
        safe_filename = f"{clean_phone}_{photo.filename}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)

        saved_photos.append(safe_filename)

    print(f"\n[NEW LEAD RECEIVED]")
    print(f"Vehicle: {car_info} | Converter: {has_converter} | Zip: {zipcode} | Phone: {phone} | Photos Saved: {len(saved_photos)}\n")

    # Send email notification
    send_email_alert(car_info, condition, has_converter, zipcode, phone, len(saved_photos))

    return {
        "status": "success",
        "message": "Car submission received! We will review the details and contact you with a cash offer."
    }
