# Tools and local workflow

## Dependencies

Configure Blender and enable Sollumz before running the helpers. This workflow was exercised on Windows with Blender 5.2.2 LTS, Sollumz 2.9.0, szio 1.3.0.dev9, .NET 10, and CodeWalker.Core 1.0.3. These are observed versions, not a guarantee for every combination. The source projects pin the CodeWalker package. Use the dependencies required by your Sollumz version.

Locate Blender on the current machine; never assume the original author's installation path. No remote execution server or exposed MCP port is required: scripts run through Blender's background Python interface. PyMateria was not used in the demonstrated workflow; CodeWalker XML provided the interchange format.

Keep .NET build artifacts in the work directory with `--artifacts-path`. First use may restore the NuGet dependency. The helpers refuse to overwrite existing final outputs; choose a new revision path.

## YFT conversion

```powershell
dotnet run --project '<skill>/scripts/codewalker-convert' --artifacts-path '<work>/tool-build' -- export-yft '<work>/original/vehicle.yft' '<work>/xml/vehicle.yft.xml'
dotnet run --project '<skill>/scripts/codewalker-convert' --artifacts-path '<work>/tool-build' -- import-yft '<work>/edited/vehicle.yft.xml' '<work>/final/vehicle.yft'
dotnet run --project '<skill>/scripts/codewalker-convert' --artifacts-path '<work>/tool-build' -- export-yft '<work>/final/vehicle.yft' '<work>/verified/vehicle.yft.xml'
```

Create output parent directories first. Repeat for `_hi` and affected optional assets. The converter reopens saved output; it does not itself prove that an edit preserved mechanical data. It does not extract embedded DDS textures: inspect embedded dictionaries and use a complete export when necessary.

## YTD export and selective patching

```powershell
dotnet run --project '<skill>/scripts/codewalker-textures' --artifacts-path '<work>/tool-build' -- export-ytd '<work>/original/vehicle.ytd' '<work>/textures.xml' '<work>/dds'
dotnet run --project '<skill>/scripts/codewalker-textures' --artifacts-path '<work>/tool-build' -- patch-ytd '<work>/original/vehicle.ytd' '<work>/final/vehicle.ytd' '<work>/edited-dds'
```

Put only changed DDS files in `edited-dds`. The patcher requires the original exported DDS header, payload size, and a matching existing texture name. It replaces pixel payloads in the original dictionary, then verifies every entry after reopening. This preserves entries that cannot be exported as DDS. It is deliberately not a texture-resizing or format-conversion tool. Inspect diffuse, alpha, normal, specular, emissive, and mip levels before selecting edits.

## Blender review

Keep `vehicle.yft.xml` and `vehicle_hi.yft.xml` together. Place final reexported DDS files in a sibling `vehicle/` folder. Accessory YFTs can reference the main YTD; ensure their image search paths resolve to that same verified texture directory.

```powershell
& '<blender>' --background --python-exit-code 1 --python '<skill>/scripts/blender_review.py' -- --input '<work>/verified/vehicle.yft.xml' --output-dir '<work>/review-01' --render --neutral-missing
```

Outputs are `modelo.blend` (original materials), `conferencia.blend` (preview scene), `frente.png`, `traseira.png`, and `report.json`. Existing products are preserved. The default front is +Y; use `--front-sign -1` for a vehicle facing -Y. Adjust cameras for side views, interiors, motorcycles, accessories, and closeups.

`--neutral-missing` substitutes missing textures in the preview scene only and lists them in the report. It cannot recover GTA's base-game materials. Review shader warnings; XML import and screenshots do not establish in-game compatibility. Preserve existing shattermap/glass data rather than assuming an exporter can regenerate it.
