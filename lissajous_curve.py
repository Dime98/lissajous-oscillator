import cv2
import numpy as np


def sine_movement(amplitude, phase, t):
    return amplitude * (1 - np.cos(2 * np.pi * phase)) / 2


def triangle_movement(amplitude, phase, t):
    phase = phase % 1.0
    return amplitude * (1.0 - abs(2.0 * phase - 1.0))

class Display:
    def __init__(self, window_name, canvas_size, circle_radius):
        self.window_name = window_name
        cv2.namedWindow(window_name)

        self.circle_radius = circle_radius
        self.canvas_size = canvas_size
        self.canvas = np.zeros((canvas_size, canvas_size, 3), dtype=np.uint8)

        self.debug = False
        self.debug_line_size = self.circle_radius // 2

        self.create_sliders()

    def create_sliders(self):
        cv2.createTrackbar("time", self.window_name, 10, 500, lambda _: None)
        cv2.setTrackbarMin("time", self.window_name, 1)

        cv2.createTrackbar("blur_kernel", self.window_name, 3, 20, lambda _: None)

        cv2.createTrackbar("trail", self.window_name, 95, 100, lambda _: None)
        cv2.setTrackbarMin("trail", self.window_name, 1)

        cv2.createTrackbar("substeps", self.window_name, 1, 1, lambda _: None)

        cv2.createTrackbar("ratio_x", self.window_name, 3, 20, lambda _: None)
        cv2.setTrackbarMin("ratio_x", self.window_name, 1)
        cv2.createTrackbar("ratio_y", self.window_name, 2, 20, lambda _: None)
        cv2.setTrackbarMin("ratio_y", self.window_name, 1)

    def get_slider_value(self, name):
        return cv2.getTrackbarPos(name, self.window_name)

    def drawing_overlay(self, coordinates, blur_kernel, alpha):
        color = [225, 225, 225]

        # different color for sub-stepped coordinates
        if self.debug:
            color = [225, 225, 225] if len(coordinates) < 2 else [0, 0, 255]

        for co in coordinates:
            x, y = co.astype(np.uint16)
            cv2.circle(self.canvas, (y, x), self.circle_radius, color, thickness=-1)
            cv2.circle(self.canvas, (y, x), int(self.circle_radius * 2.5), color, thickness=1)

        temp = np.copy(self.canvas)
        if blur_kernel > 1:
            temp = cv2.GaussianBlur(temp, (blur_kernel, blur_kernel), 0)

        if self.debug:
            x, y = coordinates[-1].astype(np.int16)
            temp[x - self.debug_line_size : x + self.debug_line_size] = [0, 50, 0]
            temp[:, y - self.debug_line_size : y + self.debug_line_size] = [0, 50, 0]
            cv2.circle(temp, (self.circle_radius, x), self.circle_radius, [0, 225, 0], thickness=1)
            cv2.circle(temp, (y, self.circle_radius), self.circle_radius, [0, 225, 0], thickness=1)

        cv2.addWeighted(self.canvas, alpha, temp, 0, 0, dst=self.canvas)

        return temp

    def reset_canvas(self):
        self.canvas = np.zeros((self.canvas_size, self.canvas_size, 3), dtype=np.uint8)


def main():
    canvas_size = 600
    canvas = np.zeros((canvas_size, canvas_size, 3), dtype=np.uint8)

    # simulation parameters
    dt = 0
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

    cv2.createTrackbar("substeps", window_name, 1, 1, lambda _: None)

    cv2.createTrackbar("ratio_x", window_name, 3, 20, lambda _: None)
    cv2.setTrackbarMin("ratio_x", window_name, 1)
    cv2.createTrackbar("ratio_y", window_name, 2, 20, lambda _: None)
    cv2.setTrackbarMin("ratio_y", window_name, 1)

    # display parameters
    circle_radius = int(canvas_size * 0.01)

    display = Display("lissajous_curve", canvas_size=canvas_size, circle_radius=circle_radius)

    last_coordinate = None
    last_t = None
    last_phase = None

    while True:
        dt += display.get_slider_value("time") / 10

        ratio_x = display.get_slider_value("ratio_x")
        ratio_y = display.get_slider_value("ratio_y")

        blur_kernel = display.get_slider_value("blur_kernel")
        blur_kernel = blur_kernel + 1 - blur_kernel % 2  # force kernel to be odd number
        temp = display.drawing_overlay(
            coordinates=lissajous_curve.points,
            blur_kernel=blur_kernel,
            alpha=display.get_slider_value("trail") / 100,
        )

        cv2.imshow("lissajous_curve", temp)
        key = cv2.waitKey(10)
        if key in [ord("q"), 27]:
            break
        if key == ord("r"):
            display.reset_canvas()
        if key == ord("d"):
            display.debug = not display.debug


if __name__ == "__main__":
    main()
