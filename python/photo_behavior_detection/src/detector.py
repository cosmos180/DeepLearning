"""
Device and Person Detection Module

Uses YOLOv8 for real-time object detection of devices (phones, cameras, tablets)
and people in video frames.
"""

import cv2
import numpy as np
import torch
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from ultralytics import YOLO
from loguru import logger


@dataclass
class Detection:
    """Represents a single object detection result."""
    bbox: Tuple[float, float, float, float]  # x1, y1, x2, y2 (normalized)
    confidence: float
    class_id: int
    class_name: str
    keypoints: Optional[np.ndarray] = None  # For pose estimation

    def to_absolute(self, img_width: int, img_height: int) -> Tuple[int, int, int, int]:
        """Convert normalized bbox to absolute pixel coordinates."""
        x1 = int(self.bbox[0] * img_width)
        y1 = int(self.bbox[1] * img_height)
        x2 = int(self.bbox[2] * img_width)
        y2 = int(self.bbox[3] * img_height)
        return (x1, y1, x2, y2)


class DeviceDetector:
    """
    Device detection using YOLOv8.

    Detects: smartphones, cameras, tablets, and other recording devices.
    """

    # COCO class IDs for devices
    DEVICE_CLASSES = {
        67: "cell phone",
        # Custom classes would be added here
        # e.g., 80: "camera", 81: "tablet"
    }

    def __init__(
        self,
        model_path: str = "yolov8m.pt",
        conf_threshold: float = 0.5,
        nms_threshold: float = 0.45,
        device: str = "cuda",
        half: bool = True,
    ):
        """
        Initialize the device detector.

        Args:
            model_path: Path to YOLOv8 model weights
            conf_threshold: Confidence threshold for detections
            nms_threshold: IoU threshold for NMS
            device: Device to run inference on (cuda/cpu)
            half: Use FP16 precision
        """
        self.model_path = model_path
        self.conf_threshold = conf_threshold
        self.nms_threshold = nms_threshold
        self.device = device
        self.half = half

        logger.info(f"Loading device detection model from {model_path}")
        self.model = YOLO(model_path)
        self.model.to(device)

        if half and device == "cuda":
            self.model.half()

        logger.info("Device detection model loaded successfully")

    def detect(
        self,
        frame: np.ndarray,
        return_segmentation: bool = False,
    ) -> List[Detection]:
        """
        Detect devices in a frame.

        Args:
            frame: Input image (BGR format)
            return_segmentation: Return segmentation masks if available

        Returns:
            List of Detection objects
        """
        # Run inference
        results = self.model(
            frame,
            conf=self.conf_threshold,
            iou=self.nms_threshold,
            verbose=False,
        )

        detections = []
        img_height, img_width = frame.shape[:2]

        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue

            for box in boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])

                # Only keep device detections
                if cls_id not in self.DEVICE_CLASSES:
                    # For custom training, filter by your device classes
                    pass

                # Get bounding box (xyxy format)
                xyxy = box.xyxy[0].cpu().numpy()

                # Normalize to [0, 1]
                x1, y1, x2, y2 = xyxy
                normalized_bbox = (
                    x1 / img_width,
                    y1 / img_height,
                    x2 / img_width,
                    y2 / img_height,
                )

                detection = Detection(
                    bbox=normalized_bbox,
                    confidence=conf,
                    class_id=cls_id,
                    class_name=self.model.names[cls_id],
                )

                detections.append(detection)

        return detections

    def detect_and_classify(
        self,
        frame: np.ndarray,
    ) -> Tuple[List[Detection], Dict[str, List[Detection]]]:
        """
        Detect devices and classify by type.

        Returns:
            Tuple of (all detections, detections by class)
        """
        detections = self.detect(frame)

        # Group by class
        by_class = {}
        for det in detections:
            if det.class_name not in by_class:
                by_class[det.class_name] = []
            by_class[det.class_name].append(det)

        return detections, by_class

    def track_devices(
        self,
        detections: List[Detection],
        max_distance: float = 0.3,
        max_disappeared: int = 30,
    ) -> Dict[int, Detection]:
        """
        Simple device tracking using centroid tracking.

        Args:
            detections: Current frame detections
            max_distance: Maximum distance for track association
            max_disappeared: Maximum frames before track is deleted

        Returns:
            Dictionary mapping track IDs to detections
        """
        if not hasattr(self, "_tracker"):
            from scipy.optimize import linear_sum_assignment

            self._tracker = CentroidTracker(max_distance, max_disappeared)

        return self._tracker.update(detections)

    def visualize(
        self,
        frame: np.ndarray,
        detections: List[Detection],
        show_confidence: bool = True,
    ) -> np.ndarray:
        """
        Visualize detections on frame.

        Args:
            frame: Input image
            detections: List of Detection objects
            show_confidence: Show confidence scores

        Returns:
            Annotated image
        """
        img_height, img_width = frame.shape[:2]
        annotated = frame.copy()

        for det in detections:
            x1, y1, x2, y2 = det.to_absolute(img_width, img_height)

            # Draw bounding box
            color = self._get_class_color(det.class_name)
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)

            # Draw label
            label = det.class_name
            if show_confidence:
                label += f" {det.confidence:.2f}"

            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            cv2.rectangle(
                annotated,
                (x1, y1 - label_size[1] - 10),
                (x1 + label_size[0], y1),
                color,
                -1,
            )
            cv2.putText(
                annotated,
                label,
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                2,
            )

        return annotated

    def _get_class_color(self, class_name: str) -> Tuple[int, int, int]:
        """Get color for visualization based on class name."""
        colors = {
            "cell phone": (255, 0, 255),  # Magenta
            "camera": (0, 255, 255),  # Cyan
            "tablet": (255, 255, 0),  # Yellow
            "recording_device": (0, 165, 255),  # Orange
        }
        return colors.get(class_name, (0, 255, 0))  # Green default


