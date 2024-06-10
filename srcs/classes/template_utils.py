import cv2

def cvt_to_binary(img_array):
    img_array = cv2.Canny(img_array, 100, 200)
    img_array = cv2.GaussianBlur(img_array, (11, 11), 0)
    #img_array = cv2.equalizeHist(img_array)
    return img_array