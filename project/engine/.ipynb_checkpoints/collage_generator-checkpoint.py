import numpy as np
import random
from engine.layout_manager import LayoutManager
from engine.mask_generator import MaskGenerator
from engine.placer import Placer
from engine.image_manager import ImageManager

# 디지털 콜라주 생성 클래스
class CollageGenerator:
    
    def __init__(self):
        self.image_manager = ImageManager(resize_scale_factor=1.2)
        self.masker = MaskGenerator()
        self.placer = Placer()
        self.canvas_margin = 100

    # 콜라주 생성
    def generate(self, image_paths, canvas_size=(1000, 700), pieces=20):
        # 1. 캔버스 생성
        canvas = self._create_canvas(canvas_size)
        
        # 2. 레이아웃 설정
        layout_manager = self._setup_layout(canvas_size)
        
        # 3. 소스 이미지 로드
        source_images = self.image_manager.load_multiple(image_paths)
        
        # 4. 랜덤 조각들 먼저 배치
        self._add_random_pieces(canvas, source_images, pieces, canvas_size, layout_manager)
        
        # 5. 이후 메인 이미지 준비 및 배치
        main_image = self._prepare_main_image(image_paths[0], layout_manager.main_area)
        self._place_main_image(canvas, main_image, layout_manager.main_area)
        
        # 6. 최종 크기로 자르기
        final = self._crop_to_final_size(canvas, canvas_size)
        
        return final

    # 작업용 캔버스 생성 (여백 포함)
    def _create_canvas(self, canvas_size):
        cw, ch = canvas_size
        work_w = cw + self.canvas_margin * 2
        work_h = ch + self.canvas_margin * 2
        canvas = np.ones((work_h, work_w, 4), dtype=np.uint8) * 255
        return canvas

    # 레이아웃 매니저 생성
    def _setup_layout(self, canvas_size):
        cw, ch = canvas_size
        work_w = cw + self.canvas_margin * 2
        work_h = ch + self.canvas_margin * 2
        return LayoutManager(canvas_size=(work_w, work_h))

    # 메인 이미지 준비 (로드, 크롭, 마스크, 회전)
    def _prepare_main_image(self, image_path, main_area):
        # 이미지 로드
        main_img = self.image_manager.load(image_path)
        
        # 크기 조정 및 랜덤 크롭
        main_resized = self.image_manager.resize_and_crop_random(
            main_img,
            main_area["width"],
            main_area["height"]
        )
        
        # 마스크 적용
        mask_np = self.masker.create_main_mask(
            main_area["mask"],
            main_area["width"],
            main_area["height"]
        )
        main_resized[:, :, 3] = mask_np
        
        # 랜덤 회전
        main_resized = self.image_manager.rotate_random(main_resized)
        
        return main_resized

    # 메인 이미지를 캔버스 중앙에 배치
    def _place_main_image(self, canvas, main_image, main_area):
        rotated_h, rotated_w = main_image.shape[:2]
        
        # 중앙 배치 좌표 계산
        center_x = main_area["x"] + main_area["width"] // 2 - rotated_w // 2
        center_y = main_area["y"] + main_area["height"] // 2 - rotated_h // 2
        
        # 배치
        self.placer.alpha_blend(canvas, main_image, center_x, center_y)

    # 랜덤 조각들을 캔버스에 추가
    def _add_random_pieces(self, canvas, source_images, pieces, canvas_size, layout_manager):
        cw, ch = canvas_size
        work_w = cw + self.canvas_margin * 2
        work_h = ch + self.canvas_margin * 2
        
        for i in range(pieces):
            # 랜덤 소스 이미지 선택
            src = random.choice(source_images)
            
            # 조각 생성
            patch = self._create_random_patch(src, cw, ch, layout_manager)
            
            # 배치 위치 결정
            px, py = self.placer.random_position_avoid_main(
                (work_w, work_h),
                (patch.shape[1], patch.shape[0]),
                layout_manager.main_area
            )
            
            # 배치
            self.placer.alpha_blend(canvas, patch, px, py)

    # 소스 이미지로부터 랜덤 조각 생성
    def _create_random_patch(self, source_img, canvas_w, canvas_h, layout_manager):
        sh, sw = source_img.shape[:2]
        
        # 레이아웃 매니저에서 조각 크기 범위 가져오기
        (min_w, max_w), (min_h, max_h) = layout_manager.get_piece_size_range(canvas_w, canvas_h)
        
        # 랜덤 조각 크기 결정
        pw = random.randint(min_w, max_w)
        ph = random.randint(min_h, max_h)
        
        # 소스 이미지보다 크지 않도록 조정
        if sw <= pw or sh <= ph:
            pw = min(pw, max(1, sw))
            ph = min(ph, max(1, sh))
        
        # 랜덤 크롭
        cx = random.randint(0, max(0, sw - pw))
        cy = random.randint(0, max(0, sh - ph))
        patch = source_img[cy:cy+ph, cx:cx+pw].copy()
        
        # 레이아웃 매니저에서 다각형 설정 가져오기
        polygon_config = layout_manager.get_polygon_config()
        polygon_mask = self.masker.create_piece_mask(pw, ph, polygon_config)
        patch[:, :, 3] = polygon_mask
        
        # 랜덤 회전
        patch = self.image_manager.rotate_random(patch)
        
        return patch

    # 작업 캔버스에서 최종 크기로 자르기
    def _crop_to_final_size(self, canvas, canvas_size):
        cw, ch = canvas_size
        final = canvas[
            self.canvas_margin:self.canvas_margin + ch,
            self.canvas_margin:self.canvas_margin + cw
        ]
        return final