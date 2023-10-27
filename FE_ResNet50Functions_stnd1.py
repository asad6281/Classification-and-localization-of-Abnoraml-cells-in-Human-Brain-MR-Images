import tensorflow as tf
import numpy as np
import cv2
from tensorflow.keras import optimizers
from skimage import io
import os


def getModel():
    with open('model_json\model_fine_tuning_16b_345_3.json', 'r') as json_file:
        json_saved_model = json_file.read()
    
    model_resnet = tf.keras.models.model_from_json(json_saved_model)
    model_resnet.load_weights('model_weights\classifier-resnet-weights_fine_tuning_16b_345_3.hdf5')
    model_resnet.compile(loss ='categorical_crossentropy', optimizer=optimizers.Adam(0.0001), metrics= ['accuracy'])
    
    return model_resnet


def PredictAbnormality(curr_dir, image_names, model, top, ClassificationProgress):
    image_path = []
    orig_index = []
    i=-1
    barIncrement = 100/len(image_names)
    ClassificationProgress.grid(row=3, column=0, columnspan=2)
    '''here'''
    for name in image_names:
        path = os.path.join(curr_dir, name)
        ClassificationProgress['value']+=barIncrement
        top.update_idletasks()
        i=i+1
        img = io.imread(path)
        img = img * 1./255.
        img = cv2.resize(img,(256,256))
        img = np.array(img, dtype = np.float64)
        img = np.reshape(img, (1,256,256,3))
        is_defect = model.predict(img)

        if np.argmax(is_defect) == 0:
            continue
        else:
            image_path.append(path)
            orig_index.append(i)
            
    return image_path, orig_index