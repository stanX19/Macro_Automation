import cv2
import numpy as np
import win32api


class ImageSelector:
    def __init__(self, image_dict, message="Select Image",
                 max_width=700, max_height=win32api.GetSystemMetrics(1) - 100):
        self.message = message
        self.image_dict = image_dict
        self.padding = 5
        self.max_width = max_width

        self._image_width = 0
        self._canvas_height = 0
        self._canvas = self.concatenate_images()
        self._selected_image_key = None
        self._clicked_cord = None
        self._scroll_y = 0
        self._displayed_height = max_height

    def concatenate_images(self):
        max_width = self.max_width
        images = []
        for key, image_path in self.image_dict.items():
            img = cv2.imread(image_path)
            if img is not None:
                # Calculate the new height while maintaining the aspect ratio
                images.append(img)
                # Update the maximum width and total height
                max_width = min(max_width, img.shape[1])
            else:
                raise Warning(f"cv2 failed to read {image_path}")

        new_heights = [i.shape[0] * (max_width / i.shape[1]) for i in images]
        total_height = int(sum(new_heights) + self.padding * len(new_heights))

        canvas = np.zeros((total_height, max_width, 3), dtype=np.uint8)

        y_position = 0
        for idx, img in enumerate(images):
            # Calculate the new height while maintaining the aspect ratio
            new_height = new_heights[idx]

            # Resize the image to fit within the maximum width
            img = cv2.resize(img, (max_width, int(new_height)))

            # Update the canvas and y position
            canvas[y_position:y_position + img.shape[0], 0:img.shape[1]] = img
            y_position += img.shape[0] + self.padding

        self._image_width = max_width
        self._canvas_height = total_height

        return canvas

    def on_mouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self._clicked_cord = (x, y + self._scroll_y)

        if event == cv2.EVENT_LBUTTONUP:
            if self._clicked_cord != (x, y + self._scroll_y):
                return

            index = (y + self._scroll_y) // (self._canvas_height // len(self.image_dict))

            if 0 <= index < len(self.image_dict):
                self._selected_image_key = list(self.image_dict.keys())[index]

        if event == cv2.EVENT_MOUSEWHEEL:
            delta = flags
            if delta > 0:
                self._scroll_y -= 50  # Scroll up
            else:
                self._scroll_y += 50  # Scroll down

            # Ensure scroll_y stays within valid bounds
            self._scroll_y = max(0, min(self._scroll_y, self._canvas_height - self._displayed_height))

    def select_image_key(self):
        window_name = self.message
        cv2.namedWindow(window_name)
        cv2.setMouseCallback(window_name, self.on_mouse)
        cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)

        self._scroll_y = 0
        while cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) > 0:
            # crop canvas copy
            displayed = self._canvas.copy()[self._scroll_y:self._scroll_y + self._displayed_height, :]
            cv2.imshow(window_name, displayed)
            cv2.waitKey(1)

            if self._selected_image_key is not None:
                break

        cv2.destroyAllWindows()
        ret = self._selected_image_key
        self._selected_image_key = None
        return ret


if __name__ == "__main__":
    import Paths
    domain_types = Paths.assets_path_dict["hsr"]["templates"]["navigation"]["domain_types"]

    selector = ImageSelector(domain_types)
    domain_type = selector.select_image_key()
    selector = ImageSelector(Paths.assets_path_dict["hsr"]["templates"]["navigation"][domain_type])
    print(selector.select_image_key())
