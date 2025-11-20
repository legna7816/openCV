import numpy as np, cv2

# mask 생성
class MaskGenerator:
    def create_mask(self, shape_type, w, h):
        mask = np.zeros((h,w), dtype=np.uint8)
        if shape_type in ("ellipse", "circle"):
            center = (w//2, h//2)
            axes = (int(w * 0.5), int(h * 0.5)) if shape_type=="ellipse" else (min(w, h) // 2,) * 2
            cv2.ellipse(mask, center, axes, 0, 0, 360, 255, -1)
        elif shape_type == "rectangle":
            cv2.rectangle(mask, (0, 0), (w, h), color=255, thickness=-1)
        else:
            mask[:] =255
        return mask