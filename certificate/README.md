# Certificate of Deployment images

Images used by the Certificate of Deployment email (n8n "SC - Certificate Email") and the certificate page on stiffcompetition.shop. Copies are also held in Shopify Files under the same names, which is where the email and page load them from.

- `sc-cert-stamp-deployed.png` - round red DEPLOYED stamp (character orders), transparent background.
- `sc-cert-stamp-issued.png` - round red ISSUED stamp (brand-only orders), transparent background.
- `sc-cert-wordmark-trim.png` - Stiff Competition wordmark, trimmed, transparent background.
- `sc-cert-monogram-trim.png` - SC badge, trimmed, used in the header of brand-only certificates.

Added 24 Oct 2026.

## Backup copies of the live code (24 Oct 2026)

- `n8n/build-certificates.js` - the Build Certificates node of n8n "SC - Certificate Email" as live on 24 Oct 2026 (final: name never splits, tests off, customers live).
- `shop-theme/` - the certificate page files in the live Shopify theme (folder name before `__`, file name after): the section, its three snippets and the page template. The page is www.stiffcompetition.shop/pages/certificate.

The live copies are in n8n and in the Shopify theme; these are for restore and reference. Full description: SC - NFT Flow Master Reference (As-Built), section 3.10.
