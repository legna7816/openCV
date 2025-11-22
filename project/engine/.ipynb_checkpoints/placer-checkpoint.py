import random
import numpy as np

class Placer:
    def __init__(self):
        pass

    def paste_with_alpha(self, target, patch, x, y):
        th, tw = target.shape[:2]
        ph, pw = patch.shape[:2]

        x1, y1 = max(0, x), max(0, y)
        x2, y2 = min(tw, x + pw), min(th, y + ph)

        px1 = x1 - x
        py1 = y1 - y
        px2 = px1 + (x2 - x1)
        py2 = py1 + (y2 - y1)

        if x2 <= x1 or y2 <= y1:
            return

        patch_region = patch[py1:py2, px1:px2]
        target_region = target[y1:y2, x1:x2]

        alpha_mask = patch_region[:, :, 3] > 0

        target_region[alpha_mask, :3] = patch_region[alpha_mask, :3]
        
        target_region[alpha_mask, 3] = patch_region[alpha_mask, 3]

    def random_position(self, canvas_size, patch_size):
        cw, ch = canvas_size
        pw, ph = patch_size
        
        rx = random.randint(0, max(0, cw - pw))
        ry = random.randint(0, max(0, ch - ph))

        return rx, ry