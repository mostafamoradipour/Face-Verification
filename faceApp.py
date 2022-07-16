# this is the main script of face verification (authentication/authorization) service.
# jobs:
#   1. extracts features of a database and saves them on the monster.
#   2. does authentication and authorization processes.

from os.path import join
from numpy import array
from cv2 import imread
from os import listdir
from tqdm import tqdm
import codecs
import pickle
import glob
import yaml

from verification.database import MyMonster
from verification import FaceVerifier


class faceEngine():
    def __init__(self):
        with open("config.yaml", 'r') as f:
            cfg = yaml.load(f)

        self.verifier = FaceVerifier(cfg)
        self.monster = MyMonster(cfg["endpoint"])
        self.database = cfg["database"]
        self.container = cfg["container"]
        self.object = cfg["object"]

    def init_feats(self):
        try:
            content = self.monster.getObjectInfo(self.container, self.object)
            feats = pickle.loads(codecs.decode(content.encode(), "base64"))
            self.verifier.features = array(list(feats.values())).squeeze()
            self.verifier.names = list(feats.keys())
            print("features are loaded from monster successfully")
        except:
            print("error in loading featrues from monster")

    def extract(self):
        img_dir = join(self.database, "images")
        names = listdir(img_dir)
        feats = {}
        for name in tqdm(names):
            img_pths = sorted(glob.glob(join(img_dir, name, '*')))
            for i, pth in enumerate(img_pths):
                img = imread(pth)[:, :, ::-1]
                feats[name+'_'+str(i)] = self.verifier.extract_feat(img)

        content = codecs.encode(pickle.dumps(feats), "base64").decode()
        self.monster.createContainer(self.container)
        self.monster.createObject(self.container, self.object, content)

    def authenticate(self, img):
        authenticated, name, conf = self.verifier.verify_one(img)
        result = {"authenticated": authenticated, "name": name,
                  "max_confidence": round(conf.astype("float64"), 3)}

        return result

    def authorize(self, img, uname):
        _, name, conf = self.verifier.verify_one(img)
        authorized = name.lower() == uname.lower()
        result = {"authorized": authorized, "name": name,
                  "max_confidence": round(conf.astype("float64"), 3)}

        return result


if __name__ == "__main__":
    engine = faceEngine()
    engine.extract()
