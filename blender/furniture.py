"""NEW HOI AN 2026 furniture, reconstructed from the supplied three-page PDF.

All dimensions are metres. X is frontage, Y is depth, the front faces -Y,
and Z is up. Product roots sit at floor centre; the mirror root is at its
lower-edge centre. Catalogue dimensions describe the wooden furniture, not
the small overhangs of soft bedding. This is authored reconstruction, not CAD
provided by the manufacturer. Concealed joinery is a design interpretation.

The cane is real, open basket-weave geometry: alternating warp/weft flattened
reeds pass over and under one another. Each insert is one mesh, not thousands
of independent objects, a photo plane, or a perforation opacity illusion.
"""

import math
import random
from contextlib import contextmanager

import core as c


PRODUCTS = {
    'LV453.B01': ('Queen Bed', (1.600, 2.140, 1.300)),
    'LV453.B02': ('King Bed', (1.900, 2.140, 1.300)),
    'LV453.B41': ('Bedside 2 Drawers', (.550, .420, .580)),
    'LV453.B51': ('Tallboy 4 Drawers', (.950, .450, 1.200)),
    'LV453.B61': ('Dresser 6 Drawers', (1.500, .450, .820)),
    'LV453.B71': ('Mirror', (1.000, .025, 1.000)),
}

_SERIAL = {}
_SKU = None


@contextmanager
def parent(obj):
    previous = c.PARENT
    c.set_parent(obj)
    try:
        yield
    finally:
        c.set_parent(previous)


def b(name, loc, dims, mat='wood', bevel=.0025, rot=None):
    return c.box(name, loc, dims, mat, bevel=bevel, rot=rot)


def cloth_mesh(name, verts, faces, mat, uvfaces=None):
    obj = c.mesh(name, verts, faces, mat, smooth=True)
    if uvfaces is not None:
        uv = obj.data.uv_layers.active
        for polygon, coords in zip(obj.data.polygons, uvfaces):
            for li, xy in zip(polygon.loop_indices, coords):
                uv.data[li].uv = xy
    return obj


def cane_panel(name, x, y, z, w, h, pitch=.0062, seed=0):
    """One closed-ribbon mesh for a fine, truly interlaced cane insert.

    The physical gap between reeds is about 2 mm. Vertical and horizontal
    reeds occupy opposite depths at every crossing, with alternate crossings
    reversed. Three subtly different natural-reed materials add restrained
    handwoven variation. No panel-scale bitmap is used to fake the weave.
    """
    rng = random.Random(seed)
    cols, rows = max(2, round(w/pitch)), max(2, round(h/pitch))
    sx, sz = w/cols, h/rows
    amp, thick = .00073, .00046
    verts, faces, uvs, indices = [], [], [], []

    def add_reed(vertical, index, other_count, spacing, other_spacing):
        # One sample at each transverse reed centre gives a subtle undulation
        # while keeping each complete bed well below one million triangles.
        span = h if vertical else w
        coords = [-span/2] + [-span/2+(j+.5)*other_spacing
                             for j in range(other_count)] + [span/2]
        centre = (index+.5)*spacing-(w if vertical else h)/2
        reed_width = spacing*(.61+rng.uniform(-.027, .027))
        reed_mat = rng.choices((0, 1, 2), weights=(78, 14, 8))[0]
        begin = len(verts)
        for along in coords:
            wave_phase = (along+span/2)/other_spacing-.5
            # Opposite phases ensure a real, nonintersecting over/under pair.
            depth = amp*math.cos(math.pi*(index+wave_phase))
            if not vertical:
                depth = -depth
            depth += .00008*math.sin(along*63+index*.73)
            for cross, dy in ((-reed_width/2, -thick/2),
                              (reed_width/2, -thick/2),
                              (reed_width/2, thick/2),
                              (-reed_width/2, thick/2)):
                xx, zz = ((centre+cross, along) if vertical
                          else (along, centre+cross))
                verts.append((x+xx, y+depth+dy, z+zz))
                uvs.append((cross+reed_width/2+index*.017, along+span/2))
        for j in range(len(coords)-1):
            a = begin+j*4
            for side in range(4):
                following = (side+1) % 4
                face = (a+side, a+following, a+4+following, a+4+side)
                # The cross section's handedness reverses for an X-axis reed.
                faces.append(face if vertical else tuple(reversed(face)))
                indices.append(reed_mat)
        caps = ((begin+3, begin+2, begin+1, begin),
                tuple(begin+4*(len(coords)-1)+i for i in range(4)))
        faces.extend(caps if vertical else [tuple(reversed(f)) for f in caps])
        indices.extend((reed_mat, reed_mat))

    for i in range(cols):
        add_reed(True, i, rows, sx, sz)
    for j in range(rows):
        add_reed(False, j, cols, sz, sx)
    obj = c.mesh(name, verts, faces, 'cane', uvs=uvs, smooth=False)
    for key in ('cane_light', 'cane_dark'):
        obj.data.materials.append(c.M[key])
    for poly, index in zip(obj.data.polygons, indices):
        poly.material_index = index
    obj['construction'] = 'Individual closed warp/weft reeds, alternating over-under basket weave'
    obj['warp_count'] = cols
    obj['weft_count'] = rows
    obj['weave_pitch_m'] = round((sx+sz)/2, 6)
    obj['has_true_gaps'] = True
    return obj


