import cv2
import easyocr
import sqlite3
import re
from PIL import Image
from transformers import pipeline

# Inicijalizacija YOLO modela za detekciju objekata i postavljanje na GPU
yolo_pipe = pipeline("object-detection", model="nickmuchi/yolos-small-finetuned-license-plate-detection", device=0)

# Inicijalizacija OCR čitača
reader = easyocr.Reader(['en'])

# Povezivanje sa bazom podataka
conn = sqlite3.connect("vozilaDB.db")
cursor = conn.cursor()


# A function to check the status of a license plate
def check_plate_in_db(plate):
    cursor.execute("SELECT status FROM registered_vehicles WHERE plate = ?", (plate,))
    result = cursor.fetchone()
    return result[0] if result else "not found"


# Start video capture
cap = cv2.VideoCapture(0)  # 0 for default camera

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Resize image to a manageable size for the pipeline
    scale_percent = 50  # reduce image size by 50% if needed
    width = int(frame.shape[1] * scale_percent / 100)
    height = int(frame.shape[0] * scale_percent / 100)
    resized_frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)

    # Convert frame to RGB and then to PIL image for YOLO model
    rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(rgb_frame)

    # Use YOLO model for object detection
    results = yolo_pipe(pil_image)

    for result in results:
        # Extract bounding box coordinates and confidence
        score = result['score']
        box = result['box']
        x1, y1, x2, y2 = int(box['xmin']), int(box['ymin']), int(box['xmax']), int(box['ymax'])

        # Adjust coordinates to original frame size
        x1, y1, x2, y2 = int(x1 / scale_percent * 100), int(y1 / scale_percent * 100), int(
            x2 / scale_percent * 100), int(y2 / scale_percent * 100)

        # Crop the detected license plate area
        cropped_image = frame[y1:y2, x1:x2]

        # Determine if the plate is single-row or double-row based on width-to-height ratio
        aspect_ratio = cropped_image.shape[1] / cropped_image.shape[0]

        if aspect_ratio > 2.5:
            # Single-row license plate
            ocr_result = reader.readtext(cropped_image)
            plate_text = re.sub(r'[^A-Za-z0-9]', '', ocr_result[0][1].upper()) if ocr_result else ""
        else:
            # Double-row license plate
            height_split = cropped_image.shape[0] // 2
            upper_part = cropped_image[:height_split, :]
            lower_part = cropped_image[height_split:, :]

            # Perform OCR on both parts
            upper_text = reader.readtext(upper_part)
            lower_text = reader.readtext(lower_part)

            # Extract and clean text, ignoring any symbols (like a crest)
            upper_plate_text = re.sub(r'[^A-Za-z0-9]', '', upper_text[0][1].upper()) if upper_text else ""
            lower_plate_text = re.sub(r'[^A-Za-z0-9]', '', lower_text[0][1].upper()) if lower_text else ""
            plate_text = upper_plate_text + lower_plate_text

        print(f"Detected Plate: {plate_text}")

        # Check plate status in database
        status = check_plate_in_db(plate_text)
        print(f"Plate Status: {status}")

        # Display the result on the frame
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, f"Plate: {plate_text} - Status: {status}", (x1, y1 - 10), font, 0.6,
                    (0, 255, 0) if status in ["registered", "speed_violation", "red_light_cross"] else (0, 0, 255), 2)
        cv2.rectangle(frame, (x1, y1), (x2, y2),
                      (0, 255, 0) if status in ["registered", "speed_violation", "red_light_cross"] else (0, 0, 255), 3)

    # Show the video with recognized plates
    cv2.imshow("License Plate Detection", frame)

    # Press 'ESC' to quit
    if cv2.waitKey(1) & 0xFF == 27:
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
conn.close()
