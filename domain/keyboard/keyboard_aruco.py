# domain/keyboard/keyboard_aruco.py
import cv2
import cv2.aruco as aruco
import numpy as np
from .keyboard_config import WARP_W, WARP_H

class ArucoTracker:
    def __init__(self):
        self.aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_APRILTAG_25h9)
        self.parameters = aruco.DetectorParameters()

        self.prev_matrix = None
        self.prev_paper_corners = None
        self.prev_marker_centers = {}

    def update(self, frame):
        """
        frame을 받아서:
        - 마커 검출
        - homography matrix 계산/업데이트
        - 키보드 종이의 코너(prev_paper_corners) 유지
        반환: matrix, prev_paper_corners
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = aruco.detectMarkers(gray, self.aruco_dict, parameters=self.parameters)

        matrix = None
        curr_marker_centers = {}

        if ids is not None:
            aruco.drawDetectedMarkers(frame, corners, ids)
            ids = ids.flatten()
            for i, tag_id in enumerate(ids):
                curr_marker_centers[tag_id] = corners[i][0].mean(axis=0)

        # 4개 모두 보일 때: 기준점 갱신
        if ids is not None and len(ids) >= 4:
            corners_map = {id: corner for id, corner in zip(ids, corners)}
            if all(i in corners_map for i in [0, 1, 2, 3]):
                try:
                    src_pts = np.array([
                        corners_map[0][0][1], corners_map[1][0][0],
                        corners_map[3][0][3], corners_map[2][0][2]
                    ], dtype=np.float32)

                    dst_pts = np.array([
                        [0, 0], [WARP_W, 0], [WARP_W, WARP_H], [0, WARP_H]
                    ], dtype=np.float32)

                    matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)

                    self.prev_matrix = matrix.copy()
                    self.prev_paper_corners = src_pts.copy()
                    self.prev_marker_centers = curr_marker_centers.copy()
                except:
                    pass

        # 2~3개일 때: 이전 프레임 기반 추적
        elif len(curr_marker_centers) >= 2 and self.prev_paper_corners is not None:
            pts_prev, pts_curr = [], []
            for tag_id in curr_marker_centers:
                if tag_id in self.prev_marker_centers:
                    pts_prev.append(self.prev_marker_centers[tag_id])
                    pts_curr.append(curr_marker_centers[tag_id])

            if len(pts_prev) >= 2:
                pts_prev = np.array(pts_prev).reshape(-1, 1, 2)
                pts_curr = np.array(pts_curr).reshape(-1, 1, 2)
                M, _ = cv2.estimateAffinePartial2D(pts_prev, pts_curr)

                if M is not None:
                    prev_pts_reshaped = self.prev_paper_corners.reshape(-1, 1, 2)
                    curr_paper_corners = cv2.transform(prev_pts_reshaped, M).reshape(4, 2)

                    dst_pts = np.array([
                        [0, 0], [WARP_W, 0], [WARP_W, WARP_H], [0, WARP_H]
                    ], dtype=np.float32)

                    matrix = cv2.getPerspectiveTransform(
                        curr_paper_corners.astype(np.float32),
                        dst_pts
                    )

                    self.prev_matrix = matrix
                    self.prev_paper_corners = curr_paper_corners
                    self.prev_marker_centers = curr_marker_centers

        # 마커가 안보이면: 이전 matrix 유지
        elif self.prev_matrix is not None:
            matrix = self.prev_matrix

        # 필요하면 종이 영역 테두리도 여기서 그릴 수 있음
        # if self.prev_paper_corners is not None:
        #     paper_poly = self.prev_paper_corners.astype(np.int32).reshape((-1, 1, 2))
        #     cv2.polylines(frame, [paper_poly], True, (0, 0, 255), 2)

        return matrix
