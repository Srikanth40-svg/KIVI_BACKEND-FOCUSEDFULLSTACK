"""Kivi phonetic memory — the words Kivi keeps."""

import sys

__version__ = "0.1.0"

# Fail here, loudly, rather than three imports deeper.
#
# The reviewing agent will not repair a misconfigured checkout, so the worst possible
# behaviour is a partial success followed by an obscure error. That is exactly what
# happened on a clean checkout: macOS ships Python 3.9 as `python3`, so `python3 -m venv`
# produced a 3.9 environment in which `kivi migrate` and `kivi seed` both worked — and
# then the server died with a pydantic TypeError about evaluating 'str | None', which
# says nothing about the real cause.
#
# 3.10 is the true floor (PEP 604 unions are evaluated at runtime by pydantic). 3.11 is
# what RUN.md asks for and what this was developed against.
_MINIMUM = (3, 10)

if sys.version_info < _MINIMUM:
    raise RuntimeError(
        "Kivi needs Python {}.{} or newer, but this is Python {}.{}.{}.\n"
        "\n"
        "On macOS, `python3` is often the system 3.9. Create the virtualenv with a newer\n"
        "interpreter instead, for example:\n"
        "\n"
        "    python3.12 -m venv .venv        # or: /opt/homebrew/bin/python3.12 -m venv .venv\n"
        "    ./.venv/bin/pip install -r requirements.txt\n"
        "\n"
        "See RUN.md section 1.".format(
            _MINIMUM[0], _MINIMUM[1], *sys.version_info[:3]
        )
    )
