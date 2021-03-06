import os
import cv2

import dlib
import torch
import numpy as np

from .models import Landmark



detector = dlib.get_frontal_face_detector()


def load_model():
    net = Landmark()
    cwd = os.path.dirname(__file__) 
    net.load_state_dict(torch.load(os.path.join(cwd, 'sd_landmark.pth')))
    net.eval()
    return net

net = load_model()

def detect(image:str):
    global net
    img = cv2.imread(image)
    # The 1 in the second argument indicates that we should upsample the image
    # 1 time.  This will make everything bigger and allow us to detect more
    # faces.
    dets = detector(img, 1)
    results = []
 
    for index, det in enumerate(dets):
        x1 = max(det.left(), 0)
        y1 = max(det.top(), 0)
        x2 = min(det.right(), img.shape[1])
        y2 = min(det.bottom(), img.shape[0])
        roi = img[y1:y2 + 1, x1:x2 + 1, ]
        gray_img = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)
        w = 60
        h = 60

        res = cv2.resize(gray_img, (w, h), interpolation=cv2.INTER_CUBIC)
        resize_mat = np.float32(res)        
        mean, std_dev = cv2.meanStdDev(resize_mat)
        new_m = mean[0][0]
        new_sd = std_dev[0][0]
        new_img = (resize_mat - new_m) / (0.000001 + new_sd)

        with torch.no_grad():
            new_img = torch.FloatTensor(new_img[None, None, ...])
            torch_out = net(new_img)
        points = torch_out.numpy().squeeze()
        points[0::2] = points[0::2] * (x2-x1) + x1
        points[1::2] = points[1::2] * (y2-y1) + y1
        results.append({'bbox': [x1, y1, x2, y2], 'landmark': points.tolist()})
    return results

def show(image:str):
    img = cv2.imread(image)
    results = detect(image)
    for result in results:
        points = result['landmark']
        x1, y1, x2, y2 = result['bbox']
        for i in range(0, len(points), 2):
            cv2.circle(img, (int(points[i]), int(points[i+1])), 1, (128, 255, 255), 2)
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
    cv2.imshow("image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return img
