# Profile artwork

- `developer-studio.png`: original 3D banner generated with Amit's Google Cloud image-generation function (`mode: image`, `model: pro`, `aspect_ratio: 21:9`). The character is a stylized male developer, not a photographic likeness. See `hero-prompt.txt` for the generation prompt.
- `build-loop.svg`: self-contained SVG workflow animation. No scripts, external fonts, or remote image services; respects reduced-motion preferences.
- `contributions-3d.svg`: real GitHub contribution calendar, projected into an isometric landscape. Column height scales with the square root of daily contribution count. Zero-contribution days remain low dark tiles. Colors use four activity levels relative to the busiest day.

The contribution workflow refreshes daily and can be run manually under **Actions → Refresh 3D contribution landscape → Run workflow**. It uses GitHub's provided Actions token; no cloud credentials or AI calls are needed for ongoing updates. GitHub's privacy rules determine which contributions are visible to that token. Failed API calls leave the last successfully generated landscape intact.

Profile facts and live project links come from https://sainiamit.com. Public repository links were verified with GitHub. The existing contribution snake workflow is preserved.
