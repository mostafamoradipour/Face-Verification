# this is the main script of face feature extraction module.
# jobs:
#   1. gets the input face image.
#   2. rezie the image to the shape of 112 * 112
#   3. extract face feature of size 512.
#   4. returns the extracted feature.

import numpy as np
import onnxruntime
import cv2


class FeatureExtractor(object):
    def __init__(self, cfg=None):
        super(FeatureExtractor, self).__init__()
        # TODO: to add openvino runtime for more efficiency on intel devices.
        self.img_size = cfg["img_size"]
        self.session = onnxruntime.InferenceSession(cfg["weights"])
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name

    def extract_one(self, img):
        '''
        this is the main function of this class:
            1. gets input face
            2. resize to 112 * 112
            3. extract feature and return it.
        '''
        img = cv2.resize(img, (self.img_size, self.img_size)) / 127.5 - 1
        input_data = np.expand_dims(
            img.transpose((2, 0, 1)), 0).astype('float32')
        feat = self.session.run([self.output_name], {self.input_name: input_data})[0]
        return feat
