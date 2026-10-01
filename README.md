# Fractional Stars

501 pre-generated, transparent five-star PNGs for Google Sheets `IMAGE()`.
Every rating from **0.00 to 5.00**, inclusive, in **0.01** increments has a file.
No server, API key, Apps Script, JavaScript rendering service, or build step is
needed to serve the images.

## Publish

1. Create a GitHub repository (for example, `fractional-stars`). A public
   repository works with GitHub Free.
2. Add this folder's **contents** to the repository root, including the complete
   `stars/` folder and the hidden `.nojekyll` file. Do not upload only the ZIP,
   or nest the project under an extra folder.
3. In **Settings → Pages → Build and deployment**, choose **Deploy from a
   branch**, **main**, and **/(root)**, then save. Select your actual branch
   if it has a different name.
4. Wait for deployment and open the URL shown in Pages settings, typically
   `https://YOUR-USERNAME.github.io/YOUR-REPO/`.
5. Open `stars/4.37.png` on that site to confirm the PNG is public, then use
   the formula below. The index page automatically inserts its published
   base URL into the displayed formulas.

The `.nojekyll` file disables Jekyll processing. All assets use relative paths
so the preview works under a project path, a user site, or a custom domain.
See the [official publishing instructions](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).

## Google Sheets formulas

Replace `YOUR-USERNAME` and `YOUR-REPO` with your published Pages address.
For a custom domain, replace the entire base URL, keeping `/stars/`.

For a numeric rating in `A2`:

```text
=IF(ISNUMBER(A2),IMAGE("https://YOUR-USERNAME.github.io/YOUR-REPO/stars/"&SUBSTITUTE(TEXT(ROUND(MAX(0,MIN(5,A2)),2),"0.00"),",",".")&".png"),"")
```

For the average of numeric ratings in `Ratings!B2:B`:

```text
=IF(COUNT(Ratings!B2:B)=0,"",IMAGE("https://YOUR-USERNAME.github.io/YOUR-REPO/stars/"&SUBSTITUTE(TEXT(ROUND(MAX(0,MIN(5,AVERAGE(Ratings!B2:B))),2),"0.00"),",",".")&".png"))
```

These formulas round to two decimal places and clamp results to 0–5. The
single-cell formula leaves blanks and text blank; the average formula leaves
an empty numeric range blank. Errors in the source cells remain visible rather
than being silently hidden. `SUBSTITUTE` ensures filenames use a decimal point.
If your locale uses semicolon argument separators, change separators outside
quotation marks to semicolons, leaving quoted strings unchanged.

`IMAGE()` defaults to preserving aspect ratio inside the cell. Increase the
column width and row height if needed. For a fixed 290 × 58 display, use
`IMAGE(url,4,58,290)`, which preserves the PNG's 5:1
ratio. See [Google's IMAGE reference](https://support.google.com/docs/answer/3093333?hl=en).

## Asset contract

```text
stars/0.00.png
stars/0.01.png
…
stars/4.37.png
…
stars/5.00.png
```

- 580 × 116 pixels; 8-bit RGBA PNG; transparent background.
- Gold: `#F5B21A`; empty stars: `#CBD5E1`.
- Five stars, each exactly 100 pixels wide, with 16-pixel gaps and 8-pixel padding.
- Whole stars fill first. The next star fills left-to-right by the fractional
  percentage of its bounding width: 4.37 means four gold stars plus 37 pixels
  of the 100-pixel-wide fifth star. This is width coverage, not area coverage.
- Edges use 8× supersampling. Each 0.01 step places the fill boundary exactly
  one pixel farther across the next star. Integer hundredths avoid floating
  point filename and fill errors.
- All URLs require two decimal places. `4.png`, `4.3.png`, and values beyond
  the provided range do not exist. The project is a static file library; URL
  query parameters cannot generate additional ratings or colors.

## Structure

```text
fractional-stars/
├── .gitignore
├── .nojekyll
├── index.html
├── README.md
├── stars/                  # 501 ready-to-serve PNGs
└── scripts/
    ├── generate.py         # Deterministic generator; Python standard library only
    └── validate.py         # Checks all PNGs and fractional fill boundaries
```

## Regenerate or validate locally

With Python 3.9 or newer, from the project root:

```sh
python3 scripts/generate.py
python3 scripts/validate.py
```

These scripts use only the standard library. Regeneration is optional; all
PNGs are already included. Validation checks file completeness, unique image
content, PNG checksums and dimensions, transparency, every visible pixel's
expected fill color, and strictly increasing gold coverage.

To preview locally, open `index.html` in a browser. The preview works from
local files; replace the placeholder URL after hosting. Local validation
does not confirm deployment or a live Google Sheets fetch. After publishing,
test both a direct PNG URL and the formula in your own spreadsheet.
