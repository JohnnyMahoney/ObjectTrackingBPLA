import cv2


class VideoCaptureHandler:
    def __init__(self, video_source='videoDron4.MP4', scale=0.5):
        self.video = cv2.VideoCapture(video_source)
        self.scale = scale

    def read_frame(self):
        ok, frame = self.video.read()
        if not ok:
            return None
        return frame

    def resize_frame(self, frame):
        height, width = frame.shape[:2]
        new_dimensions = (int(width * self.scale), int(height * self.scale))
        return cv2.resize(frame, new_dimensions)

    def release(self):
        self.video.release()