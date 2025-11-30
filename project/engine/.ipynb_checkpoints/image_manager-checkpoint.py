import cv2
import numpy as np
import random

# 이미지 로딩 및 변환 관리 클래스
class ImageManager:
    
    def __init__(self, resize_scale_factor=1.2):
        self.resize_scale_factor = resize_scale_factor

    # 이미지 로드 및 BGRA 변환
    def load(self, path):
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise FileNotFoundError(f"이미지 로딩 실패: {path}")
        
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGRA)
        elif img.shape[2] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
        
        return img

    # 여러 이미지 로드
    def load_multiple(self, paths):
        return [self.load(path) for path in paths]

    # 이미지를 확대 후 랜덤 크롭
    def resize_and_crop_random(self, img, target_width, target_height):
        h, w = img.shape[:2]
        
        scale_w = target_width / w
        scale_h = target_height / h
        scale = max(scale_w, scale_h) * self.resize_scale_factor
        
        new_w, new_h = int(w * scale), int(h * scale)
        resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
        
        max_start_x = max(0, new_w - target_width)
        max_start_y = max(0, new_h - target_height)
        
        start_x = random.randint(0, max_start_x)
        start_y = random.randint(0, max_start_y)
        
        cropped = resized[start_y:start_y+target_height, start_x:start_x+target_width]
        return cropped

    # 이미지 회전
    def rotate(self, img, angle):
        h, w = img.shape[:2]
        cx, cy = w // 2, h // 2

        rot_mat = cv2.getRotationMatrix2D((cx, cy), angle, 1.0)
        
        cos = np.abs(rot_mat[0, 0])
        sin = np.abs(rot_mat[0, 1])
        new_w = int(h * sin + w * cos)
        new_h = int(h * cos + w * sin)

        rot_mat[0, 2] += (new_w / 2) - cx
        rot_mat[1, 2] += (new_h / 2) - cy

        rotated = cv2.warpAffine(img, rot_mat, (new_w, new_h), 
                                borderMode=cv2.BORDER_CONSTANT, 
                                borderValue=(0, 0, 0, 0))
        return rotated

    # 랜덤 각도 회전
    def rotate_random(self, img):
        angle = random.randint(0, 359)
        return self.rotate(img, angle)