from picamera2 import Picamera2

picam2 = Picamera2()
config = picam2.create_preview_configuration()  # Use preview config
picam2.configure(config)

print("Frame width:", config["main"]["size"][0])
print("Frame height:", config["main"]["size"][1])
