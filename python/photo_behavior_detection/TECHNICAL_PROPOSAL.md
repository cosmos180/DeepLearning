# 拍照/录制行为检测系统技术方案

## 1. 系统概述

### 1.1 任务定义
检测人们在公共场所或特定场景中使用手机、相机等电子设备进行拍照或录制视频的行为。

### 1.2 应用场景
- 博物馆/艺术馆禁止拍照区域监控
- 隐私敏感场所行为管理
- 商业机密保护区域监控
- 演出/会议现场的版权保护

### 1.3 技术挑战
- 视角多样性：正面、侧面、背面
- 设备多样性：手机、相机、平板、运动相机
- 环境复杂性：光照变化、遮挡、人群密集
- 行为模糊性：拍照vs查看手机、录制vs观看视频

---

## 2. 算法技术路线

### 2.1 多线索融合检测框架

采用**多任务联合学习**策略，融合以下检测线索：

#### 2.1.1 人体姿态分析
**核心思路**：拍照行为具有特征性姿态模式

关键姿态特征：
- **手臂角度**：举起设备时，上臂与身体夹角 > 45°，前臂与上臂夹角 < 90°
- **头部姿态**：低头看屏幕（俯仰角 -30° ~ -60°）或平视取景
- **手部位置**：双手持机（手机居中）或单手持机（相机右侧）
- **肩膀高度**：持机侧肩膀可能抬高
- **身体稳定性**：拍照时身体相对静止 vs 走路时摆动

技术实现：
- **姿态估计模型**：MediaPipe Pose / OpenPose / ViTPose
- **关键点提取**：33点全身关键点 (MediaPipe) 或 25点 (OpenPose)
- **时序平滑**：使用卡尔曼滤波或指数移动平均减少抖动

#### 2.1.2 设备目标检测
**核心思路**：直接识别手机、相机等设备本体

检测策略：
- **常规检测**：YOLOv8/v10 / EfficientDet / RT-DETR
- **小目标优化**：手机在远距离呈现小目标，需要专门优化
- **设备分类**：
  - 智能手机（多尺寸、多姿态）
  - 单反/微单相机
  - 平板电脑（横屏/竖屏）
  - 运动相机（GoPro等）
  - 无人机/云台相机

难点：
- 设备与手部粘连，需要语义分割辅助
- 金属表面反光影响检测
- 被遮挡设备的部分可见检测

#### 2.1.3 动作识别与行为分析
**核心思路**：识别拍照/录制的动作序列

时序行为特征：
- **短时动作（2-5秒）**：
  - 举起设备 → 稳定 → 按下快门 → 放下
  - 点亮屏幕 → 取景 → 录制 → 停止
- **长时行为（>10秒）**：
  - 持续录制姿态（手臂稳定、设备持续举起）
  - 移动拍摄（边走边拍）

技术方案：
- **轻量方案**：基于姿态关键点的时序特征 + LSTM/GRU
- **中等方案**：I3D (Inflated 3D ConvNet) / SlowFast
- **高精度方案**：VideoMAE / ViViT / TimeSformer

特征工程：
- 关键点轨迹（手腕、肘部的移动轨迹）
- 光流特征（设备举起/放下的运动模式）
- 姿态变化率（手臂角度的时序导数）

#### 2.1.4 环境线索检测
**核心思路**：利用拍照产生的视觉副作用

**闪光灯检测**：
- 帧间差分检测亮度突变
- HSV颜色空间检测白色高亮区域
- 闪光灯光谱特征分析

**屏幕反光检测**：
- 面部高光区域识别
- 屏幕光在眼镜、脸部的反射模式
- 使用分割模型提取面部区域后分析

**LED指示灯**：
- 相机录制指示灯（红点）检测
- 夜间场景的手机补光灯

### 2.2 多阶段检测架构

#### 阶段1：快速筛查
- **目标**：实时处理，高召回率，允许误报
- **方法**：轻量目标检测 + 姿态粗分析
- **模型**：YOLOv8-Nano / MobileNet-SSD
- **输出**：疑似拍照区域候选框

#### 阶段2：精细分析
- **目标**：精确分类，降低误报
- **方法**：高精度姿态估计 + 设备检测 + 动作识别
- **模型**：YOLOv8-Medium + MediaPipe Pose + Temporal Model
- **输入**：阶段1的候选框 + 时序窗口（前后N帧）

#### 阶段3：后处理融合
- **目标**：最终决策，输出结果
- **方法**：多线索融合 + 时序一致性检查
- **技术**：
  - 贝叶斯融合各线索概率
  - 隐马尔可夫模型(HMM)建模状态转移
  - 规则过滤（如：设备必须位于人手附近）

---

## 3. 模型选型与对比

### 3.1 目标检测模型

| 模型 | mAP | FPS (GPU) | FPS (CPU) | 参数量 | 推荐场景 |
|------|-----|-----------|-----------|--------|----------|
| YOLOv8-Nano | 37.3 | 80+ | 10-15 | 3.2M | 边缘设备、实时筛查 |
| YOLOv8-Small | 44.9 | 150+ | 20-30 | 11.2M | 平衡性能与速度 |
| YOLOv8-Medium | 50.2 | 120+ | 10-20 | 25.9M | 高精度检测 |
| YOLOv10-B | 53.2 | 70+ | 8-12 | 19.1M | 新架构，推荐使用 |
| RT-DETR-R18 | 48.5 | 90+ | 12-18 | 20M | Transformer架构 |
| EfficientDet-D1 | 49.7 | 60+ | 5-10 | 7.8M | 轻量高效 |

