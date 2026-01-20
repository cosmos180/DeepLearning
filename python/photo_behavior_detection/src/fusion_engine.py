"""
Fusion Engine Module

Implements multi-modal fusion combining pose, device detection, and action recognition
to make final decisions about photo/video recording behavior.
"""

import cv2
import numpy as np
import torch
import torch.nn as nn
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import IntEnum
from collections import deque
from loguru import logger

try:
    from src.detector import Detection
    from src.pose_estimator import PoseFeatures
    from src.action_recognizer import ActionRecognizer
except ImportError:
    from detector import Detection
    from pose_estimator import PoseFeatures
    from action_recognizer import ActionRecognizer


class ActionType(IntEnum):
    """Action types."""
    NO_ACTION = 0
    TAKING_PHOTO = 1
    RECORDING_VIDEO = 2


@dataclass
class FusionResult:
    """Result of fusion engine."""
    action_type: ActionType
    confidence: float
    probabilities: Dict[str, float]  # Raw probabilities from each module
    metadata: Dict  # Additional metadata for debugging


@dataclass
class DetectionContext:
    """Context for a single detection."""
    person_detection: Optional[Detection]
    device_detections: List[Detection]
    pose_features: Optional[PoseFeatures]
    action_prediction: Optional[Tuple[int, float]]


class MultiModalFusion(nn.Module):
    """
    Neural network-based multi-modal fusion using attention mechanism.
    """

    def __init__(
        self,
        pose_dim: int = 256,
        device_dim: int = 128,
        spatial_dim: int = 64,
        hidden_dim: int = 256,
        num_classes: int = 3,
        dropout: float = 0.3,
    ):
        """
        Initialize the fusion model.

        Args:
            pose_dim: Pose feature dimension
            device_dim: Device detection feature dimension
            spatial_dim: Spatial relationship feature dimension
            hidden_dim: Hidden dimension for fusion
            num_classes: Number of output classes
            dropout: Dropout rate
        """
        super().__init__()

        # Feature projection layers
        self.pose_proj = nn.Linear(pose_dim, hidden_dim)
        self.device_proj = nn.Linear(device_dim, hidden_dim)
        self.spatial_proj = nn.Linear(spatial_dim, hidden_dim)

        # Cross-modal attention
        self.cross_attention = nn.MultiheadAttention(
            embed_dim=hidden_dim,
            num_heads=8,
            dropout=dropout,
            batch_first=True,
        )

        # Self-attention for refinement
        self.self_attention = nn.MultiheadAttention(
            embed_dim=hidden_dim,
            num_heads=8,
            dropout=dropout,
            batch_first=True,
        )

        # Fusion layers
        self.fusion = nn.Sequential(
            nn.Linear(hidden_dim * 3, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, num_classes),
        )

    def forward(
        self,
        pose_feat: torch.Tensor,
        device_feat: torch.Tensor,
        spatial_feat: torch.Tensor,
    ) -> torch.Tensor:
        """
        Forward pass.

        Args:
            pose_feat: Pose features [B, pose_dim]
            device_feat: Device detection features [B, device_dim]
            spatial_feat: Spatial relationship features [B, spatial_dim]

        Returns:
            Class logits [B, num_classes]
        """
        # Project features to common dimension
        pose_proj = self.pose_proj(pose_feat)  # [B, hidden_dim]
        device_proj = self.device_proj(device_feat)  # [B, hidden_dim]
        spatial_proj = self.spatial_proj(spatial_feat)  # [B, hidden_dim]

        # Stack as sequence
        features = torch.stack(
            [pose_proj, device_proj, spatial_proj], dim=1
        )  # [B, 3, hidden_dim]

        # Cross-modal attention
        crossed, _ = self.cross_attention(features, features, features)

        # Self-attention
        attended, _ = self.self_attention(crossed, crossed, crossed)

        # Flatten and classify
        fused = attended.view(attended.size(0), -1)  # [B, hidden_dim * 3]
        logits = self.fusion(fused)  # [B, num_classes]

        return logits


class DecisionFusion:
    """
    Rule-based decision fusion with probabilistic reasoning.
    """

    def __init__(
        self,
        weights: Dict[str, float] = None,
        enable_hmm: bool = True,
    ):
        """
        Initialize decision fusion.

        Args:
            weights: Weights for different modalities
            enable_hmm: Enable Hidden Markov Model for temporal consistency
        """
        self.weights = weights or {"pose": 0.4, "device": 0.3, "action": 0.3}

        # HMM for temporal consistency
        self.enable_hmm = enable_hmm
        if enable_hmm:
            self.hmm_states = [ActionType.NO_ACTION, ActionType.TAKING_PHOTO, ActionType.RECORDING_VIDEO]
            self.state_history = deque(maxlen=10)

        logger.info(f"Decision fusion initialized with weights: {self.weights}")

    def fuse(
        self,
        pose_prob: np.ndarray,
        device_prob: np.ndarray,
        action_prob: np.ndarray,
        context: DetectionContext,
    ) -> Tuple[ActionType, float, Dict]:
        """
        Fuse predictions from multiple modules.

        Args:
            pose_prob: Pose-based probabilities [3]
            device_prob: Device detection probabilities [N]
            action_prob: Action recognition probabilities [3]
            context: Detection context

        Returns:
            Tuple of (action_type, confidence, metadata)
        """
        # Ensure same shape
        if len(device_prob) > 3:
            device_prob = device_prob[:3]

        # Weighted fusion
        weighted_prob = (
            self.weights["pose"] * pose_prob
            + self.weights["device"] * device_prob
            + self.weights["action"] * action_prob
        )

        # Apply rule-based corrections
        corrected_prob = self._apply_rules(weighted_prob, context)

        # Normalize
        corrected_prob = corrected_prob / np.sum(corrected_prob)

        # Temporal smoothing with HMM
        if self.enable_hmm:
            corrected_prob = self._apply_hmm(corrected_prob)

        # Get final decision
        action_type = ActionType(np.argmax(corrected_prob))
        confidence = corrected_prob[action_type]

        # Metadata
        metadata = {
            "raw_probabilities": {
                "pose": pose_prob.tolist(),
                "device": device_prob.tolist(),
                "action": action_prob.tolist(),
            },
            "corrected_probabilities": corrected_prob.tolist(),
            "rules_applied": self._get_active_rules(context),
        }

        return action_type, confidence, metadata

    def _apply_rules(
        self,
        probabilities: np.ndarray,
        context: DetectionContext,
    ) -> np.ndarray:
        """Apply rule-based corrections."""
        corrected = probabilities.copy()

        # Rule 1: Device must be near hand
        if not self._check_device_near_hand(context):
            corrected[ActionType.TAKING_PHOTO] *= 0.1
            corrected[ActionType.RECORDING_VIDEO] *= 0.1

        # Rule 2: Arm must be elevated for photo
        if context.pose_features:
            arm_elevated = (
                context.pose_features.left_arm_angle > 45
                or context.pose_features.right_arm_angle > 45
            )
            if not arm_elevated:
                corrected[ActionType.TAKING_PHOTO] *= 0.3

        # Rule 3: High stability required for recording
        if context.pose_features:
            if context.pose_features.body_stability < 0.7:
                corrected[ActionType.RECORDING_VIDEO] *= 0.5

        # Rule 4: No devices detected
        if len(context.device_detections) == 0:
            corrected[ActionType.TAKING_PHOTO] *= 0.2
            corrected[ActionType.RECORDING_VIDEO] *= 0.2

        return corrected

    def _check_device_near_hand(
        self,
        context: DetectionContext,
        max_distance: float = 0.15,
    ) -> bool:
        """Check if device is near hand."""
        if not context.pose_features or len(context.device_detections) == 0:
            return False

        # Simple heuristic: if device detected and arms elevated
        return (
            context.pose_features.left_arm_angle > 30
            or context.pose_features.right_arm_angle > 30
        )

    def _apply_hmm(self, probabilities: np.ndarray) -> np.ndarray:
        """Apply HMM for temporal consistency."""
        if len(self.state_history) == 0:
            self.state_history.append(np.argmax(probabilities))
            return probabilities

        # Simple smoothing: favor previous state
        prev_state = self.state_history[-1]
        smoothed = probabilities.copy()

        # Boost probability of previous state
        smoothed[prev_state] *= 1.3

        # Renormalize
        smoothed = smoothed / np.sum(smoothed)

        # Update history
        self.state_history.append(np.argmax(smoothed))

        return smoothed

    def _get_active_rules(self, context: DetectionContext) -> List[str]:
        """Get list of active rules for debugging."""
        rules = []

        if not self._check_device_near_hand(context):
            rules.append("device_not_near_hand")

        if context.pose_features:
            if context.pose_features.left_arm_angle > 45 or context.pose_features.right_arm_angle > 45:
                rules.append("arm_elevated")

            if context.pose_features.body_stability > 0.7:
                rules.append("high_stability")

        if len(context.device_detections) == 0:
            rules.append("no_devices_detected")

        return rules


class FusionEngine:
    """
    High-level fusion engine coordinating all modules.
    """

    def __init__(
        self,
        fusion_method: str = "neural",  # "neural", "rule_based", "hybrid"
        device: str = "cuda",
        confidence_threshold: float = 0.8,
    ):
        """
        Initialize fusion engine.

        Args:
            fusion_method: Method for fusion
            device: Device for neural models
            confidence_threshold: Minimum confidence for alerts
        """
        self.fusion_method = fusion_method
        self.device = device
        self.confidence_threshold = confidence_threshold

        # Initialize fusion models
        if fusion_method in ["neural", "hybrid"]:
            self.neural_fusion = MultiModalFusion().to(device)
            self.neural_fusion.eval()

        if fusion_method in ["rule_based", "hybrid"]:
            self.decision_fusion = DecisionFusion()

        # Detection history for tracking
        self.detection_history = deque(maxlen=30)

        logger.info(f"Fusion engine initialized with method: {fusion_method}")

    def process(
        self,
        context: DetectionContext,
    ) -> Optional[FusionResult]:
        """
        Process a detection and make final decision.

        Args:
            context: Detection context with all modalities

        Returns:
            FusionResult or None if confidence too low
        """
        # Extract features for each modality
        pose_feat = self._extract_pose_features(context)
        device_feat = self._extract_device_features(context)
        spatial_feat = self._extract_spatial_features(context)

        # Get predictions from each modality
        pose_prob = self._predict_from_pose(context)
        device_prob = self._predict_from_device(context)
        action_prob = self._predict_from_action(context)

        # Fuse predictions
        if self.fusion_method == "neural":
            action_type, confidence, metadata = self._neural_fusion(
                pose_feat, device_feat, spatial_feat
            )
        elif self.fusion_method == "rule_based":
            action_type, confidence, metadata = self.decision_fusion.fuse(
                pose_prob, device_prob, action_prob, context
            )
        else:  # hybrid
            # Combine neural and rule-based
            result1 = self._neural_fusion(pose_feat, device_feat, spatial_feat)
            result2 = self.decision_fusion.fuse(
                pose_prob, device_prob, action_prob, context
            )

            # Average the probabilities
            combined_prob = (
                result1[1] * np.eye(3)[result1[0]]
                + result2[1] * np.eye(3)[result2[0]]
            ) / 2

            action_type = ActionType(np.argmax(combined_prob))
            confidence = combined_prob[action_type]

            metadata = {
                "neural": result1[2],
                "rule_based": result2[2],
            }

        # Filter by confidence threshold
        if confidence < self.confidence_threshold:
            return None

        # Create result
        result = FusionResult(
            action_type=action_type,
            confidence=confidence,
            probabilities={
                "pose": pose_prob.tolist() if isinstance(pose_prob, np.ndarray) else pose_prob,
                "device": device_prob.tolist() if isinstance(device_prob, np.ndarray) else device_prob,
                "action": action_prob.tolist() if isinstance(action_prob, np.ndarray) else action_prob,
            },
            metadata=metadata,
        )

        # Update history
        self.detection_history.append(result)

        return result

    def _extract_pose_features(self, context: DetectionContext) -> torch.Tensor:
        """Extract pose features for neural fusion."""
        if context.pose_features is None:
            return torch.zeros(1, 256).to(self.device)

        # Convert pose features to tensor
        # This is a simplified version - in practice, you'd extract more features
        features = np.array([
            context.pose_features.left_arm_angle,
            context.pose_features.right_arm_angle,
            context.pose_features.left_forearm_angle,
            context.pose_features.right_forearm_angle,
            context.pose_features.left_wrist_height,
            context.pose_features.right_wrist_height,
            context.pose_features.body_stability,
            int(context.pose_features.holding_device_left),
            int(context.pose_features.holding_device_right),
        ])

        # Pad to match expected dimension
        padded = np.pad(features, (0, 256 - len(features)), mode="constant")

        return torch.from_numpy(padded).float().unsqueeze(0).to(self.device)

    def _extract_device_features(self, context: DetectionContext) -> torch.Tensor:
        """Extract device detection features."""
        if len(context.device_detections) == 0:
            return torch.zeros(1, 128).to(self.device)

        # Simple features: number of devices, average confidence
        num_devices = len(context.device_detections)
        avg_conf = np.mean([d.confidence for d in context.device_detections])

        features = np.array([num_devices, avg_conf])

        # Pad
        padded = np.pad(features, (0, 128 - len(features)), mode="constant")

        return torch.from_numpy(padded).float().unsqueeze(0).to(self.device)

    def _extract_spatial_features(self, context: DetectionContext) -> torch.Tensor:
        """Extract spatial relationship features."""
        # Simple features
        features = np.zeros(64)

        # In practice, extract spatial relationships between person and devices
        # between hands and devices, etc.

        return torch.from_numpy(features).float().unsqueeze(0).to(self.device)

    def _predict_from_pose(self, context: DetectionContext) -> np.ndarray:
        """Get prediction from pose features."""
        if context.pose_features is None:
            return np.array([0.9, 0.05, 0.05])

        # Rule-based prediction
        # Placeholder - implement actual prediction logic
        return np.array([0.5, 0.3, 0.2])

    def _predict_from_device(self, context: DetectionContext) -> np.ndarray:
        """Get prediction from device detection."""
        if len(context.device_detections) == 0:
            return np.array([0.95, 0.03, 0.02])

        # Placeholder
        return np.array([0.3, 0.5, 0.2])

    def _predict_from_action(self, context: DetectionContext) -> np.ndarray:
        """Get prediction from action recognizer."""
        if context.action_prediction is None:
            return np.array([0.7, 0.2, 0.1])

        class_id, confidence = context.action_prediction
        prob = np.zeros(3)
        prob[class_id] = confidence
        prob = prob / np.sum(prob)

        return prob

    def _neural_fusion(
        self,
        pose_feat: torch.Tensor,
        device_feat: torch.Tensor,
        spatial_feat: torch.Tensor,
    ) -> Tuple[ActionType, float, Dict]:
        """Perform neural fusion."""
        with torch.no_grad():
            logits = self.neural_fusion(pose_feat, device_feat, spatial_feat)
            probs = torch.softmax(logits, dim=-1)
            confidence, pred_class = torch.max(probs, dim=-1)

        action_type = ActionType(pred_class.item())

        metadata = {
            "neural_probabilities": probs.cpu().numpy().tolist(),
        }

        return action_type, confidence.item(), metadata

    def visualize(
        self,
        frame: np.ndarray,
        context: DetectionContext,
        result: Optional[FusionResult] = None,
    ) -> np.ndarray:
        """
        Visualize fusion results on frame.

        Args:
            frame: Input image
            context: Detection context
            result: Fusion result

        Returns:
            Annotated image
        """
        annotated = frame.copy()

        # Draw person detection
        if context.person_detection:
            x1, y1, x2, y2 = context.person_detection.to_absolute(
                frame.shape[1], frame.shape[0]
            )
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (255, 0, 0), 2)

        # Draw device detections
        for device in context.device_detections:
            x1, y1, x2, y2 = device.to_absolute(frame.shape[1], frame.shape[0])
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Draw result
        if result:
            action_name = result.action_type.name
            text = f"{action_name}: {result.confidence:.2f}"

            # Choose color based on action
            if result.action_type == ActionType.TAKING_PHOTO:
                color = (0, 0, 255)  # Red
            elif result.action_type == ActionType.RECORDING_VIDEO:
                color = (0, 165, 255)  # Orange
            else:
                color = (0, 255, 0)  # Green

            cv2.putText(
                annotated,
                text,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                color,
                2,
            )

        return annotated


if __name__ == "__main__":
    # Test the fusion engine
    engine = FusionEngine(fusion_method="hybrid", device="cpu")

    # Create fake context
    context = DetectionContext(
        person_detection=None,
        device_detections=[],
        pose_features=None,
        action_prediction=None,
    )

    result = engine.process(context)

    if result:
        print(f"Action: {result.action_type.name}, Confidence: {result.confidence:.2f}")
    else:
        print("No action detected")
