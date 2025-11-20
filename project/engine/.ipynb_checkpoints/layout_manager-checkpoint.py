# 메인영역 기본값 관리
class LayoutManager:
    def __init__(self, canvas_size=(1000,700)):
        self.canvas_size = canvas_size
        self.main_area = self.default_main_area()

    def default_main_area(self):
        w, h = self.canvas_size
        
        mw = int(w * 0.4)
        mh = int(h * 0.45)
        mx = (w - mw) // 2
        my = (h - mh) // 2
        return {"x": mx, "y": my, "width": mw, "height": mh, "mask": "ellipse"}