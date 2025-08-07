

from pathlib import Path
import random

import deengi
import numpy as np

IMAGE_FOLDER_PATH = 'assets/img'

def get_positions_around(start, n):
    sx,sy = start
    positions = []
    for x in np.arange(sx-1,sx+2):
        for y in np.arange(sy-1, sy+2):
            positions.append((x,y))   
    positions.append((sx,sy+2))
    positions.append((sx+1,sy+2))
    positions.append((sx+2,sy+2))
    positions.append((sx+2,sy+1))
    positions.append((sx+2,sy))
    if n > len(positions):
        raise ValueError(f"only {len(positions)} positions available, {n} requested")
    return positions[:n]

def get_line_positions(start, n, offset=(1,1)):
    sx,sy = start
    ox, oy = offset
    return [(sx+ox*i%5+i//5, sy+oy*i%5) for i in range(n)]

def create_layout(categorized_items, anchors, pos_func):
    layout = {}
    for catname, kws in categorized_items.items():
        cat_positions = pos_func(anchors.get(catname), len(kws))
        for name in kws:
            layout[name] = cat_positions.pop()
    return layout

def get_categorized_assets(image_folder_path=None) -> dict:
    path = Path(image_folder_path or IMAGE_FOLDER_PATH)
    landscape = {}
    for category in path.iterdir():
        if not category.is_dir():
            print(f"Non categorized file {category} in {path=}")
            continue
        
        landscape[category.name] = {}
        
        for tile in category.iterdir():
            if not tile.is_file() or not tile.suffix.lower() in (".png", ".jpg"):
                print(f"Non-image file {tile} in {category=}")
                continue
            
            landscape[category.name][tile.name[:-4].upper()] = tile.as_posix().upper()
    return landscape

def get_all_assets(categorized_assets):
    flat = {}
    for cat, dictionary in categorized_assets.items():
        for key, value in dictionary.items():
            flat[key] = {"path": value, "category": cat}
    return flat

class Landscape:
    def __init__(self, image_folder_path=IMAGE_FOLDER_PATH, layout="pestel", debug=True):
        
        
        self.background_colors = {
            'Economic': (224,233,198),
            'Environmental': (161,219,246),
            "Legal": (243,200,192),
            "Political": (246,219,184), 
            "Social": (199,212,235), 
            "Technological": (221,213,170),
            "Spatial": (235,199,218),
            "Process+Methods": (184,222,212),
        }

        self.colors = {
            'Economic': (58,73,42),
            'Environmental': (34,75,94),
            "Legal": (83,43,38),
            "Political": (81,58,28), 
            "Social": (43,54,74), 
            "Technological": (63,56,15),
            "Spatial": (74,42,60),
            "Process+Methods": (31,62,54)
        }
        
        self.pestel_anchors = {
            "Political":(-4, 2.5), 
            "Spatial": (-1,1),
            'Economic':(-1,4),
            "Social": (2, 2.5), 
            "Legal":(-4, -0.5),
            'Environmental': (2,-0.5),
            "Technological": (-1,-2),
            "Process+Methods": (2.5,-4)}

        self.line_anchors = {
            'Economic':(0, 0),
            "Legal":(2,-2),
            "Social": (4,-4), 
            "Spatial": (6, -6),
            "Process+Methods": (8,-8),
            'Environmental': (10,-10),    
            "Political":(12,-12), 
            "Technological": (14,-14),
            }

        self.camera_conf={
            "pestel": {"pos": (0.5,0.5), "zoom": 1},
            "line": {"pos": (10,-5), "zoom": 0.8}
        }
        
        self.layout_name = layout
        
        self.engine = self.setup_engine(debug=debug)
        
        self.assets = get_categorized_assets(image_folder_path)
        self.keywords = get_all_assets(self.assets)
        self.keyword_names= list(self.keywords.keys())
        self.add_tiles_to_keywords(debug=debug)
        
        
        self.labels_visible = True
        self.headers_visible = True
        self.labels = self.add_labels_to_keywords()
        self.headers = self.create_header_labels()

        self.register_renderables()
        self.set_layout(self.layout_name)
                
        self.project_kw_default_amount = 10
        self.project_keywords = self.random_project_keywords()
        
        self._p = False
        self.bind_keys()
        

        
        self.layout_tiles()
        self.layout_headers()
            
    
    def random_project_keywords(self, n = 10):
        return random.sample(self.keyword_names, n)

    def set_project_keywords(self, kws=None):
        self.project_keywords = kws or self.random_project_keywords()
        self.highlight_project()
    
    def setup_engine(self, debug=True):
        engine = deengi.Engine(screen_size=(1300,1000), debug=debug)
        engine.setup_camera(rotation=45, isometry=0.57, 
                            zoom=self.camera_conf[self.layout_name]["zoom"], 
                            pos=self.camera_conf[self.layout_name]["pos"])
        engine.show_background((230,221,204))
        return engine


    def pestel_layout(self):
        """returns a dict of locations for each keyword"""
        self.anchors = self.pestel_anchors
        return create_layout(self.assets, self.anchors, get_positions_around)
    
    def line_layout(self):        
        self.anchors = self.line_anchors
        return create_layout(self.assets, self.line_anchors, get_line_positions)

        
    def add_tiles_to_keywords(self, debug=True):
        """returns a list of deengi.renderables.Tile instances"""
        for name in self.keywords:
            if debug:
                print(self.keywords[name]['path'])
            tile = deengi.renderables.Tile((0,0), (1,1), self.keywords[name]['path'], use_mask=False, name=name)
            self.keywords[name]['tile'] = tile
            
    def add_labels_to_keywords(self):
        """returns a list of deengi.renderables.Labels instances"""
        labels =   {}
        for name in self.keywords:
            bgcolor = self.colors[self.keywords[name]['category']]
            color = self.background_colors[self.keywords[name]['category']]
            label = deengi.renderables.ui.Label((0,0), 
                                        text=name.replace(" ", "\n"),
                                        color=color,
                                        size=16,
                                        outline_color=bgcolor)
            label.visible = self.labels_visible
            self.keywords[name]['label'] = label
            labels[name] = label
        return labels
            
    def create_header_labels(self):
        headers = {}
        for catname in self.assets.keys():
            color = self.colors[catname]
            bgcolor = self.background_colors[catname]
            catlabel = deengi.renderables.ui.Label((0,0), text=catname, color=bgcolor, outline_color=color, size=36)
            catlabel.font = self.engine.renderer.titlefont
            catlabel.visible = self.headers_visible
            headers[catname] = catlabel
        return headers
        
    
    def layout_tiles(self):
        """set tile and label positions according to layout"""
        for kw, pos in self.layout().items():
            tile = self.keywords[kw]["tile"]
            tile.pos = pos
            label = self.keywords[kw]["label"]
            label.pos = (pos[0]+0.75, pos[1])
            
    def layout_headers(self):
        for name, label in self.headers.items():
            p = self.anchors[name]
            label.pos = (p[0]-1, p[1]-1)
                
    def set_layout(self, layoutname="pestel"):
        if layoutname == "pestel":
            self.layout = self.pestel_layout
        elif layoutname == "line":
            self.layout = self.line_layout
        else:
            raise ValueError(f"Invalid layout: {layoutname}")
        
    def register_renderables(self):
        for kw in self.keywords:
            self.engine.add_to_layer("main", self.keywords[kw]["tile"])
        for kw in self.keywords:
            self.engine.add_to_layer("main", self.keywords[kw]["label"])
        for l in self.headers.values():
            self.engine.add_to_layer("main", l)
            
        
    def highlight_project(self):
        for name, kw in self.keywords.items():
            tile = kw["tile"]
            label = kw["label"]
            if name in self.project_keywords:
                tile.highlighted = True
                label.visible = True and self.labels_visible
            else:
                tile.highlighted = False
                label.visible = False 
                
    def show_all(self):
        for kw in self.keywords.values():
            tile = kw["tile"]
            label = kw["label"]
            tile.highlighted = True
            label.visible = True and self.labels_visible
                
    def p(self):
        if not self._p:
            self._p = True            
            self.highlight_project()
        else:
            self._p = False
            self.show_all()
            
            
    def show_labels(self, flag):
        for kws in self.keywords.values():
            label = kws.get('label')
            label.visible = flag
        
    def toggle_label_visibility(self):
        self.labels_visible = not self.labels_visible
        self.show_labels(self.labels_visible)
        self.layout_tiles()
        
    def toggle_layout(self):
        self.layout_name = "line" if self.layout_name == "pestel" else "pestel"
        self.set_layout(self.layout_name)
        self.layout_tiles()
        self.layout_headers()
                   
    
    def bind_keys(self):
        engine = self.engine
        engine.bind_key("q", engine.quit)
        engine.bind_key("d", engine.toggle_debug)
        # engine.bind_key("g", engine.toggle_visibility_cb(grid))
        engine.bind_key("p", self.p)
        engine.bind_key("n", self.set_project_keywords, binding_name="Set project keywords")
        engine.bind_key("l", self.toggle_label_visibility)
        engine.bind_key("h", engine.toggle_visibility_cb(*self.headers.values()))
        engine.bind_key("a", self.toggle_layout)
        
    def show(self):
        for key, bind_type, label in self.engine.get_keybinds():
            self.engine.show_debug(" ".join([bind_type, key, label]))
        
        self.engine.run()
        
    
if __name__ == '__main__':
    landscape = Landscape(layout="pestel", debug=True)
    
    print(landscape.keyword_names)
    
    import json
    with open("all_results_may.json", "r", encoding="utf-8") as f:
        projects = json.load(f)
    
    from functools import partial
    for i, project in enumerate(projects):
        kw_upper = set(k.upper() for k in project["keywords"])
        print(len(kw_upper), kw_upper)
        print(len(set(landscape.keyword_names) & kw_upper))
        print(len(kw_upper - set(landscape.keyword_names)), kw_upper - set(landscape.keyword_names))
        print("___")
        landscape.engine.bind_key(str(i+1), lambda: landscape.set_project_keywords(project["keywords"]), binding_name=f"Project {i+1}")
    
    landscape.show()