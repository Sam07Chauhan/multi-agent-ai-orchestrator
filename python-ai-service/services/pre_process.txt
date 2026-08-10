# services/pre_process.py
import re
from PIL import Image, ImageDraw
from ultralytics import YOLO
import config

yolo_seg_model = None

BACKGROUND_KEYWORDS = re.compile(
    r"\b(studio|backdrop|background|curtain|scene|setting|environment|"
    r"portrait\s+against|solid\s+\w+\s+backdrop|maroon|indoor)\b",
    re.IGNORECASE,
)

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

    resized = padded_image.resize(
        (config.IMAGE_SIZE, config.IMAGE_SIZE), Image.Resampling.LANCZOS
    )
    return resized, max_side, (offset_x, offset_y)

def wants_background_change(prompt: str) -> bool:
    return bool(BACKGROUND_KEYWORDS.search(prompt))

def segment_subject(input_image: Image.Image):
    """Run YOLO on the same 512x512 image that will be sent to inpainting."""
    model = get_yolo_seg()
    w, h = input_image.size
    results = model.predict(input_image, conf=0.25, verbose=False)

    auto_mask = Image.new("RGB", (w, h), (0, 0, 0))
    draw = ImageDraw.Draw(auto_mask)

    person_detected = False
    largest_area = 0
    main_polygon = None
    main_box = None

    for result in results:
        if result.masks is not None:
            for mask, box in zip(result.masks.xy, result.boxes):
                if int(box.cls[0]) == 0:
                    bbox = box.xyxy[0].tolist()
                    area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
                    if area > largest_area:
                        largest_area = area
                        main_polygon = [(int(x), int(y)) for x, y in mask]
                        main_box = bbox
                        person_detected = True

    if person_detected and main_polygon and len(main_polygon) > 2:
        draw.polygon(main_polygon, fill=(255, 255, 255))

    return auto_mask, main_box

def build_inpaint_mask(
    processed_image: Image.Image,
    person_mask: Image.Image,
    person_box,
    face_box,
    prompt: str,
) -> Image.Image:
    """
    Subject-only: inpaint person body (clothing), keep background.
    Full-scene: inpaint everything except the face (studio/backdrop prompts).
    """
    w, h = processed_image.size

    if wants_background_change(prompt):
        mask = Image.new("RGB", (w, h), (255, 255, 255))
    else:
        mask = person_mask.copy()

    if face_box is not None:
        draw = ImageDraw.Draw(mask)
        x0, y0, x1, y1 = face_box
        pad = config.FACE_BOX_PADDING
        draw.rectangle(
            [
                max(0, x0 - pad),
                max(0, y0 - pad),
                min(w, x1 + pad),
                min(h, y1 + pad),
            ],
            fill=(0, 0, 0),
        )

    if person_box is None and not wants_background_change(prompt):
        mask = Image.new("RGB", (w, h), (0, 0, 0))
        draw = ImageDraw.Draw(mask)
        draw.ellipse([w * 0.2, h * 0.05, w * 0.8, h * 0.95], fill=(255, 255, 255))

    return mask
