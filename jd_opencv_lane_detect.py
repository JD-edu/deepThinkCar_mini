import cv2
import numpy as np
import logging
import math
import datetime
import sys

show_image = False

# Black tape detector tuning for the 320x240 Pi camera image.  Ratios are
# used for geometry/area checks so the detector still behaves sensibly if a
# different resolution is delivered.
BLACK_VALUE_MAX = 110
ROI_TOP_RATIO = 0.5
MIN_COMPONENT_AREA_RATIO = 0.005
MAX_COMPONENT_AREA_RATIO = 0.14
MIN_COMPONENT_ELONGATION = 1.7
MIN_COMPONENT_THICKNESS_RATIO = 0.0125
MIN_VERTICAL_DIRECTION = 0.22
MIN_COMPONENT_BOTTOM_RATIO = 0.75
MIN_LANE_SEPARATION_RATIO = 0.12
EXPECTED_HALF_LANE_WIDTH_RATIO = 0.19


class JdOpencvLaneDetect(object):
    def __init__(self):
        self.curr_steering_angle = 90

    def get_lane(self, frame):
        show_image("orignal", frame)
        lane_lines, frame = detect_lane(frame)
        return lane_lines, frame

    def get_steering_angle(self, img_lane, lane_lines):
        if len(lane_lines) == 0:
            return 0, None
        new_steering_angle = compute_steering_angle(img_lane, lane_lines)
        self.curr_steering_angle = stabilize_steering_angle(self.curr_steering_angle, new_steering_angle, len(lane_lines))

        curr_heading_image = display_heading_line(img_lane, self.curr_steering_angle)
        show_image("heading", curr_heading_image)

        return self.curr_steering_angle, curr_heading_image

############################
# Frame processing steps
############################
def detect_lane(frame):
    logging.debug('detecting lane lines...')
    black_mask = detect_black_mask(frame)
    show_image('black mask', black_mask)

    cropped_mask = region_of_interest(black_mask)
    show_image('black mask cropped', cropped_mask)

    edges = cv2.Canny(cropped_mask, 100, 200)
    show_image('edges', edges)

    # The course is bounded by two thick black tape lines.  Treat each tape
    # strip as an elongated connected component instead of looking only at
    # its Hough edges.  This also handles a nearly vertical boundary, which
    # the old slope calculation discarded when x1 == x2.
    lane_lines = detect_lane_components(frame, cropped_mask)
    lane_lines_image = display_lines(frame, lane_lines)
    show_image("lane lines images", lane_lines_image)
  
    return lane_lines, lane_lines_image

