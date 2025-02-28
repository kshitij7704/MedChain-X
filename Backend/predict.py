from keras.preprocessing.image import load_img, img_to_array # type: ignore
import numpy as np
from keras.applications.vgg16 import preprocess_input # type: ignore
from tensorflow.keras.models import load_model # type: ignore

categories = ['Normal', 'Pneumonia']

def load_trained_model(model_path):
    try:
        return load_model(model_path)
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

def predict_sample(image_path):
    model = load_trained_model("model_vgg16.h5")
    if model is None:
        print("Model could not be loaded.")
        return None  # Ensure it doesn't try to predict with a None model

    try:
        img = load_img(image_path, target_size=(224, 224))
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)

        prediction = model.predict(img_array)
        predicted_class = np.argmax(prediction)
        confidence = float(prediction[0][predicted_class])  # Convert confidence to float for safety
        return categories[predicted_class], confidence

    except Exception as e:
        print(f"Error processing image: {e}")
        return None