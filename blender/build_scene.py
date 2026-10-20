"""Build the NEW HOI AN open exhibition from editable catalogue geometry."""
import bpy, math, sys, json, random, time
from pathlib import Path
from mathutils import Vector

BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE))
import core as c
import furniture as f

started=time.perf_counter();random.seed(453)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
c.materials();scene=bpy.context.scene
scene.unit_settings.system='METRIC';scene.unit_settings.length_unit='METERS'
scene['collection']='NEW HOI AN 2026';scene['layout']='exhibition'
scene['walls']=0;scene['roof']=False;scene['source_pages']=3
c.set_parent(None)
staging=c.empty('HOI AN | interpreted open exhibition',props={'kind':'exhibition','walls':0,'roof':False})
c.set_parent(staging)
floor=c.box('Continuous pale limestone exhibition floor',(6,5,-.10),(14,12,.20),'stone',.045)
floor['kind']='exhibition-floor'
zones={
 'king':{'name':'King suite','label':'01 / KING SUITE','center':[2.8,8.1],'size':[5.1,4.5],'bounds':[0,5.9,5.7,10.6],'camera':[[4.9,6.3,1.65],[2.45,8.3,1.08],40]},
 'queen':{'name':'Queen suite','label':'02 / QUEEN SUITE','center':[9.1,8.1],'size':[5.5,4.5],'bounds':[6.4,5.9,12,10.6],'camera':[[10.9,6.25,1.65],[8.15,8.3,1.04],40]},
 'storage':{'name':'Storage gallery','label':'03 / STORAGE GALLERY','center':[2.8,2.5],'size':[5.1,4.3],'bounds':[0,.2,5.7,4.9],'camera':[[4.9,1.05,1.65],[2.6,2.7,.86],40]},
 'craft':{'name':'The weave study','label':'04 / THE WEAVE STUDY','center':[9.1,2.5],'size':[5.5,4.3],'bounds':[6.4,.2,12,4.9],'camera':[[10.9,.95,1.65],[8.6,2.65,.9],40]},
 'aisle':{'name':'Open gallery aisle','bounds':[-.7,4.7,12.6,5.9],'camera':[[6,5.25,1.65],[8.3,5.25,1.4],40]},
}
for key,zone in zones.items():
    if key=='aisle':continue
    x,y=zone['center'];w,d=zone['size']
    c.box('Low flush display inlay | '+key,(x,y,-.016),(w,d,.03),'plinth',.02)
    c.curve('Fine timber-tone floor border | '+key,[(x-w/2,y-d/2,.002),(x+w/2,y-d/2,.002),(x+w/2,y+d/2,.002),(x-w/2,y+d/2,.002)],.003,'brass',True)

def text(name,body,loc,size=.065,mat='sign'):
    data=bpy.data.curves.new(name,'FONT');data.body=body;data.size=size
    data.align_x='CENTER';data.align_y='CENTER';data.extrude=.0002
    obj=c.link(bpy.data.objects.new(name,data));obj.location=loc
    obj.rotation_euler=(math.pi/2,0,0);data.materials.append(c.M[mat]);return obj

def sign(label,x,y):
    c.box('Freestanding display sign base',(x,y,.017),(.26,.22,.034),'wood',.004)
    c.box('Display information upright',(x,y,.46),(.018,.018,.90),'wood',.003)
    c.box('Paper display placard',(x,y-.007,.91),(.57,.014,.19),'paper',.007)
    text('Display zone heading',label,(x,y-.015,.934),.029)
    text('Display finish information','LCM127 GOLDEN SYRUP  /  RATTAN',(x,y-.015,.875),.012)
for label,x,y in [('01 / KING SUITE',.57,6.23),('02 / QUEEN SUITE',6.66,6.17),('03 / STORAGE',.62,.70),('04 / THE WEAVE STUDY',6.71,.7)]:sign(label,x,y)
text('HOI AN floor gallery title','HOI AN  /  THE WOVEN COLLECTION',(6,-.36,.01),.15).rotation_euler=(0,0,0)

