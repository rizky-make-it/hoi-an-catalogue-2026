"""Render genuine NEW HOI AN Blender images. -- [all|camera] [--preview] [--cycles]."""
import bpy, sys, time, json
from pathlib import Path
BASE=Path(__file__).resolve().parent
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['all']
name=args[0] if args else 'all';preview='--preview' in args
scene=bpy.context.scene
assert scene.get('collection')=='NEW HOI AN 2026'
# Rendering must not let the saved frame-1 overview marker override each shot.
scene.timeline_markers.clear()
scene.render.engine='CYCLES' if '--cycles' in args else 'BLENDER_EEVEE'
samples=16 if preview else 64
scene.cycles.samples=samples;scene.eevee.taa_render_samples=samples
scene.render.resolution_x=3840;scene.render.resolution_y=2160
scene.render.resolution_percentage=25 if preview else 100
out=BASE/'renders';out.mkdir(exist_ok=True)
names=['overview','king','queen','storage'] if name=='all' else [name]
for key in names:
    started=time.perf_counter();scene.camera=bpy.data.objects['Camera '+key]
    scene.render.filepath=str(out/(key+('-preview.png' if preview else '-4k.png')))
    bpy.ops.render.render(write_still=True)
    report={'camera':key,'collection':'NEW HOI AN','engine':scene.render.engine,'samples':samples,
            'width':round(scene.render.resolution_x*scene.render.resolution_percentage/100),
            'height':round(scene.render.resolution_y*scene.render.resolution_percentage/100),
            'seconds':round(time.perf_counter()-started,3),'layout':'exhibition','walls':0,'roof':False}
    (out/(key+'-settings.json')).write_text(json.dumps(report,indent=2))
    print('HOI_AN_RENDER_COMPLETE',json.dumps(report),flush=True)
if name=='all' and not preview:
    scene.camera=bpy.data.objects['Camera detail'];scene.render.resolution_x=1600;scene.render.resolution_y=2100
    scene.render.filepath=str(out/'detail-weave.png');bpy.ops.render.render(write_still=True)
    print('HOI_AN_DETAIL_COMPLETE',scene.render.filepath,flush=True)
