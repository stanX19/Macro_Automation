import cv2
import numpy as np
from PIL import Image
from PIL.PngImagePlugin import PngImageFile
from logger import logger


def find_overlap_y(top_arr: np.ndarray, bot_arr: np.ndarray, min_overlap_height: int,
                   threshold: float) -> int:
    """
    :param top_arr: np array of top image
    :param bot_arr: np array of bot image
    :param min_overlap_height: minimum height required to count as an overlap
    :param threshold: minimum match ratio required to count as an overlap
    :return: y value from top to bot of top_arr, -1 means no match
    """
    # constants
    top_n = len(top_arr)
    bot_n = len(bot_arr)

    # preprocess
    top_arr = top_arr.astype(int)
    bot_arr = bot_arr.astype(int)

    max_match = 0.0
    ret_y = -1
    top_min_y = max(0, top_n - bot_n)
    top_max_y = max(0, top_n - min_overlap_height + 1)

    # iter through height
    for top_y in range(top_min_y, top_max_y):
        height = top_n - top_y
        top_slice = top_arr[top_y: top_n]
        bot_slice = bot_arr[:height]
        cur_match = 1 - np.sum(np.abs(top_slice - bot_slice)) / top_slice.size / 255
        if cur_match > max_match:
            max_match = cur_match
            ret_y = top_y
    #     print("\r{:4}: {:.2f}%        max={:.2f}% idx: {}".format(
    #         top_y,
    #         cur_match * 100,
    #         max_match * 100,
    #         ret_y
    #     ), end='')
    #
    # print()
    logger.debug("max={:.2f}% idx: {}".format(
        max_match * 100,
        ret_y
    ))
    if max_match >= threshold:
        return ret_y

    return -1


def array_catv(top_arr: np.ndarray, bot_arr: np.ndarray, min_overlap_height=100, threshold=0.9) -> np.ndarray:
    """
    concatenate arrays vertically, removing overlapping portions if exist
    :param top_arr: 3d np array, (height, width, pixels)
    :param bot_arr: 3d np array, (height, width, pixels)
    :param min_overlap_height: minimum height required to count as an overlap
    :param threshold: minimum match ratio required to count as an overlap
    :except RuntimeError: images does not overlap
    :return:
    """
    # width check for debugging
    # for top_y in range(len(top_arr)):
    #     for idx in range(min(len(top_arr) - top_y, len(bot_arr))):
    #         if len(top_arr[top_y + idx]) != len(bot_arr[idx]):
    #             raise ValueError("Images have different width")
    # if top_arr.ndim < 3 or top_arr.ndim != bot_arr.ndim:
    #     raise ValueError("Expected arrays of same dimensions and ndim > 2")

    y = find_overlap_y(top_arr, bot_arr, min_overlap_height, threshold)
    if y >= 0:  # has overlap
        return np.vstack((top_arr[:y], bot_arr))
    else:  # no overlap
        raise RuntimeError("No overlap")  # return np.vstack((top_arr, bot_arr))


def image_catv(top_img: PngImageFile, bot_img: PngImageFile):
    """
    concatenate images vertically, removing overlapping portions if exist
    :param top_img: top portion of image
    :param bot_img: bot portion of image
    :except ValueError: images have different width
    :except RuntimeError: images does not overlap
    :return:
    """
    # Find the overlapping region
    top_arr = np.array(top_img)
    bot_arr = np.array(bot_img)
    concatenated_array = array_catv(top_arr, bot_arr)

    return Image.fromarray(concatenated_array)


# Example usage
def main():
    top_img_path = "images/img_1.png"
    bot_img_path = "images/img_2.png"
    top_img = Image.open(top_img_path)
    bot_img = Image.open(bot_img_path)

    # test
    top_arr = np.array(top_img)
    bot_arr = np.array(bot_img)
    y = find_overlap_y(top_arr, bot_arr, 100, 0.9)
    assert y == 345
    # end of test

    print("started")
    concatenated_image = image_catv(top_img, bot_img)
    concatenated_image.show()


if __name__ == '__main__':
    main()

