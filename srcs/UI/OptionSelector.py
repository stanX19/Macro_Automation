from typing import Union

import cv2
import numpy as np
import win32api


class OptionSelector:
    def __init__(self, options: Union[list[str], dict[str, bool]], message="Select Option", font_color=(255, 255, 255),
                 background_color=(0, 0, 0), outline_color=(255, 255, 255)):
        self.message = message
        self.options = options
        self.padding = 30
        self.outline = 5
        self.font_color = font_color
        self.background_color = background_color
        self.outline_color = outline_color

        self._canvas_height = 0
        self._default_selected_options = list(options.values()) if isinstance(options, dict) else [0] * len(options)
        self._selected_options = self._default_selected_options
        self._clicked_cord = None
        self._scroll_y = 0
        self._displayed_height = win32api.GetSystemMetrics(1) - 100
        self._box_cords = []
        self._box_size = 0
        self._confirm_cord = []
        self._confirmed = False

        self._canvas = self.create_canvas()

    def create_canvas(self):
        fontThickness = 2
        scale = 0.5
        max_width = int(700 / scale)
        total_height = self.outline
        text_heights = []
        baselines = []

        for option in self.options:
            # Calculate the text size to get the actual text height
            (text_width, text_height), baseline = cv2.getTextSize(option, cv2.FONT_HERSHEY_SIMPLEX, 1, fontThickness)
            total_height += max(text_height + baseline, 25) + 2 * self.padding + self.outline
            text_heights.append(text_height + baseline)
            baselines.append(baseline)

        options_height = total_height
        total_height += sorted(text_heights)[0] + 1 * self.padding
        canvas = np.zeros((total_height, max_width, 3), dtype=np.uint8)
        canvas[:, :, :] = self.background_color  # Fill the canvas

        # top, left, right outlines
        canvas[0: self.outline, :, :] = self.outline_color
        canvas[0:options_height, 0: self.outline, :] = self.outline_color
        canvas[0:options_height, -self.outline:-1, :] = self.outline_color

        cum_y = self.outline
        # change tick box size here
        box_padding = int(self.padding * 0.25)
        self._box_size = sorted(text_heights)[0] + 2 * (self.padding - box_padding)
        for idx, option in enumerate(self.options):
            text_position_x = self.padding + self.outline
            text_position_y = cum_y + self.padding + text_heights[idx] - baselines[idx]

            # Fill the outline area with white color
            upper = cum_y + text_heights[idx] + self.padding * 2
            lower = upper + self.outline
            canvas[upper: lower, :, :] = self.outline_color

            cv2.putText(canvas, option, (text_position_x, text_position_y), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        self.font_color, fontThickness)

            # Add a checkbox on the right
            checkbox_x = max_width - (self._box_size + box_padding)
            checkbox_y = cum_y + box_padding
            self._box_cords.append((checkbox_x, checkbox_y))

            cum_y += max(text_heights[idx] + self.padding, 25) + self.padding + self.outline

        # create a confirmation box
        text = "Confirm"
        (text_width, text_height), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, fontThickness)
        text_x = max_width - self.padding - text_width
        text_y = cum_y + self.padding + text_height - baseline
        confirm_width = text_width + 2 * self.padding
        confirm_height = text_height + 2 * self.padding
        confirm_x = text_x - self.padding
        confirm_y = cum_y
        canvas[confirm_y:confirm_y+confirm_height, confirm_x:confirm_x+confirm_width, :] = (200, 200, 100)
        cv2.putText(canvas, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    self.font_color, fontThickness)
        self._confirm_cord = (confirm_x, confirm_y, confirm_x + confirm_width, confirm_y + confirm_height)

        canvas = cv2.resize(canvas, (0, 0), fx=scale, fy=scale)
        total_height, total_width, _ = canvas.shape
        self._canvas_height = total_height

        self._box_size = int(self._box_size * scale)
        for idx, (x, y) in enumerate(self._box_cords):
            self._box_cords[idx] = (int(x * scale), int(y * scale))
        self._confirm_cord = [i * scale for i in self._confirm_cord]

        self._canvas = canvas
        self.update_canvas()

        return self._canvas

    def update_canvas(self):
        for idx, (x, y) in enumerate(self._box_cords):
            if self._selected_options[idx]:
                self._canvas[y:y + self._box_size, x:x + self._box_size, :] = (0, 255, 0)
            else:
                self._canvas[y:y + self._box_size, x:x + self._box_size, :] = (255, 255, 255)

    def on_mouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self._clicked_cord = (x, y + self._scroll_y)

        if event == cv2.EVENT_LBUTTONUP:
            if self._clicked_cord != (x, y + self._scroll_y):
                return

            index = -1
            for idx, box_cords in enumerate(self._box_cords):
                xb, yb = box_cords
                if xb <= x <= xb + self._box_size and yb <= y <= yb + self._box_size:
                    index = idx
                    break

            if index >= 0:
                self._selected_options[index] = not self._selected_options[index]

            x1, y1, x2, y2 = self._confirm_cord
            if x1 <= x <= x2 and y1 <= y <= y2:
                self._confirmed = True
            self.update_canvas()

        if event == cv2.EVENT_MOUSEWHEEL:
            delta = flags
            if delta > 0:
                self._scroll_y -= 25  # Scroll up
            else:
                self._scroll_y += 25  # Scroll down

            # Ensure scroll_y stays within valid bounds
            self._scroll_y = max(0, min(self._scroll_y, self._canvas_height - self._displayed_height))

    def select_option(self) -> [dict[str, bool], None]:
        window_name = self.message
        cv2.namedWindow(window_name)
        cv2.setMouseCallback(window_name, self.on_mouse)
        cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)

        self._scroll_y = 0
        while cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) > 0:
            # Crop canvas copy
            displayed = self._canvas[self._scroll_y:self._scroll_y + self._displayed_height, :]
            cv2.imshow(window_name, displayed)
            cv2.waitKey(1)
            if self._confirmed:
                break
        else:
            return None

        cv2.destroyAllWindows()
        boolean_list = self._selected_options
        self._selected_options = self._default_selected_options
        return {key: bool(boolean_list[idx]) for idx, key in enumerate(self.options)}


# Example usage:
def main():
    options = ["Option 1", "Option 2", "Option 3", "Option 4"]
    selector = OptionSelector(options, message="Select an Option")
    selected_options = selector.select_option()
    print(f"Selected Option: {selected_options}")


if __name__ == '__main__':
    main()
