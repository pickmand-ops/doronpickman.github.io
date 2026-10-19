---
name: home-design-visualizer
description: הדמיית עיצוב פנים מתמונה ומידות אמיתיות של הבית — Home interior design visualization from the user's own room photo plus real wall measurements. Checks that requested furniture fits, draws a true-to-scale placement guide on the photo, proposes 2–3 style directions, writes image-editing prompts (or generates the image when a tool is available) that keep the room identical and add only the requested pieces, and gives an interior-designer critique. Use this whenever the user uploads or mentions a photo of a room in their home and wants to see how furniture, colors, rugs, lighting, art or decor would look, asks "will this sofa fit", "how would my living room look with...", wants a before/after, a room makeover, a redesign, or design advice tied to their actual space — in Hebrew or English (עיצוב הבית, הדמיה, סלון, ספה, ריהוט, חדר שינה, צבע קיר, מעצב פנים), even if they don't say "visualize".
---

# Home Design Visualizer — הדמיית עיצוב לבית

The goal: the user photographs a real corner of their home, gives real measurements, describes what they want, and gets back an image of **their own room** with the new pieces at the **right size**, plus honest advice from a designer's eye.

Talk to the user in Hebrew (unless they write in another language). Write image-model prompts in English — current image models follow English instructions noticeably more reliably — and give a one-line Hebrew summary of what each prompt asks for.

## Why the workflow looks like this

Image-editing models (GPT Image / ChatGPT, Gemini "Nano Banana", Flux Kontext) are good at keeping a room's look while adding objects, but they have no sense of centimetres. Told "a 230 cm sofa", they guess. What they *do* follow well is a visual reference: a box drawn on the photo showing where the object goes and how big it is. So the core trick of this skill is to do the geometry ourselves (deterministically, with `scripts/scale_overlay.py`) and hand the model a marked guide image alongside the original. Fit problems are caught at the measurement stage, before anyone falls in love with a picture of a sofa that can't fit.

Be upfront that the result is a close visual approximation, not a CAD drawing: expect a few percent error from photo perspective and model drift. The numbers in the fit check are the reliable part; the image is for feel.

## Step 1 — Collect inputs (ask only for what's missing)

Needed:
- **Photo** of the area, taken as straight-on to the main wall as possible, the whole wall visible including where it meets the floor and ceiling. Wide-angle phone lens is fine.
- **Wall width** (cm) of the wall the items go against, and **ceiling height** (if unknown, assume 260 cm and say so — typical for Israeli apartments).
- **What to add/change**: each item with width × height (× depth if known), material, color, and where along the wall. If the user gives no size, propose a standard one from `references/design-rules.md` and say it's an assumption.

Helpful, ask once in a single short message if relevant: positions of windows/doors/radiators/outlets on that wall, the room's depth (for walkway checks), what stays and what goes, budget, who uses the room (kids, pets).

Don't interrogate. If the essentials are there, proceed and list assumptions.

## Step 2 — Read the photo

Open the image (Read tool) and get its pixel size (`python3 -c "from PIL import Image; print(Image.open('p.jpg').size)"`). Note: existing furniture, flooring, wall color, light sources and their direction, time of day, camera height and angle. These go into the prompt so the edit matches.

Locate the **four corners of the target wall** in pixels: top-left, top-right (wall meets ceiling) and bottom-right, bottom-left (wall meets floor). If a corner is hidden by furniture, extrapolate along the visible edges. If the wall continues out of frame, use the frame edge and reduce the wall width to the visible portion only — ask the user how many cm are visible if you can't infer it from a known object (a standard door is ~80–90 cm wide and ~210 cm tall; an outlet is ~30 cm above the floor).

## Step 3 — Fit check (numbers first)

Before any picture, check with `references/design-rules.md`:
- Does each item fit the wall, with clearance to corners, windows, doors?
- Proportion: sofa ≈ ½–⅔ of wall width; art ≈ ⅔ of the furniture below it; etc.
- Walkways and depth if room depth is known.

Report in a short table: item, size, % of wall, status ✅ / ⚠️ / ❌, note. If something doesn't fit, say so plainly and offer the nearest size that does. This is the most valuable part for a real purchase decision.

## Step 4 — Placement guide

Run the overlay script (in this skill's `scripts/` dir):

```bash
python3 <skill-dir>/scripts/scale_overlay.py --image <photo> \
  --corners "x,y x,y x,y x,y"   # TL TR BR BL of the wall
  --wall-width 420 --wall-height 260 \
  --item "A:sofa:80:230:85" \
  --item "B:art:120:150:70:130"   # LABEL:NAME:OFFSET:WIDTH:HEIGHT[:ELEVATION] in cm
  --out <outdir>/guide.png
```

OFFSET = cm from the wall's left edge to the item's left edge. ELEVATION lifts wall-mounted things (art, shelves, TV) off the floor. Height for floor items is their real height (sofa back ~80–90 cm).

The script prints warnings (overflow, overlap, taller than ceiling) — relay them. Look at the output image yourself: if the yellow wall outline doesn't sit on the real wall edges, fix the corners and rerun. Show the guide to the user and ask them to confirm placement before writing final prompts; it's much cheaper to move a box than to regenerate images.

**Depth matters for anything deeper than ~10 cm** (cabinets, wardrobes, shelving units, sofas): drawn flat, image models tend to render them almost flush with the wall. Give the script the depth direction and one known distance, and add DEPTH as the 7th item field:

```bash
  --depth-lines "x,y x,y x,y x,y"   # two segments running straight out of the wall: a side wall's ceiling and floor lines, or tile grout lines
  --depth-ref "x,y x,y 78"          # inner floor corner, and the side wall's front floor corner 78 cm out (ask the user for that length)
  --item "A:cabinet:0:30:263:0:40"  # ...:ELEVATION:DEPTH
```

The script then draws each item as a translucent 3-D box (floor footprint, sides, front face) and prints the depth vanishing point. In the prompt, state the depth in cm and in relation to something visible ("projects 40 cm, about half the depth of the side wall with the light switch").

Items standing away from the wall (coffee table, armchair in the middle) don't live on the wall plane, so the script can't place them precisely. Describe them in the prompt by relation ("coffee table centred in front of the sofa, 45 cm gap, about half the sofa's length") instead.

## Step 5 — Style directions

Propose **2–3 distinct directions** that respect what the user explicitly asked for (if they said grey sofa with oak, every direction keeps that) and vary everything else: wall color, rug, pillows, lighting, decor accents. For each: a name, 1–2 sentences on the mood, a palette of 3–5 colors (name + hex), key materials. Keep them genuinely different (e.g. warm Japandi / Mediterranean-light / modern contrast), and say which one you'd pick for this room and why.

## Step 6 — The image

**Default: prompts the user copies.** For each direction give one ready-to-paste block following `references/prompt-templates.md`. Tell the user to upload **two images** to the tool: the original photo first, then the guide image. Then paste the prompt. Recommend which tool to use (see the template file) and keep the instructions short. Name the exact site (chatgpt.com or gemini.google.com) — coding agents like Codex can't generate images — and read the "Pitfalls seen in real use" section of the template file before writing the prompt: inspiration screenshots in particular tend to become the canvas the model edits.

**If an image-generation/editing tool or API key is available in the session** (check for a connected image tool, or env vars like `OPENAI_API_KEY`, `GEMINI_API_KEY`, `REPLICATE_API_TOKEN`), generate the image directly using the same prompt with the original + guide as inputs, and save the result next to the photo. Ask before spending money on a paid API the first time.

## Step 7 — Designer review

When there's a result image (generated here, or the user uploads what they got back):
1. **Scale check**: compare the new object against the guide box (rerun the overlay on the result with the same corners if the camera didn't change). If the sofa came out noticeably bigger/smaller, say so and give a corrective follow-up prompt ("make the sofa narrower so it ends at the left edge of the window frame").
2. **Design critique**, like a good interior designer would: proportion and scale, balance and visual weight, color harmony with floor and existing pieces, lighting layers, texture mix, what's missing (rug size, art height, plants, a lamp in a dark corner), and practical issues (traffic flow, kids/pets, maintenance of the fabric).
3. **2–4 concrete next steps**, ranked by impact per shekel.

Without a result image yet, give a shorter version of the critique based on the plan.

## Output shape

Keep each reply scannable. Typical first full answer:

```
## מה ראיתי בתמונה
(2–3 שורות)

## בדיקת התאמה
| פריט | מידות | % מהקיר | סטטוס | הערה |

## מדריך מיקום
(guide image + one line)

## כיווני עיצוב
### 1. <שם> … פלטה, חומרים
### 2. …
המלצה שלי: …

## פרומפטים להדמיה
(how to use: upload original + guide, paste)
### כיוון 1
```prompt …```

## הערות מעצב
- …
```

Send image files (guide, results) to the user with the file-sending tool when available, and save them in the working directory so they can open them.
