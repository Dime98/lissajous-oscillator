import cv2
import numpy as np


class LissajousOscillator:
    def __init__(self, frequency, amplitude, distance_threshold):
        self.frequency = frequency
        self.amplitude = amplitude

        self.phase = 0
        self.current_coordinate = None
        self.last_coordinate = None
        self.last_phase = None

        self.points = None  # coordinates for display
        self.distance_threshold = distance_threshold

    def triangle_movement(self, phase):
        phase = phase % 1.0
        return self.amplitude * (1.0 - abs(2.0 * phase - 1.0))

    def sine_movement(self, phase):
        return self.amplitude * (1 - np.cos(2 * np.pi * phase)) / 2

    def compute_point(self, dt, ratio_x, ratio_y):
        self.phase = self.frequency * dt

        phases = np.asarray([self.phase * ratio_x, self.phase * ratio_y])
        x, y = self.sine_movement(phases)
        self.current_coordinate = np.array([x, y])

        return self.current_coordinate[np.newaxis, :]

    def update_parameters(self, dt):
        self.last_coordinate = np.copy(self.current_coordinate)
        self.last_phase = self.phase

    def linear_sub_steps(self):
        if self.last_coordinate is None:
            return self.current_coordinate[np.newaxis, :]

        distance = np.linalg.norm(self.current_coordinate - self.last_coordinate)
        if distance < self.distance_threshold:
            return self.current_coordinate[np.newaxis, :]

        steps = int((distance // self.distance_threshold) + 1)
        substep_coordinates = np.linspace(self.last_coordinate, self.current_coordinate, steps)
        return substep_coordinates[1:]

    def sub_steps(self, ratio_x, ratio_y):
        if self.last_coordinate is None:
            return self.current_coordinate[np.newaxis, :]

        distance = np.linalg.norm(self.current_coordinate - self.last_coordinate)
        if distance < self.distance_threshold:
            return self.current_coordinate[np.newaxis, :]

        steps = int((distance // self.distance_threshold) + 1)
        phases = np.linspace(self.last_phase, self.phase, steps)[:, np.newaxis] * np.array([ratio_x, ratio_y])
        return self.sine_movement(phases)


class Display:
    def __init__(self, window_name, canvas_size, circle_radius):
        self.window_name = window_name
        cv2.namedWindow(window_name)

        self.circle_radius = circle_radius
        self.canvas_size = canvas_size
        self.canvas = self.create_canvas()

        self.debug = False
        self.debug_line_size = self.circle_radius // 2

        self.create_sliders()

    def create_canvas(self):
        return np.zeros((self.canvas_size, self.canvas_size, 3), dtype=np.float32)

    def on_circle(self, value):
        self.circle_radius = int(np.log(value * 10) // 1)

    def create_sliders(self):
        cv2.createTrackbar("time", self.window_name, 10, 200, lambda _: None)
        cv2.setTrackbarMin("time", self.window_name, 1)

        cv2.createTrackbar("blur_kernel", self.window_name, 1, 20, lambda _: None)

        cv2.createTrackbar("circle", self.window_name, 10, 100, self.on_circle)
        cv2.setTrackbarMin("circle", self.window_name, 1)

        cv2.createTrackbar("trail", self.window_name, 95, 100, lambda _: None)
        cv2.setTrackbarMin("trail", self.window_name, 1)

        cv2.createTrackbar("substeps", self.window_name, 0, 1, lambda _: None)

        cv2.createTrackbar("ratio_x", self.window_name, 3, 70, lambda _: None)
        cv2.setTrackbarMin("ratio_x", self.window_name, 1)
        cv2.createTrackbar("ratio_y", self.window_name, 2, 70, lambda _: None)
        cv2.setTrackbarMin("ratio_y", self.window_name, 1)

    def get_slider_value(self, name):
        return cv2.getTrackbarPos(name, self.window_name)

    def drawing_overlay(self, coordinates, blur_kernel, alpha):
        color = np.asarray([1, 1, 1])

        # different color for sub-stepped coordinates
        if self.debug:
            color = np.asarray([1, 1, 1]) if len(coordinates) < 2 else np.asarray([0, 0, 1])

        for co in coordinates:
            x, y = co.astype(np.uint16)
            cv2.circle(self.canvas, (y, x), self.circle_radius, (color / 2).tolist(), thickness=-1)
            cv2.circle(self.canvas, (y, x), int(self.circle_radius * 2.5), color.tolist(), thickness=1)

        temp = np.copy(self.canvas)
        if blur_kernel > 1:
            temp = cv2.GaussianBlur(temp, (blur_kernel, blur_kernel), 0)

        if self.debug:
            x, y = coordinates[-1].astype(np.int16)
            temp[x - self.debug_line_size : x + self.debug_line_size] = [0, 0.5, 0]
            temp[:, y - self.debug_line_size : y + self.debug_line_size] = [0, 0.5, 0]
            cv2.circle(temp, (self.circle_radius, x), self.circle_radius, [0, 1, 0], thickness=2)
            cv2.circle(temp, (y, self.circle_radius), self.circle_radius, [0, 1, 0], thickness=2)

        cv2.addWeighted(self.canvas, alpha, temp, 0, 0, dst=self.canvas)

        return temp

    def reset_canvas(self):
        self.canvas = self.create_canvas()


def main():
    canvas_size = 600

    # simulation parameters
    dt = 0
    frequency = 0.005
    amplitude = canvas_size - 1

    # display parameters
    circle_radius = int(canvas_size * 0.01)

    display = Display("lissajous_curve", canvas_size=canvas_size, circle_radius=circle_radius)
    lissajous_curve = LissajousOscillator(frequency=frequency, amplitude=amplitude, distance_threshold=circle_radius)

    while True:
        dt += display.get_slider_value("time") / 10

        ratio_x = display.get_slider_value("ratio_x")
        ratio_y = display.get_slider_value("ratio_y")

        lissajous_curve.points = lissajous_curve.compute_point(dt=dt, ratio_x=ratio_x, ratio_y=ratio_y)

        use_substeps = display.get_slider_value("substeps")
        if use_substeps:
            lissajous_curve.points = lissajous_curve.sub_steps(ratio_x=ratio_x, ratio_y=ratio_y)

        lissajous_curve.update_parameters(dt=dt)

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
