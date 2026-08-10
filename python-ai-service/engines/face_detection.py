# engines/face_detection.py
import logging
import config

logger = logging.getLogger("m4_nexus")


class GeometricFaceEngine:
    """
    Zero-dependency face-box estimator.

    NOTE: despite the historical name "YoloFaceEngine" this does NOT run a
    YOLO face model (config.YOLO_FACE_MODEL_PATH / yolov8n-face.pt are unused
    dead config). It derives an approximate head region purely from the
    person segmentation box: the top 35% of the person's height, with a
    small horizontal pad.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            logger.info("Loading geometric head-region estimator (zero-dependency fallback)...")
            cls._instance = super(GeometricFaceEngine, cls).__new__(cls)
        return cls._instance

    def detect_main_face(self, image, segmentation_box: list):
        """
        Estimate a face bounding box from the person's segmentation box by
        taking the top 35% of its height (head region), padded slightly on
        the sides, and clamped to the image bounds.
        """
        if segmentation_box is None:
            return None

        x_min, y_min, x_max, y_max = segmentation_box

        person_height = y_max - y_min
        person_width = x_max - x_min

        # Top 35% of the person's bounding box height approximates the head.
        face_bottom = y_min + (person_height * 0.35)
        x_pad = person_width * 0.05

        if image is not None:
            img_w, img_h = image.size
        else:
            img_w = img_h = config.IMAGE_SIZE

        f_x0 = max(0, x_min - x_pad)
        f_y0 = max(0, y_min - 5)
        f_x1 = min(img_w, x_max + x_pad)
        f_y1 = min(img_h, face_bottom)

        return [f_x0, f_y0, f_x1, f_y1]


# Backwards-compatible alias — main.py / other callers may still import this name.
YoloFaceEngine = GeometricFaceEngine