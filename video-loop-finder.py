import numpy as np
import sys
import os
import cv2
import imageio
from glob import glob


# Search parameters ( Change as needed )
save_folder = "loops/"
min_length = 1          # Min length of gif, in seconds
max_length = 10         # Max length of gif, in seconds
threshold = 0           # The max allowed differense in hashes (default : 0)
mid_threshold = 6       # Threshold of difference required in the middle of the clip
hash_size = 8
prefer_long = 0         # Set to one to prefer longer loops over shorter ones
output_width = 0        # Width of the output file. Zero or negative for auto
output_height = 360     # Height of the output file. Zero or negative for auto



# Number of clips created so far (used for naming the files)
clips = 0


# Video information
frame_rate = 0
height = 0
width = 0


def main(filelist):
    files = []
    for i in range(1,len(filelist)):
        for arg in glob(os.path.abspath(filelist[i])):
            files.append(arg)

    if len(files) < 1:
        print("No files given, nothing to do...")
        return   
    
    print(str(len(files)) + " files given, processing...")
    
    # Go through all given files one by one
    for file in files:
        hashes = hash_frames(file)
        matches = compare_hashes(hashes)
        save_matches(file, matches, hashes)
        
    print("Finished, "+str(clips)+" total clips created")
    input("Press enter to exit...")


def save_clip(frames):
    global clips
    global frame_rate
    global width
    global height
    global output_height
    global output_width
    destfile = save_folder+str(clips)+".avi"
#    imageio.mimsave(destfile,frames, 'GIF', fps=frame_rate)

    target_height = height
    target_width = width
    if output_height <= 0 and output_width <= 0: # Both auto, no scaling
        pass
    elif output_height > 0 and output_width > 0: # Both specified numbers
        target_height = output_height
        target_width = output_width
    elif output_height > 0 and output_width <= 0: # Auto calculate width
        target_height = output_height
        target_width = round(target_height/height * width)
    elif output_height <= 0 and output_width > 0: # Auto calculate height
        target_width = output_width
        target_height = round(target_width/width * height)
    
    fourcc = cv2.VideoWriter_fourcc(*'h264')
    out = cv2.VideoWriter(destfile,fourcc,frame_rate,(target_width,target_height),True)
    
    for frame in frames:
        if target_height != height or target_width != width:
            scaled = cv2.resize(frame, (target_width, target_height))
            out.write(scaled)
        else:
            out.write(frame)
    out.release()
    
    clips += 1
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


# Calculates the hashes for each frame in the given file
def hash_frames(file):
    global frame_rate
    global width
    global height
    hashes = []
    framenum = 0
    video = cv2.VideoCapture(file)
    
    frame_rate = video.get(cv2.CAP_PROP_FPS)
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    ret, frame = video.read()
    while ret:
        print("Hashing frames: "+str(framenum)+"             ",end="\r")
        H = dhash_frame(frame)
        hashes.append(H)
        framenum += 1
        ret, frame = video.read()
    video.release()
    return hashes
 

 # Compares the hashes, trying to find similarities within the specified window
def compare_hashes(hashes):
    global max_length
    global min_length
    global frame_rate
    global prefer_long
    global threshold
    global mid_threshold
    print()
    matches = []
    min_frames = round(frame_rate * min_length)
    max_frames = round(frame_rate * max_length)
    framenum = 0
    i = 0
    while i < len(hashes)-1:
        print("Comparing hashes: "+str(framenum)+"             ",end="\r")
        if framenum+max_frames < len(hashes):
            nrange = range(framenum+min_frames,framenum+max_frames)
            if prefer_long:
                nrange = range(framenum+max_frames,framenum+min_frames,-1)
            for n in nrange:
                distance = bin(hashes[i] ^ hashes[n]).count('1')
                if distance <= threshold:
                    for x in range(i+1,n):  # Sanity check: see that it isn't ALL same hash
                        distance = bin(hashes[i] ^ hashes[x]).count('1')
                        if distance > mid_threshold:    # There is a difference frame in there, ergo valid
                            matches.append([i,n])
                            framenum = n # Skip over the segment we already saved
                            i = n
                            break
                    if i==n:
                        break
        elif framenum+min_frames < len(hashes):
            nrange = range(framenum+min_frames,len(hashes))
            if prefer_long:
                nrange = range(len(hashes)-1,framenum+min_frames,-1)
            for n in nrange:
                distance = bin(hashes[i] ^ hashes[n]).count('1')
                if distance <= threshold:
                    for x in range(i+1,n):  # Sanity check: see that it isn't ALL same hash
                        distance = bin(hashes[i] ^ hashes[x]).count('1')
                        if distance > mid_threshold:    # There is a difference frame in there, ergo valid
                            matches.append([i,n])
                            framenum = n # Skip over the segment we already saved
                            i = n
                            break
                    if i==n:
                        break
        framenum += 1
        i += 1
#    print(matches)
    return matches


# Saves clips based on previously found matches
def save_matches(file, matches, hashes):
    print()
    for match in matches:
        print("Saving clips: "+str(match[0])+"-"+str(match[1])+"             ",end="\r")
        if hashes[match[0]] == 0:
            continue    # Black screen, invalid, skip
        video = cv2.VideoCapture(file)
        ret, frame = video.read()
        framenum = 0
        while framenum < match[0]:
            # Do nothing, we don't actually need these frames
            ret, frame = video.read()
            framenum += 1
        frames = np.empty((match[1]-match[0]+1,height,width,3),dtype=np.uint8)
        frameind = 0
        while framenum >= match[0] and framenum <= match[1]:
            frames[frameind] = frame
            frameind += 1
            ret, frame = video.read()
            framenum += 1
        save_clip(frames)
        video.release()
        

if __name__ == "__main__":
    main(sys.argv)