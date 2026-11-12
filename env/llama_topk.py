"""Single-forward probe: top next-token candidates for the llm_shaping prompt."""

import os

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

os.environ["LLM_CHOICE"] = "gpt-3.5-turbo"  # keep llm_shaping from loading a model
os.environ.setdefault("OPENAI_API_KEY", "unused")
import llm_shaping

PATH = os.path.expanduser(os.environ.get("PROBE_MODEL", "~/llama-models/Llama-3.2-3B"))
WINDOW = tuple([0.0] * 24 + [0.12])
z = llm_shaping._normalize_for_prompt(WINDOW)
txt = ", ".join(f"{v:.2f}" for v in z)
prompt = llm_shaping._build_prompt(txt)
print("PATH", PATH, flush=True)
print("PROMPT_TAIL", repr(prompt[-80:]), flush=True)

tok = AutoTokenizer.from_pretrained(PATH)
mdl = AutoModelForCausalLM.from_pretrained(PATH, device_map="auto", torch_dtype=torch.float16)
print("MODEL_DEVICE", mdl.device, flush=True)
if hasattr(mdl, "hf_device_map"):
    devices = {}
    for dev in mdl.hf_device_map.values():
        devices[str(dev)] = devices.get(str(dev), 0) + 1
    print("DEVICE_MAP_COUNTS", devices, flush=True)

inputs = tok(prompt, return_tensors="pt")
input_ids = inputs["input_ids"].to(mdl.device)
attn = inputs["attention_mask"].to(mdl.device)
print("INPUT_IDS_LEN", input_ids.shape[-1], "LAST_IDS", input_ids[0, -6:].tolist(), flush=True)
with torch.no_grad():
    logits = mdl(input_ids, attention_mask=attn).logits[0, -1].float()
top = torch.topk(logits, 10)
print("TOPK_IDS", top.indices.tolist(), flush=True)
print("TOPK_TOKENS", [tok.decode([i]) for i in top.indices.tolist()], flush=True)
print("TOPK_LOGITS", [round(float(v), 4) for v in top.values.tolist()], flush=True)
print("EOS_ID", tok.eos_token_id, flush=True)
