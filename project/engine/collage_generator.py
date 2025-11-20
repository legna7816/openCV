import random
from PIL import Image
import numpy as np
import cv2
from engine.layout_manager import LayoutManager
from engine.mask_generator import MaskGenerator
from engine.placer import Placer

class CollageGenerator:
    def __init__(self):
        pass

    def load_image(self, path):
        """이미지 로드 - OpenCV로 읽고 PIL로 변환"""
        img = cv2.imread(path)
        if img is None:
            raise FileNotFoundError("이미지 로딩 실패: " + path)
        return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

    def resize_crop_center(self, img_pil, target_width, target_height):
        """PIL Image를 목표 크기로 resize & crop"""
        w, h = img_pil.size
        
        scale_w = target_width / w
        scale_h = target_height / h
        scale = max(scale_w, scale_h)
        
        new_w, new_h = int(w * scale), int(h * scale)
        resized = img_pil.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        start_x = (new_w - target_width) // 2
        start_y = (new_h - target_height) // 2
        
        cropped = resized.crop((start_x, start_y, start_x + target_width, start_y + target_height))
        return cropped

    def generate(self, image_paths, canvas_size=(1000,700), pieces=20):
        self.masker = MaskGenerator()
        lm = LayoutManager(canvas_size=canvas_size)
        main_area = lm.main_area
        cw, ch = canvas_size

        canvas = Image.new("RGBA", (cw, ch), (255,255,255,255))

        # 메인 이미지 로드
        main_img = self.load_image(image_paths[0])
        
        main_resized = self.resize_crop_center(main_img.convert("RGBA"),
                                               main_area["width"],
                                               main_area["height"])
        mask_np = self.masker.create_mask(main_area["mask"],
                                          main_area["width"],
                                          main_area["height"])
        alpha = Image.fromarray(mask_np).convert("L")
        main_rgba = main_resized.copy()
        main_rgba.putalpha(alpha)

        Placer.paste_with_alpha(canvas, main_rgba, main_area["x"], main_area["y"])

        # 소스 이미지들 로드
        src_images = [self.load_image(p) for p in image_paths]
        
        for i in range(pieces):
            src = random.choice(src_images)
            sw, sh = src.size
            pw = random.randint(int(main_area["width"]*0.08), int(main_area["width"]*0.5))
            ph = random.randint(int(main_area["height"]*0.08), int(main_area["height"]*0.5))
            if sw <= pw or sh <= ph:
                pw = min(pw, max(1, sw))
                ph = min(ph, max(1, sh))
            cx = random.randint(0, max(0, sw - pw))
            cy = random.randint(0, max(0, sh - ph))
            patch = src.crop((cx, cy, cx+pw, cy+ph)).convert("RGBA")

            shape_choice = random.choice(["rect", "ellipse"])
            if shape_choice == "ellipse":
                mask_np = self.masker.create_mask("ellipse", pw, ph)
                alpha = Image.fromarray(mask_np).convert("L")
                patch.putalpha(alpha)
            
            ang = random.randint(0, 359)
            patch = patch.rotate(ang, expand=True)

            px, py = Placer.random_position_avoid_main((cw, ch), patch.size, main_area)
            Placer.paste_with_alpha(canvas, patch, px, py)

        return canvas