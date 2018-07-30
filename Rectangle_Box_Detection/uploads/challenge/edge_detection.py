import os
import sys

import cv2
import numpy as np
import json

def read_image(input_image):
    '''

    :param input_image: get the input image
    :return: return read image
    '''
    original_image = cv2.imread(input_image)
    return original_image


def convert_to_binary(original_image):
    '''
    convert_to_binary function convert the input file into binary file
    :param original_image:
    :return: binary image
    '''
    # convert to gray scale
    gray_image = cv2.cvtColor(original_image, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray_image, (5, 5), 0)

    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, \
                                   cv2.THRESH_BINARY, 5, 3)

    thresh_binary = cv2.bitwise_not(thresh)
    return thresh_binary


def image_preprocessing(binary_image):
    '''
    Image preprocessing function is mainly used to remove noise and remove text from document
    thereby leaving only the horizontal and vertical lines.
    This function uses morphological operations.
    :param binary_image:
    :return: combined image of vertical and horizontal lines
    '''
    # first dilate all horizontal and vertical line
    # to bridge gap if there is any between lines

    hz_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 1))
    dilate_hz_lines = cv2.dilate(binary_image, hz_kernel, iterations=1)

    vert_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 5))
    dilate_vert_lines = cv2.dilate(binary_image, vert_kernel, iterations=1)

    dilate_first_image = cv2.addWeighted(dilate_hz_lines, 0.8, dilate_vert_lines, 0.8, 0)

    # Perform morphological operation to get vertical and horizontal lines
    # First erode and dilation opertion performed

    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (24, 1))
    horizontal_erode = cv2.erode(dilate_first_image, horizontal_kernel, iterations=1)
    horizontal_dilate = cv2.dilate(horizontal_erode, horizontal_kernel, iterations=1)

    horizontal_kernel1 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    horizontal_lines = cv2.erode(horizontal_dilate, horizontal_kernel1, iterations=1)

    # Morphology for vertical Lines
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 24))
    vertical_erode = cv2.erode(dilate_first_image, vertical_kernel, iterations=1)
    vertical_dilate = cv2.dilate(vertical_erode, vertical_kernel, iterations=1)

    vertical_kernel1 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    vertical_lines = cv2.erode(vertical_dilate, vertical_kernel1, iterations=1)

    combined_lines = cv2.addWeighted(horizontal_lines, 0.8, vertical_lines, 0.8, 0)
    return combined_lines


def find_coordinates(combined_lines, original_image,outputfile):
    '''
    find coordinate function takes the preprocessed image which only contains vertical and horizontal
    line. find_contours function helps to detect the shape present in the image. If rectangle is present
    find the coordinates of the rectangle.
    :param combined_lines: image containing vertical and horizontal
    :param original_image: input image
    :param outputfile: output image
    :return: coordinates in the json format
    '''
    boxes = []
    output = {}
    min_height = 15
    min_width = 15
    res, contours, h = cv2.findContours(combined_lines, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for cont in contours:
        approx = cv2.approxPolyDP(cont, 0.03 * cv2.arcLength(cont, True), True)
        rect_points = {}
        if len(approx) == 4:
            x, y, width, height = cv2.boundingRect(cont)
            if (width > min_width and height > min_height):
                coord = []
                rectangle = cv2.minAreaRect(cont)
                box = cv2.boxPoints(rectangle)
                box = np.int0(box)
                cv2.drawContours(original_image, [box], -1, (255, 0, 255), 2)

                extLeft = cont[cont[:, :, 0].argmin()][0]
                extRight = (cont[cont[:, :, 0].argmax()][0])
                extTop = (cont[cont[:, :, 1].argmin()][0])
                extBot = (cont[cont[:, :, 1].argmax()][0])

                coord.extend(([int(extLeft[0]), int(extLeft[1])], [int(extRight[0]), int(extRight[1])],
                              [int(extTop[0]), int(extTop[1])], [int(extBot[0]), int(extBot[1])],
                              [int(extLeft[0]), int(extLeft[1])]))
                rect_points["Points"] = coord
                boxes.append(rect_points)

    output["Boxes"] = boxes
    json_format = json.dumps(output)

    cv2.imwrite(outputfile,original_image)
    print(json_format)
    return json_format


def process_image(input_image):
    '''
    process_image takes input from server and calls other function
    :param input_image: input from server
    :return: None
    '''
    # input_image = input("Enter the name of the image")
    print(input_image)
    outputfilepath = input_image.replace("input","output")
    resized_image=read_image(input_image)
    binary_image=convert_to_binary(resized_image)
    combined_lines=image_preprocessing(binary_image)
    find_coordinates(combined_lines, resized_image,outputfilepath)



if __name__=="__main__":
    filename = os.path.join(os.path.dirname(__file__), 'media')
    print(filename)
    process_image(filename+"/1099_input.jpg")