**推荐选择**：
- **主检测模型**：YOLOv8-Medium 或 YOLOv10-B
- **边缘部署**：YOLOv8-Nano 或量化后的版本
- **训练策略**：COCO预训练 + 自定义数据微调

### 3.2 姿态估计模型

| 模型 | 输入分辨率 | 关键点数 | GPU FPS | CPU FPS | 特点 |
|------|-----------|----------|---------|---------|------|
| MediaPipe Pose | 256x256 | 33 | 120+ | 30-50 | 轻量、跨平台、包含手部 |
| OpenPose | 368x368 (body) | 25 | 45+ | 5-10 | 开源、多精度 |
| ViTPose-S | 256x192 | 17 | 80+ | 8-12 | Transformer、高精度 |
| HRNet-W32 | 384x288 | 17 | 60+ | 3-5 | 高分辨率精度 |

**推荐选择**：**MediaPipe Pose**
- 理由：
  - 轻量高效，适合实时系统
  - 33个关键点包含完整手部和足部
  - CPU性能优秀，便于边缘部署
  - 提供世界坐标（3D），可计算深度信息
  - 跨平台支持（Python/C++/Mobile）

### 3.3 动作识别模型

| 模型 | 输入长度 | GPU FPS | 精度(Kinetics) | 特点 |
|------|----------|---------|----------------|------|
| Temporal Conv + LSTM | 16帧 | 200+ | 中等 | 轻量、基于关键点 |
| I3D (RGB) | 64帧 | 50+ | 高 | 双流(RGB+光流) |
| SlowFast-R50 | 32×8+4 | 40+ | 高 | 多时间尺度 |
| VideoMAE-ViT-S | 16帧 | 30+ | 高 | 掩码自编码、强泛化 |
| X3D-M | 16帧 | 80+ | 高 | 扩展3D卷积、平衡 |

**推荐选择**：根据场景选择
- **低延迟场景**：基于姿态关键点的LSTM/GRU时序模型
- **高精度场景**：VideoMAE-ViT-S 或 X3D-M
- **边缘场景**：MobileNetV3 + Temporal Convolution

### 3.4 时序建模方案

#### 方案A：基于关键点的轻量时序模型
```python
# 伪代码框架
class KeypointTemporalModel(nn.Module):
    def __init__(self):
        self.pose_encoder = PoseKeypointEncoder()  # 编码单帧姿态
        self.temporal_model = nn.GRU(
            input_size=256,
            hidden_size=128,
            num_layers=2,
            bidirectional=True
        )
        self.classifier = nn.Sequential(
            nn.Linear(256, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 3)  # [无行为, 拍照, 录制]
        )

    def forward(self, keypoint_sequence):  # [B, T, 33, 3]
        features = [self.pose_encoder(kp) for kp in keypoint_sequence]
        features = torch.stack(features, dim=1)  # [B, T, 256]
        temporal_out, _ = self.temporal_model(features)
        out = self.classifier(temporal_out[:, -1, :])  # 用最后时刻
        return out
```

#### 方案B：基于视频的3D CNN
使用预训练的I3D/SlowFast模型，在自定义数据上微调。

---

## 4. 数据需求与标注策略

### 4.1 数据类型

#### 4.1.1 原始视频数据
**场景多样性**：
- 室内场景：博物馆、画廊、会议室、商场、办公室
- 室外场景：街道、广场、景点、公园
- 光照条件：白天、夜晚、逆光、室内灯光
- 角度多样性：监控摄像头视角（俯视）、平视、广角

**设备多样性**：
- 智能手机：各品牌、尺寸、颜色（黑色、白色、彩色）
- 相机：单反、微单、卡片机、运动相机
- 平板：iPad、安卓平板
- 其他：云台、手持稳定器

**行为多样性**：
- 拍照：横屏、竖屏、自拍、合影、俯拍
- 录制：手持录制、边走边拍、静止录制、自拍录制
- 干扰行为：查看手机、打电话、玩游戏、导航

#### 4.1.2 标注需求

**层级1：目标检测标注**
```
格式：COCO/YOLO
类别：
- 0: person (人)
- 1: smartphone (智能手机)
- 2: camera (相机)
- 3: tablet (平板)
- 4: recording_device (录制设备，如GoPro)
```

**层级2：姿态标注**
- 使用MediaPipe自动标注，人工修正
- 关键键点：手腕、肘部、肩膀、头部、设备位置

**层级3：行为标注**
```
时间段标注：
[Start Frame, End Frame, Label]
Label：
- 0: no_action (无拍照行为)
- 1: taking_photo (拍照行为)
- 2: recording_video (录制视频)
- 3: viewing_device (查看设备，负样本)
- 4: calling_phone (打电话，负样本)
```

**层级4：属性标注**
```
额外标签：
- device_orientation: horizontal/vertical (设备方向)
- holding_style: single_hand/double_hands (持握方式)
- position: standing/sitting/walking (体位)
- camera_angle: front/side/back (相机角度)
```

