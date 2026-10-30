using System.Runtime.InteropServices;
using System.Runtime.InteropServices.Marshalling;

namespace MyEverythingWidget.Infrastructure.Shell;

/// <summary>Shell item names (SIGDN).</summary>
internal enum ShellItemName : uint
{
    NormalDisplay = 0,
    ParentRelativeParsing = 0x80018001,
}

/// <summary>Options of <see cref="IShellItemImageFactory.GetImage"/> (SIIGBF).</summary>
[Flags]
internal enum ShellImageOptions
{
    ResizeToFit = 0x0,
    BiggerSizeOk = 0x1,
    IconOnly = 0x4,
}

[StructLayout(LayoutKind.Sequential)]
internal struct NativeSize
{
    public int Width;
    public int Height;
}

/// <summary>IShellItem: a file, folder or virtual item such as an entry of the Apps folder.</summary>
[GeneratedComInterface]
[Guid("43826d1e-e718-42ee-bc55-a1e261c37bfe")]
internal partial interface IShellItem
{
    [PreserveSig]
    int BindToHandler(nint bindContext, in Guid handler, in Guid interfaceId, out nint result);

    [PreserveSig]
    int GetParent(out nint parent);

    [PreserveSig]
    int GetDisplayName(ShellItemName nameType, out nint name);
}

/// <summary>IEnumShellItems: enumerates the children of a shell folder.</summary>
[GeneratedComInterface]
[Guid("70629033-e363-4a28-a567-0db78006e6d7")]
internal partial interface IEnumShellItems
{
    [PreserveSig]
    int Next(uint count, out nint item, out uint fetched);
}

/// <summary>IShellItemImageFactory: renders the icon or thumbnail of a shell item.</summary>
[GeneratedComInterface]
[Guid("bcc18b79-ba16-442f-80c4-8a59c30c463b")]
internal partial interface IShellItemImageFactory
{
    [PreserveSig]
    int GetImage(NativeSize size, ShellImageOptions options, out nint bitmap);
}

/// <summary>Native shell and GDI functions used to list apps and render icons.</summary>
internal static partial class ShellNative
{
    public static readonly Guid AppsFolderId = new("1e87508d-89c2-42f0-8a7e-645a0f50ca58");
    public static readonly Guid EnumItemsHandler = new("94f60519-2850-4924-aa5a-d15e84868039");
    public static readonly Guid ShellItemId = new("43826d1e-e718-42ee-bc55-a1e261c37bfe");
    public static readonly Guid EnumShellItemsId = new("70629033-e363-4a28-a567-0db78006e6d7");
    public static readonly Guid ImageFactoryId = new("bcc18b79-ba16-442f-80c4-8a59c30c463b");

    private static readonly StrategyBasedComWrappers ComWrappers = new();

    [LibraryImport("shell32.dll")]
    public static partial int SHGetKnownFolderItem(in Guid folderId, int flags, nint token, in Guid interfaceId, out nint item);

    [LibraryImport("shell32.dll", StringMarshalling = StringMarshalling.Utf16)]
    public static partial int SHCreateItemFromParsingName(string path, nint bindContext, in Guid interfaceId, out nint item);

    [LibraryImport("gdi32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    public static partial bool DeleteObject(nint handle);

    [LibraryImport("gdi32.dll")]
    public static partial int GetObjectW(nint handle, int size, out BitmapHeader bitmap);

    [LibraryImport("gdi32.dll")]
    public static partial int GetDIBits(nint deviceContext, nint bitmap, uint start, uint lines, byte[] bits, ref BitmapInfoHeader info, uint usage);

    [LibraryImport("user32.dll")]
    public static partial nint GetDC(nint window);

    [LibraryImport("user32.dll")]
    public static partial int ReleaseDC(nint window, nint deviceContext);

    /// <summary>Wraps a native COM pointer and releases the caller's reference.</summary>
    public static T Wrap<T>(nint pointer)
        where T : class
    {
        try
        {
            return (T)ComWrappers.GetOrCreateObjectForComInstance(pointer, CreateObjectFlags.None);
        }
        finally
        {
            Marshal.Release(pointer);
        }
    }

    /// <summary>Returns a shell item for a path, a URL-like shell path (<c>shell:AppsFolder\...</c>) or <see langword="null"/>.</summary>
    public static IShellItem? ItemFromParsingName(string path) =>
        SHCreateItemFromParsingName(path, 0, ShellItemId, out var pointer) >= 0 ? Wrap<IShellItem>(pointer) : null;

    /// <summary>Reads a shell item name and frees the native string.</summary>
    public static string? Name(IShellItem item, ShellItemName nameType)
    {
        if (item.GetDisplayName(nameType, out var pointer) < 0)
        {
            return null;
        }

        try
        {
            return Marshal.PtrToStringUni(pointer);
        }
        finally
        {
            Marshal.FreeCoTaskMem(pointer);
        }
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct BitmapHeader
    {
        public int Type;
        public int Width;
        public int Height;
        public int WidthBytes;
        public ushort Planes;
        public ushort BitsPixel;
        public nint Bits;
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct BitmapInfoHeader
    {
        public uint Size;
        public int Width;
        public int Height;
        public ushort Planes;
        public ushort BitCount;
        public uint Compression;
        public uint SizeImage;
        public int XPelsPerMeter;
        public int YPelsPerMeter;
        public uint ClrUsed;
        public uint ClrImportant;
    }
}