def detect_black_mask(frame):
    """Return a binary mask for black tape candidates."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    show_image("hsv", hsv)
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, BLACK_VALUE_MAX])
    mask = cv2.inRange(hsv, lower_black, upper_black)

    # Join small compression/motion-blur gaps without growing thin floor
    # seams enough to pass the component filters below.
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 3))
    return cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)


def detect_lane_components(frame, cropped_mask):
    """Fit up to two lane-boundary lines to elongated black components."""
    height, width = cropped_mask.shape
    roi_area = width * int(height * (1 - ROI_TOP_RATIO))
    min_area = max(20, int(roi_area * MIN_COMPONENT_AREA_RATIO))
    max_area = int(roi_area * MAX_COMPONENT_AREA_RATIO)

    count, labels, stats, _ = cv2.connectedComponentsWithStats(
        cropped_mask, connectivity=8
    )
    candidates = []

    for label in range(1, count):
        x, y, component_width, component_height, area = stats[label]
        if area < min_area or area > max_area:
            continue
        if y + component_height < height * MIN_COMPONENT_BOTTOM_RATIO:
            continue

        ys, xs = np.where(labels == label)
        points = np.column_stack((xs, ys)).astype(np.float32)
        rect_width, rect_height = cv2.minAreaRect(points)[1]
        short_side = max(min(rect_width, rect_height), 1.0)
        elongation = max(rect_width, rect_height) / short_side

        vx, vy, x0, y0 = cv2.fitLine(
            points, cv2.DIST_L2, 0, 0.01, 0.01
        ).flatten()
        if elongation < MIN_COMPONENT_ELONGATION:
            continue
        if short_side < width * MIN_COMPONENT_THICKNESS_RATIO:
            # Floor-board seams are dark and long too, but much thinner than
            # the tape even after the small closing operation above.
            continue
        if abs(vy) < MIN_VERTICAL_DIRECTION:
            # A nearly horizontal strip means the car is looking across the
            # track; returning no steering target is safer than driving on.
            continue

        bottom_x = x0 + (height - y0) * vx / vy
        lookahead_y = int(height * ROI_TOP_RATIO)
        lookahead_x = x0 + (lookahead_y - y0) * vx / vy
        if not (-width <= bottom_x <= 2 * width):
            continue
        if not (-width <= lookahead_x <= 2 * width):
            continue

        score = float(area * elongation * abs(vy))
        candidates.append((score, float(bottom_x), float(lookahead_x)))

    # Prefer the strongest components and avoid returning two fragments of
    # the same tape strip as the two lane boundaries.
    candidates.sort(reverse=True)
    selected = []
    min_separation = width * MIN_LANE_SEPARATION_RATIO
    for candidate in candidates:
        if all(
            abs(candidate[2] - previous[2]) >= min_separation
            for previous in selected
        ):
            selected.append(candidate)
        if len(selected) == 2:
            break

    lane_lines = []
    for _, bottom_x, lookahead_x in selected:
        bottom_x = max(-width, min(2 * width, int(round(bottom_x))))
        lookahead_x = max(-width, min(2 * width, int(round(lookahead_x))))
        lane_lines.append(
            [[bottom_x, height, lookahead_x, lookahead_y]]
        )

    lane_lines.sort(key=lambda line: line[0][2])
    return lane_lines


def detect_edges(frame):
    """Compatibility helper used by older examples and diagnostics."""
    mask = detect_black_mask(frame)

    # detect edges
    edges = cv2.Canny(mask, 100, 200)
    show_image("black edge", edges)

    return edges

def region_of_interest(canny):
    height, width = canny.shape
    mask = np.zeros_like(canny)

    # only focus bottom half of the screen
    
    polygon = np.array([[
        (0, height * ROI_TOP_RATIO),
        (width, height * ROI_TOP_RATIO),
        (width, height),
        (0, height),
    ]], np.int32)
    cv2.fillPoly(mask, polygon, 255)
    show_image("mask", mask)
    masked_image = cv2.bitwise_and(canny, mask)
    return masked_image

def detect_line_segments(cropped_edges):
    # tuning min_threshold, minLineLength, maxLineGap is a trial and error process by hand
    rho = 1  # precision in pixel, i.e. 1 pixel
    angle = np.pi / 180  # degree in radian, i.e. 1 degree
    min_threshold = 10  # minimal of votes
    line_segments = cv2.HoughLinesP(cropped_edges, rho, angle, min_threshold, np.array([]), minLineLength=15, maxLineGap=4)

    return line_segments


def average_slope_intercept(frame, line_segments):
    """
    This function combines line segments into one or two lane lines
    If all line slopes are < 0: then we only have detected left lane
    If all line slopes are > 0: then we only have detected right lane
    """
    lane_lines = []
    if line_segments is None:
        logging.info('No line_segment segments detected')
        return lane_lines

    height, width, _ = frame.shape
    left_fit = []
    right_fit = []

    boundary = 1/3
    left_region_boundary = width * (1 - boundary)  # left lane line segment should be on left 2/3 of the screen
    right_region_boundary = width * boundary # right lane line segment should be on left 2/3 of the screen
    
    for line_segment in line_segments:
        # np.array(...).flatten() normalizes both the (N,1,4) shape (older
        # OpenCV) and the (N,4) shape (OpenCV 5.x) that HoughLinesP returns.
        x1, y1, x2, y2 = np.array(line_segment).flatten()
        if x1 == x2:
            logging.info('skipping vertical line segment (slope=inf): %s' % line_segment)
            continue
        fit = np.polyfit((x1, x2), (y1, y2), 1)
        slope = fit[0]
        intercept = fit[1]
        if slope < 0:
            if x1 < left_region_boundary and x2 < left_region_boundary:
                #left_fit.append((slope, intercept))
                if slope < -0.75:
                    #print("left points:", x1, x2, y1, y2)
                    #print("left slope", slope, "intercepts:", intercept)
                    left_fit.append((slope, intercept))
        else:
            if x1 > right_region_boundary and x2 > right_region_boundary:
                #right_fit.append((slope, intercept))
                if slope > 0.75:
                    #print("right points:", x1, x2, y1, y2)
                    #print("right slope", slope, "intercepts:", intercept)
                    right_fit.append((slope, intercept))

    if len(left_fit) > 0:
        left_fit_average = np.average(left_fit, axis=0)
        lane_lines.append(make_points(frame, left_fit_average))

    if len(right_fit) > 0:
        right_fit_average = np.average(right_fit, axis=0)
        lane_lines.append(make_points(frame, right_fit_average))

    logging.debug('lane lines: %s' % lane_lines)  # [[[316, 720, 484, 432]], [[1009, 720, 718, 432]]]

    return lane_lines
 

def compute_steering_angle(frame, lane_lines):
    """ Find the steering angle based on lane line coordinate
        We assume that camera is calibrated to point to dead center
    """
    if len(lane_lines) == 0:
        logging.info('No lane lines detected, do nothing')
        return -90

    height, width, _ = frame.shape
    camera_mid_offset_percent = 0.02
    camera_mid = int(width / 2 * (1 + camera_mid_offset_percent))
    if len(lane_lines) == 1:
        # This is a two-boundary track.  When only one tape strip is in the
        # camera, infer the lane centre using the expected half-width at the
        # look-ahead row instead of treating that boundary as a centreline.
        logging.debug('Only detected one lane boundary. %s' % lane_lines[0])
        _, _, boundary_x, _ = lane_lines[0][0]
        half_lane_width = width * EXPECTED_HALF_LANE_WIDTH_RATIO
        if boundary_x < camera_mid:
            lane_center = boundary_x + half_lane_width
        else:
            lane_center = boundary_x - half_lane_width
        x_offset = lane_center - camera_mid
    else:
        _, _, left_x2, _ = lane_lines[0][0]
        _, _, right_x2, _ = lane_lines[1][0]
        x_offset = (left_x2 + right_x2) / 2 - camera_mid

    # find the steering angle, which is angle between navigation direction to end of center line
    y_offset = int(height / 2)

    angle_to_mid_radian = math.atan(x_offset / y_offset)  # angle (in radian) to center vertical line
    angle_to_mid_deg = int(angle_to_mid_radian * 180.0 / math.pi)  # angle (in degrees) to center vertical line
    steering_angle = angle_to_mid_deg + 90  # this is the steering angle needed by picar front wheel

    logging.debug('new steering angle: %s' % steering_angle)
    return steering_angle


def stabilize_steering_angle(curr_steering_angle, new_steering_angle, num_of_lane_lines, max_angle_deviation_two_lines=5, max_angle_deviation_one_lane=1):
    """
    Using last steering angle to stabilize the steering angle
    This can be improved to use last N angles, etc
    if new angle is too different from current angle, only turn by max_angle_deviation degrees
    """
    if num_of_lane_lines == 2 :
        # if both lane lines detected, then we can deviate more
        max_angle_deviation = max_angle_deviation_two_lines
    else :
        # if only one lane detected, don't deviate too much
        max_angle_deviation = max_angle_deviation_one_lane
    
    angle_deviation = new_steering_angle - curr_steering_angle
    if abs(angle_deviation) > max_angle_deviation:
        stabilized_steering_angle = int(curr_steering_angle
                                        + max_angle_deviation * angle_deviation / abs(angle_deviation))
    else:
        stabilized_steering_angle = new_steering_angle
    logging.info('Proposed angle: %s, stabilized angle: %s' % (new_steering_angle, stabilized_steering_angle))
    return stabilized_steering_angle


"""
  Utility Functions
