import numpy as np
import random

# 이미지 배치 및 합성 클래스
class Placer:

    # 알파 블렌딩으로 이미지를 합성
    def alpha_blend(self, canvas, patch, x, y):
        ch, cw = canvas.shape[:2]
        ph, pw = patch.shape[:2]

        # 캔버스 경계 내로 제한
        x1, y1 = max(0, x), max(0, y)
        x2, y2 = min(cw, x + pw), min(ch, y + ph)

        # 패치 영역 계산
        px1 = x1 - x
        py1 = y1 - y
        px2 = px1 + (x2 - x1)
        py2 = py1 + (y2 - y1)

        # 영역 밖이면 리턴
        if x2 <= x1 or y2 <= y1:
            return

        # 합성할 영역 추출
        canvas_region = canvas[y1:y2, x1:x2]
        patch_region = patch[py1:py2, px1:px2]

        # 알파 채널 추출 및 정규화
        alpha = patch_region[:, :, 3:4].astype(np.float32) / 255.0

        # 알파 블렌딩
        blended = (patch_region[:, :, :3].astype(np.float32) * alpha +
                   canvas_region[:, :, :3].astype(np.float32) * (1 - alpha))

        # RGB 채널 적용
        canvas[y1:y2, x1:x2, :3] = blended.astype(np.uint8)

        # 알파 채널 합성
        canvas_alpha = canvas_region[:, :, 3:4].astype(np.float32) / 255.0
        new_alpha = alpha + canvas_alpha * (1 - alpha)
        canvas[y1:y2, x1:x2, 3:4] = (new_alpha * 255).astype(np.uint8)

    # 메인 영역을 피해 랜덤 배치 위치 탐색
    def random_position_avoid_main(self, canvas_size, patch_size, main_area):
        cw, ch = canvas_size
        pw, ph = patch_size

        mx = main_area["x"]
        my = main_area["y"]
        mw = main_area["width"]
        mh = main_area["height"]

        for _ in range(50):  # 배치 영역 최대 50번 탐색
            rx = random.randint(0, max(0, cw - pw))
            ry = random.randint(0, max(0, ch - ph))

            # 메인 영역과의 교집합 계산
            inter_w = max(0, min(rx + pw, mx + mw) - max(rx, mx))
            inter_h = max(0, min(ry + ph, my + mh) - max(ry, my))
            inter_area = inter_w * inter_h

            # 겹침이 30% 미만이면 좌표값 리턴
            if inter_area < 0.3 * (pw * ph):
                return rx, ry

        # 실패 시 아무 위치에 반환 
        return random.randint(0, max(0, cw - pw)), random.randint(0, max(0, ch - ph))