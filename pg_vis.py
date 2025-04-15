from functools import partial
from pathlib import Path
import random

import deengi
import deengi.renderables
import numpy as np

keyword_names = ['Affordability',
 'Business Models',
 'Circular Economy',
 'Cost Analysis',
 'Financial Strategies',
 'Incentives',
 'Marketplace',
 'Ownership Structures',
 'Simulation',
 'Support and Information',
 'Circularity',
 'Climate Adaptation',
 'Embodied Energy',
 'Energy Efficiency',
 'GHG Emissions',
 'Landscape',
 'PE Balance',
 'Resilience',
 'Resource Efficiency',
 'District Regulation',
 'Energy Communities',
 'Energy Market',
 'Innovative Institutional Change',
 'Multi-level Legislation',
 'Participative Instruments',
 'Urban Landuse',
 'City Missions',
 'Decision Support Tools',
 'Distributive Implications',
 'Governance Structure',
 'Political Engagement',
 'Power Analysis',
 'Regulation and Subsidies',
 'Co-Creation',
 'Modeling Tools',
 'Monitoring',
 'Scalability',
 'Behavioural Change',
 'Community Engagement',
 'Cultural Context',
 'Everyday Practices',
 'Heritage',
 'Narrative',
 'Policy',
 'Social Innovation',
 'Social Justice',
 'Wellbeing',
 'District typologies',
 'Governance Framework',
 'Infstrastructure',
 'Mobility',
 'PED boundaries',
 'scalability',
 'Strategic planning',
 'Urban planning tools',
 'Demand-Supply Balance',
 'Energy Savings',
 'Local Renewable Production',
 'Multi-Commodity ES',
 'Storage']

anchors = {
    "Political":(-4, 2.5), 
    "Spatial": (-1,1),
    'Economic':(-1,4),
    "Social": (2, 2.5), 
    "Legal":(-4, -0.5),
    'Environmental': (2,-0.5),
    "Technological": (-1,-2),
    "Process+Methods": (2.5,-4)}

line_anchors = {
    'Economic':(0, 0),
    "Legal":(1,-1),
    "Social": (2,-2), 
    "Spatial": (3, -3),
    "Process+Methods": (4,-4),
    'Environmental': (5,-5),    
    "Political":(6,-6), 
    "Technological": (7,-7),
    }

background_colors = {
    'Economic': (224,233,198),
    'Environmental': (161,219,246),
    "Legal": (243,200,192),
    "Political": (246,219,184), 
    "Social": (199,212,235), 
    "Technological": (221,213,170),
    "Spatial": (235,199,218),
    "Process+Methods": (184,222,212),
}

colors = {
    'Economic': (58,73,42),
    'Environmental': (34,75,94),
    "Legal": (83,43,38),
    "Political": (81,58,28), 
    "Social": (43,54,74), 
    "Technological": (63,56,15),
    "Spatial": (74,42,60),
    "Process+Methods": (31,62,54)
}
           
tile_assets_path = Path("assets") / "img"
def get_landscape_assets(path=tile_assets_path) -> dict:
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
            
            landscape[category.name][tile.name[:-4]] = tile.as_posix()
    return landscape   
        

def flatten(landscape):
    flat = {}
    for cat, dictionary in landscape.items():
        for key, value in dictionary.items():
            flat[key] = {"path": value, "category": cat}
    return flat
        
        
def get_neighbor_pos(pos):
    x,y = pos
    return [(x-1,y), (x+1,y),(x,y-1),(x,y+1)]

def create_random_positions(start, number):
    positions = [start]
    while len(positions) < number-1:
        neighbors = get_neighbor_pos(positions[random.randint(0,len(positions)-1)])
        for neighbor in neighbors:
            if neighbor not in positions:
                positions.append(neighbor)
    return positions

def create_positions_around(start, n):
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

def get_orbit_points(distance, n, center=(0,0)):
    import numpy as np
    import math
    cx, cy = center
    pos = [((round(distance*math.cos(x)+cx), round(distance*math.sin(x)+cy))) for x in np.linspace(0,2*np.pi, n+1)]
    return pos

