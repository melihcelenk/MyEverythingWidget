namespace MyEverythingWidget.UiTests.Infrastructure;

/// <summary>
/// Polls a condition instead of sleeping for a fixed time.
/// </summary>
internal static class Wait
{
    private static readonly TimeSpan DefaultTimeout = TimeSpan.FromSeconds(10);
    private static readonly TimeSpan Interval = TimeSpan.FromMilliseconds(100);

    /// <summary>Returns <see langword="true"/> as soon as <paramref name="condition"/> holds, or <see langword="false"/> on timeout.</summary>
    public static bool Until(Func<bool> condition, TimeSpan? timeout = null)
    {
        var deadline = DateTime.UtcNow + (timeout ?? DefaultTimeout);
        while (DateTime.UtcNow < deadline)
        {
            if (condition())
            {
                return true;
            }

            Thread.Sleep(Interval);
        }

        return condition();
    }

    /// <summary>Returns the element as soon as <paramref name="find"/> finds it; throws on timeout.</summary>
    public static T ForElement<T>(Func<T?> find, TimeSpan? timeout = null)
        where T : class
    {
        T? found = null;
        return Until(() => (found = find()) is not null, timeout)
            ? found!
            : throw new TimeoutException("The element did not appear.");
    }
}
