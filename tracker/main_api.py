import multiprocessing
import cv2
import numpy as np
from PIL import Image
from joblib import Parallel, delayed
import multiprocessing
from tracker import two_cc, simple_segmentation
from tracker.tracking_utils import pipeline_final
from tracker.active_colloids_utils import active_colloids_tracking_pipeline

num_cores=1

def prepare_frames(vidcap, n_frames=50, window=(0, 250, 500, 430)):
    success,image = vidcap.read()
    count = 0
    while success:
        # print(image)
        cv2.imwrite("static/media/temp_vid/frame%d.jpg" % count, image)     # save frame as JPEG file
        success, image = vidcap.read()
        count += 1

    frames = []
    n = n_frames
    for i in range(n):
        image = Image.open("static/media/temp_vid/frame" + str(i * int(count / n)) + ".jpg")
        w, h = image.size
        image = image.crop(window)
        frames.append(image)
    
    return frames

def two_cc_segmentation(frames):
    num_frames = len(frames)
    num_cores = multiprocessing.cpu_count()
    segments = Parallel(n_jobs=num_cores)(delayed(two_cc.two_connected_components)(frames[i], channel="red",thresh=86) for i in range(num_frames))
    return segments

def mst_segmentation(frames):
    segments = []
    return segments

def ngc_segmentation(frames):
    segments = []
    return segments

def simple_threshold_segmentation(frames):
    segments = []
    return segments

def watershed_segmentation(frames):
    num_frames = len(frames)
    num_cores = multiprocessing.cpu_count()
    segments = Parallel(n_jobs=num_cores)(delayed(simple_segmentation.simple_segmentation)(frames[i]) for i in range(num_frames))
    return segments


def tracking_local(frames):
    num_cores = multiprocessing.cpu_count()
    start_frame = 0
    end_frame = len(frames)
    matchings = pipeline_final(start_frame, end_frame, concurrent=True, frames=frames, num_cores=num_cores)

    # for i in range(start_frame, end_frame):
    #     cv2.imwrite("static/media/matched/match%d.jpg" % i, np.float32(matchings[i]))
    
    pathOut = 'static/media/tracking_video.mkv'
    tracking_movie = cv2.VideoWriter(pathOut, apiPreference=0, fourcc = cv2.VideoWriter_fourcc(*'DIVX'), fps=15, frameSize=frames[0].size)
    for i in range(start_frame, end_frame):
        tracking_movie.write(np.uint8(matchings[i]))
    tracking_movie.release()
    return pathOut

def active_colloids_tracking(frames):
    results, G, resultFlowDict = active_colloids_tracking_pipeline(frames)

    # for i in range(start_frame, end_frame):
    #     cv2.imwrite("static/media/matched/match%d.jpg" % i, np.float32(results[i]) )
    
    pathOut = 'static/media/tracking_video.mkv'
    tracking_movie = cv2.VideoWriter(pathOut, apiPreference=0, fourcc = cv2.VideoWriter_fourcc(*'DIVX'), fps=15, frameSize=results[0].size)
    for i in range(len(frames)):
        tracking_movie.write(np.uint8(results[i]))
    tracking_movie.release()

    return pathOut
