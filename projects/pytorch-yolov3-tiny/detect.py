from __future__ import division
import time
import torch 
import torch.nn as nn
from torch.autograd import Variable
import numpy as np

from util import *
import argparse
import os 
import os.path as osp
from darknet import Darknet
import pickle as pkl

import random


def arg_parse():
    """
    Parse arguements to the detect module
    
    """
    
    parser=argparse.ArgumentParser(description='YOLO v3 Detection Module')
   
    parser.add_argument("--images", dest='images', help="Image / Directory containing images to perform detection upon",
                        default="imgs", type=str)
    parser.add_argument("--det", dest='det', help="Image / Directory to store detections to",
                        default="det", type=str)
    parser.add_argument("--bs", dest="bs", help="Batch size", default=1)
    parser.add_argument("--confidence", dest="confidence", help="Object Confidence to filter predictions", default=0.5)
    parser.add_argument("--nms_thresh", dest="nms_thresh", help="NMS Threshhold", default=0.4)
    parser.add_argument("--cfg", dest='cfgfile', help="Config file",
                        default="cfg/yolov3.cfg", type=str)
    parser.add_argument("--weights", dest='weightsfile', help="weightsfile",
                        default="yolov3.weights", type=str)
    parser.add_argument("--reso", dest='reso', help="Input resolution of the network. Increase to increase accuracy. Decrease to increase speed",
                        default="416", type=str)
    
    return parser.parse_args()

def load_classes(namefile):
    with open(namefile) as f:
        names=f.read().strip().split('\n')
    return names

args=arg_parse()
images=args.images
batch_size=int(args.bs)
confidence=float(args.confidence)
nms_thesh=float(args.nms_thresh)
start=0
CUDA=torch.cuda.is_available()

num_classes=80
classes=load_classes('data/coco.names')

print('Loading network....')
model=Darknet(args.cfgfile)
model.load_weights(args.weightsfile)
print('Network successfully loaded')

model.net_info['height']=args.reso
input_dim = int(model.net_info['height'])
assert input_dim % 32 == 0
assert input_dim > 32

if CUDA:
    model.cuda()

model.eval()

read_dir=time.time()
#Detection phase
try:
    imlist=[osp.join(osp.realpath('.'), images, img) for img in os.listdir(images)]
except NotADirectoryError:
    imlist=[]
    imlist.append(osp.join(osp.realpath('.'), images))
except FileNotFoundError:
    print ("No file or directory with the name {}".format(images))
    exit()


if not os.path.exists(args.det):
    os.makedirs(args.det)


load_batch=time.time()
loaded_ims=[Image.open(p) for p in imlist]

im_batches=list(map(prep_image, loaded_ims, [input_dim for _ in range(len(imlist))]))

# list containing dimensions of original images
im_dim_list=[x.size for x in loaded_ims]
# why repeat it?
im_dim_list=torch.FloatTensor(im_dim_list).repeat(1, 2)

write=False
start_det_loop=time.time()
for i, batch in enumerate(im_batches):
    start=time.time()
    if CUDA:
        batch=batch.cuda()
    with torch.no_grad():
        prediction=model(Variable(batch), CUDA)
    prediction=write_results(prediction, confidence, num_classes, nms_conf=nms_thesh)

    end=time.time()

    if type(prediction) == int:
        for im_num, image in enumerate(imlist[i*batch_size : min((i+1)*batch_size, len(imlist))]):
            im_id=i * batch_size + im_num
            print("{0:20s} predicted in {1:6.3f} seconds".format(image.split("/")[-1], (end - start)/batch_size))
            print("{0:20s} {1:s}".format("Objects Detected:", ""))
            print("----------------------------------------------------------")
        continue


    if not write:                      #If we have't initialised output
        output=prediction  
        write=1
    else:
        output=torch.cat((output,prediction))

    for im_num, image in enumerate(imlist[i*batch_size : min((i+1)*batch_size, len(imlist))]):
        im_id=i*batch_size + im_num
        objs=[classes[int(x[-1])] for x in output if int(x[0]) == im_id]
        print("{0:20s} predicted in {1:6.3f} seconds".format(image.split("/")[-1], (end - start)/batch_size))
        print("{0:20s} {1:s}".format("Objects Detected:", " ".join(objs)))
        print("----------------------------------------------------------")

    if CUDA:
        torch.cuda.synchronize() 

    try:
        output
    except NameError:
        print('Non detections were made')
        exit()
    
    im_dim_list=torch.index_select(im_dim_list, 0, output[:,0].long())
    scaling_factor=torch.min(input_dim/im_dim_list, 1)[0].view(-1,1)

    output[:, [1,3]] -= (input_dim - scaling_factor*im_dim_list[:,0].view(-1,1))/2
    output[:, [2,4]] -= (input_dim - scaling_factor*im_dim_list[:,1].view(-1,1))/2

    output[:, 1:5] /= scaling_factor

    for i in range(output.shape[0]):
        output[i, [1,3]]=torch.clamp(output[i, [1,3]], 0.0, im_dim_list[i,0])
        output[i, [2,4]]=torch.clamp(output[i, [2,4]], 0.0, im_dim_list[i,1])
    

    class_load=time.time()
    colors=pkl.load(open('pallete', 'rb'))

    draw=time.time()

    def write(x, results):
        c1=tuple(x[1:3].int())
        c2=tuple(x[3:5].int())
        img=results[int(x[0])]
        cls=int(x[-1])
        label='{}'.format(classes[cls])
        return img
    
    list(map(lambda x: write(x, loaded_ims), output))
    end=time.time()

    print("SUMMARY")
    print("----------------------------------------------------------")
    print("{:25s}: {}".format("Task", "Time Taken (in seconds)"))
    print()
    print("{:25s}: {:2.3f}".format("Reading addresses", load_batch - read_dir))
    print("{:25s}: {:2.3f}".format("Loading batch", start_det_loop - load_batch))
    print("{:25s}: {:2.3f}".format("Drawing Boxes", end - draw))
    print("{:25s}: {:2.3f}".format("Average time_per_img", (end - load_batch)/len(imlist)))
    print("----------------------------------------------------------")


    torch.cuda.empty_cache()