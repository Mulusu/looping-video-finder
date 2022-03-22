import sys
from glob import glob
import os
from threading import Thread

if sys.version_info >= (3,0):
    from queue import Queue
else:
    from Queue import Queue

from config import *
from save_video import *
from compare_hashes import *
from hash_frames import *


class Videoinfo:
    def __init__(self, file,filenum):
        video = cv2.VideoCapture(file)
        self.frame_rate = video.get(cv2.CAP_PROP_FPS)
        self.width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.num = filenum
        video.release()
        
        
class Status:
    def __init__(self):
        self.hashing_done = False
        self.matching_done = False
        self.saving_done = False
        
        self.hashing = 0
        self.matching = 0
        self.saving = 0
        
    def alldone(self):
        return self.hashing_done and self.matching_done and self.saving_done
        
    def get_status(self):
        return f"Hashing: {self.hashing}, Matching: {self.matching}, Saving: {self.saving}"


def main(filelist):
    files = []
    for i in range(1,len(filelist)):
        path = os.path.abspath(filelist[i])
        fls = glob(path, recursive=True)
        for arg in fls:
            files.append(arg)

    if len(files) < 1:
        print("No files given, nothing to do...")
        return   
    
    print(str(len(files)) + " files given, processing...")
    
    # Go through all given files one by one
    filenum = 1
    while len(files) > 0:
        hashes = []
        matches = []
        file = files.pop(0)
        print(f"Now processing \"{file}\"")
        status = Status()
        info = Videoinfo(file,filenum)
        
        ht = Thread(target=hash_frames, args=(hashes,file,status))
        ct = Thread(target=compare_hashes, args=(matches,hashes,info,status))
        st = Thread(target=save_matches, args=(file, matches, hashes,info,status))
        
        ht.start()
        ct.start()
        st.start()
        
        
        while not status.alldone():
            sleep(1)
            print(f"{status.get_status()}, files in queue: {len(files)}              ",end="\r")
        
        ht.join()   # Just to make sure they are all really finished
        ct.join()
        st.join()
        filenum += 1
    print("\n\nFinished!")

if __name__ == "__main__":
    main(sys.argv)