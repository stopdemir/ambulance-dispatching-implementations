from typing import Tuple

class GridHelper:
    def __init__(self, n: int):
        self.n: int = n

    def coord_to_index(self, x: int, y: int) -> int:
        return x * self.n + y

    def index_to_coord(self, index: int) -> Tuple[int, int]:
        return divmod(index, self.n)

    def calculate_manhattan_distance(self, a: int, b: int) -> int:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    
    
   


  