import cv2
import numpy as np
from time import sleep
from config import *

# Saves clips based on previously found matches
def save_matches(file, matches, hashes, info,status):
    matchnum = 1
    video = cv2.VideoCapture(file)
    framenum = 0
    while True:
        if len(matches) == 0:
            if status.matching_done:
                break
            else:
                status.saving = "waiting"
                sleep(1)
                continue
        match = matches.pop(0)
        status.saving = match
        if hashes[match[0]] == 0:
            continue    # Black screen, invalid, skip
        ret, frame = video.read()
        while framenum < match[0]:
            # Do nothing, we don't actually need these frames
            ret, frame = video.read()
            framenum += 1
        frames = np.empty((match[1]-match[0]+1,info.height,info.width,3),dtype=np.uint8)
        frameind = 0
        while framenum >= match[0] and framenum <= match[1]:
            frames[frameind] = frame
            frameind += 1
            ret, frame = video.read()
            framenum += 1
        save_clip(frames, info, matchnum)
        matchnum += 1
    video.release()
    status.saving_done = True
    status.saving = "Done"


def save_clip(frames, info, matchnum):
    global output_height
    global output_width
    destfile = save_folder+str(info.num)+"-"+str(matchnum)+".avi"

    target_height = info.height
    target_width = info.width
    if output_height <= 0 and output_width <= 0: # Both auto, no scaling
        pass
    elif output_height > 0 and output_width > 0: # Both specified numbers
        target_height = output_height
        target_width = output_width
    elif output_height > 0 and output_width <= 0: # Auto calculate width
        target_height = output_height
        target_width = round(target_height/info.height * info.width)
    elif output_height <= 0 and output_width > 0: # Auto calculate height
        target_width = output_width
        target_height = round(target_width/info.width * info.height)
    
    fourcc = cv2.VideoWriter_fourcc(*'XVID')#*'h264')
    out = cv2.VideoWriter(destfile,fourcc, info.frame_rate,(target_width,target_height),True)
    
    for frame in frames:
        if target_height != info.height or target_width != info.width:
            scaled = cv2.resize(frame, (target_width, target_height))
            out.write(scaled)
        else:
            out.write(frame)
    out.release()
    return