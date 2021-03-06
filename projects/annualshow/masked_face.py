import os
import time
import argparse

# third party
import cv2
import numpy as np
import face_recognition
from imutils import paths

# local module
from yolo import objectapi


# global variable
DATA_DIR = './dataset/images'
NAME = 0
DEPAT = 1
JOB = 2
INTRO = 3

INFO = {
    'jiang': ['江纬','AILab','研究员','day day up'],
    'zhou': ['陈周','AILab','研究员','简单'],
    'kejian': ['李科健','AILab','研究员','哈哈哈'],
    'changshu': ['陈昌澍','AILab','研究员','和你一样'],
    'fengjiao': ['王凤娇','AILab','研究员','笑死我了'],
    'zhihao': ['曹志豪','AILab','研究员','别闹'],
    'zhan': ['陈站','AILab','研究员','不学习会死'],
    'jianlong': ['邓建龙','AILab','研究员','怎么又错了'],
    'junguang': ['冼俊光','AILab','研究员', 'be a quiet man'],
    'guangyi': ['袁广益','数据平台','Java开发','快睡觉'],
    'unknown': ['unknown', 'unknown', 'unknown', 'unknown'],
}


def build_facedb(dirpath:str):
    """ build a face database as following:
    Args:
        dirpath: known face database, assume subdir name is the name of person
    Returns:
        key-value face database
    """
    db_embed = []
    db_infos = []

    image_paths = paths.list_images(dirpath)
    for imgpath in image_paths:
        img = face_recognition.load_image_file(imgpath)
        locations = face_recognition.face_locations(img)
        encodings = face_recognition.face_encodings(img, locations)
        try:
            db_embed.append(encodings[0])
        except:
            print('Could not find face!')
        else:
            db_infos.append(os.path.basename(imgpath).split('.')[0])
    return db_embed, db_infos

# build face database
DB_EMBED, DB_LABELS = build_facedb(DATA_DIR)


# for person bbox detection
def yolo_detect(img):
    results = objectapi.detect(img)
    results = [r['bbox'] for r in results if r['label'] == 'person']
    results.sort(key=lambda x: x[0], reverse=True)
    return results


# img_mask for final show
# img_dark for face recognition show
def region_mask(img, bbox):
    img_mask = img.copy()
    img_dark = img.copy()
    size = img.shape[:2]
    dark = np.zeros(size)
    dark[bbox[1]: bbox[3], bbox[0]: bbox[2]] = 1
    mask = np.where(dark==0, 0.3, 1)
    channels = img.shape[2]
    for channel in range(channels):
        img_mask[:, :, channel] = img_mask[:, :, channel] * mask
        img_dark[:, :, channel] = img_dark[:, :, channel] * dark
    img_mask.dtype = np.uint8
    img_dark.dtype = np.uint8
    return img_mask, img_dark


def recognize(img:np.array):
    locations = face_recognition.face_locations(img)
    if len(locations) == 0:
        return {'label': 'unknown', 'distance': 0.999, 'info': INFO['unknown'], 'bbox': None}
    encodings = face_recognition.face_encodings(img, locations)
    def distance_helper(compared_encoding, bbox):
        # NOTE: location just use as return value
        distances = face_recognition.face_distance(DB_EMBED, compared_encoding)
        min_index = np.argmin(distances)
        min_distance = distances[min_index]
        # threshold
        label = DB_LABELS[min_index] if min_distance < 0.70 else 'unknown'
        return {'bbox': [bbox[3], bbox[0], bbox[1], bbox[2]], 'label': label, 'distance': min_distance, 'info': INFO[label]}
    results = list(map(distance_helper, encodings, locations))
    return results[0]


