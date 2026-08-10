# engines/analysis.py
"""
Pure image-analysis engines (no generation/editing).
Returns structured measurements/labels instead of an edited image.
"""
import logging
import os
import urllib.request
import numpy as np
from PIL import Image

logger = logging.getLogger("m4_nexus")

_face_landmarker = None
_pose_model = None
_clip_model = None
_clip_processor = None

# Cache dir for downloadable model assets (Tasks API needs a .task bundle,
# unlike the old Solutions API which bundled models inside the pip package).
_MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
_FACE_LANDMARKER_MODEL = os.path.join(_MODEL_DIR, "face_landmarker.task")
_FACE_LANDMARKER_URL = (
    "https://storage.googleapis.com/mediapipe-models/face_landmarker/"
    "face_landmarker/float16/latest/face_landmarker.task"
)
_HAND_LANDMARKER_MODEL = os.path.join(_MODEL_DIR, "hand_landmarker.task")
_HAND_LANDMARKER_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/latest/hand_landmarker.task"
)


def _ensure_face_landmarker_model():
    os.makedirs(_MODEL_DIR, exist_ok=True)
    if not os.path.exists(_FACE_LANDMARKER_MODEL):
        logger.info("Downloading MediaPipe FaceLandmarker task model (one-time)...")
        urllib.request.urlretrieve(_FACE_LANDMARKER_URL, _FACE_LANDMARKER_MODEL)
    return _FACE_LANDMARKER_MODEL


def _ensure_hand_landmarker_model():
    os.makedirs(_MODEL_DIR, exist_ok=True)
    if not os.path.exists(_HAND_LANDMARKER_MODEL):
        logger.info("Downloading MediaPipe HandLandmarker task model (one-time)...")
        urllib.request.urlretrieve(_HAND_LANDMARKER_URL, _HAND_LANDMARKER_MODEL)
    return _HAND_LANDMARKER_MODEL


def _get_face_landmarker():
    """
    Uses the MediaPipe Tasks API (mp.tasks.vision.FaceLandmarker), NOT the
    legacy Solutions API (mp.solutions.face_mesh). The legacy namespace is
    not guaranteed to be present depending on platform/mediapipe build
    (this is a known source of `module 'mediapipe' has no attribute
    'solutions'` errors) and Google has been deprecating it in favor of
    Tasks. This path is the officially supported one going forward.
    """
    global _face_landmarker
    if _face_landmarker is None:
        import mediapipe as mp
        from mediapipe.tasks import python as mp_tasks
        from mediapipe.tasks.python import vision as mp_vision

        logger.info("Loading MediaPipe FaceLandmarker (Tasks API)...")
        model_path = _ensure_face_landmarker_model()
        base_options = mp_tasks.BaseOptions(model_asset_path=model_path)
        options = mp_vision.FaceLandmarkerOptions(
            base_options=base_options,
            num_faces=1,
            running_mode=mp_vision.RunningMode.IMAGE,
        )
        _face_landmarker = mp_vision.FaceLandmarker.create_from_options(options)
    return _face_landmarker


def _get_pose_model():
    global _pose_model
    if _pose_model is None:
        from ultralytics import YOLO
        logger.info("Loading YOLOv8 Pose model...")
        _pose_model = YOLO("yolov8n-pose.pt")
    return _pose_model


_hand_landmarker = None
_object_detector = None


def _get_hand_landmarker():
    global _hand_landmarker
    if _hand_landmarker is None:
        import mediapipe as mp
        from mediapipe.tasks import python as mp_tasks
        from mediapipe.tasks.python import vision as mp_vision

        logger.info("Loading MediaPipe HandLandmarker (Tasks API)...")
        model_path = _ensure_hand_landmarker_model()
        base_options = mp_tasks.BaseOptions(model_asset_path=model_path)
        options = mp_vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=2,
            running_mode=mp_vision.RunningMode.IMAGE,
        )
        _hand_landmarker = mp_vision.HandLandmarker.create_from_options(options)
    return _hand_landmarker


def _get_clip():
    global _clip_model, _clip_processor
    if _clip_model is None:
        from transformers import CLIPModel, CLIPProcessor
        logger.info("Loading CLIP zero-shot classifier...")
        _clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        _clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    return _clip_model, _clip_processor


