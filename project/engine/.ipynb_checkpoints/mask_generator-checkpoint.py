import numpy as np, cv2
import random

# 이미지 마스크 생성 클래스
class MaskGenerator:

    # 메인 이미지용 기본 도형 마스크 생성
    def create_main_mask(self, shape_type, w, h):
        mask = np.zeros((h, w), dtype=np.uint8)
        center = (w//2, h//2)
        radius = min(w, h) // 2
        cv2.circle(mask, center, radius, 255, -1)      
            
        return mask

    # 조각 이미지용 다각형 마스크 생성
    def create_piece_mask(self, w, h, polygon_config):
        mask = np.zeros((h, w), dtype=np.uint8)

        # 80% 확률로 다각형 변환
        if random.random() < 0.8:
            
            # 다각형 마스크
            center_x = w // 2
            center_y = h // 2

            # polygon_config에서 설정값 가져오기
            min_vertices = polygon_config.get("min_vertices", 3)
            max_vertices = polygon_config.get("max_vertices", 8)
            radius_min = polygon_config.get("radius_min", 0.3)
            radius_max = polygon_config.get("radius_max", 0.5)
            noise_ratio = polygon_config.get("noise_ratio", 0.1)

            # 랜덤 꼭짓점의 개수
            num_vertices = random.randint(min_vertices, max_vertices)
            
            points = []
        
            for i in range(num_vertices):
                # 기본 각도 + 노이즈 추가
                angle = (i / num_vertices) * 2 * np.pi + random.uniform(-0.3, 0.3)
    
                # 반지름 랜덤
                radius_x = w * random.uniform(radius_min, radius_max)
                radius_y = h * random.uniform(radius_min, radius_max)
    
                # 기본 좌표 계산
                px = int(center_x + np.cos(angle) * radius_x)
                py = int(center_y + np.sin(angle) * radius_y)
    
                # 추가 노이즈
                px += random.randint(-int(w * noise_ratio), int(w * noise_ratio))
                py += random.randint(-int(h * noise_ratio), int(h * noise_ratio))
    
                # 범위 내로 제한
                px = max(0, min(w-1, px))
                py = max(0, min(h-1, py))
                
                points.append([px, py])
    
            # 다각형 채우기
            points = np.array(points, dtype=np.int32)
            cv2.fillPoly(mask, [points], 255)
    
            # 가우시안 블러를 통한 경계 처리
            mask = cv2.GaussianBlur(mask, (3, 3), 0)
        else:
            cv2.rectangle(mask, (0, 0), (w, h), 255, -1) 
        
        return mask