### 4.2 数据集构建策略

#### 4.2.1 正样本（拍照/录制）
**采集方式**：
1. 受控采集：雇佣演员在不同场景摆拍
2. 网络爬取：YouTube、Pexels、Pixabay等视频网站
3. 数据合成：使用3D人体模型 + 设备模型合成

**目标数量**：
- 拍照视频：5000+ 段，每段3-10秒
- 录制视频：3000+ 段，每段5-30秒

#### 4.2.2 负样本（相似但非目标行为）
**关键负样本**：
- 查看手机（最难区分）
- 打电话
- 玩游戏
- 阅读电子书
- 使用导航
- 仅仅是手持设备但未拍照

**正负比**：1:2 或 1:3（负样本多于正样本）

### 4.3 数据增强策略

#### 空间增强
- 随机裁剪和缩放（模拟远近变化）
- 水平翻转（注意镜像对称性）
- 颜色抖动（亮度、对比度、饱和度、色调）
- 高斯模糊（模拟运动模糊）
- 遮挡增强（随机遮挡矩形，模拟人群遮挡）

#### 时序增强
- 时序裁剪：随机选择连续帧片段
- 帧率抖动：随机丢帧（模拟不同帧率）
- 时序反转：部分场景可逆
- 速度变化：0.8x - 1.2x 慢放/快放

#### 混合增强
- MixUp：混合不同视频片段
- CutMix：时空域的混合
- Mosaic：4个视频拼接（YOLO风格）

---

## 5. 系统架构设计

### 5.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                     Input Video Stream                       │
│                   (RTSP/RTMP/File/USB)                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Frame Extractor                           │
│              (Decoding + Buffer Management)                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                 Stage 1: Fast Screening                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  YOLOv8-Nano Detection (Person + Device)           │   │
│  │  ↓                                                   │   │
│  │  ROI Selection (Persons with devices nearby)       │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │ Suspicious ROIs
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                 Stage 2: Fine-grained Analysis              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Sub-task A: Pose Estimation (MediaPipe)           │   │
│  │  ┌──────────────────────────────────────────────┐  │   │
│  │  │ Extract: Arm angles, Head pose, Hand pos    │  │   │
│  │  └──────────────────────────────────────────────┘  │   │
│  │                                                      │   │
│  │  Sub-task B: Device Detection (YOLOv8-M)           │   │
│  │  ┌──────────────────────────────────────────────┐  │   │
│  │  │ Classify: Phone type, Camera, Tablet        │  │   │
│  │  └──────────────────────────────────────────────┘  │   │
│  │                                                      │   │
│  │  Sub-task C: Action Recognition (Temporal Model)   │   │
│  │  ┌──────────────────────────────────────────────┐  │   │
│  │  │ Input: Keypoint sequence (16 frames)         │  │   │
│  │  │ Output: Photo/Video/None probability         │  │   │
│  │  └──────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │ Features: Pose + Device + Action
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Stage 3: Fusion & Decision                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Multi-cue Fusion Module                           │   │
│  │  - Spatial Consistency Check                       │   │
│  │  - Temporal Smoothing (HMM/Bayesian)               │   │
│  │  - Rule-based Filtering                            │   │
│  │    * Device must be near hand                      │   │
│  │    * Arm angle must be elevated                    │   │
│  │    * Action sequence must be consistent            │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │ Final Decision
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                      Output Module                          │
│  - Alert Trigger (API/Webhook/Email)                       │
│  - Visualization Overlay (Bounding box + Label)            │
│  - Event Logging (Timestamp, Confidence, Snapshot)         │
│  - Recording Clip Export                                   │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 模块划分

#### 5.2.1 核心模块

**1. 视频输入模块** (`video_input.py`)
```python
class VideoInputStream:
    """支持多源视频输入"""
    - RTSP/RTMP流
    - 本地视频文件
    - USB摄像头
    - 帧缓冲管理
    - 帧率控制
```

**2. 检测器模块** (`detector.py`)
```python
class DeviceDetector:
    """设备目标检测"""
    - YOLO模型加载和推理
    - NMS后处理
    - 设备分类

class PersonDetector:
    """人员检测"""
    - 检测画面中所有人
    - 输出边界框和置信度
```

**3. 姿态估计模块** (`pose_estimator.py`)
```python
class PoseEstimator:
    """人体姿态分析"""
    - MediaPipe Pose集成
    - 关键点提取
    - 姿态特征计算（角度、位置）
    - 3D坐标转换
```

**4. 动作识别模块** (`action_recognizer.py`)
```python
class ActionRecognizer:
    """时序动作识别"""
    - 帧序列缓冲
    - LSTM/Transformer模型推理
    - 动作分类输出
    - 置信度平滑
```

**5. 融合决策模块** (`fusion_engine.py`)
```python
class FusionEngine:
    """多线索融合决策"""
    - 特征拼接
    - 贝叶斯融合
    - 规则过滤
    - HMM状态追踪
    - 最终决策输出
```

**6. 告警输出模块** (`alert_system.py`)
```python
class AlertSystem:
    """告警和输出"""
    - 告警触发（API调用）
    - 可视化绘制
    - 事件日志
    - 视频片段保存
```