def create_info(height, width, infos):
    label = infos['label']
    distance = infos['distance']
    prob = min((1-distance), 0.999) * 100
    info = infos['info']
    # build image path and read image
    if label == 'unknown':
        img = cv2.imread('unknown.jpg')
    else:
        path = os.path.join(DATA_DIR, f"{label}.jpg")
        img = cv2.imread(path)
    # resize to width when keeping height:width ratio by center crop
    img = resize(img, width)
    # create a canvas
    canvas = np.zeros((height, width, 3), dtype=np.uint8)
    canvas[0:width, 0:width, :] = img[:, :, :]

    def putText(canvas, info):
        from PIL import Image, ImageFont, ImageDraw
        canvas = cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(canvas)
        # support Simplified Chinese Font
        font = ImageFont.truetype('/home/mory/.mory/font/msyh.ttc', 40)
        draw = ImageDraw.Draw(img)
        # face difference
        draw.text((10, width + 0), font=font, text=f"Probability: ", fill="#ffaaee")
        draw.text((10, width + 60), font=font, text=f"{prob:.1f}%", fill="#ffaa00")
        # name
        draw.text((10, width + 120), font=font, text=f"Name: ", fill="#ffaaee")
        draw.text((10, width + 180), font=font, text=f"{info[NAME]}", fill="#ffaa00")
        # department
        draw.text((10, width + 240), font=font, text=f"Department: ", fill="#ffaaee")
        draw.text((10, width + 300), font=font, text=f"{info[DEPAT]}", fill="#ffaa00")
        # Job title
        draw.text((10, width + 360), font=font, text=f"Job: ", fill="#ffaaee")
        draw.text((10, width + 420), font=font, text=f"{info[JOB]}", fill="#ffaa00")
        # description
        draw.text((10, width + 480), font=font, text=f"Description: ", fill="#ffaaee")
        draw.text((10, width + 540), font=font, text=f"{info[INTRO]}", fill="#ffaa00")
        return np.array(img)
    img = putText(canvas, info)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    return img


# resize image by center crop
def resize(img, width):
    h, w = img.shape[:2]
    if h > w:
        start_h = (h - w) // 2
        img = img[start_h:start_h+w, :, :]
    else:
        start_w = (w - h) // 2
        img = img[:, start_w:start_w+h, :]
    return cv2.resize(img, (width, width))


def draw_facebbox(img, bbox):
    if bbox is not None:
        img = cv2.rectangle(img, (bbox[0]-20, bbox[1]-20), (bbox[2]+20, bbox[3]+20), (128, 255, 128), 3)
    return img


def append_info(img, img_info):
    width = 4
    height = img_info.shape[0]
    seperate = np.ones((height, width, 3), dtype=np.uint8)
    seperate[:, :, :] = np.array([255, 128, 0], dtype=np.uint8)
    combine = np.hstack([img, seperate, img_info])
    return combine


def parse_args():
    import argparse
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--video', '-v', required=True)
    argparser.add_argument('--dir', '-d', required=True)
    argparser.add_argument('--fmax', '-m', required=True)
    args = argparser.parse_args()
    return args


if __name__ == "__main__":
    # init
    t = time.time()
    bbox_index = 0
    frame_cnt = 0
    total_cnt = 0
    frame_max = int(args.fmax)
    cap = cv2.VideoCapture(f'/home/mory/{args.video}')
    # procedure1: read in raw image -> image
    while True:
        ret, img = cap.read()
        if not ret:
            break
        img = resize(img, 1000)
        # procedure2: yolo detect person -> person-bbox
        bboxes = yolo_detect(img)
        bboxes_num = len(bboxes)
        if not bboxes_num:
            print('empty frame')
            continue
        # procedure3: masked just one person out -> masked-image
        if bbox_index >= bboxes_num:
            continue
        bbox = bboxes[bbox_index]
        masked, darked = region_mask(img, bbox)
        # procedure4: faceapi detect the person -> infos
        infos = recognize(darked)
        # procedure5.1: create info -> info-image
        img_info = create_info(img.shape[0], 300, infos)
        # procedure5.2: draw face bbox -> face-image
        img_face = draw_facebbox(masked, infos['bbox'])
        # procedure6: combine masked-image and info-image -> END
        img = append_info(img_face, img_info)
        # cv2.imshow("test", img)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break
        cv2.imwrite('new/{}/{}.png'.format(args.dir, total_cnt), img)

        # monitor frame count
        frame_cnt += 1
        total_cnt += 1
        # switch bbox
        if frame_cnt == frame_max:
            frame_cnt = 0
            bbox_index += 1
            if bbox_index == bboxes_num:
                bbox_index = 0
        print(f'process image {total_cnt} cost: {time.time() - t}s')
