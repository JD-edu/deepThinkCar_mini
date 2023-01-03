import cv2
# Getting camera object 
cap = cv2.VideoCapture(0)
# Setup image resolution
cap.set(3,320)
cap.set(4,240)
print("Start camera and OpenCV...")
print("Please 'q' to quit test")
while(True):
    ret, frame = cap.read()
    if (ret):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
