import cv2

def cvt_to_binary(img_array):
    # img_array = cv2.equalizeHist(img_array)
    img_array = cv2.Canny(img_array, 50, 150)
    img_array = cv2.GaussianBlur(img_array, (11, 11), 0)
    return img_array