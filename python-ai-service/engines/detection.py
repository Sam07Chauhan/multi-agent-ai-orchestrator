import logging
from ultralytics import YOLO
from PIL import Image
import config

logger = logging.getLogger("m4_nexus")

class YoloEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            logger.info("Initializing YOLOv8 AI Segmentation Engine...")
            cls._instance = super(YoloEngine, cls).__new__(cls)
            cls._instance.model = YOLO("yolov8n-seg.pt")
        return cls._instance

    def segment_main_subject(self, image: Image.Image):
        results = self.model.predict(image, conf=0.25, verbose=False)
        person_detected = False
        largest_area = 0
        main_polygon = None
        main_box = None

        for result in results:
            if result.masks is not None:
                for mask, box in zip(result.masks.xy, result.boxes):
                    if int(box.cls[0]) == 0:  # Person Class
                        bbox = box.xyxy[0].tolist()
                        area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
                        
                        if area > largest_area:
                            largest_area = area
                            main_polygon = [(int(x), int(y)) for x, y in mask]
                            main_box = bbox
                            person_detected = True
                            
        return person_detected, main_polygon, main_box