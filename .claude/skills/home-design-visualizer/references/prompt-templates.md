# Prompt templates for room-edit visualizations

## Which tool to recommend

| Tool | Strength | Notes |
|---|---|---|
| ChatGPT (GPT Image) | Best at following multi-part instructions and using a second "guide" image | Upload both images in one message, then the prompt |
| Gemini (Nano Banana / Gemini image) | Very good at preserving the original room exactly; fast iterations | Good for follow-up tweaks ("now change the rug") |
| Flux Kontext (via sites like fal.ai, Replicate) | Precise local edits | Usually one input image — draw the guide boxes on the photo itself and say "replace the colored boxes" |

Default recommendation: ChatGPT for the first render, Gemini for small follow-up changes.

## Main template (original + guide image)

Fill every `<...>`. Delete lines that don't apply. Keep it in English.

```
I am attaching two images of the same room.
Image 1 is the real photo of my <living room>. Image 2 is the same photo with colored placement boxes drawn to exact scale.

Edit Image 1 photorealistically. Keep everything that is not mentioned exactly as it is: same camera position, lens and framing, same walls, windows, doors, floor, ceiling, existing furniture, and the same natural lighting coming from <the window on the left>. Do not add any objects I did not ask for.

Place the following items so each one fills its colored box in Image 2 exactly — same left and right edges, same height. The boxes are drawn to real-world scale, so match them precisely and do not enlarge or shrink the items:
- Box A (<230 cm wide, 85 cm high>): <a three-seat sofa, light grey woven fabric, low straight back, square arms, slim natural oak legs>.
- Box B (<...>): <...>.

Style direction "<Warm Japandi>": <wall color: warm off-white (#EDE6DA); rug: 200x290 cm natural jute with cream border under the front legs of the sofa; pillows: 2 rust linen, 1 sand bouclé; ...>.

Items not on the wall: <a round oak coffee table, about 90 cm diameter, centered in front of the sofa with a 45 cm gap>.

Lighting and realism: match the existing light direction and color temperature, add soft contact shadows under every new item, keep realistic fabric and wood textures. The result must look like an unedited photograph of this exact room. Remove the colored boxes and labels; they must not appear in the result.
```

## Single-image variant (Flux Kontext or a tool that takes one image)

Upload the **guide** image only and use:

```
This is a photo of my room with colored boxes marking where new furniture goes. Replace each colored box with the item described, exactly filling the box's outline, and remove all boxes, labels and the yellow outline and grid lines. Keep everything else in the photo unchanged.
- Red box A: <...>
- Blue box B: <...>
Match the room's lighting, add natural shadows, photorealistic.
```

## Follow-up correction prompts

- Size: `The sofa is too wide. Make it narrower so its right arm ends <at the left edge of the window frame / 40 cm before the corner>. Change nothing else.`
- Color: `Change only the sofa fabric to <warm mid-grey #8E8A84>. Keep the shape, position, lighting and everything else identical.`
- Swap: `Replace the rug with a <...>. Keep everything else identical.`
- Drift: `Too many things changed. Start again from the original photo and only add <item>.`

## Tips worth passing to the user (briefly)

- One change per follow-up gives the most control.
- If the tool keeps changing the room, start a new chat and upload the original again.
- Colors on screen differ from reality — use the result for feel and fabric samples for the final decision.
