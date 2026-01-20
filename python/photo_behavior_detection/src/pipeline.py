"""
Main Detection Pipeline

Orchestrates all modules for end-to-end photo/video behavior detection.
"""

import cv2
import numpy as np
import time
from typing import Optional, List, Dict
from dataclasses import dataclass
from threading import Thread, Lock
from queue import Queue
from loguru import logger

try:
    from src.detector import DeviceDetector, PersonDetector, Detection
    from src.pose_estimator import PoseEstimator, PoseLandmarks
    from src.action_recognizer import ActionRecognizer
    from src.fusion_engine import FusionEngine, DetectionContext, FusionResult, ActionType
except ImportError:
    from detector import DeviceDetector, PersonDetector, Detection
    from pose_estimator import PoseEstimator, PoseLandmarks
    from action_recognizer import ActionRecognizer
    from fusion_engine import FusionEngine, DetectionContext, FusionResult, ActionType


@dataclass
class PipelineConfig:
    """Configuration for the detection pipeline."""

    # Video settings
    source: str = "0"  # Camera index or video file path
    fps: int = 30
    width: int = 1920
    height: int = 1080

    # Processing settings
    skip_frames: int = 1  # Process every Nth frame
    processing_fps: int = 15

    # Model settings
    device: str = "cuda"
    half_precision: bool = True

    # Detection settings
    enable_fast_screening: bool = True
    confidence_threshold: float = 0.7

    # Output settings
    visualize: bool = True
    save_video: bool = False
    output_path: str = "output/recordings/"


class DetectionPipeline:
    """
    Main pipeline for photo/video behavior detection.
    """

    def __init__(self, config: PipelineConfig):
        """
        Initialize the pipeline.

        Args:
            config: Pipeline configuration
        """
        self.config = config

        # Initialize modules
        logger.info("Initializing detection modules...")

        self.person_detector = PersonDetector(
            conf_threshold=0.6,
            device=config.device,
            half=config.half_precision,
        )

        self.device_detector = DeviceDetector(
            conf_threshold=0.5,
            device=config.device,
            half=config.half_precision,
        )

        self.pose_estimator = PoseEstimator(
            model_complexity=1,
            min_detection_confidence=0.5,
        )

        self.action_recognizer = ActionRecognizer(
            sequence_length=16,
            device=config.device,
            confidence_threshold=0.7,
        )

        self.fusion_engine = FusionEngine(
            fusion_method="hybrid",
            device=config.device,
            confidence_threshold=config.confidence_threshold,
        )

        logger.info("All modules initialized successfully")

        # Video capture
        self.cap = None
        self.video_writer = None

        # Frame counter
        self.frame_count = 0
        self.processed_count = 0

        # Callbacks
        self.on_detection = None

    def start(self):
        """Start the pipeline."""
        logger.info(f"Starting pipeline with source: {self.config.source}")

        # Initialize video capture
        if self.config.source.isdigit():
            self.cap = cv2.VideoCapture(int(self.config.source))
        else:
            self.cap = cv2.VideoCapture(self.config.source)

        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open video source: {self.config.source}")

        # Set video properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.height)
        self.cap.set(cv2.CAP_PROP_FPS, self.config.fps)

        # Initialize video writer if needed
        if self.config.save_video:
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            output_file = f"{self.config.output_path}/detection_{int(time.time())}.mp4"
            self.video_writer = cv2.VideoWriter(
                output_file,
                fourcc,
                self.config.processing_fps,
                (self.config.width, self.config.height),
            )
            logger.info(f"Saving video to: {output_file}")

        logger.info("Pipeline started")

    def stop(self):
        """Stop the pipeline."""
        logger.info("Stopping pipeline...")

        if self.cap:
            self.cap.release()

        if self.video_writer:
            self.video_writer.release()

        cv2.destroyAllWindows()

        logger.info("Pipeline stopped")

    def process_frame(self, frame: np.ndarray) -> Optional[FusionResult]:
        """
        Process a single frame.

        Args:
            frame: Input frame

        Returns:
            FusionResult if action detected, None otherwise
        """
        self.frame_count += 1

        # Skip frames if needed
        if self.frame_count % self.config.skip_frames != 0:
            return None

        self.processed_count += 1

        # Stage 1: Detect people
        person_detections = self.person_detector.detect(frame)

        # Stage 2: Detect devices
        device_detections = self.device_detector.detect(frame)

        # Stage 3: Estimate pose
        pose_landmarks = self.pose_estimator.estimate(frame)
        pose_features = None

        if pose_landmarks:
            pose_features = self.pose_estimator.extract_features(pose_landmarks)

        # Stage 4: Action recognition (temporal)
        action_prediction = self.action_recognizer.update(frame, pose_landmarks)

        # Stage 5: Fusion
        # For each person-device pair, create a context and fuse
        for person_det in person_detections:
            # Associate devices with person
            associated_devices = self._associate_devices(person_det, device_detections)

            # Create detection context
            context = DetectionContext(
                person_detection=person_det,
                device_detections=associated_devices,
                pose_features=pose_features,
                action_prediction=action_prediction,
            )

            # Fuse and make decision
            result = self.fusion_engine.process(context)

            if result is not None:
                # Trigger callback
                if self.on_detection:
                    self.on_detection(frame, context, result)

                return result

        return None

    def _associate_devices(
        self,
        person: Detection,
        devices: List[Detection],
        max_distance: float = 0.3,
    ) -> List[Detection]:
        """
        Associate devices with a person.

        Args:
            person: Person detection
            devices: List of device detections
            max_distance: Maximum distance for association

        Returns:
            List of associated devices
        """
        if not devices:
            return []

        # Get person center
        px1, py1, px2, py2 = person.bbox
        person_center = ((px1 + px2) / 2, (py1 + py2) / 2)

        associated = []
        for device in devices:
            # Get device center
            dx1, dy1, dx2, dy2 = device.bbox
            device_center = ((dx1 + dx2) / 2, (dy1 + dy2) / 2)

            # Calculate distance
            distance = np.sqrt(
                (person_center[0] - device_center[0]) ** 2
                + (person_center[1] - device_center[1]) ** 2
            )

            if distance < max_distance:
                associated.append(device)

        return associated

    def run(self):
        """
        Run the pipeline continuously.

        This is the main loop that processes frames from the video source.
        """
        if not self.cap:
            self.start()

        logger.info("Starting main loop...")

        fps_timer = time.time()
        fps_counter = 0

        try:
            while True:
                ret, frame = self.cap.read()

                if not ret:
                    logger.info("End of video stream")
                    break

                # Process frame
                result = self.process_frame(frame)

                # Visualize
                if self.config.visualize:
                    annotated = self._annotate_frame(frame, result)

                    # Calculate and display FPS
                    fps_counter += 1
                    if time.time() - fps_timer >= 1.0:
                        fps = fps_counter / (time.time() - fps_timer)
                        fps_counter = 0
                        fps_timer = time.time()

                        cv2.putText(
                            annotated,
                            f"FPS: {fps:.1f}",
                            (10, annotated.shape[0] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 255, 0),
                            2,
                        )

                    cv2.imshow("Photo Behavior Detection", annotated)

                    # Save frame if recording
                    if self.video_writer and result:
                        self.video_writer.write(annotated)

                # Check for quit
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

        except KeyboardInterrupt:
            logger.info("Interrupted by user")

        finally:
            self.stop()

    def _annotate_frame(
        self,
        frame: np.ndarray,
        result: Optional[FusionResult],
    ) -> np.ndarray:
        """
        Annotate frame with detection results.

        Args:
            frame: Input frame
            result: Fusion result

        Returns:
            Annotated frame
        """
        annotated = frame.copy()

        if result:
            # Draw alert box
            color = (0, 0, 255)  # Red
            text = f"{result.action_type.name}: {result.confidence:.2f}"

            cv2.rectangle(
                annotated,
                (0, 0),
                (annotated.shape[1], 80),
                color,
                -1,
            )

            cv2.putText(
                annotated,
                "DETECTED!",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                annotated,
                text,
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )

        return annotated


