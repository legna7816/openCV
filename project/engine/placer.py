import random
from PIL import Image
import numpy as np

class Placer:
    def paste_with_alpha(target: Image.Image, patch: Image.Image, x: int, y: int):
        """알파 채널을 고려하여 이미지 붙이기"""
        target.paste(patch, (x, y), patch)

    def random_position_avoid_main(canvas_size, patch_size, main_area):
        """메인 영역을 피해서 랜덤 위치 찾기"""
        cw, ch = canvas_size
        pw, ph = patch_size
        mx = main_area["x"]
        my = main_area["y"]
        mw = main_area["width"]
        mh = main_area["height"]

        # 반복해서 랜덤 위치 찾기 (메인 영역과 겹침 최소화)
        for _ in range(40):
            rx = random.randint(0, max(0, cw - pw))
            ry = random.randint(0, max(0, ch - ph))
            
            # 겹치는 영역 계산
            inter_w = max(0, min(rx+pw, mx+mw) - max(rx, mx))
            inter_h = max(0, min(ry+ph, my+mh) - max(ry, my))
            inter_area = inter_w * inter_h
            
            # 패치 면적의 30% 미만 겹치면 OK
            if inter_area < 0.3 * (pw * ph):
                return rx, ry
        
        # 찾지 못하면 그냥 랜덤 위치 반환
        return random.randint(0, max(0, cw - pw)), random.randint(0, max(0, ch - ph))