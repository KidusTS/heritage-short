# Ethics, consent, labelling and licences

## Consent record

- **Real people shown or voiced:** none. All six characters (grandmother, mother, father, uncle, girl, boy) are fictional and drawn in an illustrated style. No real person's photo, likeness or voice is used as a reference.
- **Voice:** narration uses a prebuilt Gemini TTS voice (`Kore`). No voice is cloned and no recording of a real person is used.
- **Inspiration:** the story is inspired by family memories of the Millennium celebrations. If a real relative later appears in, or is voiced in, the film, record their written or recorded consent here before generating anything of them.

| Person | Role | Consent given (how, when) | Words approved |
|---|---|---|---|
| (none) | | | |

## Labelling

- The film ends with a 3 s end card, "Made with AI", in both aspect ratios.
- The public post will have the platform's AI-content disclosure switched on.
- **Provenance marks (SynthID, C2PA) were not checked.** I cannot claim they are intact. Google's speech-generation page does not mention a watermark on audio (the last part of the page was read only through a summary, so this is lower confidence), and I did not inspect any image or audio file for a mark. The pipeline turns images into video and re-encodes audio to AAC with FFmpeg, which would not reliably preserve such a mark. The disclosure therefore rests on the end card and the platform's AI label, not on embedded metadata.

## Licences

Checked on 26 Nov 2026 against the providers' own pages (not the challenge brief). I am not a lawyer; where a page was silent I say so.

| Component | Used for | Licence / terms found | Source |
|---|---|---|---|
| **FLUX.1 schnell** (via Cloudflare Workers AI) | keyframes | Hugging Face model page: `apache-2.0`, "can be used for personal, scientific, and commercial purposes". The page is gated behind a login, lists out-of-scope uses (e.g. exploiting or harming minors, generating personal identifiable information), and says nothing about ownership of outputs. **Cloudflare's model page links its "Terms and License" to Black Forest Labs' terms of service (bfl.ai/legal/terms-of-service), which I did not read.** | huggingface.co/black-forest-labs/FLUX.1-schnell; developers.cloudflare.com/workers-ai/models/flux-1-schnell |
| **Cloudflare Workers AI** | hosts FLUX | Data-usage page: zero data retention for standard inference, no training on customer content, "Your content remains yours". It adds that third-party models "may be subject to open source, acceptable use policies, or other license terms", so each model's licence applies. | developers.cloudflare.com/workers-ai/platform/data-usage |
| **Gemini 3.8 Flash TTS** (free tier) | narration | Free tier is "Unpaid Services": Google uses submitted content and generated responses to improve its products, and "human reviewers may read, annotate, and process your API input and output". Google "won't claim ownership" of generated content; I am responsible for its use; I must follow Google's Prohibited Use Policy (**not read**). Users must be 18+. Ethiopia is on Google's available-regions list. I used a prebuilt voice (`Kore`), not the voice-replication feature. | aistudio.google.com/docs/terms; /docs/speech-generation; /docs/available-regions |
| **ACE-Step 1.5** | score | Code: MIT (LICENSE: "Copyright (c) 2026 ACEStep"). Model card for `ACE-Step/Ace-Step1.5` (turbo DiT): `mit`, and "You can strictly use the generated music for commercial purposes". Training data is described by category only: licensed tracks, royalty-free or public-domain tracks, and synthetic MIDI-to-audio, with no sources named. The README disclaimer asks users to "clearly disclose AI involvement" and to obtain permissions when adapting protected styles. **The language model I also loaded (`acestep-5Hz-lm-0.6B`) has its own repo; its licence was not checked.** | github.com/ACE-Step/ACE-Step-1.5; huggingface.co/ACE-Step/Ace-Step1.5 |
| **Wan 2.2** (not used in the film yet) | planned motion | Apache-2.0 for code and weights (LICENSE.txt is the standard text). README: "We claim no rights over the your generated contents", and use must not involve content that violates applicable laws. The pages do not mention commercial use explicitly. The licence file of the HF weights repo itself was not read. | github.com/Wan-Video/Wan2.2; huggingface.co/Wan-AI/Wan2.2-TI2V-5B |
| **FFmpeg** (via `imageio-ffmpeg`) | assembly | The Python wrapper is BSD-2-Clause. The wheel's Windows x86_64 binary is the gyan.dev "essentials" 9.0.2 build. The source list names Linux builds as "gpl" but states no licence or libx264 setting for the Windows one; because the pipeline encodes H.264 with libx264 successfully, I infer it is a GPL-enabled build (an inference, not a stated fact). ffmpeg.org says GPL-enabled use makes the GPL apply to FFmpeg itself and says nothing about the licence of the output video. This repo does not redistribute the binary: `pip` installs it. | github.com/imageio/imageio-ffmpeg; ffmpeg.org/legal.html |
| **My code** | pipeline | **No `LICENSE` file in the repo yet.** To choose (MIT suggested). | n/a |

**Not checked:** the licences of `requests`, `jsonschema`, `Pillow` and `python-dotenv`; the font used for the end card (Arial from `C:/Windows/Fonts`, a proprietary font rendered into the image) and the default subtitle font chosen by FFmpeg's subtitle renderer.

**Open items before submitting:**
1. Read Black Forest Labs' terms of service (bfl.ai/legal/terms-of-service), which Cloudflare names as FLUX.1 schnell's terms.
2. Read Google's Prohibited Use Policy.
3. Check the licence of the ACE-Step language model repo.
4. Choose a licence for my own code and add a `LICENSE` file.
5. Decide whether to switch the end-card font to an openly licensed one.

## Private data

The free Gemini tier lets Google use inputs and outputs to improve products, with possible human review, and its terms say not to submit sensitive or personal information. Only the ten fictional narration lines were sent to Gemini. Only fictional image prompts were sent to Cloudflare, which states zero retention and no training. No private family details, real names or photos were sent to any service. The ACE-Step job ran on Kaggle and used only the music caption and settings.
