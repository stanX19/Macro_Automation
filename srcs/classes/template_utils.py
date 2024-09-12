from typing import Callable, Any

import cv2
import numpy as np
import functools


def cvt_to_binary(img_array: np.ndarray) -> np.ndarray:
    # img_array = cv2.equalizeHist(img_array)
    img_array = cv2.Canny(img_array, 50, 150)
    img_array = cv2.GaussianBlur(img_array, (11, 11), 0)
    return img_array


def use_cached_result_for_same_array(func: Callable[[Any, np.ndarray], Any]):
    """
    A method-specific cache decorator that caches the result based on the byte representation of an array.
    It stores only one cached result at a time.
    """

    HASH_NAME = f"__{func.__name__}__array_cache_hash"
    RESULT_NAME = f"__{func.__name__}__array_cache_result"

    @functools.wraps(func)
    def wrapper(self, img_gray: np.ndarray):
        img_hash = img_gray.tobytes()

        if getattr(self, HASH_NAME, None) == img_hash:
            return getattr(self, RESULT_NAME)

        result = func(self, img_gray)
        setattr(self, HASH_NAME, img_hash)
        setattr(self, RESULT_NAME, result)

        return result

    return wrapper

