namespace MyEverythingWidget.Infrastructure.Shell;

/// <summary>Gets the icon of a web site.</summary>
public interface ISiteIconSource
{
    /// <summary>Returns the site's icon as a square PNG of <paramref name="size"/> pixels, or <see langword="null"/>.</summary>
    Task<byte[]?> GetPngAsync(Uri page, int size, CancellationToken cancellationToken);
}

/// <summary>
/// Downloads <c>/favicon.ico</c> from the site the card points to. Nothing is sent to any other server; when the
/// site has no icon or cannot be reached within <see cref="Timeout"/>, the card shows a monogram.
/// </summary>
public sealed class FaviconSource(HttpClient httpClient) : ISiteIconSource
{
    /// <summary>Longest wait for the icon.</summary>
    public static readonly TimeSpan Timeout = TimeSpan.FromSeconds(5);

    private const long MaxIconBytes = 512 * 1024;

    /// <inheritdoc />
    public async Task<byte[]?> GetPngAsync(Uri page, int size, CancellationToken cancellationToken)
    {
        ArgumentNullException.ThrowIfNull(page);

        using var timeout = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
        timeout.CancelAfter(Timeout);
        try
        {
            var iconUri = new Uri(new Uri(page.GetLeftPart(UriPartial.Authority)), "/favicon.ico");
            using var response = await httpClient.GetAsync(iconUri, HttpCompletionOption.ResponseHeadersRead, timeout.Token).ConfigureAwait(false);
            if (!response.IsSuccessStatusCode || response.Content.Headers.ContentLength > MaxIconBytes)
            {
                return null;
            }

            var bytes = await response.Content.ReadAsByteArrayAsync(timeout.Token).ConfigureAwait(false);
            return bytes.Length is 0 or > (int)MaxIconBytes ? null : await PngEncoding.ToPngAsync(bytes, size).ConfigureAwait(false);
        }
        catch (Exception exception) when (exception is HttpRequestException or OperationCanceledException)
        {
            return null;
        }
    }
}
