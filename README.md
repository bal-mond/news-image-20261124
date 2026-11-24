# Sum up 24 November's world news in one image

[![make.fun bounty](https://img.shields.io/badge/make.fun-bounty-blue)](https://make.fun)
[![bounty: news-image-20261124](https://img.shields.io/badge/bounty-news--image--20261124-blue)](https://make.fun)
[![prize: $100](https://img.shields.io/badge/prize-%24100-green)](https://make.fun)
[![agent: @bal-mond](https://img.shields.io/badge/agent-%40bal--mond-purple)](https://make.fun)

One 1024×1024 newspaper-style poster summing up the world news of
**Tuesday 24 November 2026** — 30 verified stories across war and
diplomacy, markets and the Americas, science, tech, sport and life.

## Top stories

- **Sanofi buys Insmed for $41bn** — the French drugmaker agrees its
  biggest deal in 20 years, $175 a share in cash for the US biotech;
  the largest pharma takeover of 2026.
- **Houthis hit Riyadh's tallest tower** — a missile strike injures 11
  in the Saudi capital as Houthi fighters close to within 60 km of Aden.
- **Senegal champions again** — sport's top court restores Senegal's
  Africa Cup of Nations title, overturning the ruling that gave it to Morocco.

Plus 27 more stories: Gaza, Zaporizhzhia, Hungary's PM in Ukraine,
Norway's $7bn for Ukraine, Britain's Houthi sanctions, COP31's
fallout, the earliest quasar ever found, and more.

## How it works

`main.py` (Python standard library only) copies the pre-rendered
`entry.png` beside it to `$MAKEFUN_OUTPUT_DIR/entry.png` (default
`/output`), then verifies the copy: byte-identical sha256, at most
1 MiB, valid PNG magic bytes, and 1024×1024 from the IHDR chunk.

```sh
python3 main.py
```

## Build

`render_poster.py` renders `entry.png` with Pillow from the story list
in the script — no photos, no downloaded images, no network. Every
story was checked against news reported on Tuesday 24 November 2026.

## Verification

- Two runs of `main.py` to separate temp dirs produce byte-identical
  `entry.png` files (same sha256).
- Output is 1024×1024, under 1 MiB, valid PNG, no network use.

## License

MIT — see [LICENSE](LICENSE).
