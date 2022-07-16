# this is the main script of face verification module.
# methods:
#   1. extract_feat: extract feature of an image.
#   2. authenticate: verifies if the face in the img is known or not (authentication).
#   3. authorizate: verifies if the face is related to the true user.

from numpy.linalg import norm
from numpy import float32

from extraction import FeatureExtractor
from detection import FaceDetector


class FaceVerifier(object):
    def __init__(self, cfg=None):
        super(FaceVerifier, self).__init__()
        self.features = None
        self.names = None
        # face verification distance threshold
        self.thresh = cfg["thresh"]
        # loading face detection modlue
        self.detector = FaceDetector(cfg["detection"])
        # loading face feature extractor modlue
        self.extractor = FeatureExtractor(cfg["extraction"])

    def extract_feat(self, img):
        if len(img.shape) != 3:
            print("Unknown Image Type !!!")
            return None
        face = self.detector.detect_one(img)
        # TODO: to add face alignment before verification we should add 
        #       this lines instead of previous line:
        #       1. face_box, face_ldmks = self.detector.detect_one(img)
        #       2. face = self.aligner.align_one(img, face_box, face_ldmks)
        feat = self.extractor.extract_one(face)
        norm_feat = feat / norm(feat, axis=1)
        return norm_feat

    def verify_one(self, img):
        '''
        img: input image to apply face detection on, and recognize the detected face
        '''
        face = self.detector.detect_one(img)
        # TODO: to add face alignment before verification we should add 
        #       this lines instead of previous line:
        #       1. face_box, face_ldmks = self.detector.detect_one(img)
        #       2. face = self.aligner.align_one(img, face_box, face_ldmks)
        if face is not None:
            feat = self.extractor.extract_one(face)
            norm_feat = feat / norm(feat, axis=1)
            # calculate cosine distance
            confs = (1 + norm_feat @ self.features.T) / 2
            name, max_conf = self.names[confs.argmax()], confs.max()
            name = name.split('_')[0]
        else:
            return False, "None", float32(-1)
        # check if the minimum distance is smaller than threshold or not
        if max_conf > self.thresh:
            return True, name, max_conf
        else:
            return False, "Unknown", max_conf
