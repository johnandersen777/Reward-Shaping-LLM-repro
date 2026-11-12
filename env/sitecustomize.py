"""Environment shim: make os.scandir/os.walk enumerate in NTFS order.

The original experiment enumerated files on Windows/NTFS, whose directory
$I30 B-tree yields case-insensitive, ordinal (lexicographic) order. Linux
filesystems such as ext4/btrfs return hash order. This shim sorts directory
entries the way NTFS does, without touching the research code.
"""

import os as _os

_real_scandir = _os.scandir


class _SortedScandir:
    def __init__(self, entries):
        self._iter = iter(entries)

    def __iter__(self):
        return self._iter

    def __next__(self):
        return next(self._iter)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False

    def close(self):
        return None


class _NtfsOrderScandir:
    """Callable proxy for os.scandir.

    A class instance has no __get__, so pathlib's ``_NormalAccessor.scandir``
    class attribute does not turn it into a bound method.
    """

    def __call__(self, *args, **kwargs):
        it = _real_scandir(*args, **kwargs)
        try:
            entries = sorted(it, key=lambda entry: entry.name.upper())
        finally:
            close = getattr(it, "close", None)
            if close is not None:
                close()
        return _SortedScandir(entries)


_os.scandir = _NtfsOrderScandir()


# Torch CUDA must initialize before TensorFlow in this environment.
# TensorFlow first + torch CUDA op => segfault; torch first is stable.
# Enabled only when RSL_PRELOAD_TORCH=1.
if _os.environ.get("RSL_PRELOAD_TORCH") == "1":
    try:
        import torch as _torch  # noqa: F401
    except Exception:
        pass


# Optional deterministic seed. Enabled only when RSL_SEED is set.
_seed_env = _os.environ.get("RSL_SEED")
if _seed_env:
    try:
        import random as _random
        import numpy as _np

        _seed_value = int(_seed_env)
        _random.seed(_seed_value)
        _np.random.seed(_seed_value)

        _seed_log_path = _os.environ.get("RSL_SEED_LOG")

        def _append_seed_log(updates):
            if not _seed_log_path:
                return
            try:
                import json as _json

                data = {}
                if _os.path.exists(_seed_log_path):
                    with open(_seed_log_path) as fh:
                        data = _json.load(fh)
                data.update(updates)
                with open(_seed_log_path, "w") as fh:
                    _json.dump(data, fh, sort_keys=True, indent=2)
            except Exception:
                pass

        import sys as _sys

        _py_state = _random.getstate()
        _np_state = _np.random.get_state()
        _append_seed_log(
            {
                "seed": _seed_value,
                "python_hash_seed": _os.environ.get("PYTHONHASHSEED"),
                "python_version": _sys.version,
                "python_random_state": list(_py_state[1]),
                "python_random_gauss_next": _py_state[2],
                "numpy_random_state": {
                    "bit_generator": _np_state[0],
                    "state": _np_state[1].tolist(),
                    "pos": int(_np_state[2]),
                    "has_gauss": int(_np_state[3]),
                    "cached_gaussian": float(_np_state[4]),
                },
            }
        )

        import builtins as _builtins

        _real_import = _builtins.__import__
        _tf_seeded = [False]

        def _seed_tensorflow_import(name, *args, **kwargs):
            module = _real_import(name, *args, **kwargs)
            if not _tf_seeded[0] and name == "tensorflow":
                try:
                    module.compat.v1.set_random_seed(_seed_value)
                    _tf_seeded[0] = True
                    _append_seed_log(
                        {
                            "tensorflow_version": module.__version__,
                            "tensorflow_graph_seed": _seed_value,
                        }
                    )
                except Exception:
                    pass
            return module

        _builtins.__import__ = _seed_tensorflow_import
    except Exception:
        pass


# Optional raw-window mode: feed min-max values to the LLM judge instead of
# z-scores. Enabled only when RSL_RAW_WINDOWS=1. Patches llm_shaping after its
# import/reload; no paper code is edited.
if _os.environ.get("RSL_RAW_WINDOWS") == "1":
    try:
        import importlib as _importlib

        _real_reload = _importlib.reload

        def _reload_for_raw_windows(module):
            module = _real_reload(module)
            if getattr(module, "__name__", "") == "llm_shaping":
                module._normalize_for_prompt = lambda xs: list(xs)
            return module

        _importlib.reload = _reload_for_raw_windows
    except Exception:
        pass


# Optional OpenAI 0.28 -> v1-style chat shim for llm_shaping.py.
# Enabled only when RSL_OPENAI_SHIM=1 so it never affects other Python runs.
if _os.environ.get("RSL_OPENAI_SHIM") == "1":
    try:
        import openai as _openai

        if not hasattr(_openai, "chat"):

            class _Completions:
                @staticmethod
                def create(**kwargs):
                    return _openai.ChatCompletion.create(**kwargs)

            class _Chat:
                completions = _Completions()

            _openai.chat = _Chat()
    except Exception:
        pass