"""
def display_lines(frame, lines, line_color=(0, 255, 0), line_width=10):
    line_image = np.zeros_like(frame)
    if lines is not None:
        for line in lines:
            # np.array(...).flatten() normalizes both the (N,1,4) shape
            # (older OpenCV) and the (N,4) shape (OpenCV 5.x).
            x1, y1, x2, y2 = np.array(line).flatten()
            cv2.line(line_image, (int(x1), int(y1)), (int(x2), int(y2)), line_color, line_width)
    line_image = cv2.addWeighted(frame, 0.8, line_image, 1, 1)
    return line_image


def display_heading_line(frame, steering_angle, line_color=(0, 0, 255), line_width=5, ):
    heading_image = np.zeros_like(frame)
    height, width, _ = frame.shape

    # figure out the heading line from steering angle
    # heading line (x1,y1) is always center bottom of the screen
    # (x2, y2) requires a bit of trigonometry

    # Note: the steering angle of:
    # 0-89 degree: turn left
    # 90 degree: going straight
    # 91-180 degree: turn right 
    steering_angle_radian = steering_angle / 180.0 * math.pi
    x1 = int(width / 2)
    y1 = height
    x2 = int(x1 - height / 2 / math.tan(steering_angle_radian))
    y2 = int(height / 2)

    cv2.line(heading_image, (x1, y1), (x2, y2), line_color, line_width)
    heading_image = cv2.addWeighted(frame, 0.8, heading_image, 1, 1)

    return heading_image


def length_of_line_segment(line):
    x1, y1, x2, y2 = line
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def show_image(title, frame, show=show_image):
    if show:
        cv2.imshow(title, frame)


def make_points(frame, line):
    height, width, _ = frame.shape
    slope, intercept = line
    y1 = height  # bottom of the frame
    y2 = int(y1 * 1 / 2)  # make points from middle of the frame down

    # bound the coordinates within the frame
    x1 = max(-width, min(2 * width, int((y1 - intercept) / slope)))
    x2 = max(-width, min(2 * width, int((y2 - intercept) / slope)))
    return [[x1, y1, x2, y2]]