def _humanize_face(result: dict) -> str:
    if not result.get("face_detected"):
        return "No face was detected in the image."

    ratio = result.get("face_length_to_width_ratio")
    if ratio is None:
        shape = "an undetermined face shape"
    elif ratio >= 1.5:
        shape = "a long, oval-leaning face shape"
    elif ratio >= 1.25:
        shape = "a balanced, oval face shape"
    else:
        shape = "a rounder, wider face shape"

    return (
        f"The face has {shape} (length-to-width ratio ≈ {ratio}). "
        f"Eye spacing and jaw width were measured from {result['landmark_count']} facial landmark points. "
        "Note: these are relative proportions from the photo, not calibrated real-world measurements, "
        "since there's no reference object in frame to establish scale."
    )


def _humanize_body_pose(result: dict) -> str:
    if not result.get("person_detected"):
        return "No person was detected in the image."

    ratio = result.get("shoulder_to_hip_ratio")
    if ratio is None:
        build = "an undetermined body proportion"
    elif ratio >= 1.15:
        build = "shoulders noticeably broader than the hips (an athletic/inverted-triangle proportion)"
    elif ratio >= 0.95:
        build = "shoulders and hips of fairly similar width (a balanced/rectangular proportion)"
    else:
        build = "hips broader than the shoulders (a pear-shaped proportion)"

    return (
        f"The pose analysis shows {build}, with a shoulder-to-hip ratio of about {ratio}. "
        "These are relative proportions estimated from pixel distances in the photo — not calibrated "
        "real-world measurements, since there's no reference object in frame to establish scale."
    )


def _humanize_hand(result: dict) -> str:
    if not result.get("hands_detected"):
        return "No hand was detected in the image."

    n = result["hand_count"]
    hands_word = "hand" if n == 1 else "hands"
    details = []
    for h in result["hands"]:
        details.append(
            f"{h['handedness']} hand: palm width ≈ {h['palm_width_px']}px, "
            f"middle finger length ≈ {h['middle_finger_length_px']}px"
        )
    return (
        f"Detected {n} {hands_word}. " + " | ".join(details) + ". "
        "These are relative pixel proportions from the photo, not calibrated real-world "
        "measurements, since there's no reference object in frame to establish scale."
    )


def _humanize_structure(result: dict) -> str:
    top = result.get("top_label")
    conf = result.get("top_confidence")
    if not top:
        return "Could not classify the structure in the image."
    confidence_word = "high" if conf >= 0.6 else "moderate" if conf >= 0.35 else "low"
    return (
        f"This looks most like a \"{top}\" ({confidence_word} confidence, {conf:.0%}). "
        f"Other possibilities considered: "
        + ", ".join(f"{l['label']} ({l['confidence']:.0%})" for l in result["all_labels"][1:4])
        + "."
    )


def analyze_face(image: Image.Image) -> dict:
    """Return facial landmark-derived geometry (jaw width, face ratio, eye distance, etc.)."""
    import mediapipe as mp

    landmarker = _get_face_landmarker()
    rgb = np.array(image.convert("RGB"))
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    detection_result = landmarker.detect(mp_image)

    if not detection_result.face_landmarks:
        return {"face_detected": False}

    lm = detection_result.face_landmarks[0]  # list of NormalizedLandmark
    w, h = image.size

    def pt(i):
        return np.array([lm[i].x * w, lm[i].y * h])

    # A handful of standard MediaPipe Face Mesh landmark indices.
    jaw_left, jaw_right = pt(234), pt(454)
    forehead, chin = pt(10), pt(152)
    eye_left, eye_right = pt(33), pt(263)

    jaw_width = float(np.linalg.norm(jaw_left - jaw_right))
    face_length = float(np.linalg.norm(forehead - chin))
    eye_distance = float(np.linalg.norm(eye_left - eye_right))

    result = {
        "face_detected": True,
        "jaw_width_px": round(jaw_width, 1),
        "face_length_px": round(face_length, 1),
        "face_length_to_width_ratio": round(face_length / jaw_width, 2) if jaw_width else None,
        "eye_distance_px": round(eye_distance, 1),
        "landmark_count": len(lm),
    }
    result["summary"] = _humanize_face(result)
    return result


