# HOI AN — The Woven Collection / 2026

Created by Muhammad Rizky. Independent catalogue reconstruction and open 3D exhibition. Separate from the SIENNA project.

Live exhibition: https://rizky-make-it.github.io/hoi-an-catalogue-2026/

Source repository: https://github.com/rizky-make-it/hoi-an-catalogue-2026

See VERIFICATION.md and verification/ for native, local browser, and live GitHub Pages checks.

## Run the website

Node.js 24 or newer. No dependencies, API keys, or paid services required.

```
npm test
npm run dev
```

Open http://127.0.0.1:4175/. Do not open index.html with file://: GLB and module loading need an HTTP server. All production paths are relative and work below a GitHub Pages repository path. The deployable website is dist/.

## What is included

- Six catalogue SKUs: LV453.B01 Queen Bed (1600 x 2140 x 1300 mm), LV453.B02 King Bed (1900 x 2140 x 1300), LV453.B41 Bedside 2 Drawers (550 x 420 x 580), LV453.B51 Tallboy 4 Drawers (950 x 450 x 1200), LV453.B61 Dresser 6 Drawers (1500 x 450 x 820), LV453.B71 Mirror (1000 x 25 x 1000).
- Twelve furniture placements, twenty-eight articulated drawers; King, Queen, Storage, and Weave Study displays joined by an open aisle. No walls, partitions, or roof.
- dist/downloads/hoi-an-exhibition.blend: native Blender 5.2 master, packed textures, named collections and cameras, Cycles-ready. Open with Blender 5.2 or newer. Saved render settings use UHD 4K and Cycles denoising.
- dist/assets/hoi-an-exhibition.glb: Draco-compressed, batched exhibition LOD. dist/assets/models/: six full-detail individual GLBs. Moving drawer empties retained in both. Export-report.json records actual triangle and byte counts.
- dist/downloads/{overview,king,queen,storage}-4k.png: original 3840 x 2160 Blender EEVEE renders, not AI-generated illustrations. detail-weave.png: 1600 x 2100 close-up. render-proof.json contains dimensions and SHA-256 hashes. Website JPEGs are smaller viewing derivatives.
- dist/downloads/hoi-an-project.zip: native scene, texture sources, modelling/render/export scripts, original PDF, metadata, and modelling notes. Website source is the repository itself.
- Full English UI, catalogue search/filters, inspect studio, animated drawers, mobile analog joystick plus simultaneous swipe-look, pinch/zoom, native zone selector, expanded view, and phone bottom navigation.

## Contact workflow

All visible file-request buttons open the Muhammad Rizky profile popup with the supplied avatar and a WhatsApp draft to 6281393177004. No message sends automatically. Edit dist/contact-config.js to change contact details. The website and repository are public: a popup is not asset access control. The QA suite only inspects draft URLs; it never opens WhatsApp or sends a message.

## Rebuild the Blender project

The blender/ folder contains the source and photographed texture maps. Run from an HTTP-independent terminal with Blender 5.2 available:

```
blender --background --python blender/build_scene.py
blender --background blender/hoi-an-exhibition.blend --python blender/render_scene.py -- all
```

Use --cycles after all to render with Cycles instead of EEVEE. The delivered 4K gallery is EEVEE, 64 temporal samples. build_scene.py starts a fresh scene when run; it does not edit other projects. export_web.py and prepare_assets.py were authored for the original workspace structure (output/hoi-an-catalogue beside sites/hoi-an-catalogue); adjust their SITE/ROOT paths when using elsewhere. read_catalogue.py and extract_catalogue.py also require PyMuPDF and the original PDF path. Native .blend viewing/rendering needs no Python packages or external texture downloads.

## Publish manually on GitHub Pages

Create a new public repository, push this entire project to main, then Settings > Pages > Source: GitHub Actions. The supplied .github/workflows/pages.yml validates assets and publishes only dist/. No Vercel configuration or backend required. For a different repo name all assets remain relative. Keep each git file below 100 MiB; do not enable Git LFS for assets expected to be served by Pages.

## Source and fidelity

Original source: NEW HOI AN CATALOGUE 2026.pdf, Living Ikon, three scanned pages. All pages reviewed. Names and sizes transcribed from page 2; bed printed L x W x H is normalised to W x D x H. The catalogue uses one bed photograph for both printed sizes; distinct widths are modelled. Timber finish LCM127 Golden Syrup, natural rattan. See blender/inventory.json and furniture-audit.md.

These are visually authored models, not official manufacturer CAD or fabrication drawings. Hidden joinery, reed pitch, material calibration, drawer internals and complementary staging are interpretations. Bedding may slightly overhang catalogue furniture bounds. No living or dining products have been invented for this six-product bedroom catalogue.

Rattan contains solid interlaced warp/weft geometry and genuine gaps; exhibition LOD is simplified while individual products and native meshes retain full detail. Browser real-time lighting and environment reflections differ from Blender; mirrors are not planar ray-traced in the web viewer. High-detail models can be demanding on older phones; the 30 MB exhibition is lazy-loaded and 4K render browsing works without WebGL. No universal FPS claim is made.

Wood substrate: Ash Veneer by Jenelle van Heerden / Poly Haven (https://polyhaven.com/a/ash_veneer), CC0, stained to interpret Golden Syrup; not a certification of the actual timber species. Three.js 0.186.1 MIT, Draco Apache 2.0, DM Sans and Instrument Serif SIL OFL. Licence files included under assets/vendor. Original product designs/catalogue photography remain with their owners; confirm commercial redistribution rights with the catalogue owner. See dist/credits.html.

## Verification

npm test checks dimensions, counts, GLB structure, contact URL safety, mobile input logic, English copy, native files and render hashes. npm run qa uses installed Chrome headless via CDP for actual WebGL, raycast selection, drawers, six model loads, desktop and mobile. node scripts/qa.mjs --mobile-navigation-only exercises real multi-touch, 320/360/390/430 px widths and landscape. --url=https://... repeats checks against the live deployment. Local screenshots and evidence go to ignored .local/.
