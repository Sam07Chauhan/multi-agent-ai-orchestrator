# engines/face_detection.py
import logging
import config

logger = logging.getLogger("m4_nexus")

class YoloFaceEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            logger.info("Loading Pure Python Geometric Head Shield (Zero Dependency Fallback)...")
            cls._instance = super(YoloFaceEngine, cls).__new__(cls)
        return cls._instance

    def detect_main_face(self, image, segmentation_box: list):
        """
        Segmented subject ka horizontal alignment aur top coordinate extract 
        karke mathematically face box bound karta hai.
        """
        if segmentation_box is None:
            return None

        # Bounding Box unpack karein (x_min, y_min, x_max, y_max)
        x_min, y_min, x_max, y_max = segmentation_box
        
        person_height = y_max - y_min
        person_width = x_max - x_min
        
        # Bounding box ki top 35% height pure head region ko dynamic calculate karti hai
        face_bottom = y_min + (person_height * 0.35)
        x_pad = person_width * 0.05
        
        # Exact face coordinates scale limits ke andar define karte hain
        f_x0 = max(0, x_min - x_pad)
        f_y0 = max(0, y_min - 5)
        img_limit = image.size[0] if image is not None else config.IMAGE_SIZE
        f_x1 = min(img_limit, x_max + x_pad)
        f_y1 = min(img_limit, face_bottom)
        
        return [f_x0, f_y0, f_x1, f_y1]