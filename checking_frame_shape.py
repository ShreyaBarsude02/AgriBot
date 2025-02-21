from picamera2 import Picamera2
picam2 = Picamera2()
config = picam2.create_still_configuration()
print(config["size"])  # Outputs (width, height)
