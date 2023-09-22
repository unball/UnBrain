from vision.receiver import FiraClient

visionClient = FiraClient()
while True:
    msg = visionClient.receive_frame()
    print(type(msg.detection))