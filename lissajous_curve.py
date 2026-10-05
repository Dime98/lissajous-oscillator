import cv2
import numpy as np


def sine_movement(amplitude, phase, t):
    return amplitude * (1 - np.cos(2 * np.pi * phase)) / 2


def triangle_movement(amplitude, phase, t):
    phase = phase % 1.0
    return amplitude * (1.0 - abs(2.0 * phase - 1.0))


def drawing_overlay(canvas, x, y, circle_radius, blur_kernel, alpha, debug):
    cv2.circle(canvas, (y, x), circle_radius, [225, 225, 225], thickness=-1)
    cv2.circle(canvas, (y, x), int(circle_radius * 2.5), [225, 225, 225], thickness=1)

    temp = np.copy(canvas)
    if blur_kernel > 1:
        temp = cv2.GaussianBlur(temp, (blur_kernel, blur_kernel), 0)

    # debug xy position on 0th col and row
    if debug:
        cv2.circle(temp, (circle_radius, x), circle_radius, [0, 225, 0], thickness=1)
        cv2.circle(temp, (y, circle_radius), circle_radius, [0, 225, 0], thickness=1)

    cv2.addWeighted(canvas, alpha, temp, 0, 0, dst=canvas)

    canvas[canvas < 5] = 0
    return temp


def main():
    canvas_size = 600
    canvas = np.zeros((canvas_size, canvas_size, 3), dtype=np.uint8)

    # simulation parameters
    t = 0
    frequency = 0.005
    amplitude = canvas_size - 1

    # sliders
    window_name = "lissajous_curve"
    cv2.namedWindow(window_name)

    frequency_slider_factor = 1_000
    cv2.createTrackbar("frequency", window_name, 0, 50, lambda _: None)
    cv2.setTrackbarPos("frequency", window_name, int(frequency * frequency_slider_factor))
    cv2.setTrackbarMin("frequency", window_name, 1)

    cv2.createTrackbar("time", window_name, 1, 50, lambda _: None)
    cv2.setTrackbarMin("time", window_name, 1)

    cv2.createTrackbar("blur_kernel", window_name, 3, 20, lambda _: None)

    cv2.createTrackbar("trail", window_name, 95, 100, lambda _: None)
    cv2.setTrackbarMin("trail", window_name, 1)

    cv2.createTrackbar("ratio_x", window_name, 3, 20, lambda _: None)
    cv2.setTrackbarMin("ratio_x", window_name, 1)
    cv2.createTrackbar("ratio_y", window_name, 2, 20, lambda _: None)
    cv2.setTrackbarMin("ratio_y", window_name, 1)

    # display parameters
    circle_radius = int(canvas_size * 0.01)
    debug = False  # circle at 0th column and row

    while True:
        t += cv2.getTrackbarPos("time", window_name)
        # t += 1

        frequency = cv2.getTrackbarPos("frequency", window_name) / frequency_slider_factor
        phase = frequency * t

        # sine_movement
        # triangle_movement
        ratio_x = cv2.getTrackbarPos("ratio_x", window_name)
        ratio_y = cv2.getTrackbarPos("ratio_y", window_name)
        x = sine_movement(amplitude=amplitude, phase=phase * ratio_x, t=t)
        y = sine_movement(amplitude=amplitude, phase=phase * ratio_y, t=t)

        x = int(x)
        y = int(y)

        blur_kernel = cv2.getTrackbarPos("blur_kernel", window_name)
        blur_kernel = blur_kernel + 1 - blur_kernel % 2  # force kernel to be odd number
        alpha = cv2.getTrackbarPos("trail", window_name) / 100

        cv2.imshow("lissajous_curve", temp)
        key = cv2.waitKey(10)
        if key in [ord("q"), 27]:
            break
        if key == ord("r"):
            canvas = np.zeros((canvas_size, canvas_size, 3), dtype=np.uint8)
        if key == ord("d"):
            debug = not debug


if __name__ == "__main__":
    main()
