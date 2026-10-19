using System.Text;
using System.Xml.Linq;
using CodeWalker.GameFiles;

if (args.Length != 3 || (args[0] != "export-yft" && args[0] != "import-yft"))
{
    Console.Error.WriteLine("Usage: export-yft|import-yft INPUT OUTPUT (new output only)");
    return 2;
}
try
{
    var input = Path.GetFullPath(args[1]);
    var output = Path.GetFullPath(args[2]);
    if (StringComparer.OrdinalIgnoreCase.Equals(input, output) || File.Exists(output))
        throw new IOException("Choose a new output path; existing files are preserved.");
    if (!Directory.Exists(Path.GetDirectoryName(output)))
        throw new DirectoryNotFoundException("Create the output parent directory first.");
    byte[] result;
    string verification;
    if (args[0] == "export-yft")
    {
        var yft = new YftFile();
        yft.Load(File.ReadAllBytes(input));
        verification = YftXml.GetXml(yft);
        var xml = XDocument.Parse(verification);
        if (xml.Root?.Name.LocalName != "Fragment") throw new InvalidDataException("Not a YFT fragment.");
        result = new UTF8Encoding(false).GetBytes(verification);
    }
    else
    {
        var yft = XmlYft.GetYft(File.ReadAllText(input));
        result = yft.Save();
        var reopened = new YftFile();
        reopened.Load(result);
        verification = YftXml.GetXml(reopened);
        if (XDocument.Parse(verification).Root?.Name.LocalName != "Fragment")
            throw new InvalidDataException("Reopened output is not a YFT fragment.");
    }
    using (var stream = new FileStream(output, FileMode.CreateNew, FileAccess.Write)) stream.Write(result);
    var doc = XDocument.Parse(verification);
    var count = doc.Descendants("Geometries").Sum(g => g.Elements("Item").Count());
    Console.WriteLine($"OK {args[0]}: {result.Length} bytes, {count} geometries -> {output}");
    return 0;
}
catch (Exception e)
{
    Console.Error.WriteLine($"Conversion failed: {e.Message}");
    return 1;
}
