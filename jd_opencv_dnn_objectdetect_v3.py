import cv2
import time
import numpy as np

net = cv2.dnn_DetectionModel('./models/frozen_inference_graph_v3.pb', './models/ssdlite_mobilenet_v3_small_320x320_coco.pbtxt')
stop_width, stop_height = 40, 40

net.setInputSize(320, 320)
net.setInputScale(1.0 / 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

classNames = {0: 'background',
              1: 'person', 2: 'bicycle', 3: 'car', 4: 'motorcycle', 5: 'airplane', 6: 'bus',
              7: 'train', 8: 'truck', 9: 'boat', 10: 'traffic light', 11: 'fire hydrant',
              13: 'stop sign', 14: 'parking meter', 15: 'bench', 16: 'bird', 17: 'cat',
              18: 'dog', 19: 'horse', 20: 'sheep', 21: 'cow', 22: 'elephant', 23: 'bear',
              24: 'zebra', 25: 'giraffe', 27: 'backpack', 28: 'umbrella', 31: 'handbag',
              32: 'tie', 33: 'suitcase', 34: 'frisbee', 35: 'skis', 36: 'snowboard',
              37: 'sports ball', 38: 'kite', 39: 'baseball bat', 40: 'baseball glove',
              41: 'skateboard', 42: 'surfboard', 43: 'tennis racket', 44: 'bottle',
              46: 'wine glass', 47: 'cup', 48: 'fork', 49: 'knife', 50: 'spoon',
              51: 'bowl', 52: 'banana', 53: 'apple', 54: 'sandwich', 55: 'orange',
              56: 'broccoli', 57: 'carrot', 58: 'hot dog', 59: 'pizza', 60: 'donut',
              61: 'cake', 62: 'chair', 63: 'couch', 64: 'potted plant', 65: 'bed',
              67: 'dining table', 70: 'toilet', 72: 'tv', 73: 'laptop', 74: 'mouse',
              75: 'remote', 76: 'keyboard', 77: 'cell phone', 78: 'microwave', 79: 'oven',
              80: 'toaster', 81: 'sink', 82: 'refrigerator', 84: 'book', 85: 'clock',
              86: 'vase', 87: 'scissors', 88: 'teddy bear', 89: 'hair drier', 90: 'toothbrush'}

# real driving routine
def isStopSignDetected(img):
    height, _, _ = img.shape # 240, 320
    # remove top half of the image. It is not necesary 
    img_poi = img #[int(height/4):,:,:]  
    
    classes, confidences, boxes = net.detect(img_poi, confThreshold=0.4)
    isStop = False
    
    if(len(classes) != 0):
        if classes[np.where(classes==1)].size == 0 and classes[np.where(classes==3)].size == 0 and classes[np.where(classes=8)].size == 0: #nothing detected, detected no person and no stopsign
            isStop = False
        else:
            # Detect the stop sign, x,y = origin points, w = width, h = height
            for classId, confidence, box in zip(classes.flatten(), confidences.flatten(), boxes):
                if classId == 1 or classId == 3 or classId == 8:
                    # Draw rectangle around the stop sign
                    stop_sign_rectangle = cv2.rectangle(img_poi, box, (0, 255, 0), 3)
                    # Write "Stop sign" on the bottom of the rectangle
                    class_name=classNames[classId]
                    cv2.putText(stop_sign_rectangle, class_name , (box[0], box[1]+30),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 0, 255), 1)
                    if (box[2] - box[0]) > stop_width or (box[3] - box[1]) > stop_height:
                        isStop = True
    else:
        isStop = False
        
    return isStop, img_poi


if __name__ == '__main__':
    # Variables to calculate FPS
    counter, fps = 0, 0
    start_time = time.time()
    
      # Visualization parameters
    row_size = 20  # pixels
    left_margin = 24  # pixels
    text_color = (0, 0, 255)  # red
    font_size = 1
    font_thickness = 1
    fps_avg_frame_count = 10
    
    camera = cv2.VideoCapture('./video_1.avi')
    camera.set(3, 320)
    camera.set(4, 240)
    camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    while True:
    
        ret, img = camera.read()
        counter += 1
        
        if ret:
            isStop, img = isStopSignDetected(img)
            
                # Calculate the FPS
            if counter % fps_avg_frame_count == 0:
              end_time = time.time()
              fps = fps_avg_frame_count / (end_time - start_time)
              start_time = time.time()

            # Show the FPS
            fps_text = 'FPS = {:.1f}'.format(fps)
            text_location = (left_margin, row_size)
            cv2.putText(img, fps_text, text_location, cv2.FONT_HERSHEY_PLAIN,
                        font_size, text_color, font_thickness)
            
            cv2.imshow("opencv_dnn_objectdetect_v3", img)
            
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    camera.release()
    cv2.destroyAllWindows()
