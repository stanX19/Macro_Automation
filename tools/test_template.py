import cv2
from template import Template, cvt_to_binary


def test(template_path, img_path):
    # Load the image and the template
    image = cv2.imread(img_path)[540:,:]

    template = Template(template_path, crop=(20, 60, 200, 90), threshold=1.0, binary=True)

    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    template.threshold += 0.01
    location = None
    while location is None and template.threshold >= 0.0:
        template.threshold -= 0.01
        location = template.get_location_in(image_gray)

    print(location)
    print(template.threshold)

    if template._matcher.binary_preprocess:
        image = cvt_to_binary(image_gray)
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    pt = (location[0], location[1], location[2] - location[0], location[3] - location[1])
    cv2.rectangle(image, pt, (0, 255, 0), 10)
    # Display the result image with rectangles in the ROI
    cv2.imshow('Matching Result', cv2.resize(image, (960, 540)))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return template.threshold


def main():
    imgs = [
        r'C:\Users\DELL\PycharmProjects\pythonProject\Macro_Automation\assets\test\screenshot\img_23.png',
        r'C:\Users\DELL\PycharmProjects\pythonProject\Macro_Automation\assets\test\screenshot\img_25.png',
        r'C:\Users\DELL\PycharmProjects\pythonProject\Macro_Automation\assets\test\screenshot\img_29.png',
    ]
    temps = [
        r"C:\Users\DELL\PycharmProjects\pythonProject\Macro_Automation\assets\hsr\templates\navigation\domain_types\calyx_gold.png",
    ]
    # imgs = [
    #     r'C:\Users\DELL\PycharmProjects\pythonProject\Macro_Automation\assets\test\screenshot\img_31.png',
    # ]
    # temps = [
    #     r"C:\Users\DELL\PycharmProjects\pythonProject\Macro_Automation\assets\hsr\templates\navigation\teleport.png"
    # ]
    results = []
    print("started")
    for tmp in temps:
        for img in imgs:
            results.append(test(tmp, img))

    if results[0] < results[1] and results[0] < results[2]:
        print("OK!")
    else:
        print("KO!")


if __name__ == '__main__':
    main()
