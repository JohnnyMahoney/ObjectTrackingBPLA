import cv2
import threading

class ObjectTracker:
    def __init__(self, tracker_type="CSRT"):
        self.tracker = cv2.TrackerCSRT_create() if tracker_type == "CSRT" else None
        self.roi_selected = False
        self.bbox = None
        self.initial_hist = None
        self.object_lost = False
        self.lost_threshold = 0.5
        self.roi_lock = threading.Lock()

    def select_roi(self, frame):
        with self.roi_lock:
            self.bbox = cv2.selectROI('ROI Selector', frame, False)
            cv2.destroyWindow('ROI Selector')
            if self.bbox[2] > 0 and self.bbox[3] > 0:
                self.tracker.init(frame, self.bbox)
                (x, y, w, h) = [int(v) for v in self.bbox]
                initial_roi = frame[y:y + h, x:x + w]
                self.initial_hist = cv2.calcHist([initial_roi], [0], None, [256], [0, 256])
                self.initial_hist = cv2.normalize(self.initial_hist, self.initial_hist).flatten()
                self.object_lost = False
                self.roi_selected = True

    def update(self, frame, scale):
        if self.roi_selected and not self.object_lost:
            with self.roi_lock:
                ok, self.bbox = self.tracker.update(frame)
                if ok:
                    (x, y, w, h) = [int(v) for v in self.bbox]
                    roi = frame[y:y + h, x:x + w]
                    hist = cv2.calcHist([roi], [0], None, [256], [0, 256])
                    hist = cv2.normalize(hist, hist).flatten()
                    match = cv2.compareHist(self.initial_hist, hist, cv2.HISTCMP_CORREL)
                    if match < self.lost_threshold:
                        self.object_lost = True
                        return None
                    return (int(x / scale), int(y / scale)), (int((x + w) / scale), int((y + h) / scale))
                else:
                    self.object_lost = True
                    return None
        return None

    def reset_tracker(self):
        with self.roi_lock:
            self.roi_selected = False
            self.object_lost = False
            self.tracker = cv2.TrackerCSRT_create()