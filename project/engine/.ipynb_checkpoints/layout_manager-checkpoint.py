# 레이아웃 설정 관리 클래스
class LayoutManager:
    
    def __init__(self, canvas_size=(1000, 700)):
        self.canvas_size = canvas_size
        
        # 메인 영역 설정
        self.main_area_width_ratio = 0.35
        self.main_area_height_ratio = 0.35
        
        # 조각 크기 설정
        self.piece_min_size_ratio = 0.3
        self.piece_max_size_ratio = 0.8
        
        # 다각형 설정
        self.polygon_min_vertices = 3
        self.polygon_max_vertices = 8
        self.polygon_radius_min = 0.3
        self.polygon_radius_max = 0.5
        self.polygon_noise_ratio = 0.1
        
        self.main_area = self._calculate_main_area()

    # 메인 영역 계산
    def _calculate_main_area(self):
        w, h = self.canvas_size
        
        mw = int(w * self.main_area_width_ratio)
        mh = int(h * self.main_area_height_ratio)
        mx = (w - mw) // 2
        my = (h - mh) // 2
        
        return {"x": mx, "y": my, "width": mw, "height": mh, "mask": "ellipse"}

    # 조각 크기 범위 반환
    def get_piece_size_range(self, canvas_width, canvas_height):
        min_w = int(canvas_width * self.piece_min_size_ratio)
        max_w = int(canvas_width * self.piece_max_size_ratio)
        min_h = int(canvas_height * self.piece_min_size_ratio)
        max_h = int(canvas_height * self.piece_max_size_ratio)
        
        return ((min_w, max_w), (min_h, max_h))

    # 다각형 설정 반환
    def get_polygon_config(self):
        return {
            "min_vertices": self.polygon_min_vertices,
            "max_vertices": self.polygon_max_vertices,
            "radius_min": self.polygon_radius_min,
            "radius_max": self.polygon_radius_max,
            "noise_ratio": self.polygon_noise_ratio
        }