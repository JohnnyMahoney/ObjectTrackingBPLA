import cv2
import threading
import time
from video_capture_handler import VideoCaptureHandler
from object_tracker import ObjectTracker
from user_interface import UserInterface
from mavlink_connection import MavlinkConnection

class Main:
    def __init__(self):
        self.mavlink_connection: MavlinkConnection = MavlinkConnection()
        self.video_handler: VideoCaptureHandler = VideoCaptureHandler()
        self.tracker: ObjectTracker = ObjectTracker()
        self.ui: UserInterface = UserInterface()
        self.scale = self.video_handler.scale

    def run(self):
        self.mavlink_connection.connect()

        if not self.mavlink_connection.is_connected():
            print("Unable to connect to flight controller.")
            return

        while True:
            frame = self.video_handler.read_frame()
            if frame is None:
                break

            frame_resized = self.video_handler.resize_frame(frame)

            if self.tracker.roi_selected:
                bbox_coords = self.tracker.update(frame_resized, self.scale)
                if bbox_coords:
                    cv2.rectangle(frame, bbox_coords[0], bbox_coords[1], (0, 255, 0), 2, 1)
                if self.tracker.object_lost:
                    if self.ui.object_lost_time == 0:
                        self.ui.object_lost_time = time.time()
                    self.ui.handle_blinking(frame, self.tracker.object_lost)
                else:
                    self.ui.object_lost_time = 0

            select_button, cancel_button = self.ui.draw_buttons(frame)

            cv2.imshow('Tracking', frame)
            cv2.setMouseCallback('Tracking', self.ui.mouse_callback, param=(select_button, cancel_button))

            if self.ui.button_select_pressed and not self.tracker.roi_selected:
                roi_frame = frame_resized.copy()
                threading.Thread(target=self.tracker.select_roi, args=(roi_frame,)).start()
                self.ui.button_select_pressed = False

            if self.ui.button_cancel_pressed:
                self.tracker.reset_tracker()
                self.ui.button_cancel_pressed = False

            key = cv2.waitKey(self.ui.slow_motion_delay) & 0xFF
            if key == 27:
                break

        self.video_handler.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main_app = Main()
    main_app.run()