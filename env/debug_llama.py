"""Diagnose why the local Llama pipeline returns empty text.

Loads with the exact llm_shaping args, then inspects pipeline and raw generate
outputs, token ids, decoded special tokens, and top next-token candidates.
"""

import os

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

os.environ.setdefault("LLM_CHOICE", "gpt-3.5-turbo")
os.environ.setdefault("OPENAI_API_KEY", "unused")
import llm_shaping

PATH = os.path.expanduser("~/llama-models/Llama-3.2-3B")
WINDOW = tuple([0.0] * 24 + [0.12])
z = llm_shaping._normalize_for_prompt(WINDOW)
txt = ", ".join(f"{v:.2f}" for v in z)
prompt = llm_shaping._build_prompt(txt)
print("PROMPT_TAIL", repr(prompt[-120:]), flush=True)

tok = AutoTokenizer.from_pretrained(PATH)
mdl = AutoModelForCausalLM.from_pretrained(PATH, device_map="auto", torch_dtype=torch.float16)
print("DEVICE", mdl.device, flush=True)

pipe = pipeline(
    "text-generation", model=mdl, tokenizer=tok,
    max_new_tokens=32, temperature=0.0, do_sample=False, return_full_text=False,
)
out_wo = pipe(prompt)[0]["generated_text"]
print("PIPE_NO_FULL", repr(out_wo), flush=True)
out_full = pipe(prompt, return_full_text=True)[0]["generated_text"]
print("PIPE_FULL_TAIL", repr(out_full[-160:]), flush=True)

inputs = tok(prompt, return_tensors="pt")
input_ids = inputs["input_ids"].to(mdl.device)
attn = inputs["attention_mask"].to(mdl.device)
print("INPUT_IDS_LEN", input_ids.shape[-1], "LAST_IDS", input_ids[0, -8:].tolist(), flush=True)

with torch.no_grad():
    logits = mdl(input_ids, attention_mask=attn).logits[0, -1].float()
top = torch.topk(logits, 8)
print("TOPK_IDS", top.indices.tolist(), flush=True)
print("TOPK_TOKENS", [tok.decode([i]) for i in top.indices.tolist()], flush=True)

with torch.no_grad():
    gen = mdl.generate(
        input_ids,
        attention_mask=attn,
        max_new_tokens=32,
        do_sample=False,
        pad_token_id=tok.eos_token_id,
    )
new_ids = gen[0, input_ids.shape[-1]:].tolist()
print("GEN_IDS", new_ids, flush=True)
print("GEN_DECODE_SKIP", repr(tok.decode(new_ids, skip_special_tokens=True)), flush=True)
print("GEN_DECODE_RAW", repr(tok.decode(new_ids, skip_special_tokens=False)), flush=True)