def analyze_body_pose(image: Image.Image) -> dict:
    """Return body keypoints and derived proportions (shoulder width, torso length, etc.)."""
    model = _get_pose_model()
    results = model.predict(image, conf=0.25, verbose=False)

    if not results or results[0].keypoints is None or len(results[0].keypoints.xy) == 0:
        return {"person_detected": False}

    kpts = results[0].keypoints.xy[0].tolist()  # 17 COCO keypoints [x, y]
    # COCO indices: 5=L shoulder, 6=R shoulder, 11=L hip, 12=R hip
    l_shoulder, r_shoulder = np.array(kpts[5]), np.array(kpts[6])
    l_hip, r_hip = np.array(kpts[11]), np.array(kpts[12])

    shoulder_width = float(np.linalg.norm(l_shoulder - r_shoulder))
    hip_width = float(np.linalg.norm(l_hip - r_hip))
    torso_length = float(np.linalg.norm(((l_shoulder + r_shoulder) / 2) - ((l_hip + r_hip) / 2)))

    result = {
        "person_detected": True,
        "shoulder_width_px": round(shoulder_width, 1),
        "hip_width_px": round(hip_width, 1),
        "torso_length_px": round(torso_length, 1),
        "shoulder_to_hip_ratio": round(shoulder_width / hip_width, 2) if hip_width else None,
    }
    result["summary"] = _humanize_body_pose(result)
    result["keypoints"] = kpts  # raw points last, for callers that want the full skeleton
    return result


def analyze_hand(image: Image.Image) -> dict:
    """Return hand landmark-derived geometry (palm width, finger length, handedness) per detected hand."""
    import mediapipe as mp

    landmarker = _get_hand_landmarker()
    rgb = np.array(image.convert("RGB"))
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    detection_result = landmarker.detect(mp_image)

    if not detection_result.hand_landmarks:
        return {"hands_detected": False, "hand_count": 0, "hands": []}

    w, h = image.size
    hands = []
    for hand_landmarks, handedness in zip(detection_result.hand_landmarks, detection_result.handedness):
        def pt(i):
            return np.array([hand_landmarks[i].x * w, hand_landmarks[i].y * h])

        # MediaPipe Hand landmark indices: 0=wrist, 5=index MCP, 17=pinky MCP, 9=middle MCP, 12=middle tip
        wrist = pt(0)
        index_mcp, pinky_mcp = pt(5), pt(17)
        middle_mcp, middle_tip = pt(9), pt(12)

        palm_width = float(np.linalg.norm(index_mcp - pinky_mcp))
        middle_finger_length = float(np.linalg.norm(middle_mcp - middle_tip))
        hand_length = float(np.linalg.norm(wrist - middle_tip))

        hands.append({
            "handedness": handedness[0].category_name,  # "Left" or "Right"
            "confidence": round(handedness[0].score, 3),
            "palm_width_px": round(palm_width, 1),
            "middle_finger_length_px": round(middle_finger_length, 1),
            "hand_length_px": round(hand_length, 1),
        })

    result = {
        "hands_detected": True,
        "hand_count": len(hands),
        "hands": hands,
    }
    result["summary"] = _humanize_hand(result)
    return result


def analyze_structure(image: Image.Image, candidate_labels: list[str] = None) -> dict:
    """Zero-shot classify a building/structure image against candidate style/material labels."""
    if candidate_labels is None:
        candidate_labels = [
            "modern building", "colonial style building", "brick building",
            "concrete building", "glass skyscraper", "residential house",
            "industrial warehouse", "wooden cabin",
        ]

    model, processor = _get_clip()
    inputs = processor(text=candidate_labels, images=image, return_tensors="pt", padding=True)
    outputs = model(**inputs)
    probs = outputs.logits_per_image.softmax(dim=1)[0].tolist()

    ranked = sorted(zip(candidate_labels, probs), key=lambda x: x[1], reverse=True)
    result = {
        "top_label": ranked[0][0],
        "top_confidence": round(ranked[0][1], 3),
        "all_labels": [{"label": lbl, "confidence": round(p, 3)} for lbl, p in ranked],
    }
    result["summary"] = _humanize_structure(result)
    return result