#### 5.2.2 配置模块

**7. 配置管理** (`config.py`)
```python
class Config:
    """系统配置"""
    - 模型路径
    - 阈值参数
    - 视频源配置
    - 告警设置
```

**8. 日志模块** (`logger.py`)
```python
class SystemLogger:
    """日志记录"""
    - 推理时间统计
    - 错误日志
    - 性能指标记录
```

### 5.3 接口设计

#### REST API接口
```python
# 启动检测服务
POST /api/detection/start
{
    "video_source": "rtsp://...",
    "config": {...}
}

# 停止检测
POST /api/detection/stop

# 获取实时事件
GET /api/events/stream

# 历史事件查询
GET /api/events?start_time=...&end_time=...

# 配置更新
PUT /api/config
```

#### WebSocket接口
```python
# 实时检测结果推送
WS /ws/detection
{
    "frame_id": 12345,
    "timestamp": "2024-01-19T10:30:00Z",
    "events": [
        {
            "type": "photo_detected",
            "confidence": 0.92,
            "bbox": [x, y, w, h],
            "snapshot": "base64..."
        }
    ]
}
```

---

## 6. 实现细节

### 6.1 姿态特征工程

#### 6.1.1 关键特征定义

**手臂角度特征**
```python
def calculate_arm_angle(shoulder, elbow, wrist):
    """计算上臂与身体夹角"""
    # 向量: shoulder -> elbow
    upper_arm = elbow - shoulder
    # 身体参考向量: 垂直向下
    vertical = np.array([0, 1])
    # 计算夹角
    angle = arccos(dot(upper_arm, vertical) / (norm(upper_arm) * norm(vertical)))
    return degrees(angle)

def calculate_forearm_angle(elbow, wrist):
    """计算前臂与上臂夹角"""
    # 向量: elbow -> wrist 和 elbow -> shoulder
    forearm = wrist - elbow
    upper_arm_rev = shoulder - elbow
    angle = arccos(dot(forearm, upper_arm_rev) / (norm(forearm) * norm(upper_arm_rev)))
    return degrees(angle)
```

**拍照判定规则**
```python
def is_photo_pose(landmarks):
    """基于姿态特征判定拍照姿势"""
    # 关键点索引 (MediaPipe Pose 33点)
    left_shoulder = landmarks[11]
    left_elbow = landmarks[13]
    left_wrist = landmarks[15]
    right_shoulder = landmarks[12]
    right_elbow = landmarks[14]
    right_wrist = landmarks[16]

    # 计算手臂角度
    left_arm_angle = calculate_arm_angle(left_shoulder, left_elbow, left_wrist)
    right_arm_angle = calculate_arm_angle(right_shoulder, right_elbow, right_wrist)

    # 判定条件
    elevated_arm = (left_arm_angle > 45) or (right_arm_angle > 45)
    device_at_height = (left_wrist.y < shoulder.y - 0.1) or (right_wrist.y < shoulder.y - 0.1)

    return elevated_arm and device_at_height
```

#### 6.1.2 手部-设备空间关系

```python
def check_device_hand_proximity(device_bbox, hand_landmarks):
    """检查设备是否在手掌附近"""
    hand_center = np.mean([
        hand_landmarks[0],  # 手腕
        hand_landmarks[5],  # 食指根部
        hand_landmarks[17]  # 小指根部
    ], axis=0)

    device_center = np.array([
        (device_bbox[0] + device_bbox[2]) / 2,
        (device_bbox[1] + device_bbox[3]) / 2
    ])

    distance = euclidean_distance(hand_center, device_center)

    # 设备应该在手部附近（距离阈值根据图像分辨率调整）
    return distance < threshold
```

### 6.2 时序建模实现

#### 6.2.1 帧序列缓冲

```python
class FrameBuffer:
    """管理时序帧缓冲"""
    def __init__(self, max_length=32, fps=30):
        self.max_length = max_length
        self.fps = fps
        self.buffer = collections.deque(maxlen=max_length)
        self.timestamps = collections.deque(maxlen=max_length)

    def add_frame(self, frame, timestamp):
        self.buffer.append(frame)
        self.timestamps.append(timestamp)

    def get_sequence(self, length=16):
        """获取最近N帧"""
        if len(self.buffer) < length:
            return None
        return list(self.buffer)[-length:]

    def get_temporal_segment(self, start_offset, end_offset):
        """获取指定时间范围的帧段"""
        start_time = time.time() - start_offset
        end_time = time.time() - end_offset

        indices = [i for i, ts in enumerate(self.timestamps)
                   if start_time <= ts <= end_time]

        return [self.buffer[i] for i in indices]
```

#### 6.2.2 LSTM时序分类器

