---
name: comfyui-product-staging
description: Produce photorealistic studio and lifestyle e-commerce product staging on local GPU using ComfyUI, BiRefNet background segmentation, IC-Light relighting, and FLUX.1 Schnell.
---

# ComfyUI Product Staging & Relighting Skill

This skill teaches agents how to construct automated e-commerce product photography pipelines running locally on an RTX 4060 at **€0 marginal cost**.

---

## 1. Pipeline Flow

```
[Raw Supplier Image]
       │
       ▼
[BiRefNet Node] ────────► Clean Alpha Mask (Foreground Extraction)
       │
       ▼
[FLUX.1 Schnell] ───────► Generate Target Background (e.g. Modern Scandinavian Kitchen)
       │
       ▼
[IC-Light Node] ────────► Re-illuminate Product + Match Shadow/Ambient Light to Scene
       │
       ▼
[Upscaler / ResAdapter] ─► Ultra-Crisp Product Asset (1080x1080 / 1080x1920)
```

---

## 2. Key ComfyUI Nodes & Model Setup

1. **Foreground Segmentation**:
   - **Node**: `BiRefNet` or `SegmentAnythingUltra`.
   - **Role**: Automatically cuts out the product from low-quality supplier backgrounds with clean sub-pixel edge feathering.
2. **Background Synthesis**:
   - **Model**: `FLUX.1-schnell-GGUF` (or `flux1-schnell-fp8`) with 4-step inference.
   - **Prompts**: High-end minimalist interior, luxury marble counter, warm natural sunlight streaming from a window, shallow depth of field, 8k commercial product photography.
3. **IC-Light Relighting**:
   - **Model**: `iclight-bcon` (background conditioned) or `iclight-fbc` (foreground + background).
   - **Role**: Recalculates ambient reflections and directional cast shadows on the product surface so it sits seamlessly in the newly generated environment without the "cut-and-paste" sticker look.
4. **Detail Restoration**:
   - **Node**: `ResAdapter` or `4x-UltraSharp` upscaler to preserve crisp product logos, dials, and text.

---

## 3. Automation via ComfyUI API

Automate batch staging from Python by posting JSON workflow payloads to the local ComfyUI API endpoint:

```python
import json
import urllib.request

def queue_staging_job(prompt_workflow, server_address="127.0.0.1:8188"):
    p = {"prompt": prompt_workflow}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(f"http://{server_address}/prompt", data=data)
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read())
```

---

## 4. Compliance & Disclosures
Under the **EU AI Act**, any synthetic product staging must include a clean PDP disclosure:
> *"Product imagery assisted by generative AI"*
