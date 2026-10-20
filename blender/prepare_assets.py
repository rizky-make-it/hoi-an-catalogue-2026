"""Package actual Blender outputs, web derivatives, source and render evidence."""
from pathlib import Path
import sys, json, shutil, hashlib, struct, zipfile
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
sys.path.insert(0,str(ROOT/'.local/catalogue-review/packages'))
import pymupdf as fitz
SITE=ROOT/'sites/hoi-an-catalogue';DIST=SITE/'dist';DOWNLOADS=DIST/'downloads'
DOWNLOADS.mkdir(parents=True,exist_ok=True)
proof={}
for name in ('overview','king','queen','storage','detail-weave'):
    filename=name+('.png' if name=='detail-weave' else '-4k.png')
    source=BASE/'renders'/filename
    raw=source.read_bytes();width,height=struct.unpack('>II',raw[16:24])
    if name!='detail-weave':assert (width,height)==(3840,2160)
    shutil.copy2(source,DOWNLOADS/filename)
    pix=fitz.Pixmap(str(source))
    if width>1920:pix=fitz.Pixmap(pix,1920,round(height*1920/width))
    pix.save(str(DIST/'assets'/(name+'.jpg')),jpg_quality=91)
    proof[name]={'file':filename,'width':width,'height':height,'sha256':hashlib.sha256(raw).hexdigest(),'engine':'BLENDER_EEVEE','nativeScene':'hoi-an-exhibition.blend','originalBlenderRender':True}
assert len({p['sha256'] for p in proof.values()})==5
(DOWNLOADS/'render-proof.json').write_text(json.dumps(proof,indent=2))
shutil.copy2(BASE/'hoi-an-exhibition.blend',DOWNLOADS/'hoi-an-exhibition.blend')
shutil.copy2(Path('C:/Users/Admin/Downloads/NEW HOI AN CATALOGUE 2026.pdf'),DOWNLOADS/'NEW-HOI-AN-CATALOGUE-2026.pdf')
shutil.copy2(SITE/'README.md',DOWNLOADS/'README.txt')
sources=['core.py','furniture.py','build_scene.py','export_web.py','render_scene.py','prepare_assets.py','extract_catalogue.py','read_catalogue.py','inventory.json','scene.json','build-report.json','export-report.json','furniture-audit.md']
for name in sources:
    target=SITE/'blender'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(BASE/name,target)
shutil.copytree(BASE/'textures',SITE/'blender/textures',dirs_exist_ok=True)
with zipfile.ZipFile(DOWNLOADS/'hoi-an-project.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
    for name in sources:archive.write(BASE/name,'hoi-an/'+name)
    for path in (BASE/'textures').iterdir():archive.write(path,'hoi-an/textures/'+path.name)
    archive.write(BASE/'hoi-an-exhibition.blend','hoi-an/hoi-an-exhibition.blend')
    archive.write(DOWNLOADS/'README.txt','hoi-an/README.txt')
    archive.write(DOWNLOADS/'NEW-HOI-AN-CATALOGUE-2026.pdf','hoi-an/NEW-HOI-AN-CATALOGUE-2026.pdf')
    archive.write(DOWNLOADS/'render-proof.json','hoi-an/render-proof.json')
print(json.dumps({'packaged':True,'renders':proof,'nativeBytes':(DOWNLOADS/'hoi-an-exhibition.blend').stat().st_size,'sourceZipBytes':(DOWNLOADS/'hoi-an-project.zip').stat().st_size},indent=2))