class AsyncDetectionPipeline(DetectionPipeline):
    """
    Asynchronous pipeline for real-time processing with multi-threading.
    """

    def __init__(self, config: PipelineConfig):
        super().__init__(config)

        # Thread-safe queues
        self.frame_queue = Queue(maxsize=30)
        self.result_queue = Queue(maxsize=30)

        # Threads
        self.capture_thread = None
        self.process_thread = None

        # Synchronization
        self.running = False
        self.lock = Lock()

    def start(self):
        """Start the async pipeline."""
        super().start()

        self.running = True

        # Start capture thread
        self.capture_thread = Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()

        # Start process thread
        self.process_thread = Thread(target=self._process_loop, daemon=True)
        self.process_thread.start()

        logger.info("Async pipeline started")

    def stop(self):
        """Stop the async pipeline."""
        self.running = False

        if self.capture_thread:
            self.capture_thread.join(timeout=5)

        if self.process_thread:
            self.process_thread.join(timeout=5)

        super().stop()

    def _capture_loop(self):
        """Thread for capturing frames."""
        logger.info("Capture thread started")

        while self.running:
            ret, frame = self.cap.read()

            if not ret:
                logger.info("End of video stream in capture thread")
                break

            # Add to queue (non-blocking)
            try:
                self.frame_queue.put(frame, block=False)
            except:
                # Queue full, drop frame
                pass

        logger.info("Capture thread stopped")

    def _process_loop(self):
        """Thread for processing frames."""
        logger.info("Process thread started")

        while self.running:
            # Get frame from queue (blocking with timeout)
            try:
                frame = self.frame_queue.get(timeout=1.0)
            except:
                continue

            # Process frame
            result = self.process_frame(frame)

            # Add result to queue
            if result:
                self.result_queue.put((frame, result), block=False)

            # Visualize
            if self.config.visualize:
                annotated = self._annotate_frame(frame, result)
                cv2.imshow("Photo Behavior Detection (Async)", annotated)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    self.running = False

        logger.info("Process thread stopped")


def detection_callback(frame: np.ndarray, context: DetectionContext, result: FusionResult):
    """
    Example callback function for detections.

    Args:
        frame: The frame where detection occurred
        context: Detection context
        result: Fusion result
    """
    logger.info(
        f"Detection: {result.action_type.name} with confidence {result.confidence:.2f}"
    )

    # Save snapshot
    timestamp = int(time.time())
    filename = f"data/snapshots/detection_{timestamp}.jpg"
    cv2.imwrite(filename, frame)
    logger.info(f"Snapshot saved: {filename}")

    # Send alert (implement your alert mechanism here)
    # send_alert(result)


if __name__ == "__main__":
    # Configure logging
    logger.add("logs/detection_{time}.log", rotation="100 MB")

    # Create configuration
    config = PipelineConfig(
        source="0",  # Use webcam
        fps=30,
        width=1280,
        height=720,
        skip_frames=2,
        processing_fps=15,
        device="cuda",  # or "cpu"
        half_precision=True,
        visualize=True,
        save_video=True,
    )

    # Create pipeline
    pipeline = DetectionPipeline(config)
    pipeline.on_detection = detection_callback

    # Run
    try:
        pipeline.run()
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