```python
class TemporalActionClassifier(nn.Module):
    """基于姿态时序的动作分类器"""
    def __init__(self, input_dim=33*3, hidden_dim=256, num_layers=2,
                 num_classes=3, dropout=0.3):
        super().__init__()

        # 姿态编码器
        self.pose_encoder = nn.Sequential(
            nn.Linear(input_dim, 512),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(512, hidden_dim),
            nn.ReLU()
        )

        # 双向LSTM
        self.lstm = nn.LSTM(
            input_size=hidden_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0
        )

        # 注意力机制
        self.attention = nn.MultiheadAttention(
            embed_dim=hidden_dim * 2,
            num_heads=8
        )

        # 分类器
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim * 2, 128),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, num_classes)
        )

    def forward(self, pose_sequence):
        """
        Args:
            pose_sequence: [B, T, 33, 3] 姿态关键点序列
        Returns:
            logits: [B, num_classes]
        """
        B, T, _, _ = pose_sequence.shape

        # 展平关键点
        pose_flat = pose_sequence.view(B, T, -1)  # [B, T, 99]

        # 编码每一帧的姿态
        encoded = []
        for t in range(T):
            encoded.append(self.pose_encoder(pose_flat[:, t, :]))
        encoded = torch.stack(encoded, dim=1)  # [B, T, hidden_dim]

        # LSTM时序建模
        lstm_out, _ = self.lstm(encoded)  # [B, T, hidden_dim*2]

        # 注意力聚合
        attended_out, _ = self.attention(
            lstm_out.transpose(0, 1),  # [T, B, hidden_dim*2]
            lstm_out.transpose(0, 1),
            lstm_out.transpose(0, 1)
        )
        attended_out = attended_out.transpose(0, 1)  # [B, T, hidden_dim*2]

        # 使用最后时刻的输出
        final_out = attended_out[:, -1, :]

        # 分类
        logits = self.classifier(final_out)

        return logits
```

### 6.3 多线索融合

#### 6.3.1 特征级融合

```python
class MultiModalFusion(nn.Module):
    """多模态特征融合模块"""
    def __init__(self,
                 pose_dim=256,
                 device_dim=128,
                 spatial_dim=64,
                 hidden_dim=256,
                 num_classes=3):
        super().__init__()

        # 特征投影到统一维度
        self.pose_proj = nn.Linear(pose_dim, hidden_dim)
        self.device_proj = nn.Linear(device_dim, hidden_dim)
        self.spatial_proj = nn.Linear(spatial_dim, hidden_dim)

        # 交叉注意力
        self.cross_attention = nn.MultiheadAttention(
            embed_dim=hidden_dim,
            num_heads=8,
            batch_first=True
        )

        # 融合分类器
        self.fusion = nn.Sequential(
            nn.Linear(hidden_dim * 3, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, num_classes)
        )

    def forward(self, pose_feat, device_feat, spatial_feat):
        """
        Args:
            pose_feat: [B, pose_dim] 姿态特征
            device_feat: [B, device_dim] 设备检测特征
            spatial_feat: [B, spatial_dim] 空间关系特征
        Returns:
            logits: [B, num_classes]
        """
        # 特征投影
        pose_proj = self.pose_proj(pose_feat)
        device_proj = self.device_proj(device_feat)
        spatial_proj = self.spatial_proj(spatial_feat)

        # 堆叠为序列
        features = torch.stack([pose_proj, device_proj, spatial_proj], dim=1)  # [B, 3, hidden_dim]

        # 自注意力融合
        fused, _ = self.cross_attention(features, features, features)

        # 展平并分类
        fused_flat = fused.view(fused.size(0), -1)
        logits = self.fusion(fused_flat)

        return logits
```

#### 6.3.2 决策级融合

```python
class DecisionFusion:
    """决策级融合（基于规则和概率）"""
    def __init__(self, weights={'pose': 0.4, 'device': 0.3, 'action': 0.3}):
        self.weights = weights
        self.hmm = None  # 可选：初始化HMM

    def fuse(self, pose_prob, device_prob, action_prob, context_rules):
        """
        Args:
            pose_prob: [3] 姿态分类概率
            device_prob: [N] 设备检测概率
            action_prob: [3] 动作识别概率
            context_rules: dict 上下文规则结果
        Returns:
            final_prob: [3] 最终概率
            decision: int 最终决策
        """
        # 加权融合
        weighted_prob = (
            self.weights['pose'] * pose_prob +
            self.weights['device'] * device_prob[:3] +  # 取前3类
            self.weights['action'] * action_prob
        )

        # 应用规则修正
        if not context_rules['device_near_hand']:
            # 设备不在手附近，大幅降低拍照概率
            weighted_prob[1] *= 0.1
            weighted_prob[2] *= 0.1

        if not context_rules['arm_elevated']:
            # 手臂未举起，降低拍照概率
            weighted_prob[1] *= 0.3

        if context_rules['flash_detected']:
            # 检测到闪光灯，增强拍照置信度
            weighted_prob[1] = min(1.0, weighted_prob[1] * 1.5)

        # 归一化
        final_prob = weighted_prob / np.sum(weighted_prob)

        # 决策
        decision = np.argmax(final_prob)

        return final_prob, decision

    def update_hmm(self, decision):
        """更新隐马尔可夫模型状态"""
        # 实现HMM状态转移
        pass
```

### 6.4 推理优化

#### 6.4.1 TensorRT优化

```python
import tensorrt as trt

def optimize_model_with_tensorrt(onnx_path, engine_path, max_batch=8):
    """使用TensorRT优化模型"""
    TRT_LOGGER = trt.Logger(trt.Logger.INFO)

    builder = trt.Builder(TRT_LOGGER)
    network = builder.create_network(1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH))
    parser = trt.OnnxParser(network, TRT_LOGGER)

    # 解析ONNX模型
    with open(onnx_path, 'rb') as model:
        parser.parse(model.read())

    # 构建配置
    config = builder.create_builder_config()
    config.set_memory_pool_limit(trt.MemoryPoolType.WORKSPACE, 1 << 30)  # 1GB
    config.set_flag(trt.BuilderFlag.FP16)  # 启用FP16精度

    # 构建引擎
    engine = builder.build_serialized_network(network, config)

    # 保存引擎
    with open(engine_path, 'wb') as f:
        f.write(engine)

    return engine
```

#### 6.4.2 模型量化

```python
def quantize_model_ptq(model, calibration_loader):
    """训练后量化(PTQ)"""
    import torch.quantization as quantization

    # 配置量化
    model.qconfig = quantization.get_default_qconfig('fbgemm')

    # 准备量化
    quantization.prepare(model, inplace=True)

    # 校准
    with torch.no_grad():
        for data in calibration_loader:
            model(data)

    # 转换为量化模型
    quantized_model = quantization.convert(model, inplace=True)

    return quantized_model
```

#### 6.4.3 多线程流水线

```python
import threading
import queue

class InferencePipeline:
    """多线程推理流水线"""
    def __init__(self):
        self.frame_queue = queue.Queue(maxsize=30)
        self.result_queue = queue.Queue(maxsize=30)

        self.running = False

    def start(self):
        """启动流水线"""
        self.running = True

        # 启动推理线程
        self.inference_thread = threading.Thread(target=self._inference_worker)
        self.inference_thread.start()

    def stop(self):
        """停止流水线"""
        self.running = False
        self.inference_thread.join()

    def add_frame(self, frame):
        """添加待处理帧"""
        self.frame_queue.put(frame)

    def get_result(self):
        """获取推理结果（非阻塞）"""
        try:
            return self.result_queue.get_nowait()
        except queue.Empty:
            return None

    def _inference_worker(self):
        """推理工作线程"""
        while self.running:
            try:
                frame = self.frame_queue.get(timeout=1.0)

                # 执行推理
                result = self._run_inference(frame)

                # 输出结果
                self.result_queue.put(result)

            except queue.Empty:
                continue
            except Exception as e:
                print(f"Inference error: {e}")

    def _run_inference(self, frame):
        """实际推理逻辑"""
        # Stage 1: 快速检测
        rois = self.fast_detector.detect(frame)

        # Stage 2: 精细分析
        results = []
        for roi in rois:
            pose_feat = self.pose_estimator(roi)
            device_feat = self.device_detector(roi)
            action_feat = self.action_recognizer(roi)

            # 融合决策
            result = self.fusion_engine.fuse(pose_feat, device_feat, action_feat)
            results.append(result)

        return results
```

---

## 7. 边缘部署方案

### 7.1 硬件选型

| 设备 | GPU/NPU | 算力(TOPS) | 功耗 | 适用场景 |
|------|---------|-----------|------|----------|
| NVIDIA Jetson Orin Nano | 128-core Ampere | 40 | 7-15W | 高性能边缘AI |
| NVIDIA Jetson Nano | 128-core Maxwell | 472 GFLOPS | 5-10W | 低成本方案 |
| Intel Movidius MA2485 | - | 4 | 1W | 超低功耗 |
| Google Coral TPU | - | 4 TOPS | 2W | 加速卡方案 |
| Rockchip RK3588 | 6TOPS NPU | 6 | 8W | 国产方案 |

**推荐**：NVIDIA Jetson Orin Nano（性价比高，生态完善）

### 7.2 模型轻量化

#### 模型压缩策略
```python
# 1. 知识蒸馏
Teacher Model: YOLOv8-Medium (25.9M params)
Student Model: YOLOv8-Nano (3.2M params)

# 2. 剪枝
# 结构化剪枝：移除整个通道
# 非结构化剪枝：移除单个权重（需稀疏计算支持）

# 3. 量化
# FP32 → INT8 理论加速4倍，精度损失<1%
# 量化感知训练(QAT) vs 训练后量化(PTQ)

# 4. 模型分解
# 将大模型分解为多个小模型
# 例如: 设备检测和人员检测使用独立小模型
```

#### 端到端优化流程
```bash
# 1. 导出ONNX
yolo export model=yolov8m.pt format=onnx

# 2. ONNX简化
onnxsim input.onnx output.onnx

# 3. 转换TensorRT
trtexec --onnx=model.onnx --saveEngine=model.trt --fp16

# 4. 深度学习加速库
# - TensorRT (NVIDIA)
# - OpenVINO (Intel)
# - TFLite (ARM)
# - MNN (阿里)
# - NCNN (腾讯)
```

### 7.3 部署架构

```python
# 边缘部署服务架构
class EdgeDetectionService:
    """边缘端检测服务"""
    def __init__(self, config_path):
        # 加载TensorRT引擎
        self.detector_engine = self.load_tensorrt_engine('detector.trt')
        self.pose_engine = self.load_tensorrt_engine('pose.trt')
        self.action_engine = self.load_tensorrt_engine('action.trt')

        # 初始化推理上下文
        self.detector_context = self.detector_engine.create_execution_context()
        self.pose_context = self.pose_engine.create_execution_context()
        self.action_context = self.action_engine.create_execution_context()

        # 显存管理
        self.d_input = cuda.mem_alloc(1 * 3 * 640 * 640 * 4)  # FP16

    def infer(self, frame):
        """执行推理"""
        # 预处理
        input_tensor = self.preprocess(frame)

        # GPU推理
        self.detector_context.execute_v2(bindings=[...])

        # 后处理
        detections = self.postprocess_gpu(output_tensor)

        return detections

    def preprocess(self, frame):
        """GPU加速预处理"""
        # 使用CUDA核函数实现BGR2RGB, Resize, Normalize
        pass

    def postprocess_gpu(self, output):
        """GPU加速后处理"""
        # 使用CUDA实现NMS
        pass
```

### 7.4 性能优化目标

| 指标 | 桌面GPU | 边缘设备 |
|------|---------|----------|
| 推理帧率 | >30 FPS | >15 FPS |
| 端到端延迟 | <100ms | <200ms |
| 显存占用 | <4GB | <2GB |
| 功耗 | - | <15W |

---

## 8. 评估指标与测试

### 8.1 评估指标

#### 8.1.1 检测指标
```python
# 目标检测指标
- mAP@0.5: IoU阈值为0.5时的平均精度
- mAP@0.5:0.95: IoU从0.5到0.95的平均精度
- Precision: 精确率 TP/(TP+FP)
- Recall: 召回率 TP/(TP+FN)
- F1-Score: 2*(Precision*Recall)/(Precision+Recall)

# 行为分类指标
- Top-1 Accuracy: 最高置信度类别正确的比例
- Top-3 Accuracy: 正确类别在前3预测中的比例
- Confusion Matrix: 混淆矩阵分析

# 时序检测指标
- Temporal IoU: 检测时间段与真实时间段的重叠度
- Temporal mAP: 时序检测的平均精度
```

#### 8.1.2 性能指标
```python
# 实时性
- FPS: 每秒处理帧数
- Latency: 单帧处理延迟（ms）
- Throughput: 并发处理能力

# 资源占用
- GPU Memory: 显存占用(GB)
- CPU Utilization: CPU利用率(%)
- Power Consumption: 功耗(W)

# 准确性
- False Positive Rate: 误报率（每小时）
- False Negative Rate: 漏报率（每小时）
- Mean Time to Detect: 平均检测时间（从行为开始到检测到）
```

### 8.2 测试集构建

#### 8.2.1 测试集划分
```
总数据集
├── 训练集 (70%)
│   ├── 拍照行为: 3500段
│   ├── 录制行为: 2100段
│   └── 负样本: 11200段
│
├── 验证集 (15%)
│   ├── 拍照行为: 750段
│   ├── 录制行为: 450段
│   └── 负样本: 2400段
│
└── 测试集 (15%)
    ├── 拍照行为: 750段
    ├── 录制行为: 450段
    └── 负样本: 2400段
```

#### 8.2.2 难度分层
```
测试子集
├── Easy: 清晰场景、正面视角、无遮挡
├── Medium: 侧面视角、部分遮挡、复杂背景
└── Hard: 背面视角、严重遮挡、低光照、远距离
```

### 8.3 评估流程

#### 单阶段评估
```python
def evaluate_single_stage(model, test_loader, device):
    """评估单个模型"""
    model.eval()
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for batch in test_loader:
            inputs, labels = batch
            inputs = inputs.to(device)

            outputs = model(inputs)
            preds = outputs.argmax(dim=1)

            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    # 计算指标
    accuracy = accuracy_score(all_labels, all_preds)
    precision = precision_score(all_labels, all_preds, average='macro')
    recall = recall_score(all_labels, all_preds, average='macro')
    f1 = f1_score(all_labels, all_preds, average='macro')

    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1
    }
```

#### 端到端评估
```python
def evaluate_end_to_end(pipeline, test_video_dir, ground_truth):
    """评估完整流程"""
    results = []

    for video_file in os.listdir(test_video_dir):
        video_path = os.path.join(test_video_dir, video_file)

        # 运行检测
        detections = pipeline.process_video(video_path)

        # 获取ground truth
        gt_events = ground_truth[video_file]

        # 计算时序IoU
        for det in detections:
            best_iou = 0
            for gt in gt_events:
                iou = compute_temporal_iou(det['interval'], gt['interval'])
                best_iou = max(best_iou, iou)

            results.append({
                'video': video_file,
                'detected': det,
                'best_iou': best_iou,
                'is_true_positive': best_iou > 0.5
            })

    # 计算指标
    tp = sum(1 for r in results if r['is_true_positive'])
    fp = len(results) - tp
    fn = len(gt_events) - tp

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    return {
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'detailed_results': results
    }

def compute_temporal_iou(interval1, interval2):
    """计算时间段IoU"""
    start1, end1 = interval1
    start2, end2 = interval2

    intersection = max(0, min(end1, end2) - max(start1, start2))
    union = max(end1, end2) - min(start1, start2)

    return intersection / union if union > 0 else 0
```

### 8.4 A/B测试与消融实验

#### 消融实验设计
```
实验组1: Baseline (仅姿态估计)
实验组2: Baseline + 设备检测
实验组3: Baseline + 动作识别
实验组4: 完整模型 (姿态+设备+动作+融合)

对比各组合的精度提升
```

#### 融合策略对比
```
方法A: 简单加权平均
方法B: 贝叶斯融合
方法C: 注意力机制融合
方法D: HMM时序建模

对比各融合方法的性能
```

---

## 9. 风险与挑战

### 9.1 技术风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 误报率高 | 用户体验差，告警疲劳 | - 提高融合阈值<br>- 增加负样本训练<br>- 规则过滤 |
| 漏检 | 安全漏洞 | - 降低检测阈值<br>- 多模型ensemble<br>- 人工审核机制 |
| 光照敏感 | 夜间性能下降 | - 低光照模型<br>- 闪光灯检测增强<br>- 红外摄像头融合 |
| 遮挡处理 | 复杂场景失效 | - 姿态推理补全<br>- 多视角融合<br>- 可见部分建模 |

### 9.2 伦理与隐私

#### 隐私保护
- **数据脱敏**：训练数据去除人脸、敏感信息
- **边缘处理**：视频在本地处理，不上传云端
- **最小化采集**：仅采集必要的检测框和元数据
- **存储加密**：敏感数据加密存储

#### 公平性
- **偏倚检测**：测试不同种族、性别、年龄的检测精度
- **数据平衡**：确保训练数据的多样性
- **透明度**：向用户说明系统工作原理和限制

### 9.3 部署风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 边缘设备算力不足 | 帧率下降 | - 模型轻量化<br>- 云边协同<br>- 硬件升级 |
| 网络延迟 | 实时性差 | - 本地推理<br>- 断网降级策略<br>- 边缘缓存 |
| 设备故障 | 服务中断 | - 健康检查<br>- 自动重启<br>- 冗余备份 |

---

## 10. 开发计划

### Phase 1: 基础模块开发 (2-3周)
- [ ] 搭建项目框架和开发环境
- [ ] 实现视频输入模块
- [ ] 集成YOLOv8设备检测
- [ ] 集成MediaPipe姿态估计
- [ ] 基础可视化输出

### Phase 2: 数据采集与标注 (3-4周)
- [ ] 设计标注工具
- [ ] 采集正样本数据（1000+段）
- [ ] 采集负样本数据（2000+段）
- [ ] 标注团队培训
- [ ] 执行标注和质检

### Phase 3: 模型训练与优化 (4-6周)
- [ ] 训练设备检测模型
- [ ] 训练姿态特征分类器
- [ ] 训练时序动作识别模型
- [ ] 实现融合决策模块
- [ ] 模型调优和集成

### Phase 4: 系统集成与测试 (3-4周)
- [ ] 端到端集成
- [ ] 性能测试和优化
- [ ] 压力测试
- [ ] Bug修复

### Phase 5: 部署与迭代 (持续)
- [ ] 边缘设备部署测试
- [ ] 现场环境验证
- [ ] 收集反馈迭代
- [ ] 模型更新优化

---

## 11. 参考资源

### 论文
1. **YOLOv8**: Ultralytics, "YOLOv8: Industry-Leading Realtime Object Detector"
2. **MediaPipe**: Lugaresi et al., "MediaPipe: A Framework for Building Perception Pipelines" (2019)
3. **I3D**: Carreira & Zisserman, "Quo Vadis, Action Recognition? A New Model and the Kinetics Dataset" (2017)
4. **VideoMAE**: Tong et al., "VideoMAE: Masked Autoencoders for Video Pre-Training" (2022)
5. **SlowFast**: Feichtenhofer et al., "SlowFast Networks for Video Recognition" (2019)

### 数据集
- **Kinetics-700**: 大规模动作识别数据集
- **AVA**: 原子视频动作数据集
- **COCO**: 目标检测基准
- **MPII Human Pose**: 人体姿态数据集

### 开源工具
- **Ultralytics YOLOv8**: https://github.com/ultralytics/ultralytics
- **MediaPipe**: https://google.github.io/mediapipe/
- **OpenPose**: https://github.com/CMU-Perceptual-Computing-Lab/openpose
- **Detectron2**: https://github.com/facebookresearch/detectron2
- **TensorRT**: https://developer.nvidia.com/tensorrt

### 硬件平台
- **NVIDIA Jetson**: https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/
- **Google Coral**: https://coral.ai/

---

## 12. 总结

本技术方案提出了一个**多线索融合**的拍照/录制行为检测系统，核心创新点包括：

1. **多模态融合**：结合姿态、设备、动作、环境四个维度线索
2. **两阶段架构**：快速筛查 + 精细分析，平衡速度与精度
3. **端到端时序建模**：LSTM/Transformer捕捉行为时序模式
4. **可扩展部署**：支持云端GPU和边缘设备部署

预期技术指标：
- **检测精度**: mAP > 85% @ 0.5 IoU
- **实时性能**: >30 FPS (GPU), >15 FPS (边缘)
- **误报率**: < 1次/小时
- **漏检率**: < 5%

该方案可直接指导算法开发和系统实现，各模块职责清晰，技术路线可行。
