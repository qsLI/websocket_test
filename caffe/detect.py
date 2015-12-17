import gtk
import numpy as np
import caffe
import cv2



def window(x, y, im):
    return im[y:y + WINDOW_SIZE, x:x + WINDOW_SIZE]


def merge_windows(w1, w2):
    w1x1, w1y1, w1x2, w1y2 = w1
    w2x1, w2y1, w2x2, w2y2 = w2
    return min(w1x1, w2x1), min(w1y1, w2y1), max(w1x2, w2x2), max(w1y2, w2y2)


def windows_distance(w1,w2):
    [w1x1, w1y1, w1x2, w1y2] = w1
    [w2x1, w2y1, w2x2, w2y2] = w2
    w1center = np.array([(w1x1+w1x2) /2 ,  (w1y1+w1y2) /2])
    w2center = np.array([(w2x1+w2x2) /2 ,  (w2y1+w2y2) /2])
    return np.linalg.norm(w1center-w2center)


def merge_windows_list(window_list, max_distance):
    merged = False
    merged_list = []
    already_merged_list = []

    for i, w1 in enumerate(window_list):
        for j, w2 in enumerate(window_list[i+1:]):
            if w1 not in already_merged_list and w2 not in already_merged_list and windows_distance(w1, w2) < max_distance :
                merged_list.append(merge_windows(w1, w2))
                already_merged_list.append(w1)
                already_merged_list.append(w2)
                merged = True
                # print 'merged windows', w1, w2

    if merged:
        not_merged_list = [item for item in window_list if item not in already_merged_list]
        return merge_windows_list(merged_list + not_merged_list, max_distance)
    else:
        return window_list


# parameters
WINDOW_SIZE = 36
DETECTION_THRESHOLD = 0.8
MAX_DISTANCE = 10
PROTOTXT = 'NET.prototxt'
CAFFE_MODEL = 'facenet_iter_200000.caffemodel'
DETECTED_OUTPUT_PATH = 'detected/'
ZOOM_RANGE = np.arange(0.7, 1.2, 0.1)


def detect_face(image):
    caffe.set_mode_cpu()
    net = caffe.Net(PROTOTXT, CAFFE_MODEL, caffe.TEST)
    detected = []
    im_array_rgb = np.array(image)
    for rzoom in ZOOM_RANGE:
        im_array_rgb = cv2.resize(im_array_rgb, None, fx=rzoom, fy=rzoom)
        im_array = cv2.cvtColor(im_array_rgb, cv2.COLOR_RGB2GRAY)
        print 'zoom : ', rzoom
        for x in xrange(0, len(im_array[0]) - WINDOW_SIZE, 2):
            for y in xrange(0, len(im_array) - WINDOW_SIZE, 2):
                window_array = window(x, y, im_array)
                im_input = window_array[np.newaxis, np.newaxis, :, :]
                net.blobs['data'].reshape(*im_input.shape)
                net.blobs['data'].data[...] = im_input
                out = net.forward()

                if out['loss'][0][1] > DETECTION_THRESHOLD:
                    real_x = int(x * 1 / rzoom)
                    real_y = int(y * 1 / rzoom)
                    detected.append((real_x, real_y, real_x + int(WINDOW_SIZE * 1 / rzoom), real_y + int(WINDOW_SIZE * 1 / rzoom)))

    return merge_windows_list(detected, MAX_DISTANCE)

if __name__ == "__main__":
    img = cv2.imread("faces.jpg")
    faces = detect_face(img)
    for face in faces:
        cv2.rectangle(img, (face[0], face[1]), (face[2], face[3]), (255,255,0), 2)
    cv2.namedWindow("faces")
    cv2.imshow("faces", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()