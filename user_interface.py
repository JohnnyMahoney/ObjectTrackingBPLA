import cv2
import time
import numpy as np

class UserInterface:
    def __init__(self):
        self.button_select_pressed = False
        self.button_cancel_pressed = False
        self.blink_start_time = 0
        self.blink_visible = True
        self.blink_interval = 0.5
        self.object_lost_time = 0
        self.slow_motion_delay = 10
        self.select_roi_icon = cv2.imread('select_roi_icon.png', cv2.IMREAD_UNCHANGED)
        self.cancel_tracking_icon = cv2.imread('cancel_tracking_icon.png', cv2.IMREAD_UNCHANGED)
        self.crosshair_icon = cv2.imread('crosshair.png', cv2.IMREAD_UNCHANGED)

        if any(icon is None for icon in [self.select_roi_icon, self.cancel_tracking_icon, self.crosshair_icon]):
            raise FileNotFoundError("One or more icon images not found. Make sure 'select_roi_icon.png', 'cancel_tracking_icon.png', and 'crosshair.png' exist.")

    def add_padding_to_icon(self, icon, target_width, target_height):
        icon_height, icon_width = icon.shape[:2]
        scale = min(target_width / icon_width, target_height / icon_height)
        resized_icon = cv2.resize(icon, (int(icon_width * scale), int(icon_height * scale)), interpolation=cv2.INTER_AREA)

        top_padding = (target_height - resized_icon.shape[0]) // 2
        bottom_padding = target_height - resized_icon.shape[0] - top_padding
        left_padding = (target_width - resized_icon.shape[1]) // 2
        right_padding = target_width - resized_icon.shape[1] - left_padding

        padded_icon = np.zeros((target_height, target_width, 4), dtype=np.uint8)
        padded_icon[top_padding:top_padding + resized_icon.shape[0], left_padding:left_padding + resized_icon.shape[1]] = resized_icon

        return padded_icon

    def overlay_icon(self, frame, icon, x, y):
        icon_h, icon_w = icon.shape[:2]
        alpha_icon = icon[:, :, 3] / 255.0
        alpha_frame = 1.0 - alpha_icon

        for c in range(0, 3):
            frame[y:y+icon_h, x:x+icon_w, c] = (alpha_icon * icon[:, :, c] +
                                                alpha_frame * frame[y:y+icon_h, x:x+icon_w, c])

    def draw_buttons(self, frame):
        height, width = frame.shape[:2]
        button_width, button_height = 90, 90

        cancel_button_x, cancel_button_y = 40, height - button_height - 40
        select_button_x, select_button_y = 40, height - 2 * button_height - 60

        select_icon_padded = self.add_padding_to_icon(self.select_roi_icon, button_width, button_height)
        self.overlay_icon(frame, select_icon_padded, select_button_x, select_button_y)

        cancel_icon_padded = self.add_padding_to_icon(self.cancel_tracking_icon, button_width, button_height)
        self.overlay_icon(frame, cancel_icon_padded, cancel_button_x, cancel_button_y)

        crosshair_width, crosshair_height = 40, 40
        middle_x, middle_y = (width - crosshair_width) // 2, (height - crosshair_height) // 2

        crosshair_icon_padded = self.add_padding_to_icon(self.crosshair_icon, crosshair_width, crosshair_height)
        self.overlay_icon(frame, crosshair_icon_padded, middle_x, middle_y)

        return (select_button_x, select_button_y, button_width, button_height), (cancel_button_x, cancel_button_y, button_width, button_height)


    def check_button_click(self, x, y, button_x, button_y, button_width, button_height):
        return button_x <= x <= button_x + button_width and button_y <= y <= button_y + button_height

    def handle_blinking(self, frame, object_lost):
        if object_lost:
            current_time = time.time()
            if current_time - self.object_lost_time < 6:
                if current_time - self.blink_start_time > self.blink_interval:
                    self.blink_start_time = current_time
                    self.blink_visible = not self.blink_visible

                if self.blink_visible:
                    height, width = frame.shape[:2]
                    text = 'LOST OBJECT'
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    font_scale = 1.5
                    font_thickness = 3
                    text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
                    text_x = (width - text_size[0]) // 2
                    text_y = (height // 2) + text_size[1] + 50
                    cv2.putText(frame, text, (text_x, text_y), font, font_scale, (0, 0, 255), font_thickness)

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            select_button, cancel_button = param
            if self.check_button_click(x, y, *select_button):
                self.button_select_pressed = True
            if self.check_button_click(x, y, *cancel_button):
                self.button_cancel_pressed = True