from PIL import Image, ImageDraw, ImageFilter
import config

def restore_face(edited_image: Image.Image, source_image: Image.Image, face_box: list) -> Image.Image:
    """Paste the original face back onto the inpainted image (same resolution)."""
    if face_box is None:
        return edited_image

    result = edited_image.copy()
    x0, y0, x1, y1 = [int(c) for c in face_box]
    w, h = source_image.size
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(w, x1), min(h, y1)
    if x1 <= x0 or y1 <= y0:
        return result

    orig_face_crop = source_image.crop((x0, y0, x1, y1))

    mask_blur = Image.new("L", orig_face_crop.size, 0)
    draw_blur = ImageDraw.Draw(mask_blur)
    f_p = config.FEATHER_BLUR_RADIUS
    draw_blur.rectangle(
        [f_p, f_p, mask_blur.size[0] - f_p, mask_blur.size[1] - f_p],
        fill=255,
    )
    mask_blur = mask_blur.filter(ImageFilter.GaussianBlur(radius=config.FEATHER_BLUR_RADIUS))

    result.paste(orig_face_crop, (x0, y0), mask_blur)
    return result

def finalize_dimensions(edited_image: Image.Image, orig_size, offset, max_side):
    orig_w, orig_h = orig_size
    ratio = config.IMAGE_SIZE / max_side
    crop_box = (
        int(offset[0] * ratio), int(offset[1] * ratio),
        int((offset[0] + orig_w) * ratio), int((offset[1] + orig_h) * ratio)
    )
    return edited_image.crop(crop_box).resize((orig_w, orig_h), Image.Resampling.LANCZOS)
