import cv2
import numpy as np
import math
from keras.models import load_model

_SHOW_IMAGE = False

class JdDeepLaneDetect(object):

    def __init__(self, model_path=None, model=None):
        self.curr_steering_angle = 90
        if model is not None:
            self.model = model
        elif model_path is None:
            raise ValueError('model_path is required')
        else:
            # The model is used only for inference.  compile=False also lets
            # current Keras load legacy H5 files whose saved optimizer/loss
            # names can no longer be deserialized.
            self.model = load_model(model_path, compile=False)
        if tuple(self.model.input_shape[-3:]) != (66, 200, 3):
            raise ValueError('lane model input must be (66, 200, 3)')
        if tuple(self.model.output_shape[-1:]) != (1,):
            raise ValueError('lane model must return one steering angle')
    
    def follow_lane(self, frame):
        if frame is None:
            raise ValueError('frame is required')
        show_image("orig", frame)
        self.curr_steering_angle = self.compute_steering_angle(frame)
        final_frame = display_heading_line(frame, self.curr_steering_angle)
        return self.curr_steering_angle, final_frame 

    def compute_steering_angle(self, frame):
        # Pre-processing a image from camera 
        preprocessed = img_preprocess(frame)
        X = np.asarray([preprocessed])
        # Below code causes slow video frame rate   
        # steering_angle = self.model.predict(X)[0]
        # Predict lane angle using deep learning 
        prediction = np.asarray(self.model(X, training=False)).reshape(-1)
        if prediction.size != 1:
            raise RuntimeError('lane model returned %d values' % prediction.size)
        steering_angle = float(prediction[0])
        if not np.isfinite(steering_angle):
            raise RuntimeError('lane model returned a non-finite steering angle')
        if not 0.0 <= steering_angle <= 180.0:
            raise RuntimeError(
                'lane model returned an out-of-range steering angle: %.3f'
                % steering_angle
            )
        # Round the nearest positive integer without converting a rank-1
        # Tensor directly to int (NumPy 2.x rejects that conversion).
        return int(np.floor(steering_angle + 0.5))

def img_preprocess(image):
    height, _, _ = image.shape
    # remove top half of the image. It is not necesary 
    image = image[int(height/2):,:,:]
    # Nvidia model said it is best to use YUV color space
    image = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)  
    image = cv2.GaussianBlur(image, (3,3), 0)
    # input image size (200,66) Nvidia model
    image = cv2.resize(image, (200,66))
    # normalizing
    return image.astype(np.float32) / 255.0

def display_heading_line(frame, steering_angle, line_color=(0, 0, 255), line_width=5, ):
    heading_image = np.zeros_like(frame)
    height, width, _ = frame.shape

    # figure out the heading line from steering angle
    # heading line (x1,y1) is always center bottom of the screen
    # (x2, y2) requires a bit of trigonometry

    # Note: the steering angle of:
    # 0-89 degree: turn left
    # 90 degree: going straight
    # 91-180 degree: turn right
    try:
        steering_angle_radian = steering_angle / 180.0 * math.pi
        x1 = int(width / 2)
        y1 = height
        x2 = int(x1 - height / 2 / math.tan(steering_angle_radian))
        y2 = int(height / 2)

        cv2.line(heading_image, (x1, y1), (x2, y2), line_color, line_width)
        heading_image = cv2.addWeighted(frame, 0.8, heading_image, 1, 1)
    except:
       pass 

    return heading_image

def show_image(title, frame, show=_SHOW_IMAGE):
    if show:
        cv2.imshow(title, frame)
