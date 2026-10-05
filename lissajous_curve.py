import cv2
import numpy as np


def sine_movement(amplitude, phase, t):
    return amplitude * (1 - np.cos(2 * np.pi * phase)) / 2


def triangle_movement(amplitude, phase, t):
    phase = phase % 1.0
    return amplitude * (1.0 - abs(2.0 * phase - 1.0))


def drawing_overlay(canvas, coordinates, circle_radius, blur_kernel, alpha, debug):
    color = [225, 225, 225]
    if debug:
        color = [225, 225, 225] if len(coordinates) < 2 else [0, 0, 255]

    for co in coordinates:
        x, y = co.astype(np.uint16)
        cv2.circle(canvas, (y, x), circle_radius, color, thickness=-1)
        cv2.circle(canvas, (y, x), int(circle_radius * 2.5), color, thickness=1)

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


def linear_sub_steps(current_coordinate, last_coordinate, distance_threshold):
    distance = np.linalg.norm(current_coordinate - last_coordinate)
    if distance < distance_threshold:
        return current_coordinate[np.newaxis, :]
    steps = int(np.ceil(distance // distance_threshold) + 1)
    substep_coordinates = np.linspace(last_coordinate, current_coordinate, steps)
    return substep_coordinates[1:]


def sub_steps(
        current_coordinate,
        t,
        phase,
        last_coordinate,
        last_t,
        last_phase,
        distance_threshold,
        amplitude,
        ratio_x,
        ratio_y,
):
    distance = np.linalg.norm(current_coordinate - last_coordinate)
    if distance < distance_threshold:
        return current_coordinate[np.newaxis, :]
    steps = int(np.ceil(distance // distance_threshold) + 2)

    substep_coordinates = []
    for p in np.linspace(last_phase, phase, steps)[:-1]:
        x = sine_movement(amplitude=amplitude, phase=p * ratio_x, t=t)
        y = sine_movement(amplitude=amplitude, phase=p * ratio_y, t=t)
        substep_coordinates.append(np.array([x, y]))
    return substep_coordinates


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
    debug = False  # circle at 0th column and row

    last_coordinate = None
    last_t = None
    last_phase = None

    while True:
        dt += cv2.getTrackbarPos("time", window_name) / 10

        # sine_movement
        # triangle_movement
        ratio_x = cv2.getTrackbarPos("ratio_x", window_name)
        ratio_y = cv2.getTrackbarPos("ratio_y", window_name)
        x = sine_movement(amplitude=amplitude, phase=phase * ratio_x, t=t)
        y = sine_movement(amplitude=amplitude, phase=phase * ratio_y, t=t)
        current_coordinate = np.array([x, y])

        coordinates_to_display = np.copy([current_coordinate])

        use_substeps = cv2.getTrackbarPos("substeps", window_name)
        if use_substeps and last_coordinate is not None:
            substep_coordinates = sub_steps(
                current_coordinate=current_coordinate,
                t=t,
                phase=phase,
                last_coordinate=last_coordinate,
                last_t=last_t,
                last_phase=last_phase,
                distance_threshold=circle_radius,
                amplitude=amplitude,
                ratio_x=ratio_x,
                ratio_y=ratio_y,
            )
            coordinates_to_display = substep_coordinates

            last_t=dt,

        blur_kernel = cv2.getTrackbarPos("blur_kernel", window_name)
        blur_kernel = blur_kernel + 1 - blur_kernel % 2  # force kernel to be odd number
        alpha = cv2.getTrackbarPos("trail", window_name) / 100
        temp = drawing_overlay(
            canvas=canvas,
            coordinates=coordinates_to_display,
            circle_radius=circle_radius,
            blur_kernel=blur_kernel,
            alpha=alpha,
            debug=debug,
        )

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
