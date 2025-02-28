import os
from flask import Flask, render_template, request, send_file
from predict import predict_sample
from report import get_pdf

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Geting user details
        name = request.form.get("name")
        age = request.form.get("age")
        contact = request.form.get("contact")

        if not name or not age or not contact:
            return "Please fill in all the required fields"

        # Handling file upload
        if "xray_image" not in request.files:
            return "No file part"

        file = request.files["xray_image"]
        if file.filename == "":
            return "No selected file"

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        action = request.form.get("action")

        if action == "predict":
            # Predicting condition
            result = predict_sample(filepath)
            if result is None:
                return "Prediction failed. Please check the image format and try again."

            prediction, confidence = result
            return render_template("result.html", name=name, age=age, contact=contact, prediction=prediction, confidence=confidence*100)

        elif action == "report":
            # Generating report
            report_path = get_pdf(name, age, "Male", contact, filepath)
            return send_file(report_path, as_attachment=True)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