def inset_bead(name, x, y, z, w, h, mat='wood', size=.004):
    for side in (-1, 1):
        b(name+' vertical bead', (x+side*(w-size)/2, y, z),
          (size, size, h), mat, .0007)
        b(name+' horizontal bead', (x, y, z+side*(h-size)/2),
          (w-size*2, size, size), mat, .0007)


def wooden_pull(name, x, y, z, length=.115):
    """A solid matching-timber rectangular pull, not SIENNA's brass bar."""
    # Catalogue close-ups show the narrow wooden handle sitting high on the
    # face's upper rail. Its undercut supplies a usable finger gap.
    for side in (-1, 1):
        b(name+' recessed timber mount', (x+side*(length/2-.012), y-.005, z),
          (.017, .014, .010), 'wood', .0015)
    b(name+' timber grip', (x, y-.013, z+.001),
      (length, .014, .013), 'wood', .0018)


def drawer(name, x, front_y, z, w, h, depth, seed=0):
    """Hollow, operable timber drawer with framed natural-cane insert."""
    pivot = c.empty(name+' sliding pivot', (x, front_y, z), props={
        'kind': 'articulation', 'action': 'drawer', 'product_id': _SKU,
        'distance': round(min(depth*.72, .245), 4),
        'label': name, 'closed_y': front_y,
    })
    rail, stile = min(.025, h*.13), .024
    with parent(pivot):
        for sign in (-1, 1):
            b(name+' front upright', (sign*(w-stile)/2, .010, 0),
              (stile, .020, h), 'wood', .0017)
            b(name+' front cross rail', (0, .010, sign*(h-rail)/2),
              (w-2*stile, .020, rail), 'wood', .0017)
        aperture_w, aperture_h = w-2*stile-.003, h-2*rail-.003
        # The backing is set behind the actual woven sheet; it has no weave
        # picture. True gaps retain small dark recesses, as on the real drawer.
        b(name+' recessed inner front backing', (0, .018, 0),
          (w-.026, .006, h-.022), 'inside', .001)
        cane_panel(name+' handwoven insert', 0, .005, 0,
                   aperture_w, aperture_h, seed=seed)
        inset_bead(name+' inset retaining bead', 0, .003, 0,
                   aperture_w+.005, aperture_h+.005, size=.0035)
        wooden_pull(name+' upper rail pull', 0, -.001, h/2-rail*.52,
                    length=min(.130, w*.27))
        inner_w, inner_h = w-.033, h-.026
        b(name+' drawer bottom', (0, depth/2+.015, -h/2+.018),
          (inner_w, depth-.014, .009), 'inside', .001)
        for sign in (-1, 1):
            b(name+' timber box side', (sign*(w/2-.021), depth/2+.018, -.001),
              (.012, depth-.012, inner_h), 'inside', .0014)
            for k in range(3):
                b(name+' visible side joinery key',
                  (sign*(w/2-.0145), .034, -h*.28+k*h*.25),
                  (.002, .013, .006), 'wood', .0003)
        b(name+' timber box rear', (0, depth+.011, -.001),
          (inner_w, .012, inner_h), 'inside', .0014)
    # Nonmoving wooden slide guides stay within the carcass while opening.
    for sign in (-1, 1):
        b(name+' fixed timber guide',
          (x+sign*(w/2-.010), front_y+depth/2+.015, z-h/2+.014),
          (.008, depth-.030, .012), 'inside', .001)
    return pivot


def cabinet(w, d, h, rows, columns=1, label='Cabinet'):
    """Square post-and-panel case with real drawer bays and inset side panels."""
    post, base = (.044 if w < .7 else .046), (.115 if h < .9 else .125)
    top = .024
    # Posts are continuous legs; broad inset timber sides stop above the floor.
    for sign_x in (-1, 1):
        for sign_y in (-1, 1):
            b(label+' square corner post',
              (sign_x*(w-post)/2, sign_y*(d-post)/2, h/2),
              (post, post, h), 'wood', .002)
        panel_h = h-base-.049
        panel_z = base+panel_h/2+.012
        b(label+' inset solid wood side',
          (sign_x*(w/2-post*.65), .001, panel_z),
          (.014, d-2*post, panel_h), 'wood', .002)
        for zz in (base+.017, h-.035):
            b(label+' side framing rail', (sign_x*(w/2-post/2), 0, zz),
              (post, d-2*post, .032), 'wood', .0018)
    b(label+' broad top board', (0, 0, h-top/2),
      (w-.004, d-.004, top), 'wood', .0022)
    b(label+' recessed rear panel', (0, d/2-.020, (base+h-top)/2),
      (w-2*post, .011, h-top-base), 'inside', .0015)
    b(label+' lower structural shelf', (0, 0, base+.012),
      (w-2*post, d-.035, .023), 'inside', .002)
    b(label+' front lower apron', (0, -d/2+post/2, base+.012),
      (w-2*post, post, .036), 'wood', .0018)
    low, high = base+.035, h-top-.008
    usable_h, inner_w = high-low, w-2*post-.006
    row_h = usable_h/rows
    col_w = inner_w/columns
    if columns > 1:
        b(label+' central vertical drawer partition',
          (0, .007, (low+high)/2), (.014, d-.052, high-low), 'inside', .0013)
    for row in range(rows):
        for col in range(columns):
            x = -inner_w/2+col_w*(col+.5)
            z = low+row_h*(row+.5)
            drawer(label+' drawer '+str(row*columns+col+1),
                   x, -d/2+.022, z, col_w-.005, row_h-.005,
                   d-.069, seed=rows*97+row*13+col*23)
        if row < rows-1:
            b(label+' drawer bay dust rail', (0, .018, low+row_h*(row+1)),
              (inner_w-.008, d-.074, .008), 'inside', .0007)


def round_rect(width, depth, radius=.035, z=0):
    points = []
    for cx, cy, angle in ((width/2-radius, depth/2-radius, 0),
                          (-width/2+radius, depth/2-radius, math.pi/2),
                          (-width/2+radius, -depth/2+radius, math.pi),
                          (width/2-radius, -depth/2+radius, 3*math.pi/2)):
        for i in range(9):
            a = angle+i/8*math.pi/2
            points.append((cx+radius*math.cos(a), cy+radius*math.sin(a), z))
    return points


def pillow(name, loc, width=.64, depth=.43, height=.18,
           tilt=.90, spin=0, seed=0, mat='cotton', tufted=False):
    """Closed, individually wrinkled cushion, piping, and optional real tufts."""
    nx, ny = 36, 26
    verts, faces, uvfaces = [], [], []
    tufts = [((i+.5)/5, (j+.5)/3) for j in range(3) for i in range(5)]
    for side in (1, -1):
        for j in range(ny+1):
            v = j/ny
            for i in range(nx+1):
                u = i/nx
                x, y = (u-.5)*width, (v-.5)*depth
                edge = max(0, math.sin(math.pi*u)*math.sin(math.pi*v))
                puff = height*.5*edge**.38
                wrinkle = (.0048*math.sin(u*58+v*17+seed)*math.exp(-v*12)
                           +.0048*math.sin(v*48-u*11)*math.exp(-u*13)
                           +.0040*math.sin(v*53+u*8)*math.exp(-(1-u)*13))
                indent = 0
                if tufted:
                    for tu, tv in tufts:
                        r2 = ((u-tu)*width)**2+((v-tv)*depth)**2
                        indent += .013*math.exp(-r2/.00028)
                zz = side*(.006+puff+wrinkle*edge**.25-indent)
                verts.append((x+.004*math.sin(v*13+seed)*math.sin(math.pi*u),
                              y+.004*math.sin(u*16+seed)*math.sin(math.pi*v), zz))
    layer = (nx+1)*(ny+1)
    for which in range(2):
        for j in range(ny):
            for i in range(nx):
                a = which*layer+j*(nx+1)+i
                f = (a, a+1, a+nx+2, a+nx+1)
                if which:
                    f = tuple(reversed(f))
                faces.append(f)
                uvfaces.append([(verts[k][0], verts[k][1]) for k in f])
    boundary = ([i for i in range(nx+1)]
                +[j*(nx+1)+nx for j in range(1, ny+1)]
                +[ny*(nx+1)+i for i in range(nx-1, -1, -1)]
                +[j*(nx+1) for j in range(ny-1, 0, -1)])
    for k, a in enumerate(boundary):
        bb = boundary[(k+1) % len(boundary)]
        faces.append((a, a+layer, bb+layer, bb))
        uvfaces.append([(0, 0), (0, .012), (.02, .012), (.02, 0)])
    root = c.empty(name+' placement', loc)
    root.rotation_euler = (tilt, .025*math.sin(seed), spin)
    with parent(root):
        cloth_mesh(name+' inflated sewn textile', verts, faces, mat, uvfaces)
        seam = [(verts[k][0], verts[k][1], 0) for k in boundary]
        c.curve(name+' tailored perimeter piping', seam, .0014, mat, cyclic=True)
        c.curve(name+' fine perimeter seam',
                [(x*.982, y*.974, .007) for x, y, _ in seam],
                .00045, 'stitch' if mat == 'cotton' else mat, cyclic=True)
    return root


def duvet(width, length=1.56, seed=12, mat='cotton'):
    """Real sculpted cloth folds, dropped side hems, and a rolled-back edge."""
    nx, ny = 120, 94
    half = width/2
    verts, faces, uvfaces = [], [], []
    rng = random.Random(seed)
    creases = [(rng.uniform(-half*.90, half*.90), rng.uniform(.05, .85),
                rng.uniform(-.5, .5), rng.uniform(.008, .022),
                rng.uniform(.030, .066)) for _ in range(19)]
    for j in range(ny+1):
        v = j/ny
        yy = -.988+length*v
        for i in range(nx+1):
            u = i/nx*2-1
            x = half*math.sin(u*math.pi/2)
            z = .684-.176*abs(u)**14-.018*math.exp(-v*24)
            z += .008*math.sin(x*7+v*9)*math.sin(math.pi*v)
            z += .006*math.sin(x*13-v*8+.7)*(.3+.7*abs(u)**3)
            for centre, along, angle, amplitude, sigma in creases:
                delta = x-centre-angle*(v-along)
                z += amplitude*math.exp(-(delta/sigma)**2-((v-along)/.22)**2)
            z += .009*math.sin(v*48+u*6)*abs(u)**7
            y = yy+.012*math.sin(u*11+v*3)*(.22+.78*(1-v)**5)
            verts.append((x, y, z))
    for j in range(ny):
        for i in range(nx):
            a = j*(nx+1)+i
            faces.append((a, a+1, a+nx+2, a+nx+1))
            uvfaces.append([(i/nx*width, j/ny*length),
                            ((i+1)/nx*width, j/ny*length),
                            ((i+1)/nx*width, (j+1)/ny*length),
                            (i/nx*width, (j+1)/ny*length)])
    obj = cloth_mesh('Sculpted '+mat+' duvet with natural weight folds',
                     verts, faces, mat, uvfaces)
    boundary = ([i for i in range(nx+1)]
                +[j*(nx+1)+nx for j in range(1, ny+1)]
                +[ny*(nx+1)+i for i in range(nx-1, -1, -1)]
                +[j*(nx+1) for j in range(ny-1, 0, -1)])
    hem = [verts[i] for i in boundary]
    c.curve('Duvet thick tailored hem', hem, .0023, mat, cyclic=True)
    c.curve('Duvet fine sewn hem', [(x*.998, y, z+.002) for x, y, z in hem],
            .0005, 'stitch' if mat == 'cotton' else mat, cyclic=True)
    rollverts, rollfaces = [], []
    for j in range(11):
        t = j/10
        for i in range(nx+1):
            u = i/nx*2-1
            x = half*.980*math.sin(u*math.pi/2)
            y = .475+.110*t+.009*math.sin(u*9)
            z = .659+.023*math.sin(t*math.pi)-.152*abs(u)**10
            z += .004*math.sin(x*18+t*3)
            rollverts.append((x, y, z))
    for j in range(10):
        for i in range(nx):
            a = j*(nx+1)+i
            rollfaces.append((a, a+1, a+nx+2, a+nx+1))
    cloth_mesh('Duvet turned-back soft fold', rollverts, rollfaces, mat)
    return obj


def folded_quilt(width, mat='olive', seed=3):
    """Double-folded, cross-stitched quilt resting over the lower duvet."""
    nx, ny = 100, 54
    verts, faces = [], []
    half = width/2
    for j in range(ny+1):
        v = j/ny
        for i in range(nx+1):
            u = i/nx*2-1
            x = half*math.sin(u*math.pi/2)
            y = -.790+.570*v+.014*math.sin(u*5+v*7)
            z = .724-.155*abs(u)**14
            z += .011*math.sin(v*27+u*3)+.006*math.sin(u*13-v*8)
            z += .014*math.exp(-((v-.93)/.075)**2)
            # Padded quilt cells are geometry, not a flat printed grid.
            z += .006*(math.sin(i/nx*math.pi*10)**2)*(math.sin(v*math.pi*5)**2)
            verts.append((x, y, z))
    for j in range(ny):
        for i in range(nx):
            a = j*(nx+1)+i
            faces.append((a, a+1, a+nx+2, a+nx+1))
    cloth_mesh('Folded padded '+mat+' quilt', verts, faces, mat)
    # One curve object per seam family combines many disconnected splines in
    # Blender; explicit curves remain modest and show on close-up render.
    for j in range(0, ny+1, 9):
        seam = [verts[j*(nx+1)+i] for i in range(nx+1)]
        c.curve('Quilt stitched crosswise channel',
                [(x, y, z+.001) for x, y, z in seam], .00055, mat)
    for i in range(0, nx+1, 10):
        seam = [verts[j*(nx+1)+i] for j in range(ny+1)]
        c.curve('Quilt stitched lengthwise channel',
                [(x, y, z+.001) for x, y, z in seam], .00055, mat)
    for j in (0, ny):
        c.curve('Quilt folded bound edge', [verts[j*(nx+1)+i] for i in range(nx+1)],
                .0021, mat)


def bed(w, d, h, bedding='white'):
    """HOI AN's three-panel timber/cane bed, never the SIENNA frame."""
    post, frame_depth = .052, .052
    hb_y, fy = d/2-frame_depth/2, -d/2+frame_depth/2
    # Continuous square posts preserve the catalogue's stance and full height.
    for side in (-1, 1):
        b('Headboard square timber post', (side*(w-post)/2, hb_y, h/2),
          (post, frame_depth, h), 'wood', .0027)
        b('Footboard square timber leg', (side*(w-post)/2, fy, .253),
          (post, frame_depth, .506), 'wood', .0027)
    for sx in (-1, 1):
        b('Continuous bed side rail', (sx*(w/2-.034), 0, .331),
          (.046, d-2*frame_depth, .136), 'wood', .0035)
        b('Side rail inner slat support ledge', (sx*(w/2-.061), .004, .358),
          (.022, d-.137, .023), 'inside', .002)
    for j in range(15):
        y = -.902+j*.129
        b('Mattress solid timber support slat', (0, y, .379),
          (w-.128, .062, .016), 'inside', .0018)
    b('Central longitudinal support beam', (0, .004, .335),
      (.042, d-.160, .065), 'inside', .002)
    for sy in (-1, 1):
        b('Recessed central support foot', (0, sy*.655, .159),
          (.039, .039, .317), 'wood', .002)
    inner = w-2*post
    # Narrow full-width upper band: it sits above a timber cross rail.
    top_rail, band_bottom, band_top = .042, 1.069, h-.044
    b('Headboard full-width top rail', (0, hb_y, h-top_rail/2),
      (inner, frame_depth, top_rail), 'wood', .0027)
    b('Headboard upper-band lower cross rail', (0, hb_y, band_bottom-.019),
      (inner, frame_depth, .038), 'wood', .0025)
    cane_panel('Headboard continuous narrow upper cane band',
               0, hb_y-.011, (band_bottom+band_top)/2,
               inner-.010, band_top-band_bottom-.008, seed=201)
    inset_bead('Headboard upper-band inset bead', 0, hb_y-.012,
               (band_bottom+band_top)/2, inner-.006,
               band_top-band_bottom-.004, size=.004)
    bottom, top = .413, band_bottom-.040
    mullion = .036
    panel_w = (inner-2*mullion)/3
    for i in range(3):
        x = -inner/2+panel_w/2+i*(panel_w+mullion)
        cane_panel('Headboard lower tall cane panel '+str(i+1),
                   x, hb_y-.011, (bottom+top)/2,
                   panel_w-.008, top-bottom-.008, seed=210+i)
        inset_bead('Headboard lower panel bead '+str(i+1), x, hb_y-.012,
                   (bottom+top)/2, panel_w-.004, top-bottom-.004, size=.004)
        if i < 2:
            b('Headboard square intermediate stile',
              (x+panel_w/2+mullion/2, hb_y, (bottom+top)/2),
              (mullion, frame_depth, top-bottom+.010), 'wood', .002)
    b('Headboard lower structural cross rail', (0, hb_y, bottom-.019),
      (inner, frame_depth, .038), 'wood', .0025)
    # The footboard is low enough to expose the white/olive bedding, but all
    # three basket-weave sections are visible in the hero three-quarter view.
    foot_bottom, foot_top = .179, .465
    rail = .037
    for zz in (foot_bottom+rail/2, foot_top-rail/2):
        b('Footboard horizontal timber rail', (0, fy, zz),
          (inner, frame_depth, rail), 'wood', .0025)
    pane_h = foot_top-foot_bottom-2*rail
    for i in range(3):
        x = -inner/2+panel_w/2+i*(panel_w+mullion)
        cane_panel('Footboard handwoven panel '+str(i+1), x, fy-.013,
                   (foot_bottom+foot_top)/2, panel_w-.008, pane_h-.005,
                   seed=230+i)
        inset_bead('Footboard cane retaining bead '+str(i+1), x, fy-.014,
                   (foot_bottom+foot_top)/2, panel_w-.004, pane_h-.001,
                   size=.004)
        if i < 2:
            b('Footboard intermediate square stile',
              (x+panel_w/2+mullion/2, fy, (foot_bottom+foot_top)/2),
              (mullion, frame_depth, foot_top-foot_bottom), 'wood', .002)
    # Small recessed side-rail connector plugs: plausible assembly detail,
    # intentionally distinct from any proprietary concealed construction.
    for sx in (-1, 1):
        for yy in (-d/2+.10, d/2-.10):
            for zz in (.307, .354):
                plug = c.cylinder('Recessed bed rail connector plug',
                                  (sx*(w/2-.009), yy, zz), .0034, .0015, 'wood')
                plug.rotation_euler[1] = math.pi/2
    # Soft goods are exhibition styling, not extra catalogue SKUs.
    mattress_w, mattress_d = w-.108, d-.149
    b('Natural cotton mattress with rounded corners', (0, .004, .508),
      (mattress_w, mattress_d, .240), 'cotton', .047)
    for zz in (.405, .600):
        c.curve('Mattress tailored edge piping',
                [(x, y+.004, zz) for x, y, _ in round_rect(mattress_w-.005, mattress_d-.005)],
                .0015, 'stitch', cyclic=True)
    cloth = 'olive' if bedding == 'olive' else 'cotton'
    duvet(w+.014, seed=42 if cloth == 'olive' else 12, mat=cloth)
    offset = (w-.178)/4
    pw = min(.760, (w-.168)/2)
    for side in (-1, 1):
        pillow(('Left' if side < 0 else 'Right')+' standing white rear pillow',
               (side*offset, .780, .819), width=pw, depth=.485,
               height=.167, tilt=1.13, spin=side*-.018,
               seed=2 if side < 0 else 5, mat='cotton')
        pillow(('Left' if side < 0 else 'Right')+' layered '+cloth+' cushion',
               (side*offset, .606, .788), width=pw*.94, depth=.423,
               height=.155, tilt=1.03, spin=side*.012,
               seed=7 if side < 0 else 11, mat=cloth, tufted=cloth == 'olive')
    if cloth == 'olive':
        folded_quilt(w+.025, mat='olive')
        # A white turned-back sheet ties the olive styling to the hero photo.
        b('White folded sheet at cushion line', (0, .455, .660),
          (w-.130, .094, .018), 'cotton', .008)


def mirror(w, d, h):
    """Plain, thin square Golden Syrup frame with optically reflective glass."""
    rail = .043
    for side in (-1, 1):
        b('Mirror vertical timber frame', (side*(w-rail)/2, 0, h/2),
          (rail, d, h), 'wood', .0017)
        b('Mirror horizontal timber frame',
          (0, 0, rail/2 if side < 0 else h-rail/2),
          (w-2*rail, d, rail), 'wood', .0017)
    b('Mirror protective rear backing', (0, d/2-.003, h/2),
      (w-2*rail+.006, .006, h-2*rail+.006), 'inside', .0008)
    b('Reflective silvered mirror glass', (0, -d/2+.005, h/2),
      (w-2*rail+.002, .003, h-2*rail+.002), 'mirror', .0008)
    inset_bead('Mirror fine inner timber lip', 0, -d/2+.001, h/2,
               w-2*rail+.006, h-2*rail+.006, size=.0025)


def create(sku, instance=None, bedding='white'):
    """Build one of the six HOI AN products; drawer travel is local -Y."""
    global _SKU
    if sku not in PRODUCTS:
        raise ValueError('Unknown NEW HOI AN catalogue SKU: '+str(sku))
    old_sku, _SKU = _SKU, sku
    _SERIAL[sku] = _SERIAL.get(sku, 0)+1
    instance_id = instance or sku+'-'+str(_SERIAL[sku]).zfill(2)
    title, dims = PRODUCTS[sku]
    root = c.empty('NEW HOI AN '+sku+' | '+str(instance_id), props={
        'kind': 'product', 'product_id': sku, 'instance_id': instance_id,
        'title': title, 'width_m': dims[0], 'depth_m': dims[1], 'height_m': dims[2],
        'finish': 'LCM127 Golden Syrup',
        'material': 'MDF veneer / oak / pine / mountain ash timber / natural rattan',
        'source': 'NEW HOI AN CATALOGUE 2026, pages 1-3',
        'reconstruction_note': 'Visual reconstruction from catalogue, not manufacturer CAD',
        'bedding_style': bedding if sku in ('LV453.B01', 'LV453.B02') else 'not applicable',
    })
    try:
        with parent(root):
            if sku in ('LV453.B01', 'LV453.B02'):
                bed(*dims, bedding=bedding)
            elif sku == 'LV453.B41':
                cabinet(*dims, rows=2, label='Bedside')
            elif sku == 'LV453.B51':
                cabinet(*dims, rows=4, label='Tallboy')
            elif sku == 'LV453.B61':
                cabinet(*dims, rows=3, columns=2, label='Dresser')
            elif sku == 'LV453.B71':
                mirror(*dims)
    finally:
        _SKU = old_sku
    return root
