"""
Action Recognition Module

Implements temporal action recognition using LSTM/Transformer models
to classify photo-taking and video recording behaviors.
"""

import cv2
import numpy as np
import torch
import torch.nn as nn
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from collections import deque
from loguru import logger

try:
    from src.pose_estimator import PoseLandmarks, PoseFeatures
except ImportError:
    from pose_estimator import PoseLandmarks, PoseFeatures


@dataclass
class TemporalSegment:
    """A temporal segment of video frames with associated data."""
    frames: List[np.ndarray]  # Raw frames
    poses: List[PoseLandmarks]  # Pose landmarks for each frame
    features: List[PoseFeatures]  # Extracted features for each frame
    timestamps: List[float]  # Timestamp for each frame


class PoseFeatureEncoder(nn.Module):
    """
    Encodes pose features into a fixed-dimensional representation.
    """

    def __init__(self, input_dim: int = 99, hidden_dim: int = 256):
        """
        Args:
            input_dim: Dimension of input pose features (33 landmarks * 3 coords)
            hidden_dim: Output feature dimension
        """
        super().__init__()

        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 512),
            nn.ReLU(),
            nn.BatchNorm1d(512),
            nn.Dropout(0.2),
            nn.Linear(512, hidden_dim),
            nn.ReLU(),
            nn.BatchNorm1d(hidden_dim),
        )

    def forward(self, pose_landmarks: torch.Tensor) -> torch.Tensor:
        """
        Encode pose landmarks.

        Args:
            pose_landmarks: Tensor of shape [B, 33, 3] or [B, T, 33, 3]

        Returns:
            Encoded features: [B, hidden_dim] or [B, T, hidden_dim]
        """
        if pose_landmarks.dim() == 4:
            # Batch of sequences: [B, T, 33, 3]
            B, T = pose_landmarks.shape[:2]
            pose_flat = pose_landmarks.view(B * T, -1)
            encoded = self.encoder(pose_flat)
            return encoded.view(B, T, -1)
        else:
            # Single frame: [B, 33, 3]
            pose_flat = pose_landmarks.view(pose_landmarks.size(0), -1)
            return self.encoder(pose_flat)


class TemporalActionClassifier(nn.Module):
    """
    LSTM-based temporal action classifier for photo/video detection.
    """

    def __init__(
        self,
        input_dim: int = 99,  # 33 landmarks * 3 coordinates
        hidden_dim: int = 256,
        num_layers: int = 2,
        num_classes: int = 3,  # [no_action, taking_photo, recording]
        dropout: float = 0.3,
        bidirectional: bool = True,
    ):
        """
        Initialize the temporal action classifier.

        Args:
            input_dim: Input feature dimension
            hidden_dim: LSTM hidden dimension
            num_layers: Number of LSTM layers
            num_classes: Number of action classes
            dropout: Dropout rate
            bidirectional: Use bidirectional LSTM
        """
        super().__init__()

        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.num_classes = num_classes
        self.bidirectional = bidirectional

        # Pose encoder
        self.pose_encoder = PoseFeatureEncoder(input_dim, hidden_dim)

        # LSTM for temporal modeling
        self.lstm = nn.LSTM(
            input_size=hidden_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=bidirectional,
            dropout=dropout if num_layers > 1 else 0,
        )

        lstm_output_dim = hidden_dim * 2 if bidirectional else hidden_dim

        # Attention mechanism
        self.attention = nn.MultiheadAttention(
            embed_dim=lstm_output_dim,
            num_heads=8,
            dropout=dropout,
            batch_first=True,
        )

        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(lstm_output_dim, 128),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, num_classes),
        )

    def forward(
        self,
        pose_sequence: torch.Tensor,
    ) -> torch.Tensor:
        """
        Forward pass.

        Args:
            pose_sequence: Pose landmark sequence [B, T, 33, 3]

        Returns:
            Class logits [B, num_classes]
        """
        B, T, _, _ = pose_sequence.shape

        # Encode poses
        # pose_encoder expects [B, 33, 3] or [B, T, 33, 3]
        encoded = self.pose_encoder(pose_sequence)  # [B, T, hidden_dim]

        # LSTM temporal modeling
        lstm_out, (h_n, c_n) = self.lstm(encoded)  # [B, T, lstm_output_dim]

        # Self-attention
        attended_out, attention_weights = self.attention(
            lstm_out, lstm_out, lstm_out
        )  # [B, T, lstm_output_dim]

        # Use the last timestep
        final_out = attended_out[:, -1, :]  # [B, lstm_output_dim]

        # Classify
        logits = self.classifier(final_out)  # [B, num_classes]

        return logits

    def predict(
        self,
        pose_sequence: torch.Tensor,
    ) -> Tuple[int, float]:
        """
        Make a prediction.

        Args:
            pose_sequence: Pose landmark sequence [T, 33, 3]

        Returns:
            Tuple of (predicted_class, confidence)
        """
        self.eval()
        with torch.no_grad():
            # Add batch dimension
            if pose_sequence.dim() == 3:
                pose_sequence = pose_sequence.unsqueeze(0)

            logits = self.forward(pose_sequence)
            probs = torch.softmax(logits, dim=-1)
            confidence, pred_class = torch.max(probs, dim=-1)

            return pred_class.item(), confidence.item()


