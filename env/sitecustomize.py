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
