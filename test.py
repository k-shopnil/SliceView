from core.obj_parser import load_obj
data = load_obj('assets/models/cube.obj')
print(f"Loaded {len(data)//3} vertices.")