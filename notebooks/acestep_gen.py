# Run inside ACE-Step-1.5 on Kaggle:  %env MPLBACKEND=Agg  then  !uv run python gen.py
# Values come from storyboard.json -> music. Interface taken from ACE-Step's docs/en/INFERENCE.md.
# NOTE: this is the script template given for the run; if you edited it on Kaggle, paste your final version here.
from acestep.handler import AceStepHandler
from acestep.llm_inference import LLMHandler
from acestep.inference import GenerationParams, GenerationConfig, generate_music
import time

dit = AceStepHandler(); llm = LLMHandler()
dit.initialize_service(project_root=".", config_path="acestep-v15-turbo", device="cuda")
llm.initialize(checkpoint_dir="./checkpoints", lm_model_path="acestep-5Hz-lm-0.6B", backend="vllm", device="cuda")
params = GenerationParams(
    caption="gentle warm nostalgic instrumental, soft krar lyre and kirar plucks, mellow piano, "
            "light hand percussion, pentatonic Ethiopian tizita-inspired melody, no lead vocals, "
            "quiet texture that leaves room for a narrator",
    duration=75, bpm=72, keyscale="Am", instrumental=True)
config = GenerationConfig(batch_size=3, seeds=[2000, 2001, 2002], use_random_seed=False, audio_format="wav")
t0 = time.time()
result = generate_music(dit, llm, params, config, save_dir="/kaggle/working/candidates")
print("seconds:", time.time() - t0, "success:", result.success, result.error)
for a in result.audios:
    print(a["path"], a["params"]["seed"])
