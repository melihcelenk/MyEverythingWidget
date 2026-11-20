# Microsoft Store Submission

Steps to publish My Everything Widget. Building and testing are automated; the Partner Center steps need the
publisher's account and are done by hand.

## 1. One-time: reserve the name and set the identity

1. In [Partner Center](https://partner.microsoft.com/dashboard) → Apps and games → **New product** → MSIX or PWA app,
   reserve the name **My Everything Widget**.
2. Open **Product identity** and copy its values into `src/MyEverythingWidget.App/StoreIdentity.json` (already
   done for this app: `MelihCelenk.MyEverythingWidget`, Store ID `9NRSQN57C9FH`).

The manifest in the repository keeps the unsigned test publisher (`OID.2.25.311729368913984317654407730594956997722=1`)
so that local and sandbox builds install without a certificate. `scripts/publish-msix.ps1 -Store` writes the Store
identity into the manifest for that build only and restores it afterwards.

## 2. Version

The Store version is `version` in `StoreIdentity.json` (`1.0.0.0` for the first release, `1.0.1.0` for the
"Change icon" fix). The Store requires the last number to be `0`; increase the first three for every submission.

## 3. Build

```
pwsh scripts/test-ui.ps1                                            # all UI tests must pass
pwsh scripts/publish-msix.ps1 -Platform x64 -Store -OutputDirectory tmp\store-x64
pwsh scripts/publish-msix.ps1 -Platform ARM64 -Store -OutputDirectory tmp\store-arm64
```

The packages are unsigned; the Store signs them during certification.

### Try the Store package on this PC first

Windows does not install an unsigned package that runs a full-trust `.exe`, and the Store signs the package only
during certification. To try the exact Store package locally, sign a copy with a local test certificate whose subject
is the Store publisher:

```
pwsh scripts/sign-local-test.ps1      # signs tmp\local-signed\<package>.msix, exports local-test.cer
```

Then, in a PowerShell window opened as administrator, run the two commands the script prints (trust the certificate in
`Cert:\LocalMachine\TrustedPeople`, then `Add-AppxPackage`). Upload the unsigned package from `tmp\store-*`, not the
signed copy. Remove the local install with `Get-AppxPackage MelihCelenk.MyEverythingWidget | Remove-AppxPackage`.

## 4. Submission

| Partner Center section | What to enter |
|------------------------|---------------|
| Packages | Upload both `.msix` files (x64 and ARM64) |
| Store listing | Texts and screenshots from `docs/general/STORE_LISTING.md` |
| Privacy policy URL | `https://github.com/melihcelenk/MyEverythingWidget/blob/master/docs/general/PRIVACY_POLICY.md` |
| Properties → Category | Productivity |
| Additional Testing Information (Supplemental info) | Explain `runFullTrust` (below); Submission options only holds the publishing date |

`runFullTrust` justification text:

> My Everything Widget is a desktop launcher. It needs full trust to list the apps installed for the current user
> (from the Start menu's Apps folder), to read their icons, and to start the programs, folders and links that the user
> pins to the widget. It does not run in the background and collects no personal data; the only network request is
> the icon download from a website the user adds.

## 5. After release

- Publish a GitHub release on the released commit (`v1.0.0`) that points to the Store page. Do not attach the Store
  `.msix` files: they are unsigned and Windows refuses to install them.
- Keep `docs/general/STORE_LISTING.md` in sync with the listing.
