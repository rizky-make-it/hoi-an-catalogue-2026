"""Read the supplied HOI AN PDF and create unaltered page previews for modelling."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / '.local/catalogue-review/packages'))
import pymupdf as fitz

SOURCE = Path('C:/Users/Admin/Downloads/NEW HOI AN CATALOGUE 2026.pdf')
DEST = ROOT / '.local/hoi-an-review'
DEST.mkdir(parents=True, exist_ok=True)
doc = fitz.open(SOURCE)
pages = []
for index, page in enumerate(doc):
    scale = 1800 / page.rect.width
    image_path = DEST / f'page-{index+1:02}.jpg'
    page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False).save(image_path, jpg_quality=94)
    text = page.get_text()
    images = page.get_image_info(xrefs=True)
    pages.append({'page': index+1, 'size': list(page.rect), 'text': text,
                  'text_blocks': page.get_text('blocks'), 'images': images,
                  'preview': str(image_path)})
    print(f'\n--- PAGE {index+1} ---\n{text}', flush=True)
report = {'source': str(SOURCE), 'page_count': len(doc), 'pages': pages}
(DEST / 'catalogue-evidence.json').write_text(json.dumps(report, indent=2, default=lambda value: value.hex() if isinstance(value, bytes) else str(value)), encoding='utf8')
print('PAGE_COUNT', len(doc), 'EVIDENCE', DEST, flush=True)
