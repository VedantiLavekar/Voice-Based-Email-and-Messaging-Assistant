import cv2
import os
import json
import numpy as np

DATASET = "dataset"
MODEL_FILE = "trainer.yml"
LABELS_FILE = "labels.json"

recognizer = cv2.face.LBPHFaceRecognizer_create()
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

faces = []
labels = {}
label_id = 0

for file in os.listdir(DATASET):
    if not file.lower().endswith(".jpg"):
        continue

    email = file.replace(".jpg", "")
    img_path = os.path.join(DATASET, file)

    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        continue

    detected_faces = face_cascade.detectMultiScale(img, 1.3, 5)

    for (x, y, w, h) in detected_faces:
        face = img[y:y+h, x:x+w]
        face = cv2.resize(face, (200, 200))

        faces.append(face)
        labels[len(faces) - 1] = email

if len(faces) == 0:
    print("❌ No faces found in dataset")
    exit()

recognizer.train(faces, np.array(list(range(len(faces)))))
recognizer.save(MODEL_FILE)

with open(LABELS_FILE, "w") as f:
    json.dump(labels, f)

print("✅ Training completed successfully")
print("📁 trainer.yml created")
print("📁 labels.json created")