class ActionRecognizer:
    """
    High-level action recognition system.
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        sequence_length: int = 16,
        hidden_dim: int = 256,
        num_classes: int = 3,
        device: str = "cuda",
        confidence_threshold: float = 0.7,
    ):
        """
        Initialize the action recognizer.

        Args:
            model_path: Path to pretrained model weights
            sequence_length: Number of frames for temporal analysis
            hidden_dim: LSTM hidden dimension
            num_classes: Number of action classes
            device: Device to run inference on
            confidence_threshold: Minimum confidence for predictions
        """
        self.sequence_length = sequence_length
        self.num_classes = num_classes
        self.device = device
        self.confidence_threshold = confidence_threshold

        # Initialize model
        self.model = TemporalActionClassifier(
            input_dim=99,
            hidden_dim=hidden_dim,
            num_classes=num_classes,
        ).to(device)

        # Load pretrained weights if provided
        if model_path:
            logger.info(f"Loading model from {model_path}")
            checkpoint = torch.load(model_path, map_location=device)
            if "model_state_dict" in checkpoint:
                self.model.load_state_dict(checkpoint["model_state_dict"])
            else:
                self.model.load_state_dict(checkpoint)
            logger.info("Model loaded successfully")

        self.model.eval()

        # Frame buffer
        self.frame_buffer = deque(maxlen=sequence_length)
        self.pose_buffer = deque(maxlen=sequence_length)

        # Class names
        self.class_names = ["no_action", "taking_photo", "recording"]

        logger.info("Action recognizer initialized")

    def update(
        self,
        frame: np.ndarray,
        pose_landmarks: Optional[PoseLandmarks],
    ) -> Optional[Tuple[int, float]]:
        """
        Update with a new frame and get prediction if buffer is full.

        Args:
            frame: New video frame
            pose_landmarks: Pose landmarks for this frame

        Returns:
            Tuple of (predicted_class, confidence) or None if buffer not full
        """
        # Add to buffers
        self.frame_buffer.append(frame)
        if pose_landmarks is not None:
            self.pose_buffer.append(pose_landmarks)

        # Check if we have enough frames
        if len(self.pose_buffer) < self.sequence_length:
            return None

        # Prepare input
        pose_sequence = self._prepare_sequence()

        # Make prediction
        pred_class, confidence = self.model.predict(pose_sequence)

        # Filter by confidence threshold
        if confidence < self.confidence_threshold:
            return None

        return (pred_class, confidence)

    def _prepare_sequence(self) -> torch.Tensor:
        """
        Prepare pose sequence for model input.

        Returns:
            Tensor of shape [1, T, 33, 3]
        """
        # Get the most recent poses
        poses = list(self.pose_buffer)[-self.sequence_length :]

        # Stack into array
        pose_array = np.stack([p.landmarks for p in poses], axis=0)  # [T, 33, 3]

        # Convert to tensor
        pose_tensor = torch.from_numpy(pose_array).float().to(self.device)

        # Add batch dimension
        pose_tensor = pose_tensor.unsqueeze(0)  # [1, T, 33, 3]

        return pose_tensor

    def get_action_name(self, class_id: int) -> str:
        """Get human-readable action name."""
        return self.class_names[class_id]

    def reset(self):
        """Clear the frame and pose buffers."""
        self.frame_buffer.clear()
        self.pose_buffer.clear()

    def train(
        self,
        train_loader,
        val_loader=None,
        num_epochs=100,
        learning_rate=0.001,
        device="cuda",
    ):
        """
        Train the model.

        Args:
            train_loader: Training data loader
            val_loader: Validation data loader
            num_epochs: Number of training epochs
            learning_rate: Learning rate
            device: Device to train on
        """
        self.model.train()

        optimizer = torch.optim.AdamW(self.model.parameters(), lr=learning_rate)
        criterion = nn.CrossEntropyLoss()

        best_val_loss = float("inf")

        for epoch in range(num_epochs):
            # Training
            train_loss = 0.0
            for batch_idx, (pose_sequence, labels) in enumerate(train_loader):
                pose_sequence = pose_sequence.to(device)  # [B, T, 33, 3]
                labels = labels.to(device)  # [B]

                optimizer.zero_grad()

                # Forward pass
                logits = self.model(pose_sequence)

                # Compute loss
                loss = criterion(logits, labels)

                # Backward pass
                loss.backward()
                optimizer.step()

                train_loss += loss.item()

            avg_train_loss = train_loss / len(train_loader)

            # Validation
            if val_loader:
                val_loss, val_acc = self._evaluate(val_loader, device)
                logger.info(
                    f"Epoch {epoch + 1}/{num_epochs} - "
                    f"Train Loss: {avg_train_loss:.4f}, "
                    f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}"
                )

                # Save best model
                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    self._save_checkpoint("best_model.pth", epoch, optimizer)
            else:
                logger.info(f"Epoch {epoch + 1}/{num_epochs} - Train Loss: {avg_train_loss:.4f}")

            # Save checkpoint
            if (epoch + 1) % 10 == 0:
                self._save_checkpoint(f"checkpoint_epoch_{epoch + 1}.pth", epoch, optimizer)

        logger.info("Training completed")

    def _evaluate(self, val_loader, device):
        """Evaluate the model."""
        self.model.eval()

        val_loss = 0.0
        correct = 0
        total = 0

        criterion = nn.CrossEntropyLoss()

        with torch.no_grad():
            for pose_sequence, labels in val_loader:
                pose_sequence = pose_sequence.to(device)
                labels = labels.to(device)

                logits = self.model(pose_sequence)
                loss = criterion(logits, labels)

                val_loss += loss.item()

                _, predicted = torch.max(logits, dim=-1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()

        self.model.train()

        avg_val_loss = val_loss / len(val_loader)
        accuracy = correct / total

        return avg_val_loss, accuracy

    def _save_checkpoint(self, path, epoch, optimizer):
        """Save model checkpoint."""
        checkpoint = {
            "epoch": epoch,
            "model_state_dict": self.model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
        }
        torch.save(checkpoint, path)
        logger.info(f"Checkpoint saved to {path}")

    def export_to_onnx(self, output_path: str, sequence_length: int = 16):
        """
        Export model to ONNX format.

        Args:
            output_path: Path to save ONNX model
            sequence_length: Fixed sequence length for exported model
        """
        self.model.eval()

        # Create dummy input
        dummy_input = torch.randn(1, sequence_length, 33, 3).to(self.device)

        # Export
        torch.onnx.export(
            self.model,
            dummy_input,
            output_path,
            export_params=True,
            opset_version=17,
            input_names=["pose_sequence"],
            output_names=["logits"],
            dynamic_axes={
                "pose_sequence": {0: "batch_size", 1: "sequence_length"},
                "logits": {0: "batch_size"},
            },
        )

        logger.info(f"Model exported to ONNX: {output_path}")


class FrameBuffer:
    """
    Manages temporal frame buffer with efficient memory usage.
    """

    def __init__(self, max_length: int = 32, fps: int = 30):
        """
        Args:
            max_length: Maximum number of frames to store
            fps: Video frame rate
        """
        self.max_length = max_length
        self.fps = fps
        self.buffer = deque(maxlen=max_length)
        self.timestamps = deque(maxlen=max_length)

    def add_frame(self, frame: np.ndarray, timestamp: float):
        """Add a frame to the buffer."""
        self.buffer.append(frame)
        self.timestamps.append(timestamp)

    def get_sequence(self, length: int) -> Optional[List[np.ndarray]]:
        """Get the most recent N frames."""
        if len(self.buffer) < length:
            return None
        return list(self.buffer)[-length:]

    def get_temporal_segment(
        self,
        start_offset: float,
        end_offset: float,
        current_time: float,
    ) -> List[np.ndarray]:
        """
        Get frames within a time window.

        Args:
            start_offset: Start offset from current time (seconds)
            end_offset: End offset from current time (seconds)
            current_time: Current timestamp

        Returns:
            List of frames in the time window
        """
        start_time = current_time - start_offset
        end_time = current_time - end_offset

        indices = [
            i
            for i, ts in enumerate(self.timestamps)
            if start_time <= ts <= end_time
        ]

        return [self.buffer[i] for i in indices]

    def clear(self):
        """Clear the buffer."""
        self.buffer.clear()
        self.timestamps.clear()

    def __len__(self):
        return len(self.buffer)


if __name__ == "__main__":
    # Test the action recognizer
    recognizer = ActionRecognizer(device="cpu")

    # Simulate some frames
    for i in range(20):
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

        # Create fake pose landmarks
        pose_landmarks = np.random.rand(33, 3).astype(np.float32)
        pose = PoseLandmarks(
            landmarks=pose_landmarks,
            world_landmarks=pose_landmarks,
            visibility=np.ones(33),
        )

        result = recognizer.update(frame, pose)

        if result:
            pred_class, confidence = result
            print(f"Prediction: {recognizer.get_action_name(pred_class)} ({confidence:.2f})")
