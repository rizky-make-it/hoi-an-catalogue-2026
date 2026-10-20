# HOI AN furniture reconstruction notes

Source: all three pages of `NEW HOI AN CATALOGUE 2026.pdf`, including its staged
hero, the complete dimensional product sheet, and the construction close-ups.
The models are authored visual reconstructions, not supplied manufacturer CAD.

## Catalogue scope

| SKU | Product | Width × depth × height (m) | Moving drawers |
| --- | --- | --- | ---: |
| LV453.B01 | Queen Bed | 1.600 × 2.140 × 1.300 | 0 |
| LV453.B02 | King Bed | 1.900 × 2.140 × 1.300 | 0 |
| LV453.B41 | Bedside 2 Drawers | .550 × .420 × .580 | 2 |
| LV453.B51 | Tallboy 4 Drawers | .950 × .450 × 1.200 | 4 |
| LV453.B61 | Dresser 6 Drawers | 1.500 × .450 × .820 | 6 |
| LV453.B71 | Mirror | 1.000 × .025 × 1.000 | 0 |

Finish is `LCM127 Golden Syrup`, with natural basket-woven rattan. There is no
SIENNA chevron veneer or slender brass perimeter structure. The catalogue lists
MDF veneer, oak/pine/mountain ash timber, and rattan; it does not specify a unique
species or proprietary manufacturing details for every concealed component.

## Model details

- Continuous square timber posts and legs, softly bevelled frame rails, inset
  solid-wood side panels, real cabinet cavities, drawer bottoms/backs/sides,
  wooden runners, exposed side joinery keys, and solid horizontal timber pulls.
- Bed headboard: one narrow full-width upper rattan strip over three tall lower
  woven panels. Footboard: three low woven panels separated by timber stiles.
- Every rattan insert contains individual solid flattened warp and weft reeds
  combined into one mesh. Alternate crossings physically reverse depth; the
  insert has true gaps, not a printed weave image or transparency substitute.
  Mean reed pitch is approximately 6.2 mm, with 0.46 mm ribbon thickness and
  0.73 mm crossing amplitude. Pitch is a bounded visual reconstruction rather
  than a manufacturer measurement.
- Three subtle natural-reed material variations are assigned per strand.
  Drawer rattan is backed by a recessed plain inner timber panel, preserving
  genuine shallow gaps and recess shadows without exposing an empty drawer.
- White Queen styling: rounded mattress, piping, four independently shaped
  cushions, draped geometry folds, turned-back duvet edge, and thick sewn hems.
- Olive King styling: white rear pillows, tuft-indented olive front cushions,
  sculpted olive duvet, a padded folded quilt with real stitch channels, and a
  white turned-back sheet. Styling is not an extra catalogue product.

Wooden product bounds follow the catalogue. Soft bedding may overhang the
nominal width by approximately 25 mm; connector plug bevels and microscopic
trim tolerances can also extend slightly beyond nominal frame faces. Drawer
interiors, support slats, hardware positioning, tuft locations, and non-visible
joinery are reasonable design interpretations, not production drawings.

## Integration contract

`create(sku, instance=None, bedding='white')` returns a product root carrying
`kind`, `product_id`, `instance_id`, `title`, metric width/depth/height, finish,
material, source, and reconstruction notes. X is width, Y is depth, the front is
-Y, and Z is up. The mirror origin is its lower-edge centre; others are at floor
centre. Moving drawer roots carry `kind='articulation'`, `action='drawer'`,
`product_id`, `distance`, `label`, and `closed_y`; travel is local -Y.

Required core materials: `wood`, `inside`, `cane`, `cane_light`, `cane_dark`,
`cotton`, `olive`, `stitch`, and `mirror`. Core helpers are unchanged. Native
geometry is deliberately richer than a typical web asset; web export may use
controlled simplification while retaining the native full-detail Blender file.
