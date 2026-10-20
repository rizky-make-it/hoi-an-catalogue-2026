"""Extract original catalogue photographs without modifying their furniture design."""
from pathlib import Path
import sys

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
sys.path.insert(0,str(ROOT/'.local/catalogue-review/packages'))
import pymupdf as fitz

source=Path(sys.argv[1]) if len(sys.argv)>1 else Path('C:/Users/Admin/Downloads/NEW HOI AN CATALOGUE 2026.pdf')
destination=ROOT/'sites/hoi-an-catalogue/dist/assets/catalogue'
destination.mkdir(parents=True,exist_ok=True)
crops={
 'LV453.B01':(96,20,970,524), 'LV453.B02':(96,20,970,524),
 'LV453.B41':(1064,190,1368,490), 'LV453.B51':(98,690,434,1182),
 'LV453.B61':(532,770,1058,1142), 'LV453.B71':(1167,763,1411,1128),
}
doc=fitz.open(source);page=doc[1]
for sku,coords in crops.items():
    clip=fitz.Rect(coords);clip*=fitz.Matrix(page.rect.width/1800,page.rect.height/1274)
    factor=min(780/clip.width,560/clip.height)
    photo=page.get_pixmap(matrix=fitz.Matrix(factor,factor),clip=clip,alpha=False)
    thumbnail=fitz.open();canvas=thumbnail.new_page(width=800,height=600)
    left=(800-photo.width)/2;top=(600-photo.height)/2
    canvas.insert_image(fitz.Rect(left,top,left+photo.width,top+photo.height),stream=photo.tobytes('png'))
    canvas.get_pixmap(alpha=False).save(destination/(sku+'.jpg'),jpg_quality=94)
    thumbnail.close();print('HOI_AN_CATALOGUE_PHOTO',sku,flush=True)
doc.close()
