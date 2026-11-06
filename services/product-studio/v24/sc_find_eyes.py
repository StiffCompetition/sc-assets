"""Find the two eye centres on a character picture (free, no network): MediaPipe Face Mesh with iris points.
Usage: python3 sc_find_eyes.py picture.png   -> prints  x1,y1,x2,y2  (left eye first) or exits 1 when no face is found."""
import sys, numpy as np
from PIL import Image
import mediapipe as mp

def find_eyes(path):
    im = np.asarray(Image.open(path).convert('RGB'))
    h, w = im.shape[:2]
    with mp.solutions.face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.3) as fm:
        r = fm.process(im)
    if not r.multi_face_landmarks: return None
    L = r.multi_face_landmarks[0].landmark
    def ctr(ids): return [float(np.mean([L[i].x for i in ids]) * w), float(np.mean([L[i].y for i in ids]) * h)]
    a, b = ctr([468, 469, 470, 471, 472]), ctr([473, 474, 475, 476, 477])   # iris centres
    return sorted([a, b], key=lambda p: p[0])

if __name__ == '__main__':
    e = find_eyes(sys.argv[1])
    if not e: print('NO FACE'); sys.exit(1)
    print('%d,%d,%d,%d' % (e[0][0], e[0][1], e[1][0], e[1][1]))
