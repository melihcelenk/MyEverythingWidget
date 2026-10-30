# Microsoft Store Submission

Steps to publish My Everything Widget. Building and testing are automated; the Partner Center steps need the
publisher's account and are done by hand.

## 1. One-time: reserve the name and set the identity

1. In [Partner Center](https://partner.microsoft.com/dashboard) → Apps and games → **New product** → MSIX or PWA app,
   reserve the name **My Everything Widget**.
2. Open **Product identity** and copy these three values into `src/MyEverythingWidget.App/Package.appxmanifest`:

| Partner Center | Manifest |
|----------------|----------|
| Package/Identity/Name | `<Identity Name="...">` |
| Package/Identity/Publisher | `<Identity Publisher="CN=...">` |
| Package/Properties/PublisherDisplayName | `<PublisherDisplayName>` |

The manifest currently uses the unsigned-package publisher (`OID.2.25.311729368913984317654407730594956997722=1`)
so that test builds install without a certificate. Replace it only in the Store build; the sandbox UI tests install
the package unsigned and need the test identity.

## 2. Version

Set `<Identity Version="1.0.0.0">` for the first release. The Store requires the last number to be `0`; increase
the first three for every submission.

## 3. Build

```
pwsh scripts/test-ui.ps1                                            # all UI tests must pass
pwsh scripts/publish-msix.ps1 -Platform x64
pwsh scripts/publish-msix.ps1 -Platform ARM64 -OutputDirectory tmp\msix-arm64
```

The packages are unsigned; the Store signs them during certification.

## 4. Submission

| Partner Center section | What to enter |
|------------------------|---------------|
| Packages | Upload both `.msix` files (x64 and ARM64) |
| Store listing | Texts and screenshots from `docs/general/STORE_LISTING.md` |
| Privacy policy URL | The published `docs/general/PRIVACY_POLICY.md` (for example through GitHub Pages, as for TaskTimerWidget) |
| Properties → Category | Productivity |
| Submission options → Restricted capabilities | Explain `runFullTrust` (below) |

`runFullTrust` justification text:

> My Everything Widget is a desktop launcher. It needs full trust to list the apps installed for the current user
> (from the Start menu's Apps folder), to read their icons, and to start the programs, folders and links that the user
> pins to the widget. It does not run in the background and sends no data anywhere.

## 5. After release

- Tag the commit (`v1.0.0`) and attach the two `.msix` files to a GitHub release.
- Keep `docs/general/STORE_LISTING.md` in sync with the listing.
