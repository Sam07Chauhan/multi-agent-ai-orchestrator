# services/pre_process.py
from PIL import Image, ImageDraw  # FIXED: Globally imported ImageDraw here
from ultralytics import YOLO
import config

yolo_seg_model = None

def get_yolo_seg():
    global yolo_seg_model
    if yolo_seg_model is None:
        yolo_seg_model = YOLO(config.YOLO_SEG_MODEL_PATH)
    return yolo_seg_model

def preprocess_image(orig_image: Image.Image, max_side_override=None):
    orig_w, orig_h = orig_image.size
    max_side = max_side_override if max_side_override else max(orig_w, orig_h)
    
    padded_image = Image.new("RGB", (max_side, max_side), (255, 255, 255))
    offset_x = (max_side - orig_w) // 2
    offset_y = (max_side - orig_h) // 2
    padded_image.paste(orig_image, (offset_x, offset_y))
    
    return padded_image.resize((config.IMAGE_SIZE, config.IMAGE_SIZE), Image.Resampling.LANCZOS), max_side, (offset_x, offset_y)

def segment_subject(input_image: Image.Image):
    model = get_yolo_seg()
    results = model.predict(input_image, conf=0.25, verbose=False)
    
    auto_mask = Image.new("RGB", (config.IMAGE_SIZE, config.IMAGE_SIZE), (0, 0, 0))
    draw = ImageDraw.Draw(auto_mask)  # FIXED: Clean and direct assignment
    
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

    if person_detected and len(main_polygon) > 2:
        draw.polygon(main_polygon, fill=(255, 255, 255))
        
    return auto_mask, main_box