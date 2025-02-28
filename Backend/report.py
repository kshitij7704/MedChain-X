from fpdf import FPDF
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model # type: ignore
from tensorflow.keras.preprocessing.image import load_img, img_to_array # type: ignore
from tensorflow.keras.applications.vgg16 import preprocess_input # type: ignore
from fpdf import FPDF
import os
from datetime import datetime
import google.generativeai as genai
from config import API_KEY

genai.configure(api_key=API_KEY)

def load_trained_model(model_path):
    return load_model(model_path)

def predict_xray(model, image_path):
    img = load_img(image_path, target_size=(224, 224))
    img_array = img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)

    prediction = model.predict(img_array)
    predicted_class = np.argmax(prediction)
    categories = ['Normal', 'Pneumonia']
    confidence = prediction[0][predicted_class]
    
    return categories[predicted_class], confidence

def generate_ai_remarks(prediction, confidence):
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"Provide a short but informative medical remark for a chest X-ray diagnosis where the AI predicted '{prediction}' with a confidence score of {confidence*100:.2f}%."
    
    response = model.generate_content(prompt)
    
    return response.text.strip() if response and response.text else "No AI-generated remarks available."

class CustomPDF(FPDF):
    def footer(self):
        # Ensuring the footer is always at the bottom
        self.set_y(-15)
        self.set_fill_color(30, 144, 255)
        self.rect(0, self.get_y(), 210, 15, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", size=10)
        self.cell(200, 10, "MedChain-X | AI-powered Medical Diagnosis | Contact: support@medchainx.com", ln=True, align='C')

def generate_medchainx_report(patient_name, age, gender, contact, xray_path, prediction, confidence):
    pdf = CustomPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Header
    pdf.set_fill_color(30, 144, 255)
    pdf.rect(0, 0, 210, 30, 'F')
    pdf.set_font("Arial", style='B', size=20)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(200, 15, "MedChain-X: AI-Powered Diagnosis Report", ln=True, align='C')
    pdf.ln(20)

    # Patient Information Section
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", style='B', size=14)
    pdf.cell(200, 10, "Patient Details", ln=True, align='L')
    pdf.set_font("Arial", size=12)
    
    pdf.cell(100, 8, f"Name: {patient_name}", ln=False)
    pdf.cell(100, 8, f"Contact: {contact}", ln=True)
    
    pdf.cell(100, 8, f"Age: {age}", ln=False)
    pdf.cell(100, 8, f"Gender: {gender}", ln=True)

    pdf.cell(200, 8, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(5)

    # X-ray Image Section
    if os.path.exists(xray_path):
        pdf.set_font("Arial", style='B', size=14)
        pdf.cell(200, 10, "Uploaded X-ray Scan:", ln=True)
        pdf.image(xray_path, x=50, y=None, w=100)
        pdf.ln(5)

    # Diagnosis Result Section
    pdf.set_font("Arial", style='B', size=14)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(200, 10, "Diagnosis Result", ln=True, align='L', fill=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 8, f"Predicted Condition: {prediction}", ln=True)
    pdf.cell(200, 8, f"Confidence Score: {confidence*100:.2f}%", ln=True)
    pdf.ln(5)

    # AI-generated remarks Section
    ai_remarks = generate_ai_remarks(prediction, confidence)
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 8, "AI-based Remarks:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 8, ai_remarks)
    pdf.ln(5)

    # Next Steps Section
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 8, "Next Steps:", ln=True)
    pdf.set_font("Arial", size=12)
    next_steps = "- Schedule a follow-up consultation.\n- Get additional tests if necessary.\n- Maintain a healthy lifestyle and monitor symptoms."
    pdf.multi_cell(0, 8, next_steps)
    pdf.ln(5)

    # Disclaimer Section
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 8, "Disclaimer:", ln=True)
    pdf.set_font("Arial", size=12)
    disclaimer = "This AI-generated diagnosis. If not satisfied, consult a doctor instantly through MedChain-X."
    pdf.multi_cell(0, 8, disclaimer)
    pdf.ln(5)

    # Saving as PDF
    report_path = f"MedChainX_Report_{patient_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    pdf.output(report_path)
    return report_path

def get_pdf(name, age, gender, contact, xray_path):
    model = load_trained_model("model_vgg16.h5")
    prediction, confidence = predict_xray(model, xray_path)
    report_path = generate_medchainx_report(name, age, gender, contact, xray_path, prediction, confidence)
    print(f"Report generated: {report_path}")
    return report_path