def rug(name,x,y,w,d):
    c.box(name,(x,y,.014),(w,d,.027),'rug',.014)
    verts=[];faces=[]
    for side in (-1,1):
        for i in range(round(w/.019)):
            xx=x-w/2+.012+i*.019;yy=y+side*d/2;length=.055+random.random()*.023
            q=len(verts);verts.extend([(xx-.002,yy,.018),(xx+.002,yy,.018),(xx+.002+random.uniform(-.006,.006),yy+side*length,.007),(xx-.002,yy+side*length,.007)])
            faces.append((q,q+1,q+2,q+3))
    c.mesh(name+' individual woven fringe',verts,faces,'linen')
    c.curve(name+' bound selvedge',[(x-w/2+.012,y-d/2+.012,.028),(x+w/2-.012,y-d/2+.012,.028),(x+w/2-.012,y+d/2-.012,.028),(x-w/2+.012,y+d/2-.012,.028)],.002,'linen',True)
rug('King suite handwoven rug',2.65,8.02,4.5,3.8)
rug('Queen suite handwoven rug',8.65,8.02,4.5,3.8)

placements=[]
def place(sku,zone,position,rotation=0,bedding='white'):
    c.set_parent(None);root=f.create(sku,instance=zone+'-'+str(len(placements)+1),bedding=bedding)
    root.location=position;root.rotation_euler.z=math.radians(rotation);root['room']=zone
    placements.append({'sku':sku,'room':zone,'position':list(position),'rotation':rotation,'instance':root['instance_id']})
    c.set_parent(staging);return root
place('LV453.B02','king',(2.45,8.35,.028),bedding='olive')
place('LV453.B41','king',(1.13,8.89,.028))
place('LV453.B41','king',(3.77,8.89,.028))
place('LV453.B51','king',(4.67,9.25,0))
place('LV453.B01','queen',(8.10,8.35,.028))
place('LV453.B41','queen',(6.91,8.89,.028))
place('LV453.B41','queen',(9.29,8.89,.028))
place('LV453.B61','queen',(10.77,9.14,0))
place('LV453.B71','queen',(10.77,9.28,.87))
place('LV453.B61','storage',(2.0,2.63,0))
place('LV453.B71','storage',(2.0,2.77,.87))
place('LV453.B51','storage',(4.23,2.97,0))

def lamp(name,x,y,z):
    c.cylinder(name+' weighted brass base',(x,y,z+.014),.095,.026,'brass')
    c.cylinder(name+' slim brass stem',(x,y,z+.31),.014,.59,'brass')
    c.lathe(name+' linen cone shade',(x,y,z+.45),[(.19,0),(.13,.28),(.126,.28),(.186,0)],'cotton',64)
    c.sphere(name+' warm internal bulb',(x,y,z+.54),(.035,.035,.055),'light',20,12)
    c.light(name+' warm practical','POINT',(x,y,z+.48),16,(1,.78,.48))
for index,(x,y) in enumerate([(1.13,8.89),(3.77,8.89),(6.91,8.89),(9.29,8.89)]):lamp('Bedside styling lamp '+str(index+1),x,y,.608)

def books(x,y,z):
    for i,col in enumerate(['paper','sage','linen']):
        c.box('Interpreted design book',(x+random.uniform(-.015,.015),y,z+.016+i*.025),(.23,.16,.025),col,.002,rot=(0,0,random.uniform(-.08,.08)))
def vase(name,x,y,z,large=False):
    scale=1.0 if large else .48
    c.lathe(name,(x,y,z),[(r*scale,h*scale) for r,h in [(0,0),(.11,0),(.14,.04),(.16,.19),(.13,.29),(.085,.35),(.078,.36),(.066,.36),(.073,.34)]],'ceramic',48)
    for i in range(7):
        a=i*2.399;tip=(x+math.cos(a)*.21*scale,y+math.sin(a)*.19*scale,z+(.58+random.random()*.24)*scale)
        c.rod(name+' branch',(x,y,z+.27*scale),tip,.002*scale,'black')
        for j in range(2):
            leaf=c.sphere(name+' olive leaf',(tip[0]+.03*j,tip[1],tip[2]-.06*j*scale),(.055*scale,.019*scale,.009*scale),'leaf',12,6)
            leaf.rotation_euler=(random.random(),random.random(),a)
books(4.7,9.25,1.2);vase('Tallboy hand-thrown vase',4.7,9.25,1.28)
books(10.35,9.06,.82);vase('Queen dresser greenery',11.25,9.07,.82,True)
vase('Storage collection ceramic',1.44,2.57,.82);books(2.47,2.58,.82)
for xx,yy in [(2,2.77),(10.77,9.28)]:
    c.rod('Interpreted freestanding mirror support',(xx-.32,yy+.16,.83),(xx-.32,yy+.028,1.77),.013,'wood')
    c.rod('Interpreted freestanding mirror support',(xx+.32,yy+.16,.83),(xx+.32,yy+.028,1.77),.013,'wood')
for name,x,y in [('King linen pouf',4.1,6.95),('Queen linen pouf',10.1,7.05)]:
    c.lathe(name,(x,y,.03),[(0,0),(.27,0),(.29,.04),(.30,.30),(.27,.34),(0,.34)],'linen',56)
    c.curve(name+' top seam',[(x+.279*math.cos(i*math.tau/80),y+.279*math.sin(i*math.tau/80),.35) for i in range(80)],.0018,'stitch',True)

# Craft display: clearly interpreted samples, not additional catalogue SKUs.
for x in (8.05,9.25):
    for y in (2.2,2.8):c.box('Craft display table leg',(x,y,.39),(.045,.045,.78),'wood',.004)
c.box('Craft material sample table',(8.65,2.5,.80),(1.5,.8,.06),'wood',.007)
c.box('Standing cane sample upper rail',(8.65,2.72,1.59),(1.25,.05,.05),'wood',.004)
c.box('Standing cane sample lower rail',(8.65,2.72,.95),(1.25,.05,.05),'wood',.004)
for x in (8.05,9.25):c.box('Standing cane sample side stile',(x,2.72,1.27),(.05,.05,.64),'wood',.004)
f.cane_panel('Interpreted basket-weave study sample',8.65,2.696,1.27,1.15,.585,pitch=.009,seed=700)
for i,mat in enumerate(['wood','cane','linen']):
    c.box('Material finish sample '+mat,(8.15+i*.45,2.27,.845),(.32,.27,.025),mat,.006)
text('Craft display explanatory label','TIMBER  /  WEAVE  /  TEXTILE',(8.65,2.09,.842),.035).rotation_euler=(0,0,0)

# Open-air studio lighting. There is no roof, shell or hidden wall geometry.
world=bpy.data.worlds.new('HOI AN soft neutral studio') if not bpy.data.worlds else bpy.data.worlds[0]
scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.60,.65,.66,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.55
c.set_parent(None)
c.light('Large daylight key','AREA',(-3,-1,10),1800,(1,.91,.76),target=(5,6,0),size=8)
c.light('Broad neutral fill','AREA',(13,3,8),1300,(.88,.94,1),target=(6,5,1),size=7)
c.light('Top soft skylight','AREA',(5,12,10),1600,(1,.96,.86),target=(6,6,0),size=8)
sun=c.light('Warm natural sun','SUN',(-4,-8,12),1.5,(1,.93,.80),target=(5,5,0));sun.data.angle=.18

