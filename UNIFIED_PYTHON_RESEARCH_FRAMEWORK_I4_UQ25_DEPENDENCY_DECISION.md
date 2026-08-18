# Unified Python Research Framework I-4 UQ-25 Dependency Decision

Status: prospective selection complete; uninstalled and unexecuted.

## 1. Decision

Select exactly `PyNaCl==1.6.2` as the Framework I-4 Ed25519 verification
provider. The complete CPython closure is exactly `cffi==2.1.1` and
`pycparser==3.0`.

The mechanical source of every filename, byte count, SHA-256, upload state,
native member, license notice, marker, platform, lock line, API symbol, and
normalization rule is
`unified_python_research_framework_i4_uq25_dependency_contract.json`.

No distribution was installed or imported, and no candidate Python or native
code was executed. Twenty-three raw wheels were downloaded to one external
temporary directory for ZIP-only inspection and hashing. After evidence was
recorded, that exact directory and its inspection metadata were permanently
removed; they are absent from `/private/tmp` and the system Trash. Nothing was
copied into the repository.

## 2. Review method and sources

The current review was retrieved at `2026-08-18T09:27:43Z`. It used primary
or authoritative sources only:

- [PyNaCl 1.6.2 PyPI JSON](https://pypi.org/pypi/PyNaCl/1.6.2/json)
- [cffi 2.1.1 PyPI JSON](https://pypi.org/pypi/cffi/2.1.1/json)
- [cffi 2.1.1 upstream release](https://github.com/python-cffi/cffi/releases/tag/v2.1.1)
- [cffi 2.1.0...2.1.1 comparison](https://github.com/python-cffi/cffi/compare/v2.1.0...v2.1.1)
- [pycparser 3.0 PyPI JSON](https://pypi.org/pypi/pycparser/3.0/json)
- [PyNaCl changelog](https://pynacl.readthedocs.io/en/latest/changelog/)
- [PyNaCl signing API](https://pynacl.readthedocs.io/en/latest/signing/)
- [libsodium public-key signatures](https://doc.libsodium.org/public-key_cryptography/public-key_signatures)
- [libsodium point validation](https://doc.libsodium.org/advanced/point-arithmetic)
- [RFC 8032](https://www.rfc-editor.org/rfc/rfc8032.html)
- [cryptography 50.0.0 PyPI JSON](https://pypi.org/pypi/cryptography/50.0.0/json)
- [cryptography changelog](https://cryptography.io/en/latest/changelog/)

The review independently retrieved PyPI metadata, compared provider surfaces,
downloaded only the admitted wheel candidates, verified raw lengths and
SHA-256 values against PyPI, parsed ZIP central directories and text members,
hashed every selected native extension and license file, and inspected the
exact provider API source as text. Windows wheels package the inspected
PyNaCl source and notice text with CRLF while non-Windows wheels use LF; the
normalized text is identical, and both raw variants are frozen mechanically.

The inspection covered 23 wheels totaling 8,490,512 bytes. Its canonical
inventory projection is the contract's exact `artifacts` array serialized as
UTF-8 JSON with sorted keys, no insignificant whitespace, and non-ASCII left
unescaped. It is 10,421 bytes with SHA-256
`901cdd158132e7754a913d41f9c4fcbc034eeb769e58e6696724b6d7c4f4623f`.
That digest is evidence metadata, not permission to recover or execute the
temporary files.

## 3. Provider comparison

### 3.1 Selected: PyNaCl 1.6.2

PyNaCl 1.6.2 was selected because:

- its official changelog explicitly records free-threaded Python 3.14
  support;
- `nacl.signing.VerifyKey.verify` exposes the exact detached Ed25519
  verification needed here;
- standard and free-threaded wheels cover every admitted platform;
- its wheels bundle libsodium `1.0.20-stable`, 2025-12-31 build;
- its changelog records that build as resolving `CVE-2025-69277`; and
- the PyPI JSON vulnerability list for PyNaCl 1.6.2, cffi 2.1.1, and
  pycparser 3.0 was empty at retrieval.

PyNaCl is not trusted to validate framework structure. The framework performs
profile, canonical-base64url, length, key-ID, canonical-point, small-order,
and `S < L` checks before it constructs `VerifyKey`.

### 3.2 Rejected: cryptography 50.0.0

cryptography 50.0.0 is a final, non-yanked release whose PyPI vulnerability
list was empty at retrieval. Its changelog records the fix for the
`CVE-2026-69247` PKCS#7 decryption oracle that affected 49.0.0, so the old
advisory is not a reason to reject 50.0.0.

It nevertheless fails the frozen platform boundary. Its standard `abi3` and
free-threaded `cp314t` wheels cover only eight of the twelve required
interpreter/platform combinations: both modes lack macOS x86_64 and Windows
ARM64 wheels. PyNaCl covers all twelve combinations and exposes only the
three framework-reachable symbols required for detached verification.
cryptography's broader Rust/OpenSSL and multi-primitive API surface supplies
no compensating benefit. PyNaCl therefore remains the preferable provider
after the current comparison.

### 3.3 Selected closure release: cffi 2.1.1

cffi 2.1.1 is a final, non-yanked release published on 2026-08-03. Upstream
describes a compatibility repair that minimizes internal interpreter/thread
state API use and avoids an ABI break beginning with Python 3.15.0b4. The
change does not narrow the frozen CPython 3.14/3.14t boundary: all twelve
required wheels exist, are non-yanked, retain the required `cp314` or
`cp314t` tags, and declare the same sole CPython runtime dependency on
`pycparser`. Its PyPI vulnerability list was empty. There is no
evidence-backed reason to retain the superseded 2.1.0 closure, so 2.1.1 is
selected.

This is a prospective selection, not a timeless endorsement. A new advisory,
yank, artifact replacement, or missing wheel blocks later implementation and
requires a new prospective dependency decision.

## 4. Exact distribution and API boundary

The exact direct requirement is:

```text
PyNaCl==1.6.2
```

The only provider symbols reachable from production `trust.py` are:

```text
nacl.signing.VerifyKey
nacl.encoding.RawEncoder
nacl.exceptions.BadSignatureError
```

The only provider call is:

```python
VerifyKey(public_key_bytes, encoder=RawEncoder).verify(
    message_bytes,
    signature_bytes,
    encoder=RawEncoder,
)
```

Success requires an exact `bytes` return equal to `message_bytes`. Provider
`BadSignatureError`, built-in `ValueError` or `TypeError`, any other
`Exception` from construction or verification, non-bytes, unequal bytes, and
unexpected behavior normalize to `SIGNATURE_INVALID`.

Signing classes and functions are forbidden. Ed25519ctx, Ed25519ph, prehash,
multipart/streaming APIs, fallback, and algorithm negotiation reject before
provider construction.

## 5. PureEdDSA structural enforcement

The framework enforces:

- canonical unpadded base64url, round-trip exact;
- 32 decoded public-key bytes and 64 decoded signature bytes;
- key ID `ed25519:<raw-public-key-sha256>`;
- canonical edwards25519 public key and signature `R` point encodings;
- curve decompression, rejection of `x=0` with sign bit one, and rejection of
  small order by the exact contract;
- little-endian signature scalar strictly below RFC 8032 `L`;
- exact ECJ-1 message bytes; and
- no caller-selected encoder, profile, hash, context, or fallback.

Any failed precheck makes zero `VerifyKey` constructions and zero provider
verify calls. A structurally admissible signature makes exactly one of each
and never retries.

The validation authority includes the first three RFC 8032 `7.1` PureEdDSA
vectors, wrong key, wrong message, wrong signature, malformed and
noncanonical points, small-order cases, `S=L`, `S>L`, key/signature lengths,
base64url errors, and explicit ctx/ph/prehash rejection.

## 6. Complete transitive closure

For CPython 3.14, the closure is:

| Distribution | Version | Reason |
|---|---:|---|
| PyNaCl | 1.6.2 | direct provider |
| cffi | 2.1.1 | PyNaCl runtime dependency under CPython >=3.9 |
| pycparser | 3.0 | cffi runtime dependency under CPython |

No extras are enabled. PyNaCl `tests` and `docs` extras are excluded.
`pycparser` has no runtime dependency. Exactly these three installed
distributions are allowed.

Source distributions, source builds, editable installs, VCS references,
direct URLs, local paths, undeclared system packages, and additional
transitives are prohibited.

## 7. Platform and wheel policy

Both standard and free-threaded CPython 3.14 are admitted:

- standard: PyNaCl `cp38-abi3` plus cffi `cp314-cp314`;
- free-threaded: PyNaCl `cp314-cp314t` plus cffi
  `cp314-cp314t`; and
- pycparser: `py3-none-any`.

The exact supported targets are:

- macOS x86_64 10.15 or later;
- macOS arm64 11.0 or later;
- Linux glibc 2.17 or later on x86_64;
- Linux glibc 2.17 or later on aarch64;
- Windows AMD64; and
- Windows ARM64.

Musl, 32-bit Windows, ppc64le, s390x, armv7l, iOS, PyPy, other
implementations, and CPython outside 3.14 are not admitted. The contract
contains the exact 23-wheel inventory and all native-member digests.

## 8. Native library and notices

PyNaCl 1.6.2 declares bundled libsodium `1.0.20-stable`, 2025-12-31 build.
Static inspection found it incorporated into each `nacl/_sodium` extension;
no separate loadable libsodium member was present. Each extension member path,
length, and SHA-256 is frozen per wheel. System libsodium, a different bundled
build, or loader injection is forbidden.

The required notices are:

| Component | License | Notice SHA-256 |
|---|---|---|
| PyNaCl 1.6.2, non-Windows wheels | Apache-2.0 | `d3174ad63e721d4c9dccb8ad4320848992d314369bc46319720b5802c9153fe9` |
| PyNaCl 1.6.2, Windows wheels | Apache-2.0 | `77af5bbded959114b6d7a5eea518b2be364e04f4f4a95f9e87d9870c27713d24` |
| libsodium, non-Windows wheels | ISC | `508a76d186356c0dd807a670ef510964f8724557024796a2c426c6c0e19ab683` |
| libsodium, Windows wheels | ISC | `93e7cac854d71cdafc9d9e4e9f8fd28d87ae541b3dda224d7c8fe23d37875704` |
| cffi 2.1.1 | MIT-0 | `5ba24ddc57067f9249add644c3afc41a5d6dc37e23433ef759d95df370b0af63` |
| pycparser 3.0 | BSD-3-Clause | `0c846399369ea76ddd7b5c44fe6d16497415fcf015f5cbb508c24bf98b81c5b1` |

The Windows and non-Windows PyNaCl notice bytes differ only in their packaged
text encoding, but each applicable raw identity is normative. The four
notices applicable to a selected installation must remain installed and be
carried into any redistributed third-party notice bundle.

## 9. Proposed package and lock bytes

The future `pyproject.toml` edit replaces only:

```toml
dependencies = []
```

with:

```toml
dependencies = ["PyNaCl==1.6.2"]
```

Every other byte remains unchanged.

The exact proposed `requirements-framework.lock` lines appear in the
mechanical contract. Joining them with LF and appending one LF produces 2,036
bytes and raw SHA-256
`8d37c527af8caf5b168d397fbc35e651f98266c51aefc12a1ad415c97c34663a`.
It begins with `--only-binary=:all:` and `--require-hashes` and freezes all 23
wheel hashes. The real package and lock files are unchanged by this task.

## 10. Installed-distribution verification

A later implementation must verify without importing provider modules:

1. `importlib.metadata` finds exactly PyNaCl 1.6.2, cffi 2.1.1, and
   pycparser 3.0;
2. no `direct_url.json` exists;
3. an installer receipt names the exact selected wheel filename, length, and
   SHA-256;
4. the target selects exactly one admitted PyNaCl wheel, one cffi wheel, and
   the sole pycparser wheel;
5. every installed `RECORD` entry, length, digest, `METADATA` dependency,
   notice file, and native-member digest matches; and
6. no unrecorded provider file, system libsodium substitution, editable
   source, or extra provider exists.

Any failure is `DEPENDENCY_INTEGRITY_FAILURE` before provider import.

## 11. Nonclaims

This decision installs nothing, executes nothing, creates no trust anchor,
and activates no authorization. It makes no claim about platforms outside the
exact matrix. A fresh security and artifact-availability review remains
mandatory during a separately authorized implementation audit.
