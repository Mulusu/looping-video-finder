import cv2
from config import *

# Calculates the hashes for each frame in the given file
def hash_frames(hashes,file,status):
    framenum = 0
    video = cv2.VideoCapture(file)
    ret, frame = video.read()
    while ret:
        status.hashing = framenum
        H = dhash_frame(frame)
        hashes.append(H)
        framenum += 1
        ret, frame = video.read()
    video.release()
    status.hashing_done = True
    status.hashing = "Done"
    return

# Calculates the hash for the given one frame
def dhash_frame(frame):
    global hash_size
    w = hash_size + 1
    bw = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(bw, (w, w))
    flat = resized.flatten()
    row = 0
    col = 0
    
    for y in range(hash_size):
        for x in range(hash_size):
            offset = y * w + x
            row_bit = flat[offset] < flat[offset + 1]
            row = row << 1 | row_bit
            
            col_bit = flat[offset] < flat[offset + w]
            col = col << 1 | col_bit
            
    return row << (hash_size * hash_size) | col