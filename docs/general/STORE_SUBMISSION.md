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
"Change icon" fix, `1.1.0.0` for the languages and the new Settings window). The Store requires the last number to be `0`; increase the first three for every submission.
This is the only place to change the version: `Directory.Build.props` gives every assembly the same version, so the
About card shows it too, and `AppVersionTests` fails when the two drift apart.

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

## Automated submission

After the first submission, updates can be sent with the Microsoft Store Developer CLI (`msstore`) and the Store
submission API. One-time setup:

**Keep the personal account apart from the tenant.** When a personal Microsoft account (for example a Gmail address)
is added to a Microsoft Entra tenant, the tenant shows it as a guest such as
`name_gmail.com#EXT#@<tenant>.onmicrosoft.com`. The same e-mail then belongs to two identities, and the sign-in page
may keep choosing the tenant one, so the personal account seems out of reach. To avoid that:

- Let Partner Center create the tenant with its own administrator account (`admin@<new-name>.onmicrosoft.com`); never
  invite the personal e-mail into the tenant.
- Do every tenant step in an InPrivate window, signed in only with that administrator account; keep the normal browser
  on the personal account.
- Before choosing anything in step 1, read which account the page is about to use; when it names the personal e-mail as
  a work or school account, stop.
- After the key exists, the tenant is not needed again until the key expires.

These steps only keep browser sessions apart. Linking the Partner Center account to a tenant ("Sign in with Microsoft
Entra ID" on User management) is stored on Microsoft's side, so another browser or an InPrivate window does not undo it.
For an account opened with a personal Microsoft account, ask Partner Center support first whether linking a tenant
affects signing in with that personal account.

1. **Entra application:** In Partner Center open Settings (gear) → Account settings → User management → Microsoft Entra
   applications.
   - If the account is not linked to a Microsoft Entra tenant yet, Partner Center first asks to link one or create a
     new one.
   - Choose "Create Microsoft Entra application", give it a name (for example `MEW Store publishing`) and the
     **Manager** role, and save.
2. **Key:** Open the application → Keys → "Add new key".
   - Copy the client ID and the key straight away; Partner Center shows the key only once.
   - The page also shows the tenant ID.
3. **Seller ID:** Settings → Account settings → Legal info (or Developer settings) shows the **Seller ID**.
4. **CLI:** Install it once with `winget install "Microsoft Store Developer CLI"`. Then, in your own terminal (not in a
   chat or a file in the repo), run:
   ```
   msstore reconfigure --tenantId <tenant> --sellerId <seller> --clientId <client> --clientSecret <key>
   ```
   The CLI keeps the credentials in the Windows Credential Manager.

Each update after that: bump `version` in `StoreIdentity.json`, build both packages (section 3), then
`msstore publish <package> --appId 9NRSQN57C9FH` for the packages; the submission is created and sent to
certification. For GitHub Actions, the same four values become repository secrets.

The key expires (Partner Center shows the date); add a new key before then and run `msstore reconfigure` again.

## 5. After release

- Publish a GitHub release on the released commit (`v1.0.0`) that points to the Store page. Do not attach the Store
  `.msix` files: they are unsigned and Windows refuses to install them.
- Keep `docs/general/STORE_LISTING.md` in sync with the listing.