class PersonDetector(DeviceDetector):
    """
    Person detection specialized for human subjects.
    """

    # COCO class ID for person
    PERSON_CLASS_ID = 0

    def __init__(
        self,
        model_path: str = "yolov8m.pt",
        conf_threshold: float = 0.6,
        device: str = "cuda",
        half: bool = True,
    ):
        super().__init__(model_path, conf_threshold, 0.45, device, half)
        logger.info("Person detector initialized")

    def detect(self, frame: np.ndarray) -> List[Detection]:
        """Detect only people in the frame."""
        # Run inference
        results = self.model(
            frame,
            conf=self.conf_threshold,
            iou=self.nms_threshold,
            classes=[self.PERSON_CLASS_ID],  # Only person class
            verbose=False,
        )

        detections = []
        img_height, img_width = frame.shape[:2]

        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue

            for box in boxes:
                conf = float(box.conf[0])
                xyxy = box.xyxy[0].cpu().numpy()

                x1, y1, x2, y2 = xyxy
                normalized_bbox = (
                    x1 / img_width,
                    y1 / img_height,
                    x2 / img_width,
                    y2 / img_height,
                )

                detection = Detection(
                    bbox=normalized_bbox,
                    confidence=conf,
                    class_id=self.PERSON_CLASS_ID,
                    class_name="person",
                )

                detections.append(detection)

        return detections


class CentroidTracker:
    """
    Simple centroid tracking algorithm for associating detections across frames.
    """

    def __init__(self, max_distance: float = 0.3, max_disappeared: int = 30):
        self.max_distance = max_distance
        self.max_disappeared = max_disappeared

        self.next_id = 0
        self.objects = {}  # ID -> centroid
        self.disappeared = {}  # ID -> frames disappeared

    def register(self, centroid: Tuple[float, float]):
        """Register a new object."""
        self.objects[self.next_id] = centroid
        self.disappeared[self.next_id] = 0
        self.next_id += 1

    def deregister(self, object_id: int):
        """Deregister an object."""
        del self.objects[object_id]
        del self.disappeared[object_id]

    def update(self, detections: List[Detection]) -> Dict[int, Detection]:
        """
        Update tracker with new detections.

        Args:
            detections: List of Detection objects

        Returns:
            Dictionary mapping track IDs to detections
        """
        if len(detections) == 0:
            # Mark all objects as disappeared
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            return {}

        # Compute centroids of detections
        input_centroids = []
        for det in detections:
            x1, y1, x2, y2 = det.bbox
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            input_centroids.append((cx, cy))

        # If no tracked objects, register all
        if len(self.objects) == 0:
            for centroid in input_centroids:
                self.register(centroid)
        else:
            # Compute distances between existing objects and new detections
            object_ids = list(self.objects.keys())
            object_centroids = list(self.objects.values())

            # Compute distance matrix
            from scipy.spatial.distance import cdist

            D = cdist(np.array(object_centroids), np.array(input_centroids))

            # Hungarian algorithm for assignment
            from scipy.optimize import linear_sum_assignment

            rows, cols = linear_sum_assignment(D)

            used_rows = set()
            used_cols = set()

            for (row, col) in zip(rows, cols):
                if D[row, col] > self.max_distance:
                    continue

                object_id = object_ids[row]
                self.objects[object_id] = input_centroids[col]
                self.disappeared[object_id] = 0

                used_rows.add(row)
                used_cols.add(col)

            # Unmatched objects (disappeared)
            unused_rows = set(range(0, D.shape[0])).difference(used_rows)
            unused_cols = set(range(0, D.shape[1])).difference(used_cols)

            # Check for disappeared objects
            if D.shape[0] >= D.shape[1]:
                for row in unused_rows:
                    object_id = object_ids[row]
                    self.disappeared[object_id] += 1
                    if self.disappeared[object_id] > self.max_disappeared:
                        self.deregister(object_id)
            else:
                for col in unused_cols:
                    self.register(input_centroids[col])

        # Map detections to IDs
        tracked = {}
        for object_id, centroid in self.objects.items():
            # Find closest detection
            for det in detections:
                x1, y1, x2, y2 = det.bbox
                cx = (x1 + x2) / 2
                cy = (y1 + y2) / 2
                dist = np.sqrt((centroid[0] - cx) ** 2 + (centroid[1] - cy) ** 2)
                if dist < self.max_distance:
                    tracked[object_id] = det
                    break

        return tracked


if __name__ == "__main__":
    # Test the detector
    detector = DeviceDetector()
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        detections = detector.detect(frame)
        annotated = detector.visualize(frame, detections)

        cv2.imshow("Device Detection", annotated)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
