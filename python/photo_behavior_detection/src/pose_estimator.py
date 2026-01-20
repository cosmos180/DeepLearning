"""
Pose Estimation Module

Uses MediaPipe Pose for comprehensive human pose estimation including
body landmarks, hand positions, and 3D world coordinates.
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import mediapipe as mp
from loguru import logger
from enum import IntEnum


class MediaPipePoseLandmark(IntEnum):
    """MediaPipe Pose 33 landmark indices."""
    NOSE = 0
    LEFT_EYE_INNER = 1
    LEFT_EYE = 2
    LEFT_EYE_OUTER = 3
    RIGHT_EYE_INNER = 4
    RIGHT_EYE = 5
    RIGHT_EYE_OUTER = 6
    LEFT_EAR = 7
    RIGHT_EAR = 8
    MOUTH_LEFT = 9
    MOUTH_RIGHT = 10
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_PINKY = 17
    RIGHT_PINKY = 18
    LEFT_INDEX = 19
    RIGHT_INDEX = 20
    LEFT_THUMB = 21
    RIGHT_THUMB = 22
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28
    LEFT_HEEL = 29
    RIGHT_HEEL = 30
    LEFT_FOOT_INDEX = 31
    RIGHT_FOOT_INDEX = 32


@dataclass
class PoseLandmarks:
    """Container for pose landmarks data."""
    landmarks: np.ndarray  # Shape: (33, 3) - x, y, z (normalized)
    world_landmarks: np.ndarray  # Shape: (33, 3) - x, y, z (world coordinates, meters)
    visibility: np.ndarray  # Shape: (33,) - visibility scores


@dataclass
class PoseFeatures:
    """Extracted features from pose for photo/video detection."""
    # Arm features
    left_arm_angle: float  # Angle between upper arm and vertical
    right_arm_angle: float
    left_forearm_angle: float  # Angle between forearm and upper arm
    right_forearm_angle: float

    # Position features
    left_wrist_height: float  # Relative to shoulder
    right_wrist_height: float
    head_pose: Tuple[float, float, float]  # Pitch, yaw, roll (degrees)

    # Device holding indicators
    holding_device_left: bool
    holding_device_right: bool
    device_orientation: Optional[str]  # "horizontal", "vertical", None

    # Body state
    body_stability: float  # 0-1, higher is more stable
    is_standing: bool


class PoseEstimator:
    """
    MediaPipe-based pose estimation system.
    """

    def __init__(
        self,
        model_complexity: int = 1,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
        static_image_mode: bool = False,
    ):
        """
        Initialize the pose estimator.

        Args:
            model_complexity: 0, 1, or 2 (higher = more accurate but slower)
            min_detection_confidence: Minimum confidence for pose detection
            min_tracking_confidence: Minimum confidence for landmark tracking
            static_image_mode: True for single images, False for video
        """
        self.model_complexity = model_complexity
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        self.static_image_mode = static_image_mode

        logger.info("Initializing MediaPipe Pose")
        mp_pose = mp.solutions.pose
        self.pose = mp_pose.Pose(
            model_complexity=model_complexity,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
            static_image_mode=static_image_mode,
        )

        # For drawing
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        logger.info("Pose estimator initialized")

    def estimate(self, frame: np.ndarray) -> Optional[PoseLandmarks]:
        """
        Estimate pose landmarks in a frame.

        Args:
            frame: Input image (BGR format)

        Returns:
            PoseLandmarks object or None if no pose detected
        """
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process frame
        results = self.pose.process(frame_rgb)

        if results.pose_landmarks is None:
            return None

        # Extract landmarks
        landmarks = np.array(
            [[lm.x, lm.y, lm.z] for lm in results.pose_landmarks.landmark]
        )

        visibility = np.array([lm.visibility for lm in results.pose_landmarks.landmark])

        # Extract world landmarks if available
        if results.pose_world_landmarks:
            world_landmarks = np.array(
                [[lm.x, lm.y, lm.z] for lm in results.pose_world_landmarks.landmark]
            )
        else:
            world_landmarks = np.zeros((33, 3))

        return PoseLandmarks(
            landmarks=landmarks,
            world_landmarks=world_landmarks,
            visibility=visibility,
        )

    def estimate_multiple(self, frame: np.ndarray) -> List[PoseLandmarks]:
        """
        Estimate poses for multiple people in a frame.

        Note: MediaPipe Pose detects only one pose by default.
        For multi-person, use a different approach or run detection-based
        cropping and inference.

        Args:
            frame: Input image

        Returns:
            List of PoseLandmarks (usually just one with MediaPipe Pose)
        """
        result = self.estimate(frame)
        return [result] if result is not None else []

    def extract_features(self, pose_landmarks: PoseLandmarks) -> PoseFeatures:
        """
        Extract meaningful features from pose landmarks.

        Args:
            pose_landmarks: Pose landmarks from estimate()

        Returns:
            PoseFeatures object
        """
        lm = pose_landmarks.landmarks

        # Extract key points
        left_shoulder = lm[MediaPipePoseLandmark.LEFT_SHOULDER]
        right_shoulder = lm[MediaPipePoseLandmark.RIGHT_SHOULDER]
        left_elbow = lm[MediaPipePoseLandmark.LEFT_ELBOW]
        right_elbow = lm[MediaPipePoseLandmark.RIGHT_ELBOW]
        left_wrist = lm[MediaPipePoseLandmark.LEFT_WRIST]
        right_wrist = lm[MediaPipePoseLandmark.RIGHT_WRIST]
        nose = lm[MediaPipePoseLandmark.NOSE]
        left_ear = lm[MediaPipePoseLandmark.LEFT_EAR]
        right_ear = lm[MediaPipePoseLandmark.RIGHT_EAR]

        # Calculate arm angles
        left_arm_angle = self._calculate_arm_angle(left_shoulder, left_elbow, left_wrist)
        right_arm_angle = self._calculate_arm_angle(right_shoulder, right_elbow, right_wrist)

        # Calculate forearm angles
        left_forearm_angle = self._calculate_forearm_angle(left_shoulder, left_elbow, left_wrist)
        right_forearm_angle = self._calculate_forearm_angle(right_shoulder, right_elbow, right_wrist)

        # Calculate wrist heights (relative to shoulders)
        shoulder_y = (left_shoulder[1] + right_shoulder[1]) / 2
        left_wrist_height = shoulder_y - left_wrist[1]
        right_wrist_height = shoulder_y - right_wrist[1]

        # Calculate head pose
        head_pose = self._calculate_head_pose(nose, left_ear, right_ear, lm)

        # Determine device holding
        holding_left, holding_right, orientation = self._infer_device_holding(
            left_wrist, right_wrist, left_elbow, right_elbow, head_pose
        )

        # Body stability (based on lower body)
        body_stability = self._calculate_body_stability(lm)

        # Standing or not
        is_standing = self._is_standing(lm)

        return PoseFeatures(
            left_arm_angle=left_arm_angle,
            right_arm_angle=right_arm_angle,
            left_forearm_angle=left_forearm_angle,
            right_forearm_angle=right_forearm_angle,
            left_wrist_height=left_wrist_height,
            right_wrist_height=right_wrist_height,
            head_pose=head_pose,
            holding_device_left=holding_left,
            holding_device_right=holding_right,
            device_orientation=orientation,
            body_stability=body_stability,
            is_standing=is_standing,
        )

    def is_photo_pose(
        self,
        features: PoseFeatures,
        min_arm_elevation: float = 45,
        device_height_threshold: float = 0.05,
    ) -> bool:
        """
        Determine if pose indicates photo-taking behavior.

        Args:
            features: Extracted pose features
            min_arm_elevation: Minimum arm elevation angle (degrees)
            device_height_threshold: Minimum device height above shoulder (normalized)

        Returns:
            True if pose suggests photo-taking
        """
        # Check if either arm is elevated
        arm_elevated = (
            features.left_arm_angle > min_arm_elevation
            or features.right_arm_angle > min_arm_elevation
        )

        # Check if device is at height
        device_at_height = (
            features.left_wrist_height > device_height_threshold
            or features.right_wrist_height > device_height_threshold
        )

        # Check if holding device
        holding_device = features.holding_device_left or features.holding_device_right

        return arm_elevated and device_at_height and holding_device

    def is_recording_pose(
        self,
        features: PoseFeatures,
        stability_threshold: float = 0.7,
    ) -> bool:
        """
        Determine if pose indicates video recording behavior.

        Args:
            features: Extracted pose features
            stability_threshold: Minimum body stability (0-1)

        Returns:
            True if pose suggests video recording
        """
        # Recording requires more stable pose
        is_stable = features.body_stability > stability_threshold

        # Device should be held (usually two-handed for stable recording)
        holding_device = features.holding_device_left and features.holding_device_right

        # Arms typically elevated
        arm_elevated = (
            features.left_arm_angle > 30 and features.right_arm_angle > 30
        )

        return is_stable and holding_device and arm_elevated

    def _calculate_arm_angle(
        self,
        shoulder: np.ndarray,
        elbow: np.ndarray,
        wrist: np.ndarray,
    ) -> float:
        """
        Calculate the angle between upper arm and vertical.

        Args:
            shoulder: Shoulder landmark [x, y, z]
            elbow: Elbow landmark
            wrist: Wrist landmark

        Returns:
            Angle in degrees (0-180)
        """
        # Vector from shoulder to elbow (upper arm)
        upper_arm = elbow[:2] - shoulder[:2]

        # Vertical vector pointing down
        vertical = np.array([0, 1])

        # Calculate angle
        cosine_angle = np.dot(upper_arm, vertical) / (
            np.linalg.norm(upper_arm) * np.linalg.norm(vertical)
        )
        angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))

        return np.degrees(angle)

    def _calculate_forearm_angle(
        self,
        shoulder: np.ndarray,
        elbow: np.ndarray,
        wrist: np.ndarray,
    ) -> float:
        """
        Calculate the angle between forearm and upper arm.

        Args:
            shoulder: Shoulder landmark [x, y, z]
            elbow: Elbow landmark
            wrist: Wrist landmark

        Returns:
            Angle in degrees (0-180)
        """
        # Vector from elbow to wrist (forearm)
        forearm = wrist[:2] - elbow[:2]

        # Vector from elbow to shoulder (reverse of upper arm)
        upper_arm_rev = shoulder[:2] - elbow[:2]

        # Calculate angle
        cosine_angle = np.dot(forearm, upper_arm_rev) / (
            np.linalg.norm(forearm) * np.linalg.norm(upper_arm_rev)
        )
        angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))

        return np.degrees(angle)

    def _calculate_head_pose(
        self,
        nose: np.ndarray,
        left_ear: np.ndarray,
        right_ear: np.ndarray,
        all_landmarks: np.ndarray,
    ) -> Tuple[float, float, float]:
        """
        Estimate head pose (pitch, yaw, roll).

        Args:
            nose: Nose landmark
            left_ear: Left ear landmark
            right_ear: Right ear landmark
            all_landmarks: All 33 landmarks

        Returns:
            Tuple of (pitch, yaw, roll) in degrees
        """
        # Simplified head pose estimation
        # For accurate results, use a dedicated head pose estimator like HopeNet

        # Roll: rotation around Z axis (tilt left/right)
        dx = right_ear[0] - left_ear[0]
        dy = right_ear[1] - left_ear[1]
        roll = np.degrees(np.arctan2(dy, dx))

        # Yaw: rotation around Y axis (turn left/right)
        # Based on nose position relative to ear midpoint
        ear_midpoint_x = (left_ear[0] + right_ear[0]) / 2
        yaw = np.degrees(np.arctan2(nose[0] - ear_midpoint_x, 1)) * 10

        # Pitch: rotation around X axis (up/down)
        # Based on nose-y relationship to eyes
        eyes_y = (all_landmarks[2, 1] + all_landmarks[5, 1]) / 2
        chin_y = all_landmarks[152, 1] if len(all_landmarks) > 152 else all_landmarks[10, 1]
        pitch = np.degrees(np.arctan2(nose[1] - eyes_y, chin_y - eyes_y) - 0.5) * 30

        return (pitch, yaw, roll)

    def _infer_device_holding(
        self,
        left_wrist: np.ndarray,
        right_wrist: np.ndarray,
        left_elbow: np.ndarray,
        right_elbow: np.ndarray,
        head_pose: Tuple[float, float, float],
    ) -> Tuple[bool, bool, Optional[str]]:
        """
        Infer if and how a device is being held.

        Args:
            left_wrist, right_wrist: Wrist positions
            left_elbow, right_elbow: Elbow positions
            head_pose: Head pose angles

        Returns:
            Tuple of (holding_left, holding_right, orientation)
        """
        pitch, yaw, roll = head_pose

        # Check if wrists are elevated (typical of holding device)
        left_elevated = left_wrist[1] < left_elbow[1]
        right_elevated = right_wrist[1] < right_elbow[1]

        # Check if wrists are near center (typical of holding phone)
        center_x = (left_wrist[0] + right_wrist[0]) / 2
        near_center = abs(left_wrist[0] - center_x) < 0.2 and abs(right_wrist[0] - center_x) < 0.2

        # Holding indicators
        holding_left = left_elevated
        holding_right = right_elevated

        # Infer orientation
        orientation = None
        if holding_left and holding_right:
            # Two-handed - check device orientation based on wrist separation
            wrist_separation_y = abs(left_wrist[1] - right_wrist[1])
            wrist_separation_x = abs(left_wrist[0] - right_wrist[0])

            if wrist_separation_x > wrist_separation_y:
                orientation = "horizontal"
            else:
                orientation = "vertical"

        return (holding_left, holding_right, orientation)

    def _calculate_body_stability(self, landmarks: np.ndarray) -> float:
        """
        Calculate body stability based on lower body keypoints.

        Args:
            landmarks: All 33 pose landmarks

        Returns:
            Stability score (0-1, higher = more stable)
        """
        # Check visibility of lower body landmarks
        lower_body_indices = [
            MediaPipePoseLandmark.LEFT_HIP,
            MediaPipePoseLandmark.RIGHT_HIP,
            MediaPipePoseLandmark.LEFT_KNEE,
            MediaPipePoseLandmark.RIGHT_KNEE,
        ]

        visibility_sum = 0
        for idx in lower_body_indices:
            if idx < len(landmarks):
                # In normalized coordinates, z can indicate visibility
                visibility_sum += 1 if abs(landmarks[idx, 2]) < 0.1 else 0

        return visibility_sum / len(lower_body_indices)

    def _is_standing(self, landmarks: np.ndarray) -> bool:
        """
        Determine if person is standing.

        Args:
            landmarks: All 33 pose landmarks

        Returns:
            True if standing pose detected
        """
        # Simple heuristic: hips are above knees
        try:
            left_hip = landmarks[MediaPipePoseLandmark.LEFT_HIP]
            left_knee = landmarks[MediaPipePoseLandmark.LEFT_KNEE]
            return left_hip[1] < left_knee[1]  # Lower y = higher in image
        except IndexError:
            return False

    def visualize(
        self,
        frame: np.ndarray,
        pose_landmarks: PoseLandmarks,
        show_skeleton: bool = True,
        show_landmarks: bool = True,
    ) -> np.ndarray:
        """
        Visualize pose landmarks on frame.

        Args:
            frame: Input image
            pose_landmarks: Pose landmarks to visualize
            show_skeleton: Draw skeleton connections
            show_landmarks: Draw landmark points

        Returns:
            Annotated image
        """
        annotated = frame.copy()

        if pose_landmarks is None:
            return annotated

        # Convert landmarks back to MediaPipe format
        h, w = frame.shape[:2]
        landmark_list = []
        for i in range(33):
            lm = pose_landmarks.landmarks[i]
            landmark_list.append(
                mp.solutions.pose.PoseLandmark(
                    x=lm[0],
                    y=lm[1],
                    z=lm[2],
                    visibility=pose_landmarks.visibility[i],
                )
            )

        # Create a fake pose landmarks object for drawing
        class FakePoseLandmarks:
            def __init__(self, landmarks):
                self.landmark = landmarks

        fake_landmarks = FakePoseLandmarks(landmark_list)

        # Draw
        connections = mp.solutions.pose.POSE_CONNECTIONS
        if show_skeleton:
            self.mp_drawing.draw_connections(
                annotated,
                fake_landmarks,
                connections,
                landmark_drawing_spec=None,
                connection_drawing_spec=self.mp_drawing_styles.get_default_pose_connection_style(),
            )

        if show_landmarks:
            self.mp_drawing.draw_landmarks(
                annotated,
                fake_landmarks,
                connections=None,  # Already drew connections
                landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style(),
            )

        return annotated

    def visualize_features(
        self,
        frame: np.ndarray,
        features: PoseFeatures,
        pose_landmarks: PoseLandmarks,
    ) -> np.ndarray:
        """
        Visualize extracted features on frame.

        Args:
            frame: Input image
            features: Extracted pose features
            pose_landmarks: Original pose landmarks

        Returns:
            Annotated image with feature overlays
        """
        annotated = self.visualize(frame, pose_landmarks)
        h, w = annotated.shape[:2]

        # Add text overlay
        y_offset = 30
        texts = [
            f"L Arm Angle: {features.left_arm_angle:.1f}°",
            f"R Arm Angle: {features.right_arm_angle:.1f}°",
            f"Device: {'L' if features.holding_device_left else ''}{'R' if features.holding_device_right else ''}",
            f"Orientation: {features.device_orientation or 'N/A'}",
            f"Stability: {features.body_stability:.2f}",
            f"Photo Pose: {self.is_photo_pose(features)}",
            f"Record Pose: {self.is_recording_pose(features)}",
        ]

        for text in texts:
            cv2.putText(
                annotated,
                text,
                (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )
            y_offset += 30

        return annotated


if __name__ == "__main__":
    # Test the pose estimator
    estimator = PoseEstimator()
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        pose = estimator.estimate(frame)
        if pose:
            features = estimator.extract_features(pose)
            annotated = estimator.visualize_features(frame, features, pose)

            # Print analysis
            print(f"Photo pose: {estimator.is_photo_pose(features)}")
            print(f"Recording pose: {estimator.is_recording_pose(features)}")
        else:
            annotated = frame

        cv2.imshow("Pose Estimation", annotated)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
