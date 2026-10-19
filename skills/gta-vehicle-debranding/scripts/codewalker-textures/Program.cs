using CodeWalker.GameFiles;
using CodeWalker.Utils;

if (args.Length != 4 || (args[0] != "export-ytd" && args[0] != "patch-ytd"))
{
    Console.Error.WriteLine("Usage: export-ytd|patch-ytd INPUT OUTPUT TEXTURE_DIRECTORY (new outputs only)");
    return 2;
}
try
{
    var input = Path.GetFullPath(args[1]);
    var output = Path.GetFullPath(args[2]);
    var folder = Path.GetFullPath(args[3]);
    if (File.Exists(output) || input.Equals(output, StringComparison.OrdinalIgnoreCase))
        throw new IOException("Choose a new output path; existing files are preserved.");
    if (!Directory.Exists(Path.GetDirectoryName(output)))
        throw new DirectoryNotFoundException("Create the output parent directory first.");
    var original = new YtdFile();
    original.Load(File.ReadAllBytes(input));
    if (args[0] == "export-ytd")
    {
        if (Directory.Exists(folder) && Directory.EnumerateFileSystemEntries(folder).Any())
            throw new IOException("Choose an empty DDS export directory.");
        Directory.CreateDirectory(folder);
        var xml = YtdXml.GetXml(original, folder);
        File.WriteAllText(output, xml);
        Console.WriteLine($"Exported {original.TextureDict.Dict.Count} dictionary entries; {Directory.GetFiles(folder, "*.dds").Length} DDS files. Unsupported entries may have no DDS export.");
        return 0;
    }
    var files = Directory.GetFiles(folder, "*.dds");
    if (files.Length == 0) throw new IOException("No edited DDS files were provided.");
    foreach (var file in files)
    {
        var name = Path.GetFileNameWithoutExtension(file);
        var texture = original.TextureDict.Dict.Values.SingleOrDefault(t => t.Name == name)
            ?? throw new InvalidDataException("Unknown texture: " + name);
        var baseline = DDSIO.GetDDSFile(texture);
        var edited = File.ReadAllBytes(file);
        if (baseline == null || baseline.Length < 128 || edited.Length < 128)
            throw new InvalidDataException("Cannot patch unsupported DDS data: " + name);
        if (!baseline.AsSpan(0, 128).SequenceEqual(edited.AsSpan(0, 128)))
            throw new InvalidDataException("DDS header changed; preserve original export dimensions, format and mip layout: " + name);
        if (edited.Length - 128 != texture.Data.FullData.Length)
            throw new InvalidDataException("DDS payload length mismatch: " + name);
        texture.Data.FullData = edited[128..];
    }
    var bytes = original.Save();
    var check = new YtdFile();
    check.Load(bytes);
    if (check.TextureDict.Dict.Count != original.TextureDict.Dict.Count)
        throw new InvalidDataException("Texture dictionary entry count changed.");
    foreach (var texture in original.TextureDict.Dict.Values)
    {
        var other = check.TextureDict.Dict[texture.NameHash];
        if (other.Name != texture.Name || other.Width != texture.Width || other.Height != texture.Height
            || other.Format != texture.Format || other.Levels != texture.Levels
            || !(other.Data?.FullData ?? Array.Empty<byte>()).SequenceEqual(texture.Data?.FullData ?? Array.Empty<byte>()))
            throw new InvalidDataException("Reopened texture mismatch: " + texture.Name);
    }
    using (var stream = new FileStream(output, FileMode.CreateNew, FileAccess.Write)) stream.Write(bytes);
    Console.WriteLine($"Patched {files.Length} textures; reopened and verified all {check.TextureDict.Dict.Count} dictionary entries.");
    return 0;
}
catch (Exception e)
{
    Console.Error.WriteLine("YTD operation failed: " + e.Message);
    return 1;
}
