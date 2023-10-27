import tensorflow as tf
from skimage import io
import numpy as np
import cv2
import os

from tensorflow.keras import optimizers
from tensorflow.keras import backend as K

def tversky(y_true, y_pred, smooth = 1e-6):
    y_pred = tf.cast(y_pred, tf.float64)
    y_true = tf.cast(y_true, tf.float64)
    y_true_pos = K.flatten(y_true)
    y_pred_pos = K.flatten(y_pred)
    
    true_pos = K.sum(y_true_pos * y_pred_pos)
    false_neg = K.sum(y_true_pos * (1-y_pred_pos))
    false_pos = K.sum((1-y_true_pos)*y_pred_pos)
    alpha = 0.7 # if alpha > 0.5 then more attention is paid to FN
    return (true_pos + smooth)/(true_pos + alpha*false_neg + (1-alpha)*false_pos + smooth)


def focal_tversky(mask_true,mask_pred):
    mask_pred = tf.cast(mask_pred, tf.float64)
    mask_true = tf.cast(mask_true, tf.float64)
    pt_1 = tversky(mask_true, mask_pred)
    gamma = 0.75
    return K.pow((1-pt_1), gamma)


def metric_iou(mask_true, mask_pred):
    mask_true = tf.cast(mask_true, tf.float64)
    mask_pred = tf.cast(mask_pred, tf.float64)
    mask_true = K.flatten(mask_true)
    mask_pred = K.flatten(mask_pred)
    
    intersection = np.logical_and(mask_true, mask_pred)
    union = np.logical_or(mask_true, mask_pred)
    return (np.sum(intersection)/np.sum(union))


def getModel_ResUnet():
    with open('model_json/res-unet-model2.json', 'r') as json_model:
        json_saved_model = json_model.read()

    model_ResUnet = tf.keras.models.model_from_json(json_saved_model)
    model_ResUnet.load_weights('model_weights/res-unet-weights2.hdf5')
    model_ResUnet.compile(optimizer=optimizers.Adam(learning_rate=0.05, epsilon=0.1), loss=focal_tversky, metrics=[tversky])
    
    return model_ResUnet


def Localize_Abnormality(analyzed_dir_list, model, top, LocalizationProgress):
    ''' Creating empty list to store the results '''
    mask = []
    barIncrement = 100/len(analyzed_dir_list)
    LocalizationProgress.grid(row=3, column=0, columnspan=2)

    ''' iterating through each image in the test data '''
    for path in analyzed_dir_list:
        LocalizationProgress['value']+=barIncrement
        top.update_idletasks()
        
        img = io.imread(path)
        X = np.empty((1, 256, 256, 3))
        img = cv2.resize(img,(256,256))
        img = np.array(img, dtype = np.float64)
        img -= img.mean()
        img /= img.std()
        
        ''' Converting shape of image from 256,256,3 to 1,256,256,3 '''
        X[0,] = img

        predict = model.predict(X)

        ''' Sum of predicted values = 0, Abnormality Not Present '''
        if predict.round().astype(int).sum() == 0:
            mask.append('No mask')
            ''' Sum of pixel values > 0, Abnormality Present '''
        else:
            mask.append(predict)

    return mask