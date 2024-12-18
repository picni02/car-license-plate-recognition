# **Car license plate recognition app**
A simple desktop application written in Python for 
recognizing car license plates using the EasyOCR reading module 
and the YOLO model for detecting plates in an image.

## Functions

- Adding new vehicles to the mini comparison database (built in sqlite3)
- Launching the device's camera for real-time detection
- Detecting license plates of cars registered in the violation database
- Detecting different license plate types (single-line, double-line)
- Green box for match, red box for opposite

## Used libraries and model

- cv2 (openCV) - to access the device's camera
- easyocr - used for character recognition from images
- sqlite3 - to work with the database
- re - for text filtering
- PIL - to work with the image format
- transformers - to work with the YOLO model used for recognition

The pre-trained model used in this detection program was downloaded from huggingface.co and can be found at this link: https://huggingface.co/nickmuchi/yolos-small-finetuned-license-plate-detection"# car-license-plate-recognition" 
