'''
1. Importing necessary modules
'''
import cv2
from jd_opencv_lane_detect import JdOpencvLaneDetect
import os 

'''
2. Creating object from classes
  1) OpenCV lane detecting object from JdOpencvLaneDetect class 
  2) Video capture object. It get image from AVI video file in data folder.
'''
cv_detector = JdOpencvLaneDetect()
# Setting video file player object 
video_file = "data/car_video.avi"
# OpenCV lane detect object
cap = cv2.VideoCapture(video_file)

'''
3. Remove prior data images. 
Labeling data images are saved here.
'''
index = 0
# remove prior labeling data in ./data folder 
try:
    os.system("rm ./data/*.png")  
except OSError:
    print("No *.png files")

'''
4. Getting labeling images from "car_video.avi" video file.
  "car_video.avi" file: OpenCV based lane detecting self driving video. You get this video 
   from jd_1_record_video.py
  We get a image from AVI video file. And we find lane and get steering angle.
  Finally we save a image in data folder. Streering angle is embedding in video file name. 
  These label data are used for deep learning training. 
'''
while True:
    # get image from video file player
    ret, img_org = cap.read()
    if ret:
        # Find lane
        lanes, img_lane = cv_detector.get_lane(img_org)
        cv2.imshow("img", img_org)
        # Get steering agnle 
        angle, img_angle = cv_detector.get_steering_angle(img_lane, lanes)
        if img_angle is None:
            print("can't find lane...")
        else:
            # Generate labeling data. Steering angle is embedding in video file name
            cv2.imwrite("%s_%03d_%03d.png" % (video_file, index, angle), img_org)
            index += 1	
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        print("camera error")
        break

'''
5. Releasing occufied resources 
'''
cap.release()
cv2.destroyAllWindows()




