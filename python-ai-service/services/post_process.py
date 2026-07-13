from PIL import Image, ImageDraw, ImageFilter
import config

def apply_face_shield_mask(mask: Image.Image, face_box: list) -> Image.Image:
    if face_box is None:
        return mask
    draw = ImageDraw.Draw(mask)
    x0, y0, x1, y1 = face_box
    pad = config.FACE_BOX_PADDING
    draw.rectangle([max(0, x0-pad), max(0, y0-pad), min(config.IMAGE_SIZE, x1+pad), min(config.IMAGE_SIZE, y1+pad)], fill=(0, 0, 0))
    return mask

def restore_face(edited_image: Image.Image, source_image: Image.Image, face_box: list) -> Image.Image:
    if face_box is None:
        return edited_image
    x0, y0, x1, y1 = [int(c) for c in face_box]
    orig_face_crop = source_image.crop((x0, y0, x1, y1))
    
    mask_blur = Image.new("L", orig_face_crop.size, 0)
    draw_blur = ImageDraw.Draw(mask_blur)
    f_p = config.FEATHER_BLUR_RADIUS
    draw_blur.rectangle([f_p, f_p, mask_blur.size[0]-f_p, mask_blur.size[1]-f_p], fill=255)
    mask_blur = mask_blur.filter(ImageFilter.GaussianBlur(radius=config.FEATHER_BLUR_RADIUS))
    
    edited_image.paste(orig_face_crop, (x0, y0), mask_blur)
    return edited_image

def finalize_dimensions(edited_image: Image.Image, orig_size, offset, max_side):
    orig_w, orig_h = orig_size
    ratio = config.IMAGE_SIZE / max_side
    crop_box = (
        int(offset[0] * ratio), int(offset[1] * ratio),
        int((offset[0] + orig_w) * ratio), int((offset[1] + orig_h) * ratio)
    )
    return edited_image.crop(crop_box).resize((orig_w, orig_h), Image.Resampling.LANCZOS)