import numpy as np
from PIL import Image
from PIL.PngImagePlugin import PngImageFile


def find_overlap_y(top_arr: np.ndarray, bot_arr: np.ndarray, min_overlap_height=100):
    """
    :param top_arr: np array of top image
    :param bot_arr: np array of bot image
    :param min_overlap_height: minimum height required to count as an overlap
    :return: y value from top to bot of top_arr, -1 means no match
    """
    # iter through height
    top_max_y = len(top_arr) - min_overlap_height + 1
    for top_y in range(top_max_y):
        height = min(top_max_y - top_y, len(bot_arr))
        top_slice = top_arr[top_y: top_y + height]
        bot_slice = bot_arr[:height]
        if np.array_equal(top_slice, bot_slice):
            return top_y
    return -1


def image_catv(top_img: PngImageFile, bot_img: PngImageFile):
    """
    concatenate images vertically, removing overlapping portions if exist
    :param top_img:
    :param bot_img:
    :except ValueError: images have different width
    :return:
    """
    # Find the overlapping region
    top_arr = np.array(top_img)
    bot_arr = np.array(bot_img)

    # width check
    for top_y in range(len(top_arr)):
        for idx in range(min(len(top_arr) - top_y, len(bot_arr))):
            if len(top_arr[top_y + idx]) != len(bot_arr[idx]):
                raise ValueError("Images have different width")

    y = find_overlap_y(top_arr, bot_arr)
    if y >= 0:  # has overlap
        concatenated_image = np.vstack((top_arr[:y], bot_arr))
    else:  # no overlap
        concatenated_image = np.vstack((top_arr, bot_arr))
    return Image.fromarray(concatenated_image)


# Example usage
def main():
    top_img_path = "images/img_1.png"
    bot_img_path = "images/img_2.png"
    top_img = Image.open(top_img_path)
    bot_img = Image.open(bot_img_path)

    # test
    top_arr = np.array(top_img)
    bot_arr = np.array(bot_img)
    y = find_overlap_y(top_arr, bot_arr)
    assert y == 345
    # end of test

    concatenated_image = image_catv(top_img, bot_img)
    concatenated_image.show()


if __name__ == '__main__':
    main()

