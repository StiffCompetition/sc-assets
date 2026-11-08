# NFT BUNDLE - NOT IN USE (removed 8 Nov 2026)
Status: NOT IN USE. Removed from the shop on 8 Nov 2026 at Andy's request. Everything needed to switch it on again is saved. Do not put any of it back without Andy's yes.

## What the bundle was
One-of-one NFT T-shirt and NFT poster sold tied to an NFT the buyer owns, with a bundle discount by NFT grade (Training 10%, General 15%, Field 20%, Combat 24%, Command 27%). Built 24-27 Oct 2026. Playbook: SC - NFT Bundle Playbook (Google Drive). Todoist task "NFT bundle: shirt, poster and NFT bundle to go-live".

## Where the saved copies are
- Theme code (full): GitHub sc-assets `theme/nft-bundle/` (sections, snippets, templates, assets) and the Shopify theme "NOT IN USE - NFT bundle theme archive (8 Nov 2026)" (complete copy of the live theme with the bundle in it).
- Cleaned theme files that replaced them: `theme/nft-bundle-removed/` (4 edited files + empty stubs).
- Mint service code that was removed: `mint-service-shirt-hooks-removed.patch` in this folder (apply with `git apply -R` on shopify-sell-nfts commit 00f20fa to restore). Commit before removal: 516f380.
- Earlier rollback theme: "DRAFT - NFT bundle (25 Oct 2026, evening)".
- Mock-ups: Drive folders NFT T-shirt Mock-ups and NFT Poster Mock-ups.

## What was switched off (all kept, renamed NOT IN USE)
- 15 automatic discounts "NOT IN USE - NFT bundle: <grade> (T-shirt | poster | T-shirt and poster)": deactivated. Reactivate in Shopify admin Discounts.
- Products "NOT IN USE - NFT Shirt (bundle removed 8 Nov 2026)" (handle not-in-use-nft-shirt, 54 variants) and "NOT IN USE - NFT Poster ..." (handle not-in-use-nft-poster): draft, tags not-in-use, nft-bundle-removed. Original handles were nft-shirt and nft-poster, original tags are not recorded.
- n8n workflows "NOT IN USE - SC - Shirt Order" (ZyXcX8MLra6Yj1OO), "NOT IN USE - SC - Shirt Preview" (NB8EoxUyfDLecTH3), "NOT IN USE - SC - Shirt Offer" (BZph6N9Vwbfx6WfN): unpublished, nodes untouched.
- Theme: 11 snippets/sections, 3 templates and 18 garment photos replaced by empty NOT IN USE stubs (files cannot be deleted from here); cart link line, print panel block, pair-it block, T-shirt studio section and certificate shirt/poster lines taken out of 4 files.
- Mint service: shirt hand-offs after a mint and after a paid shirt-only order removed.
- SC - Certificate Email: NFT T-shirt and NFT poster manifest rows removed from Build Certificates.

## To switch it back on (in order)
1. Restore mint code (patch above) and set SHIRT_HOOK_URL and SHIRT_HOOK_SECRET on Railway.
2. Publish the three n8n workflows; re-add the certificate email manifest rows.
3. Copy the files in `theme/nft-bundle/` back into a draft duplicate of the live theme (stage in sc-assets, File Lock, themeFilesUpsert by commit link), re-add the render lines listed in the playbook; Andy publishes.
4. Rename and activate the products, reactivate the 15 discounts, check the prices and the free-shipping rules.
