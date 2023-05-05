# -*- coding: utf-8 -*-
"""
Scripts to use

Usage:
    cobit_deep_learning_training.py data/

Description:
    This script finds all PNG files in data folder and trains all images.

Output: ***.h5

'''
1. Importing necessary python modules 
'''
"""
# python standard libraries
import os
import random
import fnmatch
import datetime
import pickle

# data processing
import numpy as np
np.set_printoptions(formatter={'float_kind':lambda x: "%.4f" % x})

# tensorflow
import tensorflow as tf
from tensorflow.keras.models import Sequential 
from tensorflow.keras.layers import Conv2D, MaxPool2D, Dropout, Flatten, Dense
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import load_model
from tensorflow.keras.callbacks import ModelCheckpoint

# sklearn
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split

# imaging
import cv2
from imgaug import augmenters as img_aug
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image

class JdDeepLearning: 

    def __init__(self):

        print( f'tf.__version__: {tf.__version__}' )
        print( f'keras.__version__: {keras.__version__}' )
        
        data_dir = 'data'
        file_list = os.listdir(data_dir)
        image_paths = []
        steering_angles = []
        pattern = "*.png"
        self.model_output_dir = 'output'
        for filename in file_list:
            if fnmatch.fnmatch(filename, pattern):
                image_paths.append(os.path.join(data_dir, filename))
                angle = int(filename[-7:-4])
                steering_angles.append(angle)

        self.X_train, self.X_valid, self.y_train, self.y_valid = train_test_split( image_paths, steering_angles, test_size=0.2)
        print("Training data: %d\nValidation data: %d" % (len(self.X_train), len(self.X_valid)))
	
    '''
    labeling image data augmentation 
    '''
    # put it together
    def random_augment(self, image, steering_angle):
        if np.random.rand() < 0.5:
            image = self.pan(image)
        if np.random.rand() < 0.5:
            image = self.zoom(image)
        if np.random.rand() < 0.5:
            image = self.blur(image)
        if np.random.rand() < 0.5:
            image = self.adjust_brightness(image)
        image, steering_angle = self.random_flip(image, steering_angle)
        
        return image, steering_angle

    def my_imread(self, image_path):
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image

    def zoom(self, image):
        zoom = img_aug.Affine(scale=(1, 1.3))  # zoom from 100% (no zoom) to 130%
        image = zoom.augment_image(image)
        return image

    def pan(self, image):
        # pan left / right / up / down about 10%
        pan = img_aug.Affine(translate_percent= {"x" : (-0.1, 0.1), "y": (-0.1, 0.1)})
        image = pan.augment_image(image)
        return image

    def adjust_brightness(self, image):
        # increase or decrease brightness by 30%
        brightness = img_aug.Multiply((0.7, 1.3))
        image = brightness.augment_image(image)
        return image
    
    def blur(self, image):
        kernel_size = random.randint(1, 5)  # kernel larger than 5 would make the image way too blurry
        image = cv2.blur(image,(kernel_size, kernel_size))
    
        return image

    def random_flip(self, image, steering_angle):
        is_flip = random.randint(0, 1)
        if is_flip == 1:
            # randomly flip horizon
            image = cv2.flip(image,1)
            steering_angle = 180 - steering_angle
    
        return image, steering_angle
    
    def img_preprocess(self, image):
        height, _, _ = image.shape
        image = image[int(height/2):,:,:]  # remove top half of the image, as it is not relavant for lane following
        image = cv2.cvtColor(image, cv2.COLOR_RGB2YUV)  # Nvidia model said it is best to use YUV color space
        image = cv2.GaussianBlur(image, (3,3), 0)
        image = cv2.resize(image, (200,66)) # input image size (200,66) Nvidia model
        image = image / 255 # normalizing, the processed image becomes black for some reason.  do we need this?
        return image

    '''
    Creating Convolution Neural Network 
    '''
    def nvidia_model(self):
        model = Sequential(name='Nvidia_Model')
        
        # elu=Expenential Linear Unit, similar to leaky Relu
        # skipping 1st hiddel layer (nomralization layer), as we have normalized the data
        
        # Convolution Layers
        model.add(Conv2D(24, (5, 5), strides=(2, 2), input_shape=(66, 200, 3), activation='elu')) 
        model.add(Conv2D(36, (5, 5), strides=(2, 2), activation='elu')) 
        model.add(Conv2D(48, (5, 5), strides=(2, 2), activation='elu')) 
        model.add(Conv2D(64, (3, 3), activation='elu')) 
        model.add(Dropout(0.2)) # not in original model. added for more robustness
        model.add(Conv2D(64, (3, 3), activation='elu')) 
        
        # Fully Connected Layers
        model.add(Flatten())
        model.add(Dropout(0.2)) # not in original model. added for more robustness
        model.add(Dense(100, activation='elu'))
        model.add(Dense(50, activation='elu'))
        model.add(Dense(10, activation='elu'))
        
        # output layer: turn angle (from 45-135, 90 is straight, <90 turn left, >90 turn right)
        model.add(Dense(1)) 
        
        # since this is a regression problem not classification problem,
        # we use MSE (Mean Squared Error) as loss function
        optimizer = Adam(lr=1e-3) # lr is learning rate
        model.compile(loss='mse', optimizer=optimizer)
        
        return model

    '''
    Generating image for deep leanring with data augmentation
    '''
    def image_data_generator(self, image_paths, steering_angles, batch_size, is_training):
        while True:
            batch_images = []
            batch_steering_angles = []
            
            for i in range(batch_size):
                random_index = random.randint(0, len(image_paths) - 1)
                image_path = image_paths[random_index]
                image = self.my_imread(image_paths[random_index])
                steering_angle = steering_angles[random_index]
                if is_training:
                    # training: augment image
                    image, steering_angle = self.random_augment(image, steering_angle)
                
                image = self.img_preprocess(image)
                batch_images.append(image)
                batch_steering_angles.append(steering_angle)
                
            yield( np.asarray(batch_images), np.asarray(batch_steering_angles))
    '''
    3. deep_learning()
    - Actual deep learning traiing method 
    '''
    def deep_training(self):
        '''
        3-1. Creating CNN network based on nVIDIA model 
        '''
        model = self.nvidia_model()
        print(model.summary())

        ncol = 2
        nrow = 2

        '''
        3-2. Spliting labeling dataset into train data and test data  
        '''
        X_train_batch, y_train_batch = next(self.image_data_generator(self.X_train, self.y_train, nrow, True))
        X_valid_batch, y_valid_batch = next(self.image_data_generator(self.X_valid, self.y_valid, nrow, False))

        '''
        3-3. Saving the model weights (inference file) after each epoch. Model is saved as name of 'lane_navigation_check.h5' at './output' folder.
        '''
        # saves the model weights after each epoch if the validation loss decreased
        checkpoint_callback = ModelCheckpoint(filepath=os.path.join(self.model_output_dir,'lane_navigation_check.h5'), verbose=1, save_best_only=True)

        '''
        3-4. Performing actual deep learning training 
        '''
        history = model.fit_generator(self.image_data_generator( self.X_train, self.y_train, batch_size=100, is_training=True),
                                    steps_per_epoch=300,
                                    epochs=10,
                                    validation_data = self.image_data_generator( self.X_valid, self.y_valid, batch_size=100, is_training=False),
                                    validation_steps=200,
                                    verbose=1,
                                    shuffle=1,
                                    callbacks=[checkpoint_callback])
	
        '''
        3-5. Saving final model weight(inference file) after training is finished.  
        '''
        # always save model output as soon as model finishes training
        model.save(os.path.join(self.model_output_dir,'lane_navigation_final.h5'))

        '''
        3-6. Reporting training result. 
        ''' 
        date_str = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
        history_path = os.path.join(self.model_output_dir,'history.pickle')
        with open(history_path, 'wb') as f:
            pickle.dump(history.history, f, pickle.HIGHEST_PROTOCOL)

import datetime


'''
2. Executing main code 
 - Creating object ( from JdDeepLearning class 
 - Running deep_learning() method 
'''
if __name__ == '__main__':
    jdlab = JdDeepLearning()
    jdlab.deep_training()
    print("Deep learinig training finished!")



