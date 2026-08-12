# Unified Python Research Framework I-1 Packaging Amendment

**Amendment version:** 1.1.0
**Status:** Prospective packaging authority; fully specification-ready; unimplemented
**Date:** 2026-08-13
**Scope:** Resolve only I-1 packaging backend and frontend-identity blockers
**Mechanical contract:**
`unified_python_research_framework_packaging_contract.json`
**Mechanical-contract raw SHA-256:**
`89f54bd55802c99d292851619439bf96b9e391ef111fb4223adb37e738aa0e28`

---

## 1. Decision

I-1 SHALL use one explicitly manifested, in-tree, standard-library-only PEP
517 backend. The later `pyproject.toml` SHALL contain exactly this build-system
selection:

```toml
[build-system]
requires = []
build-backend = "ebu_build_backend"
backend-path = ["build_backend"]
```

The sole backend source SHALL be
`build_backend/ebu_build_backend.py`. It SHALL implement the bounded contract
in this amendment and the matching JSON contract. It SHALL not be installed
in the wheel. No backend code, `pyproject.toml`, package, lock, schema,
fixture, build, wheel, sdist, or release is created by this amendment.

This choice is not based merely on avoiding a dependency. It is selected
because a complete project-specific contract can be kept to one reviewed
file, can reject unknown package data, can build without VCS or network
discovery, and can remove compression-library, timestamp, permission, source
path, and environment variability from the output bytes. If I-1 review cannot
implement the complete contract without weakening it or materially expanding
the backend, I-1 SHALL stop. A later prospective amendment must then select an
audited third-party backend.

I-1 is now `FULLY_SPECIFICATION_READY_UNIMPLEMENTED`. The two frontend roles
and their exact external validation-tool closures are frozen in §12. This
amendment does not authorize I-1 implementation or validation and does not
begin I-1.

## 2. Authority and narrow precedence

This amendment began prospectively from repository commit
`b76c99d7e8ce05b8ddceba63f82ad12067802a7c` on branch
`v3.0-local-ebu-foundation`, with these unchanged governing documents:

| Authority | Version | Required raw SHA-256 |
|---|---:|---|
| `UNIFIED_PYTHON_RESEARCH_FRAMEWORK_SPECIFICATION.md` | 0.1.1 | `a52b0232595719afd554d842aefb16d6dba0e039ced75c4aed05b358964c6de1` |
| `UNIFIED_PYTHON_RESEARCH_FRAMEWORK_IMPLEMENTATION_PLAN.md` | 0.2.1 | `d89fe92ac6cafd8990588e72d294bcf547cbb478d4b43b638a380e38116ba42e` |

This Markdown file is the normative human rendering. The JSON file named at
the top is the mechanical ordering and value source. They SHALL agree. A
mismatch fails closed; it is not permission to select one selectively.

The amendment supersedes only:

- statements that I-1 is blocked by the explicit-backend/stdlib-only
  contradiction;
- statements that unresolved frontend identity blocks I-1 acceptance;
- the packaging rows and closed-manifest mechanics necessary to add the one
  backend source file;
- I-1 packaging inputs, validation, refusal, acceptance, and readiness
  language.

Every scientific definition, dependency, equation, object, hash projection,
capability classification, stage boundary, and later-stage exclusion in the
specification and plan remains unchanged. Gate 1D-C remains outside scope.

The signed `foundation-v0.1.0` tag object
`90646d3c7e1ff2201eab4739e894598b80782b79` remains at commit
`fa08920a56485962b368bfa032fa284f455413eb`. Its original specification hash
`4c2b3bc65628d37fefb874ab577f8b9ce173554ae2399c788e2d7d301abead38`
and original plan hash
`a1cebfa63528e49d9bada3c6564c7d40616369a45afd97640ff937ae07389674`
remain historical only. This later amendment was not present at that
milestone and neither moves nor reinterprets it.

## 3. Current official packaging requirements verified

The applicable primary specifications were checked on 2026-08-13:

- the current PyPA [`pyproject.toml`
  specification](https://packaging.python.org/en/latest/specifications/pyproject-toml/);
- [PEP 517](https://peps.python.org/pep-0517/), including hook execution,
  build environments, and in-tree `backend-path` rules;
- [PEP 660](https://peps.python.org/pep-0660/) for the optional editable hook
  boundary;
- the current PyPA [source-distribution
  specification](https://packaging.python.org/en/latest/specifications/source-distribution-format/);
- the current PyPA [wheel/binary-distribution
  specification](https://packaging.python.org/en/latest/specifications/binary-distribution-format/);
- current PyPA [Core Metadata
  2.6](https://packaging.python.org/en/latest/specifications/core-metadata/);
- PyPA [`build-details.json`
  v1.0](https://packaging.python.org/en/latest/specifications/build-details/),
  available with Python 3.14;
- the PyPA [`build` 1.5.0 release record](https://pypi.org/project/build/1.5.0/)
  and [frontend documentation](https://build.pypa.io/en/stable/); and
- the PyPA [`pip` 26.2.1 release record](https://pypi.org/project/pip/26.2.1/),
  [`pip wheel` documentation](https://pip.pypa.io/en/stable/cli/pip_wheel/),
  and [build-system interface](https://pip.pypa.io/en/stable/reference/build-system/).

The requirements relevant to the decision are:

1. `[build-system].requires` is mandatory when `[build-system]` exists and is
   a list of dependency specifiers. The standards schema specifies no
   nonempty minimum, so `requires = []` is valid when the backend needs no
   external package.
2. `build-backend` explicitly names the backend object. Omitting it invokes
   legacy fallback behavior and does not satisfy I-1.
3. `backend-path` exists specifically for in-tree backends. Each entry is
   relative to the source root, must resolve inside it, and must contain the
   code from which the backend is loaded.
4. A backend may assume only the standard library and packages declared as
   build requirements. Build frontends are responsible for making declared
   requirements available and should isolate builds by default.
5. PEP 517 requires `build_wheel` and `build_sdist`; the dependency-query and
   wheel-metadata hooks are optional, but this contract supports them
   explicitly.
6. A standard sdist is a `{name}-{version}.tar.gz` containing one matching
   top-level directory, `pyproject.toml`, and `PKG-INFO` at Core Metadata 2.2
   or later, using POSIX.1-2001 pax tar format.
7. A wheel is a ZIP archive with `METADATA`, `WHEEL`, and `RECORD`. Every
   member other than `RECORD` must have a secure `RECORD` hash; SHA-256 is
   selected here.
8. PEP 660 editable hooks are optional. Their absence is a supported refusal,
   not a PEP 517 defect.
9. Current Core Metadata is 2.6, and a producer may emit the lowest version
   containing all fields it uses. This contract selects 2.5 because it uses
   `Import-Name` and does not use the 2.6 extension to `Dynamic`.
10. PyPA `build` is a general PEP 517 distribution-building frontend. Its
    isolated API and explicit `--wheel` and `--sdist` operations can exercise
    and preserve evidence for the source-tree metadata, direct-wheel, and
    sdist roles required here.
11. `pip wheel` is an independently maintained installation-oriented PEP 517
    frontend. Given the exact local sdist, it creates an isolated build
    environment, prepares metadata, and builds a wheel without installing the
    result.

## 4. Alternatives evaluated

### 4.1 Selected: narrow in-tree backend

The selected backend has no external or vendored dependency, uses only
CPython 3.14 standard-library modules, and has one project-specific file
selection rule. It supports both wheel and sdist construction, including the
metadata fast path. Its stricter contract refuses unknown files and produces
stored wheel members and a fixed stored-block gzip stream, eliminating two
common sources of byte drift.

Its risk is local backend correctness. That risk is bounded by keeping the
surface small, making unsupported behavior explicit, freezing the archive
algorithms and metadata, comparing direct and sdist-derived wheels byte for
byte, and requiring independent frontend interoperability. The selection is
conditional on all of those controls being implemented and accepted.

### 4.2 Exact third-party candidate: `flit_core==3.12.0`

The exact candidate evaluated was:

```toml
[build-system]
requires = ["flit_core==3.12.0"]
build-backend = "flit_core.buildapi"
```

The audited PyPI artifact identities were:

| Artifact | Raw SHA-256 |
|---|---|
| `flit_core-3.12.0-py3-none-any.whl` | `e7a0304069ea895172e3c7bb703292e992c5d1555dd1233ab7b5621b5b69e62c` |
| `flit_core-3.12.0.tar.gz` | `18f63100d6f94385c6ed57a72073443e1a71a4acb4339491615d0f16d6ff01b2` |

The packaging-scope audit checked the PyPI identity and attestation, full
wheel file inventory, metadata, licenses, import closure, hook surface,
package-discovery behavior, and published reproducibility documentation. It
is not a general security certification. The installed wheel contains 3,534
lines across its Python source files, bundled `tomli` 1.2.3 material, and the
corresponding BSD licenses.

Flit is mature, PyPA-maintained, supports editable installs, separates its
build-time dependency from the built package's runtime dependencies, and
documents reproducible wheels. It was not selected because it would require a
nonempty and separately locked/audited build closure, carries a materially
larger recurring audit surface, uses generic package discovery rather than
the exact refusal rule below, and makes backend version plus
`SOURCE_DATE_EPOCH` behavior part of artifact reproducibility. Its
`Requires-Python: >=3.6` metadata admits Python 3.14, but framework-specific
CPython 3.14 acceptance evidence would still be required. Those are acceptable
engineering tradeoffs in many projects, but weaker than the bounded contract
feasible here.

### 4.3 Vendored third-party backend

Copying an audited third-party backend under `backend-path` with
`requires = []` is standards-compliant and supports offline isolation. It is
not a standard-library-only backend: it turns the third-party dependency into
vendored source. It would materially expand the file manifest, license and
SBOM surface, review burden, and update obligation. It is not selected.

### 4.4 Legacy fallback or undeclared preinstalled backend

Omitting `build-backend`, relying on `setuptools.build_meta:__legacy__`, or
assuming an undeclared backend is already installed does not satisfy the
explicit-backend requirement. Assuming undeclared packages also violates the
PEP 517 build-environment contract. These options are nonconforming and are
rejected.

## 5. Closed file-manifest amendment

Exactly one implementation path is added prospectively:

| Path | Owner | State | Responsibility |
|---|---|---|---|
| `build_backend/ebu_build_backend.py` | I-1 | New | Sole in-tree stdlib-only PEP 517 backend; implements this contract; excluded from the wheel |

The existing packaging rows are clarified, not duplicated:

| Path | Amended responsibility and ownership |
|---|---|
| `pyproject.toml` | I-1 owns the exact backend selection, static metadata, CPython 3.14 boundary, and initial empty dependency list. I-4 retains its already-frozen sole later authority to add exact Ed25519 runtime dependency metadata. |
| `requirements-framework.lock` | The framework/scientific-runtime closure, initially empty. It is not a build-frontend or build-backend lock. I-4 retains the exact cryptographic runtime closure update/finalization. |

No build-dependency lock is added because the backend dependency closure is
empty. Every other path in implementation-plan §9 remains unchanged. Adding
another backend source, helper, manifest, lock, generated file, or packaging
configuration requires a new prospective amendment.

After this amendment is accepted, I-1 preflight must hash the specification,
implementation plan, this Markdown amendment, this JSON contract, and the
three unchanged imported framework authorities. The two amendment hashes are
additional prospective authority evidence; they do not replace historical
hashes.

## 6. Exact backend and `pyproject.toml` contract

### 6.1 Static project identity

The I-1 `pyproject.toml` SHALL declare static metadata equivalent to:

```toml
[project]
name = "ebu-framework"
version = "0.1.0a1"
description = "Pre-alpha typed and reproducible research-framework infrastructure for EBU"
requires-python = ">=3.14,<3.15"
dependencies = []
dynamic = []
license = "MIT"
license-files = ["LICENSE"]
import-names = ["ebu_framework"]
```

There SHALL be no script, GUI-script, other entry point, dynamic metadata,
direct-URL dependency, `setup.py`, or `setup.cfg`. The `0.1.0a1` value is an
unreleased implementation version. It does not create or authorize the alpha
milestone described by the plan.

### 6.2 Backend identity and environment

The backend contract identity is `ebu-in-tree-pep517-backend/1`. The module
is `ebu_build_backend`; the only source is
`build_backend/ebu_build_backend.py`. At I-1 acceptance its raw SHA-256 and
byte length SHALL be bound to the accepted implementation source commit and
validation evidence.

The backend SHALL:

- run only on final CPython `>=3.14.0,<3.15.0`;
- import only Python 3.14 standard-library modules and its own module;
- make no network, VCS, subprocess, framework, scientific, historical-runner,
  results, or Gate 1D-C access;
- make no source-tree write and require no cache;
- accept only `config_settings is None` or an empty mapping;
- refuse an already-existing output artifact or metadata directory rather
  than overwrite it; and
- read selected inputs into one immutable byte snapshot, with pre/post
  `lstat` identity and content checks that refuse links, nonregular files, or
  any selected-set, identity, size, or content change during the snapshot.

The source tree may be read-only. Outputs go only to the frontend-supplied
directory. Builds use the captured bytes rather than reopening source files
while writing archives.

### 6.3 Supported hooks

| Hook | Exact behavior |
|---|---|
| `get_requires_for_build_wheel(config_settings=None)` | Return `[]` after configuration and interpreter validation |
| `get_requires_for_build_sdist(config_settings=None)` | Return `[]` after configuration and interpreter validation |
| `prepare_metadata_for_build_wheel(metadata_directory, config_settings=None)` | Create and return the exact `ebu_framework-0.1.0a1.dist-info` directory |
| `build_wheel(wheel_directory, config_settings=None, metadata_directory=None)` | Create and return `ebu_framework-0.1.0a1-cp314-none-any.whl` |
| `build_sdist(sdist_directory, config_settings=None)` | Create and return `ebu_framework-0.1.0a1.tar.gz` |

PEP 660 `build_editable`, `get_requires_for_build_editable`, and
`prepare_metadata_for_build_editable` SHALL not be exported. Editable
installation is explicitly unsupported. Legacy operations, extensions,
platform wheels, wheel build tags, generated source, and arbitrary build
configuration are also unsupported.

## 7. Metadata construction

Core Metadata 2.5 SHALL be emitted as UTF-8 with LF endings and a terminal
blank line. Header order is:

1. `Metadata-Version: 2.5`
2. `Name: ebu-framework`
3. `Version: 0.1.0a1`
4. `Summary: Pre-alpha typed and reproducible research-framework infrastructure for EBU`
5. `Requires-Python: >=3.14,<3.15`
6. `License-Expression: MIT`
7. `License-File: LICENSE`
8. `Import-Name: ebu_framework`
9. any later authorized `Requires-Dist` fields in their static
   `pyproject.toml` declaration order.

I-1 has no `Requires-Dist`. `PKG-INFO` uses the same core metadata bytes.

Prepared wheel metadata contains exactly:

```text
ebu_framework-0.1.0a1.dist-info/METADATA
ebu_framework-0.1.0a1.dist-info/WHEEL
ebu_framework-0.1.0a1.dist-info/licenses/LICENSE
```

It contains no `RECORD`, signature, or backend-private state. If
`metadata_directory` is later passed to `build_wheel`, the backend SHALL
validate its basename, complete member set, paths, modes, and bytes against
freshly generated expected metadata, then copy those exact bytes. Any missing,
extra, or changed member refuses the build. Prepared metadata directories use
mode `0755` and their regular files use mode `0644`.

## 8. Package-data inclusion and exclusion

The wheel's installed tree is rooted at `ebu_framework/`, mapped from
`src/ebu_framework/`. A source file is eligible only if its repository path
is present in the accepted closed implementation manifest for the completed
stage and it is one of:

- a regular, non-symlink `src/ebu_framework/**/*.py` file;
- the exact `src/ebu_framework/py.typed` marker;
- `src/ebu_framework/data/core_registry_v1.json`; or
- the two exact Unicode 15.0.0 data assets already frozen by the plan.

At I-1 acceptance, every I-1 package path in plan §9.3 is required. The
Unicode data retain the plan's raw hashes. The registry file is included as
package data. `LICENSE` appears in `.dist-info/licenses/`, not in the import
package.

The backend directory, tests, fixtures, authority documents, results, legacy
modules, bytecode, caches, dotfiles, temporary files, VCS files, and every
other file are excluded. An unknown file anywhere below
`src/ebu_framework` is a refusal, not something silently ignored or included.

Archive paths are ASCII with POSIX separators. Empty, `.`, `..`, absolute,
backslash, control-character, duplicate, Unicode-normalization-colliding, and
case-fold-colliding paths are forbidden. Symlinks, hardlinks, devices, FIFOs,
and sockets are forbidden.

## 9. Deterministic wheel contract

The sole wheel filename and tag are
`ebu_framework-0.1.0a1-cp314-none-any.whl` and `cp314-none-any`.

Members appear in this order:

1. installed package files sorted by UTF-8 path bytes;
2. `ebu_framework-0.1.0a1.dist-info/METADATA`;
3. `ebu_framework-0.1.0a1.dist-info/WHEEL`;
4. `ebu_framework-0.1.0a1.dist-info/licenses/LICENSE`; and
5. `ebu_framework-0.1.0a1.dist-info/RECORD`.

Directory entries are omitted. Every member uses `ZIP_STORED`, timestamp
`1980-01-01 00:00:00`, regular-file mode `0644`, `create_system=3`, ZIP
create/extract version 20, zero internal attributes, and empty extra fields.
External attributes are exactly `(stat.S_IFREG | 0o644) << 16`; general-
purpose flag bits are zero. The archive comment is empty. Paths are ASCII, so
no host-dependent filename encoding is needed.

`WHEEL` is exactly:

```text
Wheel-Version: 1.0
Generator: ebu-in-tree-pep517-backend/1
Root-Is-Purelib: true
Tag: cp314-none-any

```

`RECORD` uses CSV with comma delimiter, double-quote quote character, minimal
quoting, and LF. Rows follow member order. Each non-`RECORD` member records
`sha256=` plus URL-safe base64 of the raw SHA-256 without padding and its
base-10 byte length. The final self-row has empty hash and size.

No `.pyc`, setup file, signature, `entry_points.txt`, or `.data` directory is
permitted.

## 10. Deterministic source-distribution contract

The sole sdist is `ebu_framework-0.1.0a1.tar.gz`, with exactly one effective
top-level directory named `ebu_framework-0.1.0a1`. Its source files are:

- `pyproject.toml`;
- `build_backend/ebu_build_backend.py`;
- `LICENSE`; and
- the exact package source paths selected in §8.

It also contains generated `PKG-INFO`. No test, authority document, repository
history, README, result, legacy source, cache, or unknown file is included.
The archive is nevertheless self-contained: the extracted sdist has the
backend, metadata, license, and every file needed to build the identical
wheel.

Required directory and regular-file member paths, including the top-level
prefix, are sorted lexicographically by UTF-8 path bytes; directory paths end
in `/`. The tar stream uses Python 3.14 `tarfile.PAX_FORMAT` with the sole
ordered global pax header `comment=ebu-sdist-v1`. It uses 512-byte blocks,
exactly two zero end blocks and no later tar record padding, directory mode
`0755`, regular-file mode `0644`, UID/GID zero, empty owner/group names,
empty link name, and `mtime=0`. The required global pax header is the sole
extension record; only effective directory and regular-file members exist.

To remove compression-library variability, the gzip envelope is constructed
by the backend rather than a compressor library:

- fixed header hex `1f8b08000000000000ff`;
- RFC 1951 stored blocks in tar-byte order: every nonfinal block is exactly
  65,535 bytes, the final nonempty block is the remaining 1–65,535 bytes, and
  an empty final block is used only for empty input;
- no gzip filename, comment, or extra field; and
- little-endian CRC32 of the tar bytes followed by their little-endian length
  modulo (2^{32}).

The result remains a standards-compliant gzip/deflate stream and must be
readable with Python 3.14 `tarfile.open(..., mode="r:gz")`. It must also pass
`tarfile`'s data filter, have no unsafe path or member type, and have no
trailing payload.

## 11. Determinism and hashes

All packaging digests below are conventional raw SHA-256 values explicitly
labelled as packaging/source artifact hashes. They never substitute for
`ObjectContentHash`, `ArtifactByteHash`, or another scientific hash domain.

The backend creates an internal UTF-8 build-input manifest beginning with:

```text
ebu-build-input-manifest-v1
```

Each following line is:

```text
sha256=<64 lowercase hex> size=<base-10 bytes> path=<ASCII POSIX relative path>
```

Entries are ordered by path UTF-8 bytes and the final line ends in LF. The
manifest covers `pyproject.toml`, backend source, `LICENSE`, and all selected
package source files. Generated metadata and outputs are excluded. Its
identity is the raw SHA-256 of the complete manifest bytes.

I-1 validation evidence SHALL record:

- the backend raw SHA-256 and byte length;
- the build-input-manifest SHA-256;
- raw SHA-256 and length of `METADATA`, `WHEEL`, and the prepared metadata
  tree manifest;
- raw SHA-256 and length of the wheel and sdist;
- every wheel `RECORD` hash and size;
- the raw SHA-256 and size of every effective sdist regular file;
- exact CPython build identity, including `build-details.json` bytes/hash
  when present; and
- exact frontend artifact identities and hashes used for interoperability.

Output bytes SHALL be invariant to absolute checkout path, source mtimes,
umask, locale, time zone, `PYTHONHASHSEED`, irrelevant environment variables,
VCS state, network availability, and caches. A changed relevant source byte
changes the build-input-manifest hash and normally the appropriate output
hash; an unchanged input snapshot produces identical artifact bytes.

## 12. Frontend interoperability, isolation, and dependency boundary

### 12.1 Exact frontend roles

P10 requires two distinct PEP 517 frontend roles:

1. `F1_SOURCE_DISTRIBUTION_PRODUCER` operates on the accepted source-tree
   snapshot. It invokes isolated wheel-metadata preparation, creates the
   direct wheel, and creates the sdist. This role is frozen to PyPA `build`.
2. `F2_SDIST_WHEEL_CONSUMER` accepts only the exact sdist emitted by F1. It
   performs isolated metadata preparation and wheel construction from the
   safely extracted sdist. It neither creates an sdist nor installs the built
   wheel. This role is frozen to `pip wheel`.

The roles are intentionally asymmetric. Requiring both tools to expose the
same CLI surface would not add interoperability evidence. Together they prove
that one general distribution frontend and one installation-oriented frontend
can drive the applicable backend hooks, and that source-tree, sdist, metadata,
and wheel boundaries agree.

### 12.2 Frozen frontend artifacts and closure

Only these non-yanked universal wheels form the CPython 3.14 POSIX validation-
tool closure:

| Use | Project/version | Exact distribution and raw SHA-256 | Bytes | Declared Python range | License identity |
|---|---|---|---:|---|---|
| F1 frontend | `build==1.5.0` | [`build-1.5.0-py3-none-any.whl`](https://files.pythonhosted.org/packages/0d/fe/6bea5c9162869c5beba5d9c8abbed835ec85bf1ec1fba05a3822325c45f3/build-1.5.0-py3-none-any.whl), `13f3eecb844759ab66efec90ca17639bbf14dc06cb2fdf37a9010322d9c50a6f` | 26,018 | `>=3.10`; classifier includes Python 3.14 and CPython | `MIT` |
| F1 dependency | `packaging==26.3` | [`packaging-26.3-py3-none-any.whl`](https://files.pythonhosted.org/packages/63/34/ba1c580383c9eada3711951fef0795c80b829a078d72188184bcab9dd527/packaging-26.3-py3-none-any.whl), `d7193f7c8e4e93f444fde0262bf90af30e16fa0ad0ad44cb553c87339b23cd1c` | 129,956 | `>=3.9`; classifier includes Python 3.14 and CPython | `Apache-2.0 OR BSD-2-Clause` |
| F1 dependency | `pyproject_hooks==1.2.0` | [`pyproject_hooks-1.2.0-py3-none-any.whl`](https://files.pythonhosted.org/packages/bd/24/12818598c362d7f300f18e74db45963dbcb85150324092410c8b49405e42/pyproject_hooks-1.2.0-py3-none-any.whl), `9e5c6bfa8dcc30091c74b0cf803c81fdd29d94f01992a7707bc97babb1141913` | 10,216 | `>=3.7` | `MIT` |
| F2 frontend and F1 isolation installer | `pip==26.2.1` | [`pip-26.2.1-py3-none-any.whl`](https://files.pythonhosted.org/packages/f3/6e/1736e5b4ae2b778ef2f81c47d797de9f891d4d8acb047a24ca37a60294dd/pip-26.2.1-py3-none-any.whl), `71138adf1f4ca900cdb7d289c21b7494329f2332b6d85f0e1c42108c0384ed3e` | 1,816,632 | `>=3.10`; classifier includes Python 3.14 and CPython | `MIT`, with the wheel's complete bundled third-party license inventory retained |

The authoritative project/release records are the exact PyPI release pages
for [`build` 1.5.0](https://pypi.org/project/build/1.5.0/),
[`packaging` 26.3](https://pypi.org/project/packaging/26.3/),
[`pyproject_hooks` 1.2.0](https://pypi.org/project/pyproject-hooks/1.2.0/),
and [`pip` 26.2.1](https://pypi.org/project/pip/26.2.1/). The raw hashes above
were independently recomputed from the named PyPI files during this
prospective amendment.

On the frozen CPython 3.14 POSIX environment, `build`'s complete active
`Requires-Dist` closure is `packaging>=24.0` plus `pyproject_hooks`; the exact
selected satisfiers are shown above. `colorama` is false under `os_name ==
"nt"`; `importlib-metadata` and `tomli` are false at Python 3.14; and no
`keyring`, `uv`, or `virtualenv` extra is selected. `pip` declares no external
`Requires-Dist`; its private vendored closure and license notices are within
the exact hashed wheel. `pip` is an operational isolation installer for F1,
not a declared dependency of `build`.

For audit completeness, the exact private inventory recorded by the selected
`pip` wheel is: `CacheControl==0.14.4`, `distlib==0.4.2`, `distro==1.9.0`,
`msgpack==1.1.2`, `packaging==26.2`, `platformdirs==4.10.0`,
`pyproject-hooks==1.2.0`, `requests==2.34.2`, `certifi==2026.6.17`,
`idna==3.18`, `urllib3==2.7.0`, `rich==14.2.0`, `pygments==2.20.0`,
`resolvelib==1.2.1`, `setuptools==70.3.0`, `tomli==2.4.1`,
`tomli-w==1.2.0`, and `truststore==0.10.4`. These are vendored implementation
contents, not separately installed distribution dependencies; their bytes and
license files are bound by the `pip` wheel hash.

No sdist may substitute for any frontend-closure wheel. A version-compatible
but differently hashed file is not equivalent. A yanked release, extra,
platform marker that changes the four-artifact closure, or dependency resolver
substitution refuses validation.

### 12.3 Exact validation environment and commands

Validation SHALL use a final CPython `>=3.14.0,<3.15.0` on POSIX. These names
denote absolute paths outside the repository: `I1_VALIDATION_ROOT` is a new
temporary root; `I1_WHEELHOUSE` contains exactly the four read-only wheels in
§12.2; `I1_F1_ENV` and `I1_F2_ENV` are distinct new temporary virtual
environments; `I1_SOURCE_SNAPSHOT` is the accepted read-only source snapshot;
`I1_EVIDENCE` is a new empty evidence directory; and the four output
directories `I1_BUILD_METADATA_OUT`, `I1_BUILD_DIRECT_OUT`,
`I1_BUILD_SDIST_OUT`, and `I1_PIP_OUT` are new and empty. None may resolve
within the repository or source snapshot.

Before a hook is called, validation SHALL recompute all four wheel hashes,
reject any additional wheelhouse member, create both environments using the
selected CPython's standard-library `venv`, and install with `pip install
--isolated --no-index --no-deps`. F1 receives exactly all four named wheels;
F2 receives exactly `pip-26.2.1-py3-none-any.whl`. Each environment is invalid
until `importlib.metadata` proves its exact project versions, active
`Requires-Dist` closure, and license metadata. No other installed distribution
may remain. Bootstrap tooling and the validation wheels never enter a backend
build environment merely by being present in a frontend environment.

The environment-construction argv sequences are exactly:

```text
I1_CPYTHON314_ABSOLUTE_PATH -I -m venv I1_F1_ENV
I1_F1_ENV/bin/python -I -m pip --isolated install --no-index --no-deps --disable-pip-version-check --no-input --no-color --force-reinstall I1_WHEELHOUSE/pip-26.2.1-py3-none-any.whl I1_WHEELHOUSE/packaging-26.3-py3-none-any.whl I1_WHEELHOUSE/pyproject_hooks-1.2.0-py3-none-any.whl I1_WHEELHOUSE/build-1.5.0-py3-none-any.whl
I1_CPYTHON314_ABSOLUTE_PATH -I -m venv I1_F2_ENV
I1_F2_ENV/bin/python -I -m pip --isolated install --no-index --no-deps --disable-pip-version-check --no-input --no-color --force-reinstall I1_WHEELHOUSE/pip-26.2.1-py3-none-any.whl
```

These four sequences run physically offline from `I1_EMPTY_CWD`. The two
`venv` commands run under `env -i` with only `PATH=/usr/bin:/bin`, a distinct
empty `TMPDIR`, `LC_ALL=C`, `LANG=C`, `TZ=UTC`, and
`PYTHONDONTWRITEBYTECODE=1`. Each install command uses the applicable F1 or F2
official process environment defined next.

Each official command SHALL run with a physically disabled network and this
exact process environment: `env -i`, `PATH` containing only the applicable
`I1_F1_ENV/bin` or `I1_F2_ENV/bin`, `/usr/bin`, and `/bin` in that order;
`TMPDIR` set to a distinct new empty directory under `I1_VALIDATION_ROOT` for
each command; `LC_ALL=C`; `LANG=C`;
`TZ=UTC`; `PYTHONHASHSEED=0`; `PYTHONNOUSERSITE=1`;
`PYTHONDONTWRITEBYTECODE=1`; `PIP_CONFIG_FILE=/dev/null`;
`PIP_DISABLE_PIP_VERSION_CHECK=1`; and `PIP_NO_INDEX=1`. No `PYTHONPATH`, pip
index/find-links setting, credential, proxy, or user-site input may survive.
The executable is exactly the applicable environment's `bin/python` with
`-I`.

With stdout and stderr captured separately under `I1_EVIDENCE`, the F1
commands are exactly:

```text
python -I -c '
import pathlib
import sys
from build import ProjectBuilder
from build.env import DefaultIsolatedEnv

with DefaultIsolatedEnv(installer="pip") as isolated_env:
    builder = ProjectBuilder.from_isolated_env(
        isolated_env, sys.argv[1]
    )
    if builder.build_system_requires:
        raise SystemExit("nonempty declared build requirements")
    if builder.get_requires_for_build("wheel"):
        raise SystemExit("nonempty hook-returned wheel requirements")
    prepared = builder.prepare("wheel", sys.argv[2])
    if prepared is None:
        raise SystemExit("prepare_metadata_for_build_wheel missing")
    metadata_path = pathlib.Path(prepared)
    print(metadata_path.name)
' I1_SOURCE_SNAPSHOT I1_BUILD_METADATA_OUT
```

```text
python -I -m build --installer pip --wheel --outdir I1_BUILD_DIRECT_OUT I1_SOURCE_SNAPSHOT
python -I -m build --installer pip --sdist --outdir I1_BUILD_SDIST_OUT I1_SOURCE_SNAPSHOT
```

The F2 command is exactly:

```text
python -I -m pip --isolated --disable-pip-version-check --no-color --no-cache-dir --verbose wheel --use-pep517 --check-build-dependencies --no-deps --no-index --no-input --wheel-dir I1_PIP_OUT I1_BUILD_SDIST_OUT/ebu_framework-0.1.0a1.tar.gz
```

The textual `python` token expands to `I1_F1_ENV/bin/python` for F1 and
`I1_F2_ENV/bin/python` for F2; path tokens expand only to the absolute paths
defined in this subsection. The JSON `argv` and `python_source` values are the
mechanical command source; shell quoting is not an additional input. No
omitted option, config setting, requirement, constraint, environment
variable, or current-working-directory input is permitted. F1 uses `build`'s
isolated `venv` API plus the exact F2 `pip` artifact as installer. The metadata
command preserves the exact prepared metadata tree for byte hashing. Because
declared and hook-returned build requirements are empty, neither F1 nor F2
installs a backend dependency. F2's default PEP 517 build isolation remains
enabled; `--no-build-isolation` is forbidden.

### 12.4 Required frontend evidence

P10 evidence SHALL record the four downloaded artifact filenames, byte
lengths, recomputed hashes, PyPI source URLs, installed versions, active
dependency/marker evaluation, license identities, CPython identity, complete
sanitized environment, exact argv, exit status, and captured stdout/stderr for
every command. It SHALL additionally show that:

- F1 metadata invokes `prepare_metadata_for_build_wheel` under isolation and
  yields the exact metadata contract;
- F1 produces the exact direct wheel and exact sdist and observes empty
  declared and hook-returned build requirements;
- F2 consumes the exact F1 sdist, invokes isolated metadata preparation and
  `build_wheel`, and produces no installation or source-tree write;
- the F1 direct wheel and F2 sdist-derived wheel are byte-identical;
- both frontends receive the exact metadata and archive names frozen here;
- no network access or undeclared dependency lookup succeeds; and
- all frontend environments, caches, outputs, and evidence remain external to
  the repository.

### 12.5 Dependency classification

All four artifacts are external I-1 validation tooling. They SHALL NOT appear
in `[build-system].requires`, `[project].dependencies`, a wheel `Requires-Dist`
field for `ebu-framework`, `requirements-framework.lock`, the closed
implementation file manifest, or the built wheel/sdist. They are not backend
requirements, backend helpers, package data, framework dependencies, or
scientific-runtime dependencies.

`[build-system].requires`, `get_requires_for_build_wheel`, and
`get_requires_for_build_sdist` remain exactly empty. The isolated backend
environment contains CPython 3.14's standard library and frontend hook
transport only. The backend imports only the standard library and its exact
in-tree module.

`requirements-framework.lock` initially represents an empty
framework/scientific-runtime dependency closure. The backend is not installed
at runtime. I-4 retains the existing, separate authority to add only its
audited Ed25519 provider to `[project].dependencies` and to finalize the
runtime lock. `build-system.requires` remains empty in I-4.

Any future external backend or backend helper requires a new prospective
amendment and a separately named, exact build-dependency lock added to the
closed manifest before implementation. Changing a frozen validation frontend
or its active closure requires a prospective amendment to this validation-
tool contract, but never converts that tooling into a package dependency.

## 13. Python 3.14 compatibility

The build interpreter is final CPython `>=3.14.0,<3.15.0`. The wheel tag is
`cp314-none-any`; `Requires-Python` is `>=3.14,<3.15`. The backend uses
standard-library `tomllib`. It refuses another Python implementation, Python
3.13 or earlier, Python 3.15 or later, and prerelease 3.14.

Build evidence records `sys.implementation`, `sys.version`,
`sys.version_info`, the executable's raw hash where permitted, ABI/cache
identity, and `build-details.json` v1.0 when present. A future widening of
runtime or wheel compatibility requires a prospective compatibility
amendment; it is not inferred from pure-Python source.

## 14. Validation vectors and acceptance

All vectors are packaging-only T0 or inert T1. None may import or invoke
framework/scientific behavior.

| ID | Class | Required acceptance relation |
|---|---:|---|
| P1 | T0 | Backend realpath is within the sole `build_backend` path and module origin is the exact backend file |
| P2 | T0 | Declared and returned build requirements are empty; isolated offline hooks import no non-stdlib package |
| P3 | T0 | Prepared, direct-wheel, and sdist-derived metadata are byte-identical and match §7 |
| P4 | T0 | Installed package contains every and only allowed file; all package data retain source hashes |
| P5 | T0 | Three direct builds under varied path/mtime/umask/locale/TZ/hash-seed/environment produce identical wheel bytes |
| P6 | T0 | The same perturbations produce identical sdist bytes and exact archive properties |
| P7 | T0 | Direct wheel and isolated wheel built from the safely extracted sdist are byte-identical |
| P8 | T0 | Independent standard-library parsing verifies filenames, members, CRCs, hashes, sizes, CSV, and archive safety |
| P9 | Inert T1 | Read-only source succeeds; pre-existing output refuses without source/output modification or accepted partial artifact |
| P10 | Inert T1 | Exact `build==1.5.0` F1 and `pip==26.2.1` F2 closures execute the role-specific §12.3 commands under isolation; F1 direct and F2 sdist-derived wheels are byte-identical |
| P11 | T0 | CPython 3.14 produces the exact tag/metadata and other interpreter boundaries refuse |
| P12 | T0 | Static reachability finds no scientific/framework execution, historical runner, Gate 1D-C, result, network, or subprocess path in the backend; external frontends may handle source bytes only as inert packaging inputs, cannot import or execute them, cannot access prohibited repository paths, and are physically network-disabled |

Every vector must complete with nonzero checks. Skipped, terminated, or
zero-check vectors are not passes. Acceptance also requires the exact hashes
listed in §11, a complete closed-manifest audit, current PyPA conformance, an
empty initial build closure, an empty initial runtime closure, and an explicit
record that no scientific code or model state executed.

Principal refusal classes are authority/contract mismatch, unsupported
interpreter, backend-path escape or origin mismatch, undeclared dependency,
unsupported configuration, dynamic metadata, file-set or package-data
mismatch, unsafe path, source mutation, output collision, metadata-directory
mismatch, wheel/sdist/`RECORD` mismatch, nondeterminism, sdist/wheel
divergence, editable-build request, and scientific reachability. The exact
machine-readable codes and ordering are frozen in the JSON contract.

## 15. Stage consequences

For I-1:

- the status changes only from `BLOCKED` to
  `FULLY_SPECIFICATION_READY_UNIMPLEMENTED`;
- these two amendment documents become exact-hash inputs;
- the one backend file becomes an I-1 closed-manifest implementation path;
- backend construction and P1–P12 are added to I-1 work and acceptance; and
- implementation still requires a new explicit authorization.

For I-4, build requirements remain empty. I-4's existing narrow ownership of
the audited Ed25519 runtime dependency and runtime-lock finalization remains
unchanged.

For I-9, the audit must include the backend source, packaging file set,
artifact hashes, current PyPA conformance, exact frontend artifacts and active
closures, role separation and isolation, direct/sdist wheel identity, archive
safety, and the build/runtime dependency separation.

No later implementation stage begins automatically. This amendment creates
no distribution or release and authorizes no upload, tag, commit, push,
scientific configuration, model step, runner, trajectory, interpretation, or
publication.

## 16. Remaining packaging questions

The selected backend and frontend-validation contracts are complete enough
for I-1 implementation and acceptance. No unresolved frontend identity blocks
I-1. These genuinely future questions remain deliberately outside it:

| ID | Question | Blocks | Owner |
|---|---|---|---|
| PKG-OQ-02 | Which exact final CPython 3.14 patch/build is the release reference environment? | Distribution release only; all conforming 3.14 builds must already agree | Future release checklist |
| PKG-OQ-03 | Will a stable release support anything beyond CPython 3.14? | Future compatibility expansion | Prospective compatibility amendment |
| PKG-OQ-04 | Will editable installation ever be supported? | Editable workflow only | Prospective PEP 660 amendment |
| PKG-OQ-05 | What version/destination follows the unreleased `0.1.0a1` artifacts? | Release/publication only | Separately authorized release plan |

None permits a hidden default or blocks I-1 implementation or acceptance.
PKG-OQ-02 and PKG-OQ-05 remain release-stage questions; the others require
prospective amendments only if their features are requested.

## 17. Present nonclaims

This amendment specifies a future packaging solution. It does not claim that:

- the backend, package metadata, wheel, or sdist exists;
- any hook, archive, install, import, or Python 3.14 behavior has been
  implemented or tested;
- the frozen frontend commands or interoperability vectors have been run;
- I-1 or another implementation stage has begun or passed;
- a third-party backend has received a full security certification;
- the package is released, installable, scientifically validated, or fit for
  production; or
- any framework, scientific, Gate 1D-C, model-state, result, or publication
  operation occurred.