cameras={
 'overview':((17,-11,14),(6,5.1,.35),47),
 'king':((6.00,3.90,2.60),(2.68,8.55,.71),49),
 'queen':((11.85,4.45,2.48),(8.65,8.6,.75),48),
 'storage':((6.1,-1.95,2.55),(2.7,2.8,.77),51),
 'detail':((4.16,1.29,1.08),(3.95,2.735,.70),82),
}
for key,(location,target,lens) in cameras.items():
    data=bpy.data.cameras.new('Lens '+key);camera=bpy.data.objects.new('Camera '+key,data)
    scene.collection.objects.link(camera);camera.location=location
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    data.lens=lens;data.clip_start=.03;data.clip_end=200;data.dof.use_dof=False
scene.camera=bpy.data.objects['Camera overview']
scene.render.engine='CYCLES';scene.cycles.samples=128;scene.cycles.use_denoising=True
scene.render.resolution_x=3840;scene.render.resolution_y=2160;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.image_settings.color_depth='8'
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
scene.render.film_transparent=False;scene.render.image_settings.compression=20
if hasattr(scene,'eevee'):scene.eevee.taa_render_samples=64
info={'collection':'NEW HOI AN','units':'metres','layout':'exhibition','walls':0,'roof':False,
      'floorBounds':[-1,-1,13,11], 'rooms':zones,'placements':placements,
      'colliders':[[3.80,6.65,4.40,7.25],[9.8,6.75,10.4,7.35],[7.9,2.10,9.40,2.90]],
      'overview':{'position':[17,14,11],'target':[6,.35,-5.1],'fov':45},
      'source':'NEW HOI AN CATALOGUE 2026.pdf','sourcePages':3,'finish':'LCM127 Golden Syrup',
      'interpretations':['Open exhibition and complementary styling','Concealed joinery','Freestanding mirror supports']}
scene['web_scene_info']=json.dumps(info)
(BASE/'scene.json').write_text(json.dumps(info,indent=2),encoding='utf8')

def collection(name,parent=None):
    col=bpy.data.collections.new(name);(parent or scene.collection).children.link(col);return col
catalogue=collection('01 | HOI AN catalogue products');decoration=collection('02 | Interpreted exhibition and styling');lighting=collection('03 | Cameras and lighting')
zone_cols={key:collection(zone['name'],catalogue) for key,zone in zones.items() if key!='aisle'}
product_cols={}
def ancestor(obj):
    while obj:
        if obj.get('kind')=='product':return obj
        obj=obj.parent
for obj in list(scene.objects):
    root=ancestor(obj)
    if root:
        if root.name not in product_cols:product_cols[root.name]=collection(root['product_id']+' | '+root['instance_id'],zone_cols[root['room']])
        target=product_cols[root.name]
    else:target=lighting if obj.type in {'LIGHT','CAMERA'} else decoration
    target.objects.link(obj)
    for previous in list(obj.users_collection):
        if previous!=target:previous.objects.unlink(obj)
for index,name in enumerate(['overview','king','queen','storage']):
    marker=scene.timeline_markers.new(name.title(),frame=index*30+1);marker.camera=bpy.data.objects['Camera '+name]
scene.frame_set(1);scene.frame_start=1;scene.frame_end=120
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_perspective='CAMERA'
            area.spaces.active.region_3d.view_camera_zoom=0
            area.spaces.active.shading.type='MATERIAL'
bpy.ops.file.pack_all()
report={'products':6,'placements':len(placements),'movingParts':sum(obj.get('kind')=='articulation' for obj in scene.objects),
        'objects':len(scene.objects),'meshes':sum(obj.type=='MESH' for obj in scene.objects),
        'wovenPanels':sum(bool(obj.get('has_true_gaps')) for obj in scene.objects),
        'walls':0,'roof':False,'seconds':time.perf_counter()-started}
(BASE/'build-report.json').write_text(json.dumps(report,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'hoi-an-exhibition.blend'),compress=True)
print('HOI_AN_BUILD_COMPLETE',json.dumps(report),flush=True)
