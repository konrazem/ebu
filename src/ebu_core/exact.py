"""Exact rational numbers for the EBU core.

Every authoritative quantity in ``ebu_core`` is a :class:`fractions.Fraction`.
This module is the single entry point that turns caller input into such a
value. It never routes a value through a binary float, so no rounding can
enter an authoritative result. Rounding, if ever wanted, belongs to display
code only.

Accepted inputs
---------------
* ``int`` (but never ``bool``, even though ``bool`` subclasses ``int``);
* :class:`~fractions.Fraction` (normalised to a plain ``Fraction``);
* ``str`` written in a strict ASCII grammar:

  - decimal:     ``20``, ``-0.5``, ``.5``, ``5.``, ``+3``
  - scientific:  ``1e-2``, ``6.091102297113866550e-24``, ``2E+3``
  - rational:    ``1/100``, ``-4/5`` (integer over positive integer)

Everything else is rejected: ``float`` (including NaN and infinities),
``bool``, :class:`decimal.Decimal`, ``complex``, ``None``, malformed strings,
nonfinite words such as ``"nan"`` or ``"inf"``, zero denominators,
surrounding whitespace, underscores and non-ASCII digits. (Python's own
``Fraction(str)`` would silently accept the last three, so the grammar is
checked first.)

Wrong *kinds* of input raise :class:`TypeError`; a string of the right kind
but invalid content raises :class:`ValueError`.
"""

from __future__ import annotations

import re
from fractions import Fraction

__all__ = ["to_exact", "W_CS", "W_CS_TEXT"]

# Strict ASCII grammars. ``[0-9]`` is used instead of ``\d`` because ``\d``
# also matches non-ASCII digits. ``re.fullmatch`` is used so that a trailing
# newline cannot slip through as it would with ``$``.
_DECIMAL = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?")
_RATIONAL = re.compile(r"([+-]?[0-9]+)/([0-9]+)")


def to_exact(value: object, name: str = "value") -> Fraction:
    """Return ``value`` as an exact :class:`~fractions.Fraction`.

    ``name`` is used only to make error messages point at the offending
    argument (for example ``"K"`` or ``"x_star"``).
    """
    # ``bool`` must be tested before ``int`` because ``True`` is an ``int``.
    if isinstance(value, bool):
        raise TypeError(f"{name}: booleans are not numbers here, got {value!r}")
    if isinstance(value, int):
        return Fraction(int(value))
    if isinstance(value, Fraction):
        # Strip any subclass so the result is a plain Fraction.
        return Fraction(value.numerator, value.denominator)
    if isinstance(value, str):
        return _parse_text(value, name)
    if isinstance(value, float):
        raise TypeError(
            f"{name}: binary floats are not accepted (got {value!r}); "
            "pass an int, a Fraction or exact decimal text such as '0.01'"
        )
    raise TypeError(
        f"{name}: expected int, Fraction or numeric text, got {type(value).__name__}"
    )


def _parse_text(text: str, name: str) -> Fraction:
    match = _RATIONAL.fullmatch(text)
    if match is not None:
        numerator, denominator = (int(group) for group in match.groups())
        if denominator == 0:
            raise ValueError(f"{name}: zero denominator in {text!r}")
        return Fraction(numerator, denominator)
    if _DECIMAL.fullmatch(text) is not None:
        # The grammar has been checked, so Fraction's exact decimal parser is
        # safe to use here: it works in integer arithmetic, not floats.
        return Fraction(text)
    raise ValueError(f"{name}: not a finite decimal, scientific or rational number: {text!r}")


#: The fixed denomination, written exactly as decimal text.
W_CS_TEXT = "6.091102297113866550e-24"

#: W_Cs = h * nu_Cs, in joules per EBU. It is fixed: it is never rescaled by
#: cell size, cell count or network size.
W_CS: Fraction = to_exact(W_CS_TEXT, "W_CS")