def create_line_positions(start, offset, n):
    sx,sy = start
    ox, oy = offset
    return [(sx+ox*i%5+i//5, sy+oy*i%5) for i in range(n)]

    
def create_label(pos, kw_name, color, bgcolor, size=16):
    return deengi.renderables.ui.Label((pos[0]+0.75, pos[1]), 
                                        text=kw_name.replace(" ", "\n"),
                                        color=color,
                                        size=size,
                                        outline_color=bgcolor)


def show_all(eng, layout="row", tooltips=True, catlabels=True, tilelabels=True):
    landscape = get_landscape_assets()
    categories = list(landscape.keys())
    # keywords = flatten(landscape)
    tilemap = deengi.renderables.Tilemap()    
    labels = []
    for catname, keywords in landscape.items():
        if layout=="row":
            positions = create_line_positions(line_anchors[catname], (1,1),len(keywords))
        elif layout=="pestel":
            positions = create_positions_around(anchors[catname], len(keywords))
        else:
            raise ValueError("Invalid layout, only 'row' and 'pestel'")
        
        for (keyword, path), pos in zip(keywords.items(), positions):
            tile = deengi.renderables.Tile(pos, (1,1),path, use_mask=False, name=keyword)
            tilemap.add(tile)
            if tooltips: 
                eng.add_tooltip(tile, f"{keyword}")
                 
            labels.append(create_label(pos, keyword, background_colors.get(catname),colors[catname]))
        
        if catlabels:
            x,y=line_anchors[catname]
            catlabel = create_label((x-1,y-1), catname, background_colors.get(catname), colors[catname], size=36)
            catlabel.font = eng.renderer.titlefont
            eng.add_to_layer("main", catlabel)
            
    eng.add_to_layer("main", *tilemap)
    eng.add_to_layer("main", *labels)
    return tilemap, labels
        
    
def show_keywords(eng, keyword_list):
    landscape = flatten(get_landscape_assets())
    positions = create_positions_around((0,0), len(keyword_list))
    print(keyword_list)
    for pos, kw in zip(positions, keyword_list):
        tile = deengi.renderables.Tile(pos, (1,1),landscape[kw]["path"], use_mask=False)
        eng.add_to_layer("main", tile)
    
def show_pestel_topics(eng):
    for catname, pos in anchors.items():
        tile = deengi.renderables.Tile((pos[0]-0.71, pos[1]-1.15), (2.85,2.85), color=background_colors[catname])
        eng.add_to_layer("main", tile)
        catlabel = create_label((pos[0], pos[1]+1), catname, background_colors.get(catname), colors[catname], size=36)
        catlabel.font = eng.renderer.titlefont
        #eng.add_to_layer("main", catlabel)
    
def get_renderables_not_in_kws(keywords, tilemap, labels):
    l = []
    for tile, label in zip(tilemap, labels):
        if not tile.name in keywords:
            l.append(tile)
            l.append(label)
    return l

def create_dummy_project(n=10):
    return [random.choice(keyword_names) for i in range(n)]

def change_group(group, tilemap, labels):
    group.members=[]
    print(len(group.members))#
    new = create_dummy_project()
    print(new)
    group.add(*get_renderables_not_in_kws(new, tilemap, labels))
    print(len(group.members))

if __name__ == "__main__":
    
    eng = deengi.Engine(screen_size=(1300,1000))
    eng.setup_camera(rotation=45, isometry=0.57, zoom=100, pos=(0.5,0.5))

    eng.show_background((230,221,204))
    show_pestel_topics(eng)
    tilemap, labels = show_all(eng, layout="pestel", catlabels=False)
    
    project_kws = [
 'Simulation',
 'Energy Efficiency',
 'PE Balance',
 'Energy Communities',
 'Participative Instruments',
 'City Missions',
 'Modeling Tools',
 'Scalability',
 'Heritage',
 'Narrative',
 'Policy',
 'District typologies',
 'Mobility',
 'PED boundaries',
 'scalability',
 'Urban planning tools',
 'Demand-Supply Balance',
 'Energy Savings',
 'Local Renewable Production',
        ]


    
    grid = eng.show_grid()
    eng.bind_key("d", eng.toggle_debug)
    eng.bind_key("g", eng.toggle_visibility_cb(grid))
    rs = get_renderables_not_in_kws(project_kws, tilemap, labels)
    group = deengi.renderables.RenderGroup("project")
    group.add(*rs)
    callback = partial(get_renderables_not_in_kws, create_dummy_project(10), tilemap, labels)
    eng.bind_key("p", eng.toggle_visibility_cb(*group))
    eng.bind_key("l", eng.toggle_visibility_cb(*labels))
    eng.bind_key("n", partial(change_group, group, tilemap, labels))
    eng.run()
    
