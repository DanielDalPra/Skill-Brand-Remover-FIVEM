# Full branding audit

Use for requests covering every logo, sticker, and branded inscription. The vehicle examples describe decisions, not reusable coordinates or geometry indices.

## Visual coverage

Inventory textures and material connections. Make contact sheets and enlarged crops. Adjust contrast only in inspection images to reveal black-on-black marks; inspect alpha separately because a white-looking atlas can be fully transparent.

Look beyond the vehicle manufacturer: component suppliers, tire brands/product names, tuners, design studios, and stylized model names. The 360 Spider audit found Ferrari, Brembo, Pininfarina, Michelin/Pilot Sport, and 360 Modena; smaller symbols also appeared on an airbag label, barcode sticker, console, and engine cap. Read the pixels instead of guessing a brand from memory.

Check textures and meshes independently. Chrome lettering may exist entirely in geometry with a uniform material. Diffuse/alpha atlas variants can carry the same mark. Follow actual diffuse, normal, specular, and emissive sampler links, including mip levels.

Preserve the supporting surface, bolts, stitchwork, functional warnings, and controls. Clone from matching material and color; a red caliper patch is not a replacement for a black label region. Separate removal of a textured mark, removal of volumetric faces, and an authorized solid-color finish in the report.

## DDS and YTD preservation

Preserve dimensions, compression, alpha, mip count, and data outside the masks. A top-mip-only edit can make branding return at a distance. Compressed block edits affect 4 × 4 neighborhoods: inspect edges and preserve adjacent texture detail. Do not apply a generic annular tire mask to a different UV layout; retain tread and unbranded rubber detail.

DDS export may omit dictionary entries unsupported by the exporter. One tested YTD had 33 entries but exported 32 DDS files; `stitch` was omitted. Rebuilding from those DDS files alone would lose an entry. Load the original YTD and patch only changed texture payloads. Verify names/hashes, formats, dimensions, levels, and pixel bytes after reopening; compare untouched entries byte for byte when their representation is preserved.

Some exported legacy DDS files have shorter mip tails than a conventional block-size formula predicts. Check actual bounds; never silently pad or truncate payloads. Validate with the reader used by the workflow.

## Geometry and final evidence

Reopen the final YFT/YTD, reexport, and render those files. Blender images packed before a texture edit can still show the previous revision; reimport or reload them before regenerating evidence.

Compare vertex attributes, changed index buffers, skeleton, glass, and physics properties. XML conversion can quantize collision vertices: investigate and report measured differences instead of claiming binary identity or adopting a universal tolerance. One 360 Spider round trip measured about 0.067 mm maximum collision displacement.

If an accessory YFT contains only decal planes, degenerating all triangles can produce a face-less drawable that the Blender importer rejects even when the binary reader accepts it. For planar alpha decals, clear the artwork/alpha while keeping a valid resource and check for residual specular/normal detail. This does not replace removing a volumetric emblem.

## Motorcycle graphics and accessories

Distinguish preserving stripes from replacing the entire fairing with a solid color. Confirm the color if unspecified. The Africa Twin example used solid black at the user's request; this is not a default for later vehicles. Preserve tires, seats, lights, reflectors, and unrelated metal finishes. Inspect alternate liveries and optional parts so selecting them does not reintroduce branding or the previous graphics.

Integrated embossed lettering may share a connected surface with a luggage lid. Restore only the affected surface from adjacent geometry and correct local normals; retain the lid's edges, shape, and hardware. Produce a closeup of the repaired area.

Record inspected regions, actual removals, preview limits, and whether the vehicle was tested in-game. Package the revision shown in the review images. Verify upload name/size when authorized; never overwrite a different vehicle's delivery by reusing its Drive ID.
