from time import sleep
from config import *

# Compares the hashes, trying to find similarities within the specified window
def compare_hashes(matches,hashes,info,status):
    global max_length
    global min_length
    global prefer_long
    global threshold
    global mid_threshold
    
    min_frames = round(info.frame_rate * min_length)
    max_frames = round(info.frame_rate * max_length)
    framenum = 0
    i = 0
    while True:
        # No unhashed frames in array
        if i >= len(hashes)-1:
            # All frames hashed
            if status.hashing_done:
                break
            # Wait for hashing thread
            else:
                status.matching = "waiting"
                sleep(1)
                continue
                
        status.matching = framenum
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
    status.matching_done = True
    status.matching = "Done"
    return