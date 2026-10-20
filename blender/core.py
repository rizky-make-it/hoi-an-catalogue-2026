"""HOI AN metric geometry and physically based materials. Blender 5.2+."""
import bpy, math, random
import numpy as np
from pathlib import Path
from mathutils import Vector

BASE=Path(__file__).resolve().parent
M={}; PARENT=None
def set_parent(obj):
    global PARENT
    PARENT=obj
def link(obj):
    bpy.context.scene.collection.objects.link(obj)
    if PARENT: obj.parent=PARENT
    return obj
def empty(name,loc=(0,0,0),props=None):
    ob=link(bpy.data.objects.new(name,None)); ob.location=loc
    ob.empty_display_size=.15
    for k,v in (props or {}).items(): ob[k]=v
    return ob
def mesh(name,verts,faces,mat=None,uvs=None,smooth=False):
    data=bpy.data.meshes.new(name); data.from_pydata(verts,[],faces); data.update()
    ob=link(bpy.data.objects.new(name,data))
    if mat: data.materials.append(M[mat] if isinstance(mat,str) else mat)
    if uvs is not None:
        uv=data.uv_layers.new(name='UVMap')
        flat=[]
        # Accept either one UV per vertex, or per polygon corner.
        per_vertex=len(uvs)==len(verts) and len(uvs)!=len(data.loops)
        for p in data.polygons:
            for li in p.loop_indices:
                flat.extend(uvs[data.loops[li].vertex_index] if per_vertex else uvs[li])
        uv.data.foreach_set('uv',flat)
    else:
        uv=data.uv_layers.new(name='UVMap')
        for p in data.polygons:
            axis=max(range(3),key=lambda a:abs(p.normal[a])); axes=[a for a in range(3) if a!=axis]
            for li in p.loop_indices:
                co=data.vertices[data.loops[li].vertex_index].co
                uv.data[li].uv=(co[axes[0]],co[axes[1]])
    if smooth:
        for p in data.polygons: p.use_smooth=True
    return ob
def box(name,loc,dims,mat=None,bevel=.004,rot=None):
    x,y,z=[v/2 for v in dims]
    verts=[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
    ob=mesh(name,verts,[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],mat)
    ob.location=loc
    if rot: ob.rotation_euler=rot
    if bevel:
        mod=ob.modifiers.new('Soft manufactured edge','BEVEL'); mod.width=min(bevel,min(dims)*.42); mod.segments=3
        mod=ob.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL'); mod.keep_sharp=True
    return ob
def sphere(name,loc,scale,mat,segments=32,rings=16):
    verts=[]; faces=[]; uvs=[]
    for j in range(rings+1):
        t=math.pi*j/rings
        for i in range(segments+1):
            a=2*math.pi*i/segments
            verts.append((scale[0]*math.sin(t)*math.cos(a),scale[1]*math.sin(t)*math.sin(a),scale[2]*math.cos(t)))
            uvs.append((i/segments,j/rings))
    for j in range(rings):
        for i in range(segments):
            q=j*(segments+1)+i; faces.append((q,q+1,q+segments+2,q+segments+1))
    ob=mesh(name,verts,faces,mat,uvs,True); ob.location=loc; return ob
def lathe(name,loc,profile,mat,segments=48):
    verts=[]; faces=[];uvs=[]
    for j,(r,z) in enumerate(profile):
        for i in range(segments+1):
            a=2*math.pi*i/segments; verts.append((r*math.cos(a),r*math.sin(a),z));uvs.append((i/segments,z))
    for j in range(len(profile)-1):
        for i in range(segments):
            q=j*(segments+1)+i;faces.append((q,q+1,q+segments+2,q+segments+1))
    ob=mesh(name,verts,faces,mat,uvs,True);ob.location=loc;return ob
def cylinder(name,loc,radius,depth,mat):
    return lathe(name,loc,[(0,-depth/2),(radius,-depth/2),(radius,depth/2),(0,depth/2)],mat,32)
def rod(name,start,end,radius,mat):
    a,b=Vector(start),Vector(end);ob=cylinder(name,(a+b)/2,radius,(b-a).length,mat);ob.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return ob
def curve(name,points,radius,mat,cyclic=False):
    data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D';data.resolution_u=1;data.bevel_depth=radius;data.bevel_resolution=2
    p=data.splines.new('POLY');p.points.add(len(points)-1);p.use_cyclic_u=cyclic
    for pt,co in zip(p.points,points):pt.co=(*co,1)
    ob=link(bpy.data.objects.new(name,data));data.materials.append(M[mat] if isinstance(mat,str) else mat);return ob
def material(name,color,roughness=.6,metallic=0):
    mat=bpy.data.materials.new(name);mat.use_nodes=True;mat.diffuse_color=(*color,1)
    bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=roughness;bs.inputs['Metallic'].default_value=metallic
    return mat
def image_map(mat,path,channel,noncolor=False,strength=.35):
    nodes=mat.node_tree.nodes;links=mat.node_tree.links;bs=nodes.get('Principled BSDF')
    image=bpy.data.images.load(str(path),check_existing=True)
    if noncolor:image.colorspace_settings.name='Non-Color'
    image.pack();tex=nodes.new('ShaderNodeTexImage');tex.image=image
    if channel=='Normal':
        normal=nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=strength
        links.new(tex.outputs['Color'],normal.inputs['Color']);links.new(normal.outputs['Normal'],bs.inputs['Normal'])
    else:links.new(tex.outputs['Color'],bs.inputs[channel])
    return tex
def generated(name,rgba,noncolor=False):
    h,w=rgba.shape[:2];im=bpy.data.images.new(name,width=w,height=h,alpha=False)
    if noncolor:im.colorspace_settings.name='Non-Color'
    im.pixels.foreach_set(rgba.astype(np.float32).ravel());im.filepath_raw=str(BASE/'textures'/f'{name}.png');im.file_format='PNG';im.save();im.pack();return Path(im.filepath_raw)
def materials():
    """LCM127 Golden Syrup timber, actual woven cane and cotton microstructure."""
    tex=BASE/'textures';tex.mkdir(exist_ok=True)
    source=bpy.data.images.load(str(tex/'ash_veneer_Diffuse.jpg'),check_existing=True)
    pixels=np.array(source.pixels[:],dtype=np.float32).reshape((source.size[1],source.size[0],4))
    rgb=pixels[:,:,:3];mean=rgb.mean(axis=(0,1))
    pixels[:,:,:3]=np.clip((mean+(rgb-mean)*2.7)*np.array([.60,.50,.36]),.014,1)
    stained=generated('golden_syrup_timber',pixels)
    M['wood']=material('LCM127 Golden Syrup | photographed ash veneer',(.32,.23,.13),.43)
    M['inside']=material('Natural timber drawer interior',(.31,.22,.13),.66)
    for key in ['wood','inside']:
        image_map(M[key],stained,'Base Color')
        image_map(M[key],tex/'ash_veneer_nor_gl.jpg','Normal',True,.28 if key=='wood' else .18)
        image_map(M[key],tex/'ash_veneer_Rough.jpg','Roughness',True)
        mat=M[key];nodes=mat.node_tree.nodes;links=mat.node_tree.links
        coord=nodes.new('ShaderNodeTexCoord');mapping=nodes.new('ShaderNodeMapping')
        mapping.inputs['Scale'].default_value=(.60,.60,1)
        links.new(coord.outputs['UV'],mapping.inputs['Vector'])
        for node in nodes:
            if node.type=='TEX_IMAGE':links.new(mapping.outputs['Vector'],node.inputs['Vector'])
        mat['source']='Ash Veneer / Jenelle van Heerden / Poly Haven / CC0'
        mat['finish']='Interpretation of catalogue LCM127 Golden Syrup'
    colors={
      'cane':((.57,.39,.18),.73,0),'cane_light':((.65,.47,.25),.73,0),
      'cane_dark':((.43,.28,.12),.78,0),'cotton':((.88,.87,.82),.91,0),
      'olive':((.24,.29,.13),.92,0),'linen':((.57,.51,.39),.94,0),
      'stitch':((.76,.72,.60),.88,0),'mirror':((.93,.95,.96),.025,1),
      'black':((.022,.030,.031),.44,.08),'leather':((.29,.16,.07),.6,0),
      'stone':((.72,.69,.61),.82,0),'plinth':((.81,.77,.66),.76,0),
      'floor':((.64,.59,.48),.78,0),'sage':((.24,.30,.22),.84,0),
      'ceramic':((.61,.56,.44),.48,0),'paper':((.77,.73,.63),.92,0),
      'leaf':((.12,.20,.09),.75,0),'rug':((.68,.62,.49),.98,0),
      'soil':((.022,.018,.012),1,0),'sign':((.035,.075,.080),.8,0),
      'light':((.98,.81,.53),.4,0),'glass':((.93,.95,.94),.08,0),
      'brass':((.39,.29,.15),.36,.75),'plaster':((.77,.74,.66),.9,0),
      'trim':((.79,.76,.68),.7,0),
    }
    for key,(col,r,metal) in colors.items():M[key]=material(key.title(),col,r,metal)
    n=1024;yy,xx=np.mgrid[0:n,0:n]/n
    dx=np.cos(xx*math.tau*148)*np.sin(yy*math.tau*152)*.19
    dy=np.sin(xx*math.tau*148)*np.cos(yy*math.tau*152)*.19
    normal=np.stack([.5-dx,.5-dy,np.ones_like(xx),np.ones_like(xx)],axis=2)
    cloth=generated('woven_fibre_normal',normal,True)
    for key in ['cotton','olive','linen','rug','stitch']:
        image_map(M[key],cloth,'Normal',True,.42 if key=='cotton' else .63)
        M[key].node_tree.nodes.get('Principled BSDF').inputs['Sheen Weight'].default_value=.28
    for key in ['cane','cane_light','cane_dark','stone','ceramic','leather']:
        mat=M[key];nodes=mat.node_tree.nodes;links=mat.node_tree.links
        bs=nodes.get('Principled BSDF');noise=nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value=360 if key.startswith('cane') else 175
        bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12
        bump.inputs['Distance'].default_value=.00022 if key.startswith('cane') else .0008
        links.new(noise.outputs['Fac'],bump.inputs['Height'])
        links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    bs=M['glass'].node_tree.nodes.get('Principled BSDF')
    bs.inputs['Transmission Weight'].default_value=1;bs.inputs['IOR'].default_value=1.45
    bs=M['light'].node_tree.nodes.get('Principled BSDF')
    bs.inputs['Emission Color'].default_value=(1,.79,.48,1);bs.inputs['Emission Strength'].default_value=3
    return M

def light(name,kind,loc,power,color=(1,.86,.68),target=None,size=1):
    data=bpy.data.lights.new(name,kind);data.energy=power;data.color=color
    if kind=='AREA':data.shape='DISK';data.size=size
    ob=link(bpy.data.objects.new(name,data));ob.location=loc
    if target:ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
    return ob


