# Verification — HOI AN 2026

Local verification completed on 20 October 2026. Publication verification will be recorded separately after GitHub Pages becomes available.

- npm test: 13 tests passed, plus static asset validation. Six catalogue dimensions checked against inventory.json; 12 placed products and 28 articulation nodes verified in the binary GLB.
- Native Blender 5.2 master reopened successfully: six unique SKUs, twelve product roots, twenty-eight drawers, forty-three true-gap woven panels, four packed image textures, five cameras, UHD settings, Cycles-ready, no walls or roof.
- Five genuine Blender EEVEE images produced from the master: four 3840 x 2160 renders and a 1600 x 2100 material study. All have distinct SHA-256 hashes in dist/downloads/render-proof.json.
- Desktop Chrome/CDP: all six product GLBs loaded; actual raycast selection, keyboard walking, drag-look, zoom, collision-safe routes, opening and closing all six dresser drawers, idle rendering, category filters, SKU search, galleries and project files passed. No runtime exceptions, console errors, or HTTP failures.
- Mobile Chrome/CDP: 320/360/390/430 px layouts and 844 x 390 landscape; real multi-touch joystick, simultaneous second-thumb look, release/cancel stop, pinch zoom, zoom buttons, all zone choices, latest request during loading, touch product selection, product panel below canvas, expanded mode and zone picker, dialog scroll lock, and bottom navigation passed.
- All contact requests used the creator-provided 6281393177004 number, supplied avatar, exact English invitation, correct per-file draft, focus restoration and nested modal scroll locking. Tests only inspected links; no WhatsApp link was opened or message sent.
- SIENNA repository remains clean at commit 617dcc8. Its files and deployment were not changed. The former 18:30 Windows job is disabled to avoid duplicate execution.

Browser evidence is stored locally in .local/qa-final.json and .local/qa-mobile-navigation-local.json, with screenshots. These checks use desktop Chrome with emulated mobile viewports and touch input, not physical-device testing; no universal mobile FPS or perfect catalogue/CAD equivalence is claimed.
