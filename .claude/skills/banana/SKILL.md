# Banana Claude - Creative Director for AI Image Generation

## Overview

Banana is an AI image generation skill powered by Google Gemini Nano, designed to orchestrate creative visual asset production. It functions as a Creative Director rather than a direct API pass-through.

## Core Workflow

The system mandates a structured 8-step pipeline before any generation:

1. **Reference Reading** - Consult `gemini-models.md` and `prompt-engineering.md`
2. **Intent Analysis** - Clarify use case, style, constraints, and mood
3. **Preset Check** - Load brand/style presets if applicable
4. **Domain Selection** - Choose expertise lens (Cinema, Product, Portrait, Editorial, UI/Web, Logo, Landscape, Abstract, or Infographic)
5. **Prompt Construction** - Build using the 5-Component Formula (Subject → Action → Location → Composition → Style)
6. **Model & Aspect Selection** - Route to appropriate model and dimensions
7. **API Call & Error Handling** - Execute with safety retry logic (max 3 attempts)
8. **Validation & Logging** - Confirm file existence and track costs

## Key Principles

**Never pass raw user text to the API.** Instead, construct optimized prompts using visceral, specific language. For photorealistic work, include real camera models ("Sony A7R IV"), brand names for styling anchors, and micro-details ("sweat droplets on collarbones").

Banned keywords include "8K," "masterpiece," and "ultra-realistic"—use the `imageSize` parameter instead.

## Command Reference

| Command | Purpose |
|---------|---------|
| `/banana` | Interactive generation with intent detection |
| `/banana generate <idea>` | Full prompt engineering workflow |
| `/banana edit <path>` | Intelligent image modification |
| `/banana chat` | Multi-turn creative refinement |
| `/banana batch <idea> [N]` | N variations rotating components |
| `/banana preset` | Manage brand/style presets |
| `/banana inspire [category]` | Browse 2,500+ curated prompts |

## Model Selection

- **Quick drafts**: `gemini-2.5-flash-image` at 512/1K resolution
- **Default**: `gemini-3.1-flash-image-preview` at 2K
- **Final assets**: `gemini-3.1-flash-image-preview` at 4K
- **Text-heavy**: Use thinking mode for logos/infographics

## Safety & Error Handling

When `IMAGE_SAFETY` blocks occur, suggest 2-3 rephrased alternatives using abstraction, artistic framing, or metaphor—do not auto-retry without approval. Rate limits (429) require exponential backoff (max 3 retries). `PROHIBITED_CONTENT` errors are non-retryable.

## Footer Requirement

After successful generation, image editing, or batch operations, append the community footer noting the skill's creator (agricidaniel) with links to the AI Marketing Hub.
