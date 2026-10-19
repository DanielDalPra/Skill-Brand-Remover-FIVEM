"""Run inside Blender: --python blender_review.py -- --input car.yft.xml --output-dir new-review --render."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def main():
    parser = argparse.ArgumentParser(description='Import a GTA vehicle through Sollumz and make a separate visual review.')
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--render', action='store_true')
    parser.add_argument('--neutral-missing', action='store_true')
    parser.add_argument('--front-sign', type=int, choices=(-1, 1), default=1)
    parser.add_argument('--width', type=int, default=1280)
    parser.add_argument('--samples', type=int, default=32)
    opts = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    source = opts.input.resolve()
    if not source.is_file() or not source.name.lower().endswith('.yft.xml'):
        raise ValueError('Expected an existing CodeWalker .yft.xml, with matching _hi XML and texture directory nearby.')
    if opts.width < 256 or opts.samples < 1:
        raise ValueError('Width must be at least 256; samples must be positive.')
    out = opts.output_dir.resolve()
    products = ('modelo.blend', 'conferencia.blend', 'report.json', 'frente.png', 'traseira.png')
    if any((out / name).exists() for name in products):
        raise FileExistsError('Use a new review directory. Existing review products are preserved.')
    out.mkdir(parents=True, exist_ok=True)
    if not hasattr(bpy.types.Object, 'sollum_type'):
        import addon_utils
        addon_utils.enable('Sollumz', default_set=False)
    if not hasattr(bpy.types.Object, 'sollum_type'):
        raise RuntimeError('Sollumz is not fully enabled. Check the local-workflow reference and its dependencies.')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    result = bpy.ops.sollumz.import_assets(directory=str(source.parent), files=[{'name': source.name}])
    meshes = [o for o in bpy.data.objects if o.type == 'MESH' and not o.hide_render]
    if result != {'FINISHED'} or not meshes:
        raise RuntimeError('Sollumz did not import a visible mesh. Inspect the importer log.')
    roots = [o for o in bpy.data.objects if o.type == 'ARMATURE' and o.sollum_type == 'sollumz_fragment']
    for root in roots:
        bpy.context.view_layer.objects.active = root
        root.select_set(True)
        if bpy.ops.sollumz.generate_wheel_instances.poll():
            bpy.ops.sollumz.generate_wheel_instances()
    missing = []
    for image in bpy.data.images:
        if image.source == 'FILE':
            if image.size[0] and image.size[1] and image.has_data:
                image.pack()
            else:
                missing.append({'name': image.name, 'path': image.filepath})
    bpy.ops.wm.save_as_mainfile(filepath=str(out / 'modelo.blend'))
    # Only the conference scene receives neutral textures and viewport hiding.
    for item in missing if opts.neutral_missing else []:
        image = bpy.data.images[item['name']]
        name = image.name.lower()
        color = (1, 1, 1, 0) if 'glasswindows' in name else ((.5, .5, 1, 1) if name.endswith('_n') or 'normal' in name else (
            (.7, .7, .7, 1) if name.startswith('plate') else ((.1, .1, .1, 1) if 'spec' in name else (0, 0, 0, 1)))
        )
        image.source = 'GENERATED'
        image.generated_width = image.generated_height = 16
        image.generated_color = color
    for obj in bpy.context.scene.objects:
        if obj.hide_render:
            obj.hide_set(True)
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    points = []
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH' and not obj.hide_render and obj.visible_get():
            evaluated = obj.evaluated_get(depsgraph)
            points.extend(evaluated.matrix_world @ Vector(corner) for corner in evaluated.bound_box)
    if not points:
        raise RuntimeError('No visible geometry found for the review cameras.')
    low = Vector([min(p[i] for p in points) for i in range(3)])
    high = Vector([max(p[i] for p in points) for i in range(3)])
    center = (low + high) / 2
    size = high - low
    span = max(size)
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.eevee.taa_render_samples = opts.samples
    scene.render.resolution_x = opts.width
    scene.render.resolution_y = round(opts.width * .7)
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.world = bpy.data.worlds.new('Review World')
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.16, .18, .22, 1)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .7
    for name, offset, energy in [('Key', (1, 1, 1.5), 1800), ('Fill', (-1, .5, 1), 1200), ('Rear', (.5, -1, 1.5), 1800)]:
        light = bpy.data.lights.new('Review ' + name, 'AREA')
        light.energy = energy * (span / 6) ** 2
        light.size = span * .8
        obj = bpy.data.objects.new(light.name, light)
        scene.collection.objects.link(obj)
        obj.location = center + Vector(offset) * span * .8
        obj.rotation_euler = (center - obj.location).to_track_quat('-Z', 'Y').to_euler()
    camera = bpy.data.cameras.new('Review Camera')
    camera.type = 'ORTHO'
    camera.ortho_scale = max(size.x, size.z / .7) * 1.15
    obj = bpy.data.objects.new(camera.name, camera)
    scene.collection.objects.link(obj)
    scene.camera = obj
    for name, sign in [('frente', opts.front_sign), ('traseira', -opts.front_sign)]:
        obj.location = center + Vector((0, sign * max(span * 2, 5), 0))
        obj.rotation_euler = (center - obj.location).to_track_quat('-Z', 'Y').to_euler()
        scene.render.filepath = str(out / (name + '.png'))
        if opts.render:
            bpy.ops.render.render(write_still=True)
    obj.location = center + Vector((0, opts.front_sign * max(span * 2, 5), 0))
    obj.rotation_euler = (center - obj.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.ops.object.select_all(action='DESELECT')
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                space = area.spaces.active
                space.region_3d.view_perspective = 'CAMERA'
                space.shading.type = 'MATERIAL'
                space.shading.use_scene_lights = space.shading.use_scene_world = True
                space.overlay.show_overlays = False
    bpy.ops.wm.save_as_mainfile(filepath=str(out / 'conferencia.blend'))
    report = {'input': str(source), 'input_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'blender': bpy.app.version_string, 'visible_meshes': len(meshes), 'images': len(bpy.data.images),
              'missing_images': missing, 'neutral_preview_only': opts.neutral_missing, 'rendered': opts.render,
              'in_game_tested': False}
    (out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print('REVIEW_OK', out)


if __name__ == '__main__':
    main()