def _humanize_object_shape(result: dict) -> str:
    if not result.get("object_detected"):
        return "No distinct object was detected in the image."

    ar = result["aspect_ratio"]
    if ar >= 1.6:
        shape = "elongated / wide"
    elif ar <= 0.63:
        shape = "elongated / tall"
    else:
        shape = "roughly square/rounded"

    label = result.get("label", "object")
    return (
        f"Detected a {label} — {shape} in proportion, "
        f"about {result['width_px']}px wide by {result['height_px']}px tall "
        f"(aspect ratio {ar}). "
        "These are pixel dimensions from the photo, not calibrated real-world size, "
        "since there's no reference object in frame to establish scale."
    )


def _get_object_detector():
    global _object_detector
    if _object_detector is None:
        from ultralytics import YOLO
        logger.info("Loading YOLOv8 general object detector...")
        _object_detector = YOLO("yolov8n.pt")
    return _object_detector


def analyze_object_shape(image: Image.Image) -> dict:
    """Detect the most prominent object in the image and report its size/shape."""
    model = _get_object_detector()

    results = model.predict(image, conf=0.25, verbose=False)
    if not results or len(results[0].boxes) == 0:
        return {"object_detected": False}

    # Pick the largest-area detection as "the" object.
    boxes = results[0].boxes
    areas = [(b.xyxy[0][2] - b.xyxy[0][0]) * (b.xyxy[0][3] - b.xyxy[0][1]) for b in boxes]
    idx = int(np.argmax([a.item() for a in areas]))
    box = boxes[idx]
    x0, y0, x1, y1 = box.xyxy[0].tolist()
    label = model.names[int(box.cls[0])]

    width = round(x1 - x0, 1)
    height = round(y1 - y0, 1)

    result = {
        "object_detected": True,
        "label": label,
        "width_px": width,
        "height_px": height,
        "aspect_ratio": round(width / height, 2) if height else None,
    }
    result["summary"] = _humanize_object_shape(result)
    return result


# ---------------------------------------------------------------------------
# Analyzer registry
#
# Adding a NEW analysis type (e.g. "hair", "clothing", "vehicle") only
# requires:
#   1. Write the analyze_xxx(image) function above.
#   2. Add one entry to ANALYZERS below.
# main.py never needs to change — it just loops over this registry.
# Keep each analyzer's `keywords` list specific to avoid the collisions
# that caused "hand structure" to wrongly hit building classification.
# ---------------------------------------------------------------------------
ANALYZERS = {
    "face": {
        "func": analyze_face,
        "keywords": ["face", "jaw", "facial"],
    },
    "hand": {
        "func": analyze_hand,
        "keywords": ["hand", "finger", "palm"],
    },
    "body": {
        "func": analyze_body_pose,
        "keywords": ["body", "pose", "posture", "shoulder"],
    },
    "object_shape": {
        "func": analyze_object_shape,
        "keywords": ["shape", "size", "dimensions", "how big", "how large"],
    },
    "structure": {
        "func": analyze_structure,
        "keywords": ["building", "architecture", "facade"],
    },
}


def run_analyzers(categories: list, image: Image.Image) -> dict:
    """
    Run a specific set of analyzer(s) by name and return the combined result.
    Returns the single analyzer's dict directly if only one category given,
    otherwise a dict keyed by analyzer name.
    """
    categories = [c for c in categories if c in ANALYZERS]
    if not categories:
        categories = list(ANALYZERS.keys())

    result = {name: ANALYZERS[name]["func"](image) for name in categories}

    if len(result) == 1:
        return next(iter(result.values()))
    return result


def route_analysis_by_keywords(prompt: str, image: Image.Image) -> dict:
    """
    Fallback routing: plain keyword matching against each analyzer's
    `keywords` list. Used when Llama-based classification is unavailable
    (e.g. Ollama is down). Prone to collisions between similar-sounding
    categories — prefer Llama-based routing when possible.
    """
    prompt_lower = prompt.lower()
    matched = [
        name for name, spec in ANALYZERS.items()
        if any(k in prompt_lower for k in spec["keywords"])
    ]
    return run_analyzers(matched, image)