import random
import numpy as np
import cv2
from engine.layout_manager import LayoutManager
from engine.mask_generator import MaskGenerator
from engine.placer import Placer

class CollageGenerator:
    def __init__(self):
        self.placer = Placer()

    def load_image(self, path):
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise FileNotFoundError("이미지 로딩 실패: " + path)
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGRA)
        elif img.shape[2] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
        return img

    def resize_crop_random(self, img, target_width, target_height):
        h, w = img.shape[:2]
        
        scale_w = target_width / w
        scale_h = target_height / h
        scale = max(scale_w, scale_h) * 1.4
        
        new_w, new_h = int(w * scale), int(h * scale)
        resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        
        max_start_x = max(0, new_w - target_width)
        max_start_y = max(0, new_h - target_height)
        
        start_x = random.randint(0, max_start_x)
        start_y = random.randint(0, max_start_y)
        
        cropped = resized[start_y:start_y+target_height, start_x:start_x+target_width]
        return cropped
    
    def generate(self, image_paths, canvas_size=(1000, 700), pieces=20):
        self.masker = MaskGenerator()
        self.placer = Placer()

        cw, ch = canvas_size
        margin = 100
        work_w = cw + margin * 2
        work_h = ch + margin * 2

        canvas = np.ones((work_h, work_w, 4), dtype=np.uint8) * 255

        lm = LayoutManager(canvas_size=(work_w, work_h))
        main_area = lm.main_area

        main_img = self.load_image(image_paths[0])
        main_resized = self.resize_crop_random(main_img,
                                               main_area["width"],
                                               main_area["height"])
        mask_np = self.masker.create_mask(main_area["mask"],
                                          main_area["width"],
                                          main_area["height"])
        main_resized[:, :, 3] = mask_np

        src_images = [self.load_image(p) for p in image_paths]

        for i in range(pieces):
            src = random.choice(src_images)
            sh, sw = src.shape[:2]
            
            pw = random.randint(int(cw * 0.1), int(cw * 0.4))
            ph = random.randint(int(ch * 0.1), int(ch * 0.4))
            
            if sw <= pw or sh <= ph:
                pw = min(pw, max(1, sw))
                ph = min(ph, max(1, sh))
            
            cx = random.randint(0, max(0, sw - pw))
            cy = random.randint(0, max(0, sh - ph))
            patch = src[cy:cy+ph, cx:cx+pw].copy()

            shape_choice = random.choice(["rect", "ellipse"])
            if shape_choice == "ellipse":
                mask_np = self.masker.create_mask("ellipse", pw, ph)
                patch[:, :, 3] = mask_np

            px, py = self.placer.random_position((work_w, work_h),
                                                 (patch.shape[1], patch.shape[0]))
            
            self.placer.paste_with_alpha(canvas, patch, px, py)

        self.placer.paste_with_alpha(canvas, main_resized, main_area["x"], main_area["y"])

        final = canvas[margin:margin+ch, margin:margin+cw]

        return final

    def to_pil(self, img):
        from PIL import Image
        if img.shape[2] == 4:
            return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA))
        else:
            return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))