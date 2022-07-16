# this is the main script of face detection module.
# jobs:
#   1. gets the input image.
#   2. detects if there is a face in the image.
#   3. returns the  cropped face image.

import torch
import copy
import cv2

from utils.general import check_img_size, non_max_suppression_face, scale_coords, xyxy2xywh
from utils.utils import get_box, get_largest_face_img, letterbox, scale_coords_landmarks
from models.experimental import attempt_load


class FaceDetector(object):
    def __init__(self, cfg=None):
        super(FaceDetector, self).__init__()
        # TODO: 1. to add onnx runtime.
        #       2. to add openvino runtime for more efficiency on intel devices.
        device = "cpu" if not torch.cuda.is_available() else cfg["device"]
        self.device = torch.device(device)
        self.device = cfg["device"]
        self.img_size = cfg["img_size"]
        self.conf_thres = cfg["conf_thres"]
        self.iou_thres = cfg["iou_thres"]

        self.model = attempt_load(cfg["weights"], map_location=self.device)

    def detect_one(self, orgimg):
        if orgimg is None or orgimg.shape[2] != 3:
            return None

        img0 = copy.deepcopy(orgimg)
        h0, w0 = orgimg.shape[:2]  # orig hw
        r = self.img_size / max(h0, w0)  # resize image to img_size
        if r != 1:  # always resize down, only resize up if training with augmentation
            interp = cv2.INTER_AREA if r < 1 else cv2.INTER_LINEAR
            img0 = cv2.resize(img0, (int(w0 * r), int(h0 * r)),
                              interpolation=interp)

        imgsz = check_img_size(
            self.img_size, s=self.model.stride.max())  # check img_size

        img = letterbox(img0, new_shape=imgsz)[0]
        # Convert to 3xwxh
        img = img.transpose(2, 0, 1).copy()

        # Run inference
        img = torch.from_numpy(img).to(self.device)
        img = img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        # Inference
        pred = self.model(img)[0]

        # Apply NMS
        pred = non_max_suppression_face(pred, self.conf_thres, self.iou_thres)

        # Process detections
        for i, det in enumerate(pred):  # detections per image
            gn = torch.tensor(orgimg.shape)[[1, 0, 1, 0]].to(
                self.device)  # normalization gain whwh
            gn_lks = torch.tensor(orgimg.shape)[[1, 0, 1, 0, 1, 0, 1, 0, 1, 0]].to(
                self.device)  # normalization gain landmarks
            if len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_coords(
                    img.shape[2:], det[:, :4], orgimg.shape).round()

                # Print results
                for c in det[:, -1].unique():
                    n = (det[:, -1] == c).sum()  # detections per class

                det[:, 5:15] = scale_coords_landmarks(
                    img.shape[2:], det[:, 5:15], orgimg.shape).round()

                boxes = []
                for j in range(det.size()[0]):
                    xywh = (xyxy2xywh(det[j, :4].view(
                        1, 4)) / gn).view(-1).tolist()
                    _ = det[j, 4].cpu().numpy()
                    landmarks = (det[j, 5:15].view(1, 10) /
                                 gn_lks).view(-1).tolist()
                    _ = det[j, 15].cpu().numpy()
                    box = get_box(orgimg, xywh)
                    boxes.append(box)

                face = get_largest_face_img(orgimg, boxes)
                
                return face

            return None
