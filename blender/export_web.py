"""Export full product GLBs and an efficient, genuinely geometric exhibition LOD."""
import bpy, sys, json
from pathlib import Path
from collections import defaultdict
from mathutils import Matrix
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[1]
OUT=ROOT/'sites/hoi-an-catalogue/dist/assets';(OUT/'models').mkdir(parents=True,exist_ok=True)
inventory=json.loads((BASE/'inventory.json').read_text())
by_sku={p['sku']:p for p in inventory['products']}
scene=bpy.context.scene;assert scene.get('collection')=='NEW HOI AN 2026'
original=list(scene.objects)
def ancestor(obj,kind):
    while obj:
        if obj.get('kind')==kind:return obj
        obj=obj.parent
    return None
roots=[obj for obj in original if obj.get('kind')=='product']
parts=[obj for obj in original if obj.get('kind')=='articulation']
for image in bpy.data.images:
    if max(image.size)>1024 and image.name!='Render Result':
        ratio=1024/max(image.size);image.scale(max(1,round(image.size[0]*ratio)),max(1,round(image.size[1]*ratio)))
for mat in bpy.data.materials:
    if not mat.use_nodes:continue
    bs=mat.node_tree.nodes.get('Principled BSDF')
    if bs and bs.inputs['Normal'].is_linked and bs.inputs['Normal'].links[0].from_node.type=='BUMP':
        mat.node_tree.links.remove(bs.inputs['Normal'].links[0])
    if bs and mat.name.lower().startswith('mirror'):
        bs.inputs['Metallic'].default_value=.85;bs.inputs['Roughness'].default_value=.10
groups=defaultdict(list)
for obj in original:
    if obj.type in {'MESH','CURVE','FONT'}:groups[ancestor(obj,'articulation') or ancestor(obj,'product')].append(obj)
dg=bpy.context.evaluated_depsgraph_get();batches=[];full_triangles=0
for owner,objects in groups.items():
    vertices=[];faces=[];uvs=[];normals=[];indices=[];smooth=[];materials=[];mi={}
    inverse=owner.matrix_world.inverted_safe() if owner else Matrix.Identity(4)
    for obj in objects:
        evaluated=obj.evaluated_get(dg);data=evaluated.to_mesh(preserve_all_data_layers=True,depsgraph=dg)
        if not data:continue
        data.calc_loop_triangles();matrix=inverse@obj.matrix_world;nmat=matrix.to_3x3().inverted_safe().transposed();offset=len(vertices)
        vertices.extend(tuple(matrix@v.co) for v in data.vertices)
        for tri in data.loop_triangles:
            mat=data.materials[tri.material_index] if data.materials else bpy.data.materials.get('Stone')
            if mat is None:mat=bpy.data.materials['Stone']
            mat=bpy.data.materials.get(mat.name)
            if mat.name not in mi:mi[mat.name]=len(materials);materials.append(mat)
            indices.append(mi[mat.name]);smooth.append(tri.use_smooth);faces.append(tuple(offset+i for i in tri.vertices))
            for loop in tri.loops:
                uvs.extend(tuple(data.uv_layers.active.data[loop].uv) if data.uv_layers.active else (0,0))
                normals.append(tuple((nmat@data.corner_normals[loop].vector).normalized()))
        evaluated.to_mesh_clear()
    data=bpy.data.meshes.new((owner.name if owner else 'Open exhibition')+' web batch');data.from_pydata(vertices,[],faces);data.update()
    for mat in materials:data.materials.append(mat)
    for polygon,index,sm in zip(data.polygons,indices,smooth):polygon.material_index=index;polygon.use_smooth=sm
    uv=data.uv_layers.new(name='UVMap');uv.data.foreach_set('uv',uvs);data.normals_split_custom_set(normals)
    obj=bpy.data.objects.new(data.name,data);scene.collection.objects.link(obj)
    if owner:obj.parent=owner
    else:obj['kind']='exhibition-staging';obj['walls']=0;obj['roof']=False
    batches.append(obj);full_triangles+=len(faces)
    print('HOI_AN_WEB_BATCH',owner.name if owner else 'Staging',len(faces),flush=True)
for obj in original:
    if obj.type in {'MESH','CURVE','FONT','LIGHT','CAMERA'}:obj.hide_render=True;obj.hide_set(True)
scene.camera=None
def select(objects):
    for obj in scene.objects:obj.select_set(False)
    for obj in objects:obj.select_set(True)
def export(path):
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,
        export_yup=True,export_normals=True,export_tangents=True,export_materials='EXPORT',
        export_animations=False,export_cameras=False,export_lights=False,export_extras=True,
        export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6,
        export_draco_position_quantization=14,export_draco_normal_quantization=10,export_draco_texcoord_quantization=12)
report=[];seen=set()
for root in roots:
    sku=root['product_id']
    if sku in seen:continue
    seen.add(sku);desc=[obj for obj in root.children_recursive if obj in batches or obj in parts]
    oldloc=root.location.copy();oldrot=root.rotation_euler.copy();root.location=(0,0,0);root.rotation_euler=(0,0,0)
    select([root]+desc);export(OUT/'models'/(sku+'.glb'))
    root.location=oldloc;root.rotation_euler=oldrot
    report.append({**by_sku[sku],'room':root['room'],'model':'assets/models/'+sku+'.glb',
                   'articulations':sum(obj.get('kind')=='articulation' for obj in desc),'finish':inventory['finish']})
# Full inspectors retain the fine weave. The full-room LOD reduces repeated
# triangle work while keeping geometric openings and all moving-part roots.
for obj in batches:
    if obj.parent and len(obj.data.polygons)>12000:
        select([obj]);bpy.context.view_layer.objects.active=obj
        mod=obj.modifiers.new('Exhibition-only geometry LOD','DECIMATE');mod.ratio=.54;mod.use_collapse_triangulate=True
        bpy.ops.object.modifier_apply(modifier=mod.name)
select(batches+roots+parts);export(OUT/'hoi-an-exhibition.glb')
order={p['sku']:i for i,p in enumerate(inventory['products'])};report.sort(key=lambda p:order[p['sku']])
(OUT/'products.json').write_text(json.dumps(report,indent=2),encoding='utf8')
(OUT/'scene.json').write_text(scene['web_scene_info'],encoding='utf8')
summary={'collection':'NEW HOI AN','products':len(report),'placements':len(roots),'movingParts':len(parts),
         'fullTriangles':full_triangles,'exhibitionTriangles':sum(len(obj.data.polygons) for obj in batches),
         'batches':len(batches),'exhibitionBytes':(OUT/'hoi-an-exhibition.glb').stat().st_size,
         'productBytes':{p['sku']:(OUT/'models'/(p['sku']+'.glb')).stat().st_size for p in report}}
(BASE/'export-report.json').write_text(json.dumps(summary,indent=2));print('HOI_AN_EXPORT_COMPLETE',json.dumps(summary),flush=True)
