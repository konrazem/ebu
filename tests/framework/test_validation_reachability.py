from __future__ import annotations

import ast
import copy
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "ebu_framework"
AUTHORITY_FILES = (
    "unified_python_research_framework_i9_contract.json",
    "unified_python_research_framework_i9_validation_contract.json",
    "unified_python_research_framework_i9_predecessor_manifest.json",
    "unified_python_research_framework_i9_implementation_path_manifest.json",
)
AUTHORITY_RAW_SHA256 = {
    "UNIFIED_PYTHON_RESEARCH_FRAMEWORK_I9_AUTHORITY_AMENDMENT.md": (
        "11c48ec99e2d8238f455487139b87e1f7e170ec594f3f2f98bb0aebe7c59e2e4"
    ),
    "unified_python_research_framework_i9_contract.json": (
        "29b6b715f4fdc64ddc60a5323e103d664021927f951cf8edbde2ac93f6c50406"
    ),
    "unified_python_research_framework_i9_validation_contract.json": (
        "64097d37828ce46af80bece7a394f43e82ab1be2840f55917307267b0e8579c4"
    ),
    "unified_python_research_framework_i9_predecessor_manifest.json": (
        "012d3c64003833acbb72e4e9151bddc2f953a1d402e07a195293f8a736ecc06c"
    ),
    "unified_python_research_framework_i9_implementation_path_manifest.json": (
        "7a339f851e09a3e79755fabd143c9a2ce1efa6f52a9c85aa12f5f7f29b2f2f8b"
    ),
}
IMPLEMENTATION_PATHS = (
    ".github/workflows/tests.yml",
    "src/ebu_framework/validation.py",
    "tests/framework/safety.py",
    "tests/framework/test_validation_reachability.py",
)
PRIVATE_NAMES = (
    "_validate_group_descriptor",
    "_validate_source_locks",
    "_validate_implementation_surface",
    "_validate_forbidden_reachability",
    "_validate_group_evidence",
    "_validate_audit_mapping",
    "_authorize_t2_fixture",
)
CONSTANT_NAMES = (
    "_VALIDATION_GROUPS",
    "_I9_IMPLEMENTATION_PATHS",
    "_I9_ROOT_EXPORTS",
    "_I9_FAILURE_CODES",
    "_I9_PUBLIC_SIGNATURES",
    "_I9_DIRECT_IMPORTS",
    "_I9_T2_ALLOWLIST",
    "_I9_AUDIT_REGISTER",
)
T0_PATHS = (
    "tests/framework/test_ecj1.py",
    "tests/framework/test_hash_preimages.py",
    "tests/framework/test_identity_registry.py",
    "tests/framework/test_numeric.py",
    "tests/framework/test_primitives_envelopes.py",
    "tests/framework/test_i3_integration.py",
    "tests/framework/test_i3a_declarations.py",
    "tests/framework/test_i3b_declarations.py",
    "tests/framework/test_i3c_declarations.py",
    "tests/framework/test_i3d_declarations.py",
    "tests/framework/test_atomic_declarations.py",
    "tests/framework/test_interaction_declarations.py",
    "tests/framework/test_event_ownership.py",
    "tests/framework/test_route_guards.py",
    "tests/framework/test_validation_reachability.py",
)
T1_PATHS = (
    "tests/framework/test_authorization.py",
    "tests/framework/test_authorization_use.py",
    "tests/framework/test_capabilities.py",
    "tests/framework/test_event_ownership.py",
    "tests/framework/test_inert_durability.py",
    "tests/framework/test_artifact_recovery_publication.py",
)
T2_PATHS = (
    "tests/framework/test_bridge_exact_fixtures.py",
    "tests/framework/test_dynamic_static_identities.py",
)
CURRENT_T0_PATHS = (
    "tests/framework/test_closed_loop_correction_diagnostics.py",
)
CORRECTION_AUTHORITY_FILES = (
    "POST_I9_CI_DURABILITY_CORRECTION_AUTHORITY_AMENDMENT.md",
    "post_i9_ci_durability_correction_contract.json",
    "post_i9_ci_durability_correction_validation_contract.json",
    "post_i9_ci_durability_correction_predecessor_manifest.json",
    "post_i9_ci_durability_correction_implementation_path_manifest.json",
)
CORRECTION_AUTHORITY_RAW_SHA256 = {
    "POST_I9_CI_DURABILITY_CORRECTION_AUTHORITY_AMENDMENT.md": (
        "bf5fdfe517e9eecaf05421b108b8f59e90f54b1ea282b3efece3d148fa053b83"
    ),
    "post_i9_ci_durability_correction_contract.json": (
        "da65c29ba4cbab79d811d3652eb7346365584efb116c6ee85c44f1815cf49351"
    ),
    "post_i9_ci_durability_correction_validation_contract.json": (
        "2c134d81257e093dd12699262e684b69513a8cf9abff47c76cd39c1cc6098b6d"
    ),
    "post_i9_ci_durability_correction_predecessor_manifest.json": (
        "42272d732895483b865e548a3a2112042f4166ee5315e698e826cd6eda1fd6f4"
    ),
    "post_i9_ci_durability_correction_implementation_path_manifest.json": (
        "ccfa979c0c4166411224421b0263988a7dc2efd3764f557bf79706a02ea6f285"
    ),
}
COORDINATE_CHAIN = {
    "accepted_i9_authority_base": {
        "commit": "4ab6f9ca32e32a3801c6a4b6872b34b206e6da7e",
        "tree": "591ad275116e9dc28bf0443aae80142e5ad86ec5",
    },
    "accepted_i9_authority_candidate": {
        "commit": "15c721cf745d79fabeda749badbac35a7fda9993",
        "tree": "8f570082e40304b156aa18714c65938777126f74",
    },
    "accepted_i9_authority_target": {
        "commit": "2e7848dc495c4b2d5fb2ea09d668f2b240d3ec02",
        "tree": "8f570082e40304b156aa18714c65938777126f74",
    },
    "accepted_i9_implementation_candidate": {
        "commit": "f8623fe5f0d313e16558eb9a4c985940e6baf9dd",
        "tree": "3b1cfbdbcc844e0a4944447e012f20981af6998a",
    },
    "accepted_i9_implementation_target": {
        "commit": "ffc910329957f61deaa7e9fc09ba77a0e3f51381",
        "tree": "3b1cfbdbcc844e0a4944447e012f20981af6998a",
    },
    "accepted_later_documentation_feature": {
        "commit": "5674ea9c33b72b94669c86e7e4f1a35c0db5775a",
        "tree": "18aa3399e1c832d261cb1cfff0fb5a6fc3f70bc3",
    },
    "required_current_target": {
        "commit": "fc20d71e69cf226e6cecd9de7575f1d6249b193f",
        "tree": "18aa3399e1c832d261cb1cfff0fb5a6fc3f70bc3",
    },
}
COORDINATE_ENV = {
    "accepted_i9_authority_base": "EBU_I9_AUTHORITY_BASE",
    "accepted_i9_authority_candidate": "EBU_I9_AUTHORITY_CANDIDATE",
    "accepted_i9_authority_target": "EBU_I9_AUTHORITY_TARGET",
    "accepted_i9_implementation_candidate": "EBU_I9_IMPLEMENTATION_CANDIDATE",
    "accepted_i9_implementation_target": "EBU_I9_IMPLEMENTATION_TARGET",
    "accepted_later_documentation_feature": "EBU_I9_LATER_DOCUMENTATION_FEATURE",
    "required_current_target": "EBU_I9_REQUIRED_CURRENT_TARGET",
}
IMPLEMENTATION_BASE_COMMIT = "5de9f64db189f0e1db4da72efc2f2049e16ab4be"
IMPLEMENTATION_BASE_TREE = "c3dd8b47194e85679eb19e197080676771d3826f"
STAGE_C_PREDECESSOR_COMMIT = "3c0b8939b9902e05584501e31d74e2bcb57c302a"
CURRENT_HEAD_ENV = "EBU_POST_I9_CURRENT_HEAD"
POST_I9_AUTHORIZED_PATHS = (
    ".github/workflows/tests.yml",
    "tests/framework/test_validation_reachability.py",
)
STAGE_C_AUTHORITY_PATHS = (
    "FRAMEWORK_ALPHA_PACKAGING_RELEASE_CANDIDATE_AUTHORITY_AMENDMENT.md",
    "framework_alpha_packaging_release_candidate_contract.json",
    "framework_alpha_packaging_release_candidate_implementation_path_manifest.json",
    "framework_alpha_packaging_release_candidate_predecessor_manifest.json",
    "framework_alpha_packaging_release_candidate_validation_contract.json",
)
STAGE_C_MODIFIED_PATHS = (
    ".github/workflows/tests.yml",
    "build_backend/ebu_build_backend.py",
    "pyproject.toml",
    "tests/framework/test_artifact_recovery_publication.py",
    "tests/framework/test_atomic_declarations.py",
    "tests/framework/test_bridge_exact_fixtures.py",
    "tests/framework/test_capabilities.py",
    "tests/framework/test_i3_integration.py",
    "tests/framework/test_i3a_declarations.py",
    "tests/framework/test_i3b_declarations.py",
    "tests/framework/test_i3c_declarations.py",
    "tests/framework/test_i3d_declarations.py",
    "tests/framework/test_interaction_declarations.py",
    "tests/framework/test_primitives_envelopes.py",
    "tests/framework/test_validation_reachability.py",
)
STAGE_C_NEW_PATHS = (
    "LICENSE-UNICODE",
    "scripts/validate_stage_c_release_candidate.py",
    "tests/framework/installed_artifact_probe.py",
    "tests/framework/test_packaging_release_candidate.py",
)
STAGE_C_AUTHORITY_SCOPE = frozenset(
    POST_I9_AUTHORIZED_PATHS + STAGE_C_AUTHORITY_PATHS
)
STAGE_C_IMPLEMENTATION_SCOPE = frozenset(
    POST_I9_AUTHORIZED_PATHS
    + STAGE_C_AUTHORITY_PATHS
    + STAGE_C_MODIFIED_PATHS
    + STAGE_C_NEW_PATHS
)
STAGE_D_ACCEPTED_BASE_COMMIT = "fb9ae7b6dae14550a702e060600132faec539eca"
STAGE_D_ACCEPTED_BASE_TREE = "1e3f02e4efc2ce5b0ca3c15fb8a95c3df98c277d"
STAGE_D_AUTHORITY_CANDIDATE = "8936bb437426ee53556f8bcb0590215620e1065c"
STAGE_D_AUTHORITY_TARGET = "388ccb864163cddf6bd4a0a83c24f29f6535cc68"
STAGE_D_AUTHORITY_TREE = "773bd9c4cbb35ff96377b61d2f3b29171aadbc5d"
STAGE_D_AUTHORITY_PATHS = (
    "STAGE_D_SCIENTIFIC_VALIDATION_AUTHORITY.md",
    "stage_d_scientific_validation_contract.json",
    "stage_d_scientific_validation_evidence_schema.json",
    "stage_d_scientific_validation_master_matrix.json",
    "stage_d_scientific_validation_predecessor_manifest.json",
    "stage_d_scientific_validation_validation_contract.json",
)
STAGE_D_AUTHORITY_RAW_SHA256 = {
    "STAGE_D_SCIENTIFIC_VALIDATION_AUTHORITY.md": (
        "f755c38aff690fe317b29550f0f1ef7d627c75902c0f555d9f8ca594499dba16"
    ),
    "stage_d_scientific_validation_contract.json": (
        "1b12c97f51d99720979700f048ac527cb0d97c1323f051fe53e0fda3ac743089"
    ),
    "stage_d_scientific_validation_evidence_schema.json": (
        "956ff0fd38dce4cd72208dc029de15d092ea9e477151522306f9763dc3d621b3"
    ),
    "stage_d_scientific_validation_master_matrix.json": (
        "081f2e994c23051514aef19a0516d1996d9c4b86cd528dfc05bf9d17658bdb81"
    ),
    "stage_d_scientific_validation_predecessor_manifest.json": (
        "d3216726c1759ee6dad86ce8e5bba40ee9318c1e4cea52f12db0ec19b746adee"
    ),
    "stage_d_scientific_validation_validation_contract.json": (
        "2707d9d645b3fc7ecc4ee61f02d861ba88c5d220d7bf6812ab98ece93ba51227"
    ),
}
STAGE_D_AUTHORITY_CANONICAL_SHA256 = {
    "stage_d_scientific_validation_contract.json": (
        "321709990be3a270db493050fa7a4a80789c4add5ed63de50c1944d4517a30c1"
    ),
    "stage_d_scientific_validation_evidence_schema.json": (
        "527f6b65ba39b8b8e0485f30116e4f00ada6d0bd6abce207ab88d60d55ffd43e"
    ),
    "stage_d_scientific_validation_master_matrix.json": (
        "e974840f0dabc29ee0ce0841443095b2dc17014d26b6b67ea244f1299dfa9db1"
    ),
    "stage_d_scientific_validation_predecessor_manifest.json": (
        "e1b842e81f11bd10e51a5be881d607a292d2a9d63f3e4b152fbea4a4d101ba15"
    ),
    "stage_d_scientific_validation_validation_contract.json": (
        "d8bc80fecaa7ba7d3f8b687a52880dc049d182ffa8d26a246d923dbed0fafb76"
    ),
}
STAGE_D_AUTHORITY_SCOPE = STAGE_C_IMPLEMENTATION_SCOPE | frozenset(
    STAGE_D_AUTHORITY_PATHS
)
STAGE_D_CONTINUATION_ACCEPTED_BASE_COMMIT = (
    "d000015cbf3e3238e34f961c4916626c930ba90f"
)
STAGE_D_CONTINUATION_ACCEPTED_BASE_TREE = (
    "8bff192813649300a8aa8b298c441b851cea26d7"
)
STAGE_D_CONTINUATION_AUTHORITY_CANDIDATE = (
    "ce1b52b3084b84e8c8f81bc0625a05ecd15d9331"
)
STAGE_D_CONTINUATION_AUTHORITY_TARGET = (
    "4a67a7e8bf783e40b4e302bf810d2993f9fd4eee"
)
STAGE_D_CONTINUATION_AUTHORITY_TREE = (
    "da342b70b812225e570e5380c4c066a783cb5ad2"
)
STAGE_D_CONTINUATION_AUTHORITY_PATHS = (
    "STAGE_D_COMPLETION_ORIENTED_CONTINUATION_AUTHORITY_AMENDMENT.md",
    "stage_d_completion_oriented_continuation_contract.json",
    "stage_d_completion_oriented_continuation_evidence_schema.json",
    "stage_d_completion_oriented_continuation_predecessor_manifest.json",
    "stage_d_completion_oriented_continuation_validation_contract.json",
)
STAGE_D_CONTINUATION_AUTHORITY_RAW_SHA256 = {
    "STAGE_D_COMPLETION_ORIENTED_CONTINUATION_AUTHORITY_AMENDMENT.md": (
        "8e92550fd444c39516f35f1bd9d4d69f22018edc51b23b28aaf1c8e83fd98276"
    ),
    "stage_d_completion_oriented_continuation_contract.json": (
        "9c668e43e2fd06e6260296ca9608fc94ad5b6d806e317ff8f168eb0858802577"
    ),
    "stage_d_completion_oriented_continuation_evidence_schema.json": (
        "66ef7d3189e692404d0d8ef773bd15b7d70eb4172e44ca6b1b6f3a4a4da16f88"
    ),
    "stage_d_completion_oriented_continuation_predecessor_manifest.json": (
        "b49c3318e3aa2f8367b3909c0a0dfa1fa62f2a90915d5e8728f5a331dff1725c"
    ),
    "stage_d_completion_oriented_continuation_validation_contract.json": (
        "73a27fee64f0b035150a57f9eb10568ea1cfc9559c4bccbcd0ef44402735baa3"
    ),
}
STAGE_D_CONTINUATION_AUTHORITY_CANONICAL_SHA256 = {
    "stage_d_completion_oriented_continuation_contract.json": (
        "64201850cac7a4384f55511a1f21d019ad165993874d521f5f4299410bd88a59"
    ),
    "stage_d_completion_oriented_continuation_evidence_schema.json": (
        "05da12e24c7971cda7a59a05564c7d828572cd2e432e577be7fc4fdb245ec442"
    ),
    "stage_d_completion_oriented_continuation_predecessor_manifest.json": (
        "83e403f9de49e15e5c975e986243da1a30874ee76df80ac0c89051d0a9bb77a6"
    ),
    "stage_d_completion_oriented_continuation_validation_contract.json": (
        "e6933d1b05f82e70768e3ddcec51919ac573bdff24e7ad73e81f0454556f21de"
    ),
}
STAGE_D_CONTINUATION_AUTHORITY_SCOPE = STAGE_D_AUTHORITY_SCOPE | frozenset(
    STAGE_D_CONTINUATION_AUTHORITY_PATHS
)
STAGE_E_ACCEPTED_BASE_COMMIT = "d68bfb75fd822d2219c803fb3933ca60b54af4e0"
STAGE_E_ACCEPTED_BASE_TREE = "15a128783388075978f9faa716bae1c8066361c9"
STAGE_E_AUTHORITY_CANDIDATE = "0b1d58ab089d01901c9f0c384d6a7220593af0d8"
STAGE_E_AUTHORITY_TARGET = "d3a9994d93f40cd1c0a72ee9322d181f69353024"
STAGE_E_AUTHORITY_TREE = "b43b48dd2337edf4ef4494956ebfb958d3474161"
STAGE_E_AUTHORITY_CHAIN = (
    "3eda3f7be8796685c2edbd81d57df4ae40273d13",
    "d1ebf9f5e1b94fd792c869316e0bcf2fdfcbadaa",
    "d611b38c5cef347eb8ab2668ac2c23a185e956c3",
    "ab57c9d147443ba0a53dc2c6b968f1a094bcdd69",
    "1512369700e7eb1e40ecb43993cb0af78dc71d9d",
    "547c2304982bcb45d2db7e74bb5a22ad91f33943",
    STAGE_E_AUTHORITY_CANDIDATE,
)
STAGE_E_AUTHORITY_PATHS = (
    "STAGE_E_SCIENTIFIC_HARNESS_AUTHORITY.md",
    "stage_e_scientific_harness_contract.json",
    "stage_e_scientific_harness_evidence_schema.json",
    "stage_e_scientific_harness_implementation_path_manifest.json",
    "stage_e_scientific_harness_predecessor_manifest.json",
    "stage_e_scientific_harness_validation_contract.json",
)
STAGE_E_AUTHORITY_RAW_SHA256 = {
    "STAGE_E_SCIENTIFIC_HARNESS_AUTHORITY.md": (
        "997fc4d864b8c08f85adba8f4c481ed1f6eaeefe4a8c353b9df253ed221c3da8"
    ),
    "stage_e_scientific_harness_contract.json": (
        "4abbb2e79bb7261a862ec6ab08902adcd43d9a7a0b6dce9141b05f007621f989"
    ),
    "stage_e_scientific_harness_evidence_schema.json": (
        "f473e445416cfb2d5d6f596a85b90c5cd3fdc5dda06e05a2f45d095ccf114aae"
    ),
    "stage_e_scientific_harness_implementation_path_manifest.json": (
        "b2b0e9bd5473815e3222cfc2d319649562a4723430cba0943e3e970c4835bb38"
    ),
    "stage_e_scientific_harness_predecessor_manifest.json": (
        "c065a1270dd36d9e7972ec84ffae917002f9eb0765be4d9812a54876601973a7"
    ),
    "stage_e_scientific_harness_validation_contract.json": (
        "7c8017bfe3af6235654d1f1103b53c195512002f534e85e79a99d2811c4e929d"
    ),
}
STAGE_E_AUTHORITY_CANONICAL_SHA256 = {
    "stage_e_scientific_harness_contract.json": (
        "6f68868165145c4354c580ea31aa79e8c539054c96dd2558b872e07fe6048685"
    ),
    "stage_e_scientific_harness_evidence_schema.json": (
        "76bb32fe827de66c445b908990d1b2a3dba9026cc9f09c10189794125de0c0aa"
    ),
    "stage_e_scientific_harness_implementation_path_manifest.json": (
        "5a404f33fefb922eba99ab008faa51c0e5877655fa87fc3a63583878ce2db4e9"
    ),
    "stage_e_scientific_harness_predecessor_manifest.json": (
        "a54d4f56075d058a5f62931ddad68adf6d0020efcec523598c61537bbd3f0aaa"
    ),
    "stage_e_scientific_harness_validation_contract.json": (
        "dfc7a2bc807f5a014db564f408fc86fae4d06e07e8519cee18cd3e575afca71a"
    ),
}
STAGE_E_HARNESS_IMPLEMENTATION_PATHS = (
    ".github/workflows/tests.yml",
    "scripts/build_stage_e_harness_zipapp.py",
    "scripts/validate_stage_e_harness.py",
    "stage_e_harness/__init__.py",
    "stage_e_harness/__main__.py",
    "stage_e_harness/accounting.py",
    "stage_e_harness/cache.py",
    "stage_e_harness/canonical.py",
    "stage_e_harness/checkpoint.py",
    "stage_e_harness/dag.py",
    "stage_e_harness/environment.py",
    "stage_e_harness/execution.py",
    "stage_e_harness/mobius.py",
    "stage_e_harness/oracles.py",
    "stage_e_harness/records.py",
    "stage_e_harness/registry.py",
    "stage_e_harness/rng.py",
    "stage_e_harness/schema.py",
    "stage_e_harness/adapters/__init__.py",
    "stage_e_harness/adapters/base.py",
    "stage_e_harness/adapters/sd01.py",
    "stage_e_harness/adapters/sd02.py",
    "stage_e_harness/adapters/sd03.py",
    "stage_e_harness/adapters/sd04.py",
    "stage_e_harness/adapters/sd05.py",
    "stage_e_harness/adapters/sd06.py",
    "stage_e_harness/adapters/sd07.py",
    "stage_e_harness/adapters/sd08.py",
    "stage_e_harness/adapters/sd09.py",
    "stage_e_harness/adapters/sd10.py",
    "stage_e_harness/adapters/sd11.py",
    "stage_e_harness/adapters/sd12.py",
    "stage_e_harness/adapters/sd13.py",
    "stage_e_harness/adapters/sd14.py",
    "tests/stage_e/__init__.py",
    "tests/stage_e/fixtures/deterministic_empty_checkpoint.json",
    "tests/stage_e/fixtures/schema_negative_cases.json",
    "tests/stage_e/fixtures/stochastic_checkpoint.json",
    "tests/stage_e/test_adapters_and_guards.py",
    "tests/stage_e/test_authority_bindings.py",
    "tests/stage_e/test_complexity_evidence.py",
    "tests/stage_e/test_dag_cache.py",
    "tests/stage_e/test_environment_isolation.py",
    "tests/stage_e/test_identity_rng_checkpoint.py",
    "tests/stage_e/test_mobius_oracles.py",
    "tests/stage_e/test_schema_records.py",
)
STAGE_E_AUTHORITY_SCOPE = STAGE_D_CONTINUATION_AUTHORITY_SCOPE | frozenset(
    STAGE_E_AUTHORITY_PATHS
)
STAGE_E_HARNESS_IMPLEMENTATION_SCOPE = STAGE_E_AUTHORITY_SCOPE | frozenset(
    STAGE_E_HARNESS_IMPLEMENTATION_PATHS
)
STAGE_E_WORKFLOW_APPEND_BLOCK = br"""
  stage-e-scientific-harness:
    if: github.event_name == 'push' || github.event_name == 'pull_request' || github.event_name == 'workflow_dispatch'
    needs: [test, framework-t0, framework-t1, framework-t2, packaging-release-candidate]
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-python@v5
        with:
          python-version: "3.14"
      - name: Prepare frozen offline Stage E inputs
        run: |
          set -euo pipefail
          stage_root="$RUNNER_TEMP/stage-e-${GITHUB_JOB}"
          mkdir -p "$stage_root/source" "$stage_root/frontend-wheelhouse" "$stage_root/dependency-wheelhouse" "$stage_root/stage-c-evidence" "$stage_root/stage-c-work"
          cp -a "$GITHUB_WORKSPACE/." "$stage_root/source/"
          python -m pip download --only-binary=:all: --no-deps --dest "$stage_root/frontend-wheelhouse" build==1.5.0 packaging==26.3 pyproject_hooks==1.2.0 pip==26.2.1
          python -m pip download --only-binary=:all: --require-hashes --dest "$stage_root/dependency-wheelhouse" -r requirements-framework.lock
          find "$stage_root/source" -type f -exec chmod a-w {} +
          find "$stage_root/source" -type d -exec chmod a-w {} +
          docker pull "$EBU_STAGE_C_IMAGE"
      - name: Run complete outcome-blind Stage E validation
        run: |
          set -euo pipefail
          stage_root="$RUNNER_TEMP/stage-e-${GITHUB_JOB}"
          head_tree="$(git -C "$stage_root/source" rev-parse "${GITHUB_SHA}^{tree}")"
          container=(docker run --rm --network none --read-only --platform linux/amd64 --user "$(id -u):$(id -g)" --tmpfs /tmp:rw,nosuid,nodev,exec,mode=1777 --tmpfs /private/tmp:rw,nosuid,nodev,exec,mode=1777 -e "EBU_STAGE_C_IMAGE_DIGEST=$EBU_STAGE_C_IMAGE_DIGEST" -v "$stage_root:/stage-e" -v "$stage_root/source:/stage-e/source:ro" "$EBU_STAGE_C_IMAGE")
          "${container[@]}" python -I /stage-e/source/scripts/validate_stage_c_release_candidate.py static-authority --source /stage-e/source --evidence /stage-e/stage-c-evidence
          "${container[@]}" python -I /stage-e/source/scripts/validate_stage_c_release_candidate.py packaging --source /stage-e/source --wheelhouse /stage-e/frontend-wheelhouse --work /stage-e/stage-c-work --evidence /stage-e/stage-c-evidence
          "${container[@]}" python -I -c 'import sys,unittest; sys.path.insert(0,"/stage-e/source"); suite=unittest.defaultTestLoader.discover("/stage-e/source/tests/stage_e",top_level_dir="/stage-e/source"); result=unittest.TextTestRunner(verbosity=2).run(suite); raise SystemExit(0 if result.wasSuccessful() else 1)'
          "${container[@]}" python -I /stage-e/source/scripts/validate_stage_e_harness.py \
            --source /stage-e/source \
            --output /stage-e/stage-e-evidence \
            --work /stage-e/harness-work \
            --head-commit "$GITHUB_SHA" \
            --head-tree "$head_tree" \
            --direct-wheel /stage-e/stage-c-work/artifacts/direct/ebu_framework-0.1.0a1-cp314-none-any.whl \
            --sdist-wheel /stage-e/stage-c-work/artifacts/sdist-wheel/ebu_framework-0.1.0a1-cp314-none-any.whl \
            --sdist /stage-e/stage-c-work/artifacts/sdist/ebu_framework-0.1.0a1.tar.gz \
            --direct-python /stage-e/stage-c-work/direct-env/bin/python \
            --sdist-python /stage-e/stage-c-work/sdist-env/bin/python \
            --debian-identity libsqlite3-0:amd64=3.46.1-7+deb13u1 \
            --image-digest "$EBU_STAGE_C_IMAGE_DIGEST"
      - name: Retain private Stage E harness evidence
        uses: actions/upload-artifact@v4
        with:
          name: stage-e-scientific-harness-${{ github.sha }}
          path: |
            ${{ runner.temp }}/stage-e-stage-e-scientific-harness/stage-e-evidence
            ${{ runner.temp }}/stage-e-stage-e-scientific-harness/harness-work/stage-e-harness-*.pyz
          if-no-files-found: error
          retention-days: 30
"""
CLCD_AUTHORIZED_PREDECESSOR_MODIFICATIONS = (
    "src/ebu_framework/__init__.py",
    "src/ebu_framework/errors.py",
)
LATER_DOCUMENTATION_PATHS = (
    "COUPLED_INTERACTION_INFERENCE_FEEDBACK_STABILITY_PROGRAMME_REVIEW.md",
    "EBU_FUTURE_BOOKS_STRUCTURE.md",
    "coupled_interaction_inference_feedback_book_traceability_manifest.json",
)
TEST_SELF_SEAL = "5a0a4fc4d43bb6473e151286d76104bc21513e162d323e6348884b79da48d5d9"
WORKFLOW_ROUTING_BLOCK = b"""    env:
      EBU_I9_AUTHORITY_BASE: 4ab6f9ca32e32a3801c6a4b6872b34b206e6da7e
      EBU_I9_AUTHORITY_CANDIDATE: 15c721cf745d79fabeda749badbac35a7fda9993
      EBU_I9_AUTHORITY_TARGET: 2e7848dc495c4b2d5fb2ea09d668f2b240d3ec02
      EBU_I9_IMPLEMENTATION_CANDIDATE: f8623fe5f0d313e16558eb9a4c985940e6baf9dd
      EBU_I9_IMPLEMENTATION_TARGET: ffc910329957f61deaa7e9fc09ba77a0e3f51381
      EBU_I9_LATER_DOCUMENTATION_FEATURE: 5674ea9c33b72b94669c86e7e4f1a35c0db5775a
      EBU_I9_REQUIRED_CURRENT_TARGET: fc20d71e69cf226e6cecd9de7575f1d6249b193f
      EBU_POST_I9_CURRENT_HEAD: ${{ github.sha }}
"""
WORKFLOW_T1_COMPATIBILITY_BLOCK = b"""      - name: Provide the historical cross-platform temporary directory
        run: |
          if [ ! -d /private/tmp ]; then
            sudo install -d -m 1777 /private/tmp
          fi
          test -d /private/tmp
          test -w /private/tmp
"""
WORKFLOW_T1_RUNNER_BLOCK = b"""  framework-t1:
    if: github.event_name == 'push' || github.event_name == 'pull_request'
    runs-on: ubuntu-26.04
"""
WORKFLOW_T1_HISTORICAL_RUNNER_BLOCK = b"""  framework-t1:
    if: github.event_name == 'push' || github.event_name == 'pull_request'
    runs-on: ubuntu-latest
"""
WORKFLOW_CLCD_T0_BLOCK = b"""      - name: Run current-head CLCD diagnostics with a positive test-count gate
        run: |
          export PYTHONPATH="$PWD/src:$PWD/tests/framework"
          python - <<'PY'
          import unittest

          suite = unittest.TestLoader().discover(
              "tests/framework", "test_closed_loop_correction_diagnostics.py"
          )
          count = suite.countTestCases()
          if count <= 0:
              raise SystemExit("T0 CLCD current-head test count must be positive")
          result = unittest.TextTestRunner(verbosity=2).run(suite)
          if (
              not result.wasSuccessful()
              or result.testsRun != count
              or result.skipped
              or result.expectedFailures
              or result.unexpectedSuccesses
          ):
              raise SystemExit(1)
          print(f"T0_CLCD_CURRENT_HEAD_TESTS={count}")
          PY
"""
EXPECTED_NEGATIVE = {
    "APPEND_UTF8_BYTES": "FAIL_UNAUTHORIZED_I9_IMPLEMENTATION_PATH_DRIFT",
    "APPEND_ROOT_EXPORT": "FAIL_ROOT_EXPORT_DRIFT",
    "APPEND_FAILURE_CODE": "FAIL_FAILURE_CODE_DRIFT",
    "REPLACE_PUBLIC_SIGNATURE": "FAIL_PUBLIC_SIGNATURE_DRIFT",
    "APPEND_HASH_DOMAIN": "FAIL_HASH_DOMAIN_DRIFT",
    "REPLACE_PRIVATE_VALIDATOR_SIGNATURE": "FAIL_VALIDATOR_DRIFT",
    "REPLACE_PRIVATE_CONSTANT": "FAIL_CONSTANT_DRIFT",
    "APPEND_DIRECT_EDGE": "FAIL_GRAPH_DRIFT",
    "ADD_CYCLE": "FAIL_GRAPH_CYCLE",
    "FILTER_ONE_VECTOR": "FAIL_VECTOR_DRIFT",
    "DECREMENT_COMPLETED_CHECK_COUNT": "FAIL_COUNT_DRIFT",
    "REPLACE_PROJECTION_SHA256": "FAIL_PROJECTION_DRIFT",
    "RELABEL_CURRENT_BOOK_LOCK_AS_HISTORICAL": "FAIL_STALE_LOCK_RELABEL",
    "USE_CURRENT_HEAD_FOR_HISTORICAL_LANE": "FAIL_CURRENT_SUBSTITUTED_FOR_HISTORY",
    "USE_I9_TARGET_FOR_CURRENT_LANE": "FAIL_HISTORY_SUBSTITUTED_FOR_CURRENT",
    "DROP_PUSH_TRIGGER": "FAIL_PUSH_TRIGGER_LOSS",
    "DROP_PULL_REQUEST_TRIGGER": "FAIL_PULL_REQUEST_TRIGGER_LOSS",
    "DROP_T0_JOB_OR_PATH": "FAIL_T0_LOSS",
    "DROP_T1_JOB_OR_PATH": "FAIL_T1_LOSS",
    "DROP_MANUAL_T2": "FAIL_T2_LOSS",
    "MAKE_T2_AUTOMATIC": "FAIL_T2_GATE_BROADENING",
    "ADD_T3_JOB_OR_PATH": "FAIL_T3_INTRODUCTION",
    "FILTER_TEST_OR_VECTOR": "FAIL_FILTERING",
    "ACCEPT_SKIPPED_TEST": "FAIL_SKIP_MASKING",
    "ACCEPT_EXPECTED_FAILURE": "FAIL_EXPECTED_FAILURE_MASKING",
    "SUBSTITUTE_REPRESENTATIVE_INTERFACE": "FAIL_REPRESENTATIVE_SUBSTITUTION",
    "READ_CURRENT_FILES_AS_HISTORICAL_LOCKS": "FAIL_CURRENT_FILES_AS_HISTORY",
    "MODIFY_UNAUTHORIZED_SOURCE_PATH": "FAIL_CURRENT_SOURCE_DRIFT",
    "ADD_LATER_DOC_TO_I9_FOUR_PATH_DELTA": "FAIL_HISTORICAL_DELTA_BROADENING",
    "ADD_PRODUCTION_MODULE_PATH": "FAIL_SCOPE_BROADENING",
    "MODIFY_DEPENDENCY_OR_FIXTURE": "FAIL_DEPENDENCY_OR_FIXTURE_DRIFT",
    "MUTATE_SOURCE_LOCK_RAW_IDENTITY": "FAIL_SOURCE_LOCK_DRIFT",
    "DISAGREE_TREE_AND_ARCHIVE_ROUTES": "FAIL_GIT_ROUTE_DISAGREEMENT",
    "RELABEL_AUTHORITY_COORDINATE": "FAIL_COORDINATE_RELABEL",
    "ACCEPT_ZERO_COMPLETED_CHECKS": "FAIL_ZERO_CHECK_ACCEPTANCE",
    "MODIFY_NONFRAMEWORK_TEST_JOB": "FAIL_SCIENTIFIC_SEMANTICS_CHANGE",
    "ADD_MODEL_POLICY_STATE_RUNNER_OR_NETWORK_ENTRY": "FAIL_FORBIDDEN_REACHABILITY",
    "DELETE_RENAME_OR_MODE_CHANGE_AUTHORIZED_PATH": "FAIL_PATH_CONSTRUCTION",
}


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_json_lf(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def _independent_canonical_json_lf(value: object) -> bytes:
    if value is None:
        encoded = "null"
    elif value is True:
        encoded = "true"
    elif value is False:
        encoded = "false"
    elif type(value) is int:
        encoded = str(value)
    elif type(value) is str:
        encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    elif type(value) is list:
        encoded = "[" + ",".join(
            _independent_canonical_json_lf(item).decode("utf-8")[:-1]
            for item in value
        ) + "]"
    elif type(value) is dict:
        encoded = "{" + ",".join(
            json.dumps(key, ensure_ascii=False)
            + ":"
            + _independent_canonical_json_lf(value[key]).decode("utf-8")[:-1]
            for key in sorted(value)
        ) + "}"
    else:
        raise TypeError(f"unsupported authority JSON value: {type(value).__name__}")
    return (encoded + "\n").encode("utf-8")


def _strict_json_bytes(raw: bytes, label: str) -> object:
    if raw.startswith(b"\xef\xbb\xbf") or not raw.endswith(b"\n") or b"\r" in raw:
        raise AssertionError(f"invalid authority JSON text encoding: {label}")

    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def reject_float(value):
        raise ValueError(f"floating JSON number: {value}")

    def reject_constant(value):
        raise ValueError(f"non-finite JSON number: {value}")

    document = json.loads(
        raw.decode("utf-8", "strict"),
        object_pairs_hook=unique_pairs,
        parse_float=reject_float,
        parse_constant=reject_constant,
    )
    if type(document) is not dict:
        raise AssertionError(f"authority JSON top level is not an object: {label}")
    if _canonical_json_lf(document) != raw:
        raise AssertionError(f"authority JSON is not canonical: {label}")
    if _independent_canonical_json_lf(document) != raw:
        raise AssertionError(f"independent authority encoding differs: {label}")
    return document


def _strict_json(path: Path) -> tuple[object, bytes]:
    raw = path.read_bytes()
    document = _strict_json_bytes(raw, str(path))
    return document, raw


def _strict_stage_d_json_bytes(raw: bytes, label: str) -> object:
    if raw.startswith(b"\xef\xbb\xbf") or not raw.endswith(b"\n") or b"\r" in raw:
        raise AssertionError(f"invalid Stage D authority JSON text encoding: {label}")

    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate Stage D JSON key: {key}")
            result[key] = value
        return result

    def reject_float(value):
        raise ValueError(f"floating Stage D JSON number: {value}")

    def reject_constant(value):
        raise ValueError(f"non-finite Stage D JSON number: {value}")

    document = json.loads(
        raw.decode("utf-8", "strict"),
        object_pairs_hook=unique_pairs,
        parse_float=reject_float,
        parse_constant=reject_constant,
    )
    if type(document) is not dict:
        raise AssertionError(f"Stage D authority JSON top level is not an object: {label}")
    return document


def _git(*args: str) -> bytes:
    allowed = (
        args[:2] == ("rev-parse", "--verify")
        or args[:1] == ("rev-parse",)
        or args[:4] == ("ls-tree", "-rz", "-r", "--full-tree")
        or args[:2] == ("cat-file", "blob")
        or args[:2] == ("archive", "--format=tar")
        or args
        == (
            "merge-base",
            STAGE_E_ACCEPTED_BASE_COMMIT,
            STAGE_E_AUTHORITY_CANDIDATE,
        )
        or args
        == (
            "rev-list",
            "--reverse",
            "--parents",
            f"{STAGE_E_ACCEPTED_BASE_COMMIT}..{STAGE_E_AUTHORITY_CANDIDATE}",
        )
        or args
        == (
            "show",
            f"{STAGE_C_PREDECESSOR_COMMIT}:.github/workflows/tests.yml",
        )
    )
    if not allowed:
        raise AssertionError(f"forbidden Git-object command: {args!r}")
    completed = subprocess.run(
        ("git", "-C", str(ROOT), *args),
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", "replace").strip()
        raise AssertionError(f"required immutable Git object is unavailable: {args!r}: {detail}")
    return completed.stdout


def _routed_coordinates(contract: dict[str, object]) -> dict[str, dict[str, str]]:
    authority_chain = contract["coordinate_chain"]
    if authority_chain != COORDINATE_CHAIN:
        raise AssertionError("correction coordinate chain differs from the frozen chain")
    routed = copy.deepcopy(COORDINATE_CHAIN)
    for name, variable in COORDINATE_ENV.items():
        supplied = os.environ.get(variable)
        if supplied is not None and supplied != routed[name]["commit"]:
            raise AssertionError(f"routed historical coordinate differs: {variable}")
    return routed


def _tree_entries(commit: str) -> dict[str, dict[str, object]]:
    raw = _git("ls-tree", "-rz", "-r", "--full-tree", commit)
    entries = {}
    for record in raw.split(b"\0"):
        if not record:
            continue
        metadata, separator, encoded_path = record.partition(b"\t")
        if not separator:
            raise AssertionError("malformed immutable ls-tree record")
        mode, object_type, git_object = metadata.decode("ascii", "strict").split()
        path = encoded_path.decode("utf-8", "strict")
        if path in entries:
            raise AssertionError(f"duplicate immutable tree path: {path}")
        entries[path] = {
            "mode": mode,
            "object_type": object_type,
            "git_object": git_object,
        }
    return entries


def _archive_members(commit: str) -> dict[str, bytes]:
    raw = _git("archive", "--format=tar", commit)
    members = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:") as archive:
        for member in archive.getmembers():
            if not member.isfile():
                continue
            extracted = archive.extractfile(member)
            if extracted is None:
                raise AssertionError(f"immutable archive member is unreadable: {member.name}")
            if member.name in members:
                raise AssertionError(f"duplicate immutable archive path: {member.name}")
            members[member.name] = extracted.read()
    return members


def _object_row(
    path: str,
    entries: dict[str, dict[str, object]],
    archive: dict[str, bytes],
) -> tuple[dict[str, object], bytes]:
    if path not in entries or path not in archive:
        raise AssertionError(f"required immutable path is absent: {path}")
    entry = entries[path]
    if entry["object_type"] != "blob":
        raise AssertionError(f"required immutable path is not a blob: {path}")
    git_object = entry["git_object"]
    if not isinstance(git_object, str) or re.fullmatch(r"[0-9a-f]{40}", git_object) is None:
        raise AssertionError(f"invalid immutable blob identity: {path}")
    tree_raw = _git("cat-file", "blob", git_object)
    archive_raw = archive[path]
    if tree_raw != archive_raw:
        raise AssertionError(f"immutable tree/archive routes disagree: {path}")
    return (
        {
            "byte_count": len(tree_raw),
            "git_object": git_object,
            "mode": entry["mode"],
            "object_type": entry["object_type"],
            "path": path,
            "raw_sha256": _sha256(tree_raw),
        },
        tree_raw,
    )


def _normalized_test_bytes(raw: bytes) -> bytes:
    pattern = re.compile(
        rb'TEST_SELF_SEAL = "[0-9a-f]{64}"'
    )
    normalized, count = pattern.subn(
        b'TEST_SELF_SEAL = "' + (b"0" * 64) + b'"', raw, count=1
    )
    if count != 1:
        raise AssertionError("test self-seal marker is absent or ambiguous")
    return normalized


def _workflow_without_routing(raw: bytes) -> bytes:
    if raw.count(WORKFLOW_ROUTING_BLOCK) != 1:
        raise AssertionError("workflow historical/current routing block differs")
    if raw.count(WORKFLOW_T1_COMPATIBILITY_BLOCK) != 1:
        raise AssertionError("workflow T1 compatibility block differs")
    if raw.count(WORKFLOW_T1_RUNNER_BLOCK) != 1:
        raise AssertionError("workflow T1 runner block differs")
    if raw.count(WORKFLOW_CLCD_T0_BLOCK) != 1:
        raise AssertionError("workflow CLCD T0 block differs")
    return (
        raw.replace(
            WORKFLOW_T1_RUNNER_BLOCK, WORKFLOW_T1_HISTORICAL_RUNNER_BLOCK, 1
        )
        .replace(WORKFLOW_ROUTING_BLOCK, b"", 1)
        .replace(WORKFLOW_T1_COMPATIBILITY_BLOCK, b"", 1)
        .replace(WORKFLOW_CLCD_T0_BLOCK, b"", 1)
    )


def _literal_assignments(tree: ast.Module) -> dict[str, object]:
    assignments = {}
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
        ):
            try:
                assignments[node.targets[0].id] = ast.literal_eval(node.value)
            except (TypeError, ValueError):
                continue
    return assignments


def _signature(node: ast.FunctionDef) -> str:
    def argument(value: ast.arg) -> str:
        result = value.arg
        if value.annotation is not None:
            result += ": " + ast.unparse(value.annotation)
        return result

    parts = []
    positional = node.args.posonlyargs + node.args.args
    defaults = [None] * (len(positional) - len(node.args.defaults)) + list(
        node.args.defaults
    )
    for index, (value, default) in enumerate(zip(positional, defaults)):
        rendered = argument(value)
        if default is not None:
            rendered += "=" + ast.unparse(default)
        parts.append(rendered)
        if node.args.posonlyargs and index + 1 == len(node.args.posonlyargs):
            parts.append("/")
    if node.args.vararg is not None:
        parts.append("*" + argument(node.args.vararg))
    elif node.args.kwonlyargs:
        parts.append("*")
    for value, default in zip(node.args.kwonlyargs, node.args.kw_defaults):
        rendered = argument(value)
        if default is not None:
            rendered += "=" + ast.unparse(default)
        parts.append(rendered)
    if node.args.kwarg is not None:
        parts.append("**" + argument(node.args.kwarg))
    result = "(" + ", ".join(parts) + ")"
    if node.returns is not None:
        result += " -> " + ast.unparse(node.returns)
    return result


def _module_exports(tree: ast.Module) -> tuple[str, ...]:
    exports: tuple[str, ...] = ()
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "__all__"
        ):
            exports = ast.literal_eval(node.value)
        elif (
            isinstance(node, ast.AugAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == "__all__"
            and isinstance(node.op, ast.Add)
        ):
            exports += ast.literal_eval(node.value)
    return exports


def _direct_imports(tree: ast.Module, package_modules: tuple[str, ...]) -> tuple[str, ...]:
    result = []
    for node in tree.body:
        if not isinstance(node, ast.ImportFrom) or node.level != 1:
            continue
        names = (
            (node.module.split(".", 1)[0],)
            if node.module is not None
            else tuple(alias.name.split(".", 1)[0] for alias in node.names)
        )
        for name in names:
            if name in package_modules and name not in result:
                result.append(name)
    return tuple(result)


def _base_candidate_projection(path: str, raw: bytes) -> bytes:
    if path == "tests/framework/safety.py":
        prefix, separator, _ = raw.partition(b"\n\n_I9_FORBIDDEN_T3_INTERFACES = (")
        if not separator:
            raise AssertionError("I-9 safety append marker is absent")
        return prefix
    if path == ".github/workflows/tests.yml":
        prefix, separator, _ = raw.partition(b"\n\n  framework-t0:\n")
        if not separator:
            raise AssertionError("I-9 workflow append marker is absent")
        restored = (prefix + b"\n").replace(b"  workflow_dispatch:\n", b"", 1)
        if b"workflow_dispatch" in restored:
            raise AssertionError("workflow dispatch restoration was ambiguous")
        return restored
    return raw


def _base_candidate_bytes(path: str) -> bytes:
    return _base_candidate_projection(path, (ROOT / path).read_bytes())


def _blob_id(raw: bytes) -> str:
    framed = b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
    return hashlib.sha1(framed).hexdigest()


def _assert_projection(value: object, identity: dict[str, object]) -> None:
    encoded = _canonical_json_lf(value)
    if len(encoded) != identity["byte_count"]:
        raise AssertionError("canonical projection byte count differs")
    if _sha256(encoded) != identity["sha256"]:
        raise AssertionError("canonical projection hash differs")


def _table_rows(path: Path) -> tuple[tuple[str, ...], ...]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not (stripped.startswith("|") and stripped.endswith("|")):
            continue
        cells = tuple(cell.strip() for cell in stripped[1:-1].split("|"))
        if cells and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        rows.append(cells)
    return tuple(rows)


def _assert_ordered_table_rows(path: Path, expected: list[list[str]]) -> None:
    actual = _table_rows(path)
    cursor = 0
    for row in expected:
        wanted = tuple(row)
        while cursor < len(actual) and actual[cursor] != wanted:
            cursor += 1
        if cursor == len(actual):
            raise AssertionError(f"authority table row is absent from {path.name}: {wanted[0]}")
        cursor += 1


def _apply_mutations(baseline: dict[str, object], mutations: list[dict[str, object]]):
    materialized = copy.deepcopy(baseline)
    for mutation in mutations:
        operation = mutation["op"]
        path = mutation["path"]
        if type(path) is not list or not path:
            raise AssertionError("mutation path is not a nonempty JSON array")
        if operation == "APPEND":
            target = materialized
            for component in path:
                target = target[component]
            if type(target) is not list:
                raise AssertionError("APPEND target is not an exact list")
            target.append(copy.deepcopy(mutation["value"]))
            continue
        parent = materialized
        for component in path[:-1]:
            parent = parent[component]
        leaf = path[-1]
        if operation == "REPLACE":
            parent[leaf] = copy.deepcopy(mutation["value"])
        elif operation == "DELETE":
            del parent[leaf]
        else:
            raise AssertionError(f"unknown mutation operation: {operation}")
    return materialized


def _recursive_tuple(value: object) -> object:
    if type(value) is list:
        return tuple(_recursive_tuple(item) for item in value)
    return value


def _derive_i9_failure_id(code: str, owner: str, ordinal: int) -> str:
    def frame(value: str) -> bytes:
        encoded = value.encode("utf-8", "strict")
        return len(encoded).to_bytes(8, "big") + encoded

    preimage = b"".join(
        (
            frame("ebu.failure-id.v1"),
            frame(code),
            frame("I-9"),
            frame("APPLICABLE"),
            frame("ebu_framework.validation"),
            frame(owner),
            frame("1.0.0"),
            (0).to_bytes(8, "big"),
            frame("NOT_APPLICABLE"),
            frame(str(ordinal)),
        )
    )
    return "ebu:failure:core:sha256-" + hashlib.sha256(preimage).hexdigest()


class ValidationReachabilityTests(unittest.TestCase):
    def test_historical_i9_reconstruction(self) -> None:
        historical = self._historical_reconstruction()
        inventory = historical["validation_contract"]["inventory"]
        self.assertEqual(inventory["vector_count"], 97)
        self.assertEqual(inventory["completed_check_count_total"], 292)
        self.assertEqual(len(historical["source_lock_rows"]), 73)
        self.assertEqual(tuple(historical["implementation_rows"]), IMPLEMENTATION_PATHS)
        print(
            "POST_I9_HISTORICAL_LANE=PASS SOURCE_LOCKS=73 "
            "I9_IMPLEMENTATION_PATHS=4 GIT_ROUTES=2"
        )

    def test_current_head_durability(self) -> None:
        historical = self._historical_reconstruction()
        current = self._static_audit(historical)
        validation_contract = historical["validation_contract"]
        self._dynamic_replay(validation_contract)
        inventory = validation_contract["inventory"]
        self.assertEqual(current["actual_head"], _git("rev-parse", "--verify", "HEAD^{commit}").decode().strip())
        print(
            "POST_I9_CURRENT_HEAD_LANE=PASS I9_AUTHORITY_VECTORS=97 "
            "DYNAMIC=69 STATIC=28 CHECKS=292 ACTIVE_PREDICATES=50"
        )

    def test_post_i9_authority_cases(self) -> None:
        correction = self._load_correction_authority()
        historical = self._historical_reconstruction(correction)
        current = self._static_audit(historical, correction)
        baseline = self._case_baseline(correction, historical, current)
        rows = correction["validation"]["case_inventory"]["rows"]
        self.assertEqual(len(rows), 44)
        self.assertEqual(
            tuple(row["case_id"] for row in rows),
            tuple(f"P9C-{index:03d}" for index in range(1, 45)),
        )
        for row in rows:
            with self.subTest(case_id=row["case_id"]):
                operation = row["mutation"]["op"]
                if row["classification"] == "POSITIVE":
                    self.assertEqual(operation, "NONE")
                    if row["case_id"] == "P9C-001":
                        self.assertTrue(historical["passed"])
                    elif row["case_id"] == "P9C-002":
                        self.assertTrue(historical["passed"])
                        self.assertEqual(self._evaluate_case(baseline), "PASS")
                    elif row["case_id"] == "P9C-003":
                        self._audit_documentation_feature(correction, historical)
                    else:
                        self.fail(f"unknown positive authority case: {row['case_id']}")
                    self.assertEqual(row["expected"], "PASS")
                    continue
                mutated = copy.deepcopy(baseline)
                self._apply_authority_case_mutation(mutated, row)
                self.assertEqual(self._evaluate_case(mutated), row["expected"])
        print("POST_I9_AUTHORITY_CASES=44 POSITIVE=3 NEGATIVE=41 EXACT_FALSIFIERS=41")

    def _load_correction_authority(self) -> dict[str, object]:
        raw_files = {}
        for path in CORRECTION_AUTHORITY_FILES:
            raw = (ROOT / path).read_bytes()
            self.assertEqual(_sha256(raw), CORRECTION_AUTHORITY_RAW_SHA256[path], path)
            raw_files[path] = raw
        documents = {
            path: _strict_json_bytes(raw_files[path], path)
            for path in CORRECTION_AUTHORITY_FILES[1:]
        }
        correction = {
            "contract": documents[CORRECTION_AUTHORITY_FILES[1]],
            "validation": documents[CORRECTION_AUTHORITY_FILES[2]],
            "predecessor": documents[CORRECTION_AUTHORITY_FILES[3]],
            "manifest": documents[CORRECTION_AUTHORITY_FILES[4]],
            "raw_files": raw_files,
        }
        self._audit_correction_agreement(correction)
        return correction

    def _audit_correction_agreement(self, correction: dict[str, object]) -> None:
        contract = correction["contract"]
        validation = correction["validation"]
        predecessor = correction["predecessor"]
        manifest = correction["manifest"]
        self.assertEqual(contract["coordinate_chain"], COORDINATE_CHAIN)
        self.assertEqual(
            validation["historical_reconstruction_contract"]["accepted_coordinate_chain"],
            COORDINATE_CHAIN,
        )
        self.assertEqual(
            contract["accepted_i9_frozen_inventory"],
            validation["accepted_i9_frozen_inventory"],
        )
        self.assertEqual(contract["workflow_contract"], validation["workflow_contract"])
        self.assertEqual(
            manifest["workflow_delta_contract"]["preserve_test_path_inventory"],
            contract["workflow_contract"],
        )
        self.assertEqual(
            tuple(contract["future_implementation_boundary"]["modified_paths"]),
            POST_I9_AUTHORIZED_PATHS,
        )
        self.assertEqual(
            tuple(row["path"] for row in manifest["authorized_inventory"]["rows"]),
            POST_I9_AUTHORIZED_PATHS,
        )
        self.assertEqual(predecessor["tree_inventory"]["row_count"], 330)
        self.assertEqual(len(predecessor["rows"]), 330)
        self.assertEqual(validation["case_inventory"]["case_count"], 44)
        self.assertEqual(validation["case_inventory"]["classification_counts"], {"NEGATIVE": 41, "POSITIVE": 3})
        self.assertEqual(
            set(validation["mutation_language"]["closed_operations"]),
            set(EXPECTED_NEGATIVE) | {"NONE"},
        )
        _assert_projection(
            validation["case_inventory"]["rows"],
            validation["case_inventory"]["projection"],
        )
        _assert_projection(
            [
                [row[field] for field in predecessor["row_schema"]]
                for row in predecessor["rows"]
            ],
            predecessor["tree_inventory"]["row_projection"],
        )

    def _historical_reconstruction(
        self, correction: dict[str, object] | None = None
    ) -> dict[str, object]:
        if correction is None:
            correction = self._load_correction_authority()
        coordinates = _routed_coordinates(correction["contract"])
        for name, coordinate in coordinates.items():
            actual_commit = _git(
                "rev-parse", "--verify", f"{coordinate['commit']}^{{commit}}"
            ).decode("ascii").strip()
            actual_tree = _git("rev-parse", f"{coordinate['commit']}^{{tree}}").decode("ascii").strip()
            self.assertEqual(actual_commit, coordinate["commit"], name)
            self.assertEqual(actual_tree, coordinate["tree"], name)

        routed_commits = {
            name: (
                _tree_entries(coordinates[name]["commit"]),
                _archive_members(coordinates[name]["commit"]),
            )
            for name in (
                "accepted_i9_authority_base",
                "accepted_i9_authority_target",
                "accepted_i9_implementation_candidate",
                "accepted_i9_implementation_target",
            )
        }
        authority_entries, authority_archive = routed_commits["accepted_i9_authority_target"]
        authority_rows = correction["validation"]["historical_reconstruction_contract"]["authority_file_rows"]
        authority_raw = {}
        for expected in authority_rows:
            actual, raw = _object_row(expected["path"], authority_entries, authority_archive)
            self.assertEqual(actual, expected, expected["path"])
            authority_raw[expected["path"]] = raw
        historical_documents = {
            path: _strict_json_bytes(authority_raw[path], f"immutable I-9 authority:{path}")
            for path in AUTHORITY_FILES
        }
        contract = historical_documents[AUTHORITY_FILES[0]]
        validation_contract = historical_documents[AUTHORITY_FILES[1]]
        predecessor = historical_documents[AUTHORITY_FILES[2]]
        manifest = historical_documents[AUTHORITY_FILES[3]]

        expected_locks = correction["contract"]["accepted_i9_frozen_inventory"]["source_locks"]["rows"]
        self.assertEqual(contract["governing_source_chain"]["locks"], expected_locks)
        base_entries, base_archive = routed_commits["accepted_i9_authority_base"]
        source_lock_rows = {}
        for expected in expected_locks:
            actual, _ = _object_row(expected["path"], base_entries, base_archive)
            comparable = {key: actual[key] for key in expected}
            self.assertEqual(comparable, expected, expected["path"])
            source_lock_rows[expected["path"]] = comparable
        projected_locks = list(expected_locks)
        _assert_projection(
            projected_locks,
            correction["contract"]["accepted_i9_frozen_inventory"]["source_locks"]["projection"],
        )

        target_entries = authority_entries
        candidate_entries, candidate_archive = routed_commits["accepted_i9_implementation_candidate"]
        implementation_target_entries, implementation_target_archive = routed_commits[
            "accepted_i9_implementation_target"
        ]
        changed = tuple(
            sorted(
                path
                for path in set(target_entries) | set(candidate_entries)
                if target_entries.get(path) != candidate_entries.get(path)
            )
        )
        self.assertEqual(changed, tuple(sorted(IMPLEMENTATION_PATHS)))
        expected_implementation = {
            row["path"]: row
            for row in correction["validation"]["historical_reconstruction_contract"]["implementation_path_rows"]
        }
        implementation_rows = {}
        implementation_raw = {}
        for path in IMPLEMENTATION_PATHS:
            candidate_row, candidate_raw = _object_row(path, candidate_entries, candidate_archive)
            target_row, target_raw = _object_row(
                path, implementation_target_entries, implementation_target_archive
            )
            self.assertEqual(candidate_row, expected_implementation[path], path)
            self.assertEqual(target_row, expected_implementation[path], path)
            self.assertEqual(candidate_raw, target_raw, path)
            implementation_rows[path] = candidate_row
            implementation_raw[path] = candidate_raw
        self.assertEqual(manifest["future_root_export_suffix"], [])
        self.assertEqual(manifest["future_failure_suffix"], [])
        self.assertEqual(manifest["future_public_signature_rows"], [])

        inventory = validation_contract["inventory"]
        self.assertEqual(inventory["vector_count"], 97)
        self.assertEqual(inventory["dynamic_vector_count"], 69)
        self.assertEqual(inventory["static_witness_count"], 28)
        self.assertEqual(inventory["completed_check_count_total"], 292)
        self.assertEqual(inventory["active_predicate_count_total"], 50)
        self.assertEqual(
            inventory["outcome_counts"],
            {"FAILURE": 50, "STATIC_PASS": 28, "SUCCESS": 19},
        )
        self.assertEqual(len(validation_contract["vectors"]), 97)
        _assert_projection(
            validation_contract["vectors"], validation_contract["projections"]["all_vectors"]
        )
        historical_book = source_lock_rows["EBU_FUTURE_BOOKS_STRUCTURE.md"]
        self.assertEqual(historical_book["byte_count"], 132360)
        self.assertEqual(historical_book["git_object"], "654145ef732814047a0e5a45bdd0edb732104390")
        return {
            "passed": True,
            "coordinates": coordinates,
            "contract": contract,
            "validation_contract": validation_contract,
            "predecessor": predecessor,
            "manifest": manifest,
            "authority_raw": authority_raw,
            "source_lock_rows": source_lock_rows,
            "implementation_rows": implementation_rows,
            "implementation_raw": implementation_raw,
            "historical_book": historical_book,
            "route_identity": _sha256(
                _canonical_json_lf(
                    [source_lock_rows[path] for path in source_lock_rows]
                )
            ),
        }

    def _audit_documentation_feature(
        self, correction: dict[str, object], historical: dict[str, object]
    ) -> None:
        feature = COORDINATE_CHAIN["accepted_later_documentation_feature"]
        entries = _tree_entries(feature["commit"])
        archive = _archive_members(feature["commit"])
        self.assertEqual(
            _git("rev-parse", f"{feature['commit']}^{{tree}}").decode().strip(),
            feature["tree"],
        )
        i9_entries = _tree_entries(COORDINATE_CHAIN["accepted_i9_implementation_target"]["commit"])
        changed = tuple(
            sorted(
                path
                for path in set(i9_entries) | set(entries)
                if i9_entries.get(path) != entries.get(path)
            )
        )
        self.assertEqual(changed, tuple(sorted(LATER_DOCUMENTATION_PATHS)))
        expected_docs = {
            row["path"]: row for row in correction["contract"]["later_documentation_delta"]["rows"]
        }
        for path in LATER_DOCUMENTATION_PATHS:
            row, _ = _object_row(path, entries, archive)
            row["change_from_i9_target"] = "MODIFY" if path in i9_entries else "ADD"
            self.assertEqual(row, expected_docs[path], path)
        for path in IMPLEMENTATION_PATHS:
            row, _ = _object_row(path, entries, archive)
            self.assertEqual(row, historical["implementation_rows"][path], path)

    def _static_audit(
        self,
        historical: dict[str, object],
        correction: dict[str, object] | None = None,
    ) -> dict[str, object]:
        if correction is None:
            correction = self._load_correction_authority()
        documents = []
        for path in AUTHORITY_FILES:
            document, raw = _strict_json(ROOT / path)
            self.assertEqual(_sha256(raw), AUTHORITY_RAW_SHA256[path])
            self.assertEqual(raw, historical["authority_raw"][path], path)
            documents.append(document)
        for path, expected in AUTHORITY_RAW_SHA256.items():
            self.assertEqual(_sha256((ROOT / path).read_bytes()), expected)
        contract, validation_contract, predecessor, manifest = documents

        self.assertEqual(
            manifest["authority"]["accepted_predecessor"],
            "fully integrated accepted I-8 coordinate",
        )
        self.assertEqual(
            predecessor["authority"]["required_start_commit"],
            "4ab6f9ca32e32a3801c6a4b6872b34b206e6da7e",
        )
        self.assertEqual(
            predecessor["authority"]["required_start_tree"],
            "591ad275116e9dc28bf0443aae80142e5ad86ec5",
        )

        inventory = validation_contract["inventory"]
        self.assertEqual(inventory["vector_count"], 97)
        self.assertEqual(inventory["dynamic_vector_count"], 69)
        self.assertEqual(inventory["static_witness_count"], 28)
        self.assertEqual(
            inventory["outcome_counts"],
            {"FAILURE": 50, "STATIC_PASS": 28, "SUCCESS": 19},
        )
        self.assertEqual(inventory["completed_check_count_total"], 292)
        self.assertEqual(inventory["active_predicate_count_total"], 50)
        for zero_key in (
            "filesystem_write_count_total",
            "model_call_count_total",
            "network_call_count_total",
            "policy_call_count_total",
            "runner_call_count_total",
            "state_advance_count_total",
            "subprocess_call_count_total",
        ):
            self.assertEqual(inventory[zero_key], 0)

        vectors = validation_contract["vectors"]
        self.assertEqual(
            tuple(vector["vector_id"] for vector in vectors[:69]),
            tuple(f"I9V-{index:03d}" for index in range(1, 70)),
        )
        self.assertEqual(
            tuple(vector["vector_id"] for vector in vectors[69:]),
            tuple(f"I9S-{index:03d}" for index in range(1, 29)),
        )
        vector_024 = vectors[23]
        self.assertEqual(vector_024["vector_id"], "I9V-024")
        self.assertEqual(vector_024["precedence"]["first_failure_ordinal"], 3)
        self.assertEqual(
            vector_024["precedence"]["active_predicates"], ["CLASS_NOT_T3"]
        )
        self.assertEqual(
            vector_024["expected"]["failure_code"],
            "CAPABILITY_ESCALATION_FORBIDDEN",
        )
        self.assertEqual(
            vector_024["expected"]["failure_id"],
            "ebu:failure:core:sha256-a05524aae5b8bda0625ba6b2ee1c669632bf46b480c8489cbb425900280ac3d0",
        )
        _assert_projection(vectors, validation_contract["projections"]["all_vectors"])
        _assert_projection(vectors[:69], validation_contract["projections"]["dynamic_vectors"])
        _assert_projection(vectors[69:], validation_contract["projections"]["static_vectors"])
        _assert_projection(
            validation_contract["construction_baselines"],
            validation_contract["projections"]["construction_baselines"],
        )
        _assert_projection(
            validation_contract["checklists"],
            validation_contract["projections"]["checklists"],
        )
        _assert_projection(
            validation_contract["failure_identity_contract"]["coordinate_catalogue"],
            validation_contract["projections"]["failure_coordinate_catalogue"],
        )

        current_scope = self._audit_current_head_scope(correction, historical)
        if current_scope["stage_d_phase"] in (
            "STAGE_D_AUTHORITY_ONLY",
            "STAGE_D_CONTINUATION_AUTHORITY_ONLY",
        ):
            self._audit_stage_d_authority(current_scope)
        if current_scope["stage_d_phase"] == "STAGE_D_CONTINUATION_AUTHORITY_ONLY":
            self._audit_stage_d_continuation_authority(current_scope)
        if current_scope["stage_e_phase"] in (
            "STAGE_E_HARNESS_AUTHORITY_ONLY",
            "STAGE_E_HARNESS_COMPLETED_IMPLEMENTATION",
        ):
            self._audit_stage_e_authority(current_scope)
        clcd_contract = json.loads(
            (ROOT / "closed_loop_correction_diagnostics_contract.json").read_text(
                encoding="utf-8"
            )
        )
        self._audit_validation_ast(contract, manifest)
        self._audit_public_surface(contract, manifest, clcd_contract)
        self._audit_import_graph(manifest, clcd_contract)
        self._audit_tables(contract)
        self._audit_safety_and_ci(
            manifest,
            current_scope["stage_c_phase"],
            current_scope["stage_e_phase"],
        )
        self._audit_text_and_markdown(contract)
        self._audit_static_vectors(validation_contract)
        self._audit_cross_document(contract, validation_contract, predecessor, manifest)
        return {
            "actual_head": current_scope["actual_head"],
            "current_path_bytes": current_scope["current_path_bytes"],
            "contract": contract,
            "validation_contract": validation_contract,
            "predecessor": predecessor,
            "manifest": manifest,
        }

    def _audit_current_head_scope(
        self, correction: dict[str, object], historical: dict[str, object]
    ) -> dict[str, object]:
        actual_head = _git("rev-parse", "--verify", "HEAD^{commit}").decode("ascii").strip()
        routed_head = os.environ.get(CURRENT_HEAD_ENV)
        if routed_head is not None:
            self.assertEqual(routed_head, actual_head, "routed current HEAD differs")
        self.assertEqual(
            _git("rev-parse", "--verify", f"{IMPLEMENTATION_BASE_COMMIT}^{{commit}}").decode().strip(),
            IMPLEMENTATION_BASE_COMMIT,
        )
        self.assertEqual(
            _git("rev-parse", f"{IMPLEMENTATION_BASE_COMMIT}^{{tree}}").decode().strip(),
            IMPLEMENTATION_BASE_TREE,
        )
        base_entries = _tree_entries(IMPLEMENTATION_BASE_COMMIT)
        head_entries = _tree_entries(actual_head)
        changed_paths = frozenset(
            path
            for path in set(base_entries) | set(head_entries)
            if head_entries.get(path) != base_entries.get(path)
        )
        if changed_paths == STAGE_C_AUTHORITY_SCOPE:
            stage_c_phase = "AUTHORITY_ONLY"
            stage_d_phase = None
            stage_e_phase = None
        elif changed_paths == STAGE_C_IMPLEMENTATION_SCOPE:
            stage_c_phase = "COMPLETED_IMPLEMENTATION"
            stage_d_phase = None
            stage_e_phase = None
        elif changed_paths == STAGE_D_AUTHORITY_SCOPE:
            stage_c_phase = "COMPLETED_IMPLEMENTATION"
            stage_d_phase = "STAGE_D_AUTHORITY_ONLY"
            stage_e_phase = None
        elif changed_paths == STAGE_D_CONTINUATION_AUTHORITY_SCOPE:
            stage_c_phase = "COMPLETED_IMPLEMENTATION"
            stage_d_phase = "STAGE_D_CONTINUATION_AUTHORITY_ONLY"
            stage_e_phase = None
        elif changed_paths == STAGE_E_AUTHORITY_SCOPE:
            stage_c_phase = "COMPLETED_IMPLEMENTATION"
            stage_d_phase = "STAGE_D_CONTINUATION_AUTHORITY_ONLY"
            stage_e_phase = "STAGE_E_HARNESS_AUTHORITY_ONLY"
        elif changed_paths == STAGE_E_HARNESS_IMPLEMENTATION_SCOPE:
            stage_c_phase = "COMPLETED_IMPLEMENTATION"
            stage_d_phase = "STAGE_D_CONTINUATION_AUTHORITY_ONLY"
            stage_e_phase = "STAGE_E_HARNESS_COMPLETED_IMPLEMENTATION"
        else:
            self.fail(
                "current HEAD is neither the exact Stage C authority phase nor "
                "the exact completed implementation, Stage D authority-only, "
                "Stage D continuation-authority-only, Stage E harness "
                "authority-only, or Stage E harness completed-implementation "
                f"phase: {sorted(changed_paths)!r}"
            )
        self.assertEqual(len(STAGE_C_AUTHORITY_SCOPE), 7)
        self.assertEqual(len(STAGE_C_IMPLEMENTATION_SCOPE), 24)
        self.assertEqual(len(STAGE_D_AUTHORITY_SCOPE), 30)
        self.assertEqual(len(STAGE_D_CONTINUATION_AUTHORITY_SCOPE), 35)
        self.assertEqual(len(STAGE_E_AUTHORITY_SCOPE), 41)
        self.assertEqual(len(STAGE_E_HARNESS_IMPLEMENTATION_SCOPE), 86)
        for path in changed_paths:
            self.assertIn(path, head_entries)
            self.assertEqual(head_entries[path]["mode"], "100644", path)
            self.assertEqual(head_entries[path]["object_type"], "blob", path)

        predecessor = correction["predecessor"]
        self.assertEqual(len(predecessor["rows"]), 330)
        predecessor_coordinate = COORDINATE_CHAIN["required_current_target"]
        predecessor_entries = _tree_entries(predecessor_coordinate["commit"])
        predecessor_archive = _archive_members(predecessor_coordinate["commit"])
        self.assertEqual(len(predecessor_entries), 330)
        self.assertEqual(len(predecessor_archive), 330)
        for row in predecessor["rows"]:
            path = row["path"]
            reconstructed, _ = _object_row(
                path, predecessor_entries, predecessor_archive
            )
            self.assertEqual(
                reconstructed,
                {
                    key: row[key]
                    for key in (
                        "byte_count",
                        "git_object",
                        "mode",
                        "object_type",
                        "path",
                        "raw_sha256",
                    )
                },
                path,
            )
            candidate = ROOT / path
            self.assertTrue(candidate.is_file(), path)
            actual_mode = "100755" if candidate.stat().st_mode & 0o111 else "100644"
            self.assertEqual(actual_mode, row["mode"], path)
            if path in changed_paths or path in CLCD_AUTHORIZED_PREDECESSOR_MODIFICATIONS:
                continue
            raw = candidate.read_bytes()
            self.assertEqual(len(raw), row["byte_count"], path)
            self.assertEqual(_sha256(raw), row["raw_sha256"], path)
            self.assertEqual(_blob_id(raw), row["git_object"], path)

        current_path_bytes = {
            path: (ROOT / path).read_bytes() for path in IMPLEMENTATION_PATHS
        }
        if stage_c_phase == "AUTHORITY_ONLY":
            self.assertEqual(
                _workflow_without_routing(current_path_bytes[".github/workflows/tests.yml"]),
                historical["implementation_raw"][".github/workflows/tests.yml"],
            )
        self.assertNotEqual(TEST_SELF_SEAL, "0" * 64)
        self.assertEqual(
            _sha256(
                _normalized_test_bytes(
                    current_path_bytes["tests/framework/test_validation_reachability.py"]
                )
            ),
            TEST_SELF_SEAL,
        )
        for path in ("src/ebu_framework/validation.py", "tests/framework/safety.py"):
            self.assertEqual(current_path_bytes[path], historical["implementation_raw"][path], path)
        current_book = next(
            row
            for row in predecessor["rows"]
            if row["path"] == "EBU_FUTURE_BOOKS_STRUCTURE.md"
        )
        self.assertEqual(current_book["byte_count"], 150664)
        self.assertEqual(current_book["git_object"], "af33c79b89372a8a1a9dc1939ca5f66974c23e56")
        self.assertNotEqual(current_book["raw_sha256"], historical["historical_book"]["raw_sha256"])
        return {
            "actual_head": actual_head,
            "current_path_bytes": current_path_bytes,
            "stage_c_phase": stage_c_phase,
            "stage_d_phase": stage_d_phase,
            "stage_e_phase": stage_e_phase,
        }

    def _audit_stage_d_authority(self, current_scope: dict[str, object]) -> None:
        self.assertEqual(
            _git("rev-parse", "--verify", f"{STAGE_D_ACCEPTED_BASE_COMMIT}^{{commit}}").decode().strip(),
            STAGE_D_ACCEPTED_BASE_COMMIT,
        )
        self.assertEqual(
            _git("rev-parse", f"{STAGE_D_ACCEPTED_BASE_COMMIT}^{{tree}}").decode().strip(),
            STAGE_D_ACCEPTED_BASE_TREE,
        )
        self.assertEqual(
            _git("rev-parse", f"{STAGE_D_AUTHORITY_CANDIDATE}^{{tree}}").decode().strip(),
            STAGE_D_AUTHORITY_TREE,
        )
        self.assertEqual(
            _git("rev-parse", f"{STAGE_D_AUTHORITY_TARGET}^{{tree}}").decode().strip(),
            STAGE_D_AUTHORITY_TREE,
        )
        self.assertEqual(
            _git("rev-parse", f"{STAGE_D_AUTHORITY_TARGET}^1").decode().strip(),
            STAGE_D_ACCEPTED_BASE_COMMIT,
        )
        self.assertEqual(
            _git("rev-parse", f"{STAGE_D_AUTHORITY_TARGET}^2").decode().strip(),
            STAGE_D_AUTHORITY_CANDIDATE,
        )

        base_entries = _tree_entries(STAGE_D_ACCEPTED_BASE_COMMIT)
        candidate_entries = _tree_entries(STAGE_D_AUTHORITY_CANDIDATE)
        target_entries = _tree_entries(STAGE_D_AUTHORITY_TARGET)
        current_entries = _tree_entries(current_scope["actual_head"])
        candidate_delta = frozenset(
            path
            for path in set(base_entries) | set(candidate_entries)
            if base_entries.get(path) != candidate_entries.get(path)
        )
        self.assertEqual(candidate_delta, frozenset(STAGE_D_AUTHORITY_PATHS))
        self.assertEqual(candidate_entries, target_entries)
        implementation_delta = frozenset(
            path
            for path in set(target_entries) | set(current_entries)
            if target_entries.get(path) != current_entries.get(path)
        )
        expected_implementation_delta = {
            "tests/framework/test_validation_reachability.py"
        }
        if current_scope["stage_d_phase"] == "STAGE_D_CONTINUATION_AUTHORITY_ONLY":
            expected_implementation_delta.update(STAGE_D_CONTINUATION_AUTHORITY_PATHS)
        if current_scope["stage_e_phase"] is not None:
            expected_implementation_delta.update(STAGE_E_AUTHORITY_PATHS)
        if current_scope["stage_e_phase"] == "STAGE_E_HARNESS_COMPLETED_IMPLEMENTATION":
            expected_implementation_delta.update(STAGE_E_HARNESS_IMPLEMENTATION_PATHS)
        self.assertEqual(
            implementation_delta,
            frozenset(expected_implementation_delta),
        )

        candidate_archive = _archive_members(STAGE_D_AUTHORITY_CANDIDATE)
        target_archive = _archive_members(STAGE_D_AUTHORITY_TARGET)
        documents = {}
        raw_by_path = {}
        for path in STAGE_D_AUTHORITY_PATHS:
            candidate_row, candidate_raw = _object_row(
                path, candidate_entries, candidate_archive
            )
            target_row, target_raw = _object_row(path, target_entries, target_archive)
            self.assertEqual(candidate_row, target_row, path)
            self.assertEqual(candidate_raw, target_raw, path)
            current_raw = (ROOT / path).read_bytes()
            self.assertEqual(current_raw, candidate_raw, path)
            self.assertEqual(_sha256(current_raw), STAGE_D_AUTHORITY_RAW_SHA256[path], path)
            self.assertTrue(current_raw.endswith(b"\n") and not current_raw.endswith(b"\n\n"), path)
            self.assertNotIn(b"\r", current_raw, path)
            raw_by_path[path] = current_raw
            if path.endswith(".json"):
                documents[path] = _strict_stage_d_json_bytes(current_raw, path)
                canonical = _canonical_json_lf(documents[path])[:-1]
                self.assertEqual(
                    _sha256(canonical),
                    STAGE_D_AUTHORITY_CANONICAL_SHA256[path],
                    path,
                )

        contract = documents["stage_d_scientific_validation_contract.json"]
        schema = documents["stage_d_scientific_validation_evidence_schema.json"]
        matrix = documents["stage_d_scientific_validation_master_matrix.json"]
        predecessor = documents["stage_d_scientific_validation_predecessor_manifest.json"]
        validation = documents["stage_d_scientific_validation_validation_contract.json"]
        self.assertEqual(
            tuple(contract["candidate_files"]), STAGE_D_AUTHORITY_PATHS
        )
        self.assertEqual(
            tuple(validation["candidate_paths"]), STAGE_D_AUTHORITY_PATHS
        )
        self.assertEqual(validation["candidate_path_count"], 6)
        self.assertEqual(
            contract["accepted_software_alpha"]["commit"],
            STAGE_D_ACCEPTED_BASE_COMMIT,
        )
        self.assertEqual(
            contract["accepted_software_alpha"]["tree"],
            STAGE_D_ACCEPTED_BASE_TREE,
        )
        self.assertEqual(predecessor["accepted_base"]["commit"], STAGE_D_ACCEPTED_BASE_COMMIT)
        self.assertEqual(predecessor["accepted_base"]["tree"], STAGE_D_ACCEPTED_BASE_TREE)

        source_rows = predecessor["source_rows"]
        self.assertEqual(predecessor["source_count"], 39)
        self.assertEqual(len(source_rows), 39)
        self.assertEqual(len({row["path"] for row in source_rows}), 39)
        predecessor_archive = _archive_members(STAGE_D_ACCEPTED_BASE_COMMIT)
        for row in source_rows:
            reconstructed, _ = _object_row(
                row["path"], base_entries, predecessor_archive
            )
            self.assertEqual(reconstructed["object_type"], "blob", row["path"])
            self.assertEqual(
                {
                    "path": reconstructed["path"],
                    "mode": reconstructed["mode"],
                    "git_object": reconstructed["git_object"],
                    "byte_count": reconstructed["byte_count"],
                    "sha256": reconstructed["raw_sha256"],
                },
                row,
                row["path"],
            )

        study_order = tuple(f"SD-{index:02d}" for index in range(1, 15))
        universal_fields = tuple(contract["universal_study_fields"])
        self.assertEqual(len(universal_fields), 21)
        self.assertEqual(tuple(contract["study_order"]), study_order)
        self.assertEqual(tuple(matrix["study_order"]), study_order)
        self.assertEqual(len(matrix["studies"]), 14)
        for index, row in enumerate(matrix["studies"], 1):
            self.assertEqual(row["study_id"], f"SD-{index:02d}")
            self.assertEqual(row["order"], index)
            self.assertEqual(set(row), set(universal_fields), row["study_id"])

        predecessor_paths = {row["path"] for row in source_rows}
        path_references = set()
        for row in matrix["studies"]:
            for reference in (*row["dependencies"], *row["owners"]["authority_sources"]):
                if reference.endswith((".md", ".json")):
                    path_references.add(reference)
        self.assertEqual(len(path_references), 18)
        self.assertTrue(path_references <= predecessor_paths)

        controls = contract["verbatim_user_mobius_topology_controls"]
        self.assertEqual(len(controls), 10)
        self.assertEqual(matrix["mandatory_controls_text"], controls)
        self.assertEqual(schema["verbatim_user_mobius_topology_controls"], controls)
        self.assertEqual(validation["verbatim_user_mobius_topology_controls"], controls)
        self.assertEqual(
            matrix["hard_cap_profile_role_mapping"]["role_field"],
            contract["evidence_hard_cap_normalization"]["record_role_profile_binding"]["role_field"],
        )
        self.assertEqual(
            tuple(contract["evidence_hard_cap_normalization"]["record_role_profile_binding"]["closed_roles"]),
            ("STUDY_EXECUTION", "MOBIUS_CONFORMANCE", "DAG_CONFORMANCE", "CACHE_CONFORMANCE"),
        )

        expected_counts = validation["expected_counts"]
        self.assertEqual(expected_counts["positive_check_count"], 121)
        self.assertEqual(expected_counts["negative_case_count"], 48)
        self.assertEqual(expected_counts["predecessor_source_count"], 39)
        self.assertEqual(expected_counts["study_count"], 14)
        self.assertEqual(expected_counts["total_schema_definition_count"], 22)
        self.assertEqual(len(schema["$defs"]), 22)
        self.assertEqual(len(schema["$defs"]["hard_caps"]["oneOf"]), 17)
        self.assertEqual(
            tuple(row["case_id"] for row in schema["prospective_negative_schema_cases"]),
            tuple(f"SCHEMA-N{index:02d}" for index in range(1, 17)),
        )
        self.assertEqual(
            tuple(check.split()[0] for group in validation["check_groups"] for check in group["checks"]),
            tuple(f"SDV-{index:03d}" for index in range(1, 122)),
        )
        self.assertEqual(
            tuple(row["id"] for row in validation["negative_cases"]),
            tuple(f"SDV-N{index:02d}" for index in range(1, 49)),
        )

        self.assertEqual(set(contract["stage_boundary"]["stage_d"]["counters"].values()), {0})
        self.assertEqual(set(matrix["stage_d_observations"].values()), {0})
        self.assertEqual(schema["stage_d_instance_count"], 0)
        for key, value in expected_counts.items():
            if key.startswith("stage_d_"):
                self.assertEqual(value, 0, key)
        marker = contract["completion_marker"]
        self.assertEqual(marker, validation["completion_marker"])
        self.assertEqual(
            raw_by_path["STAGE_D_SCIENTIFIC_VALIDATION_AUTHORITY.md"].count(
                marker.encode("utf-8")
            ),
            1,
        )

        durability = contract["prospective_durability_implementation"]
        self.assertEqual(durability["modified_path_count"], 1)
        self.assertEqual(
            durability["modified_paths"],
            ["tests/framework/test_validation_reachability.py"],
        )
        self.assertEqual(durability["new_path_count"], 0)
        self.assertEqual(durability["authority_plus_implementation_unique_path_count"], 7)
        self.assertEqual(durability["required_new_phase"], "STAGE_D_AUTHORITY_ONLY")
        self.assertEqual(durability["scientific_harness_or_execution"], "FORBIDDEN")
        self.assertEqual(
            tuple(
                name
                for name, value in self.__class__.__dict__.items()
                if name.startswith("test_") and callable(value)
            ),
            (
                "test_historical_i9_reconstruction",
                "test_current_head_durability",
                "test_post_i9_authority_cases",
            ),
        )

    def _audit_stage_d_continuation_authority(
        self, current_scope: dict[str, object]
    ) -> None:
        self.assertEqual(
            _git(
                "rev-parse",
                "--verify",
                f"{STAGE_D_CONTINUATION_ACCEPTED_BASE_COMMIT}^{{commit}}",
            )
            .decode()
            .strip(),
            STAGE_D_CONTINUATION_ACCEPTED_BASE_COMMIT,
        )
        self.assertEqual(
            _git(
                "rev-parse", f"{STAGE_D_CONTINUATION_ACCEPTED_BASE_COMMIT}^{{tree}}"
            )
            .decode()
            .strip(),
            STAGE_D_CONTINUATION_ACCEPTED_BASE_TREE,
        )
        self.assertEqual(
            _git(
                "rev-parse", f"{STAGE_D_CONTINUATION_AUTHORITY_CANDIDATE}^{{tree}}"
            )
            .decode()
            .strip(),
            STAGE_D_CONTINUATION_AUTHORITY_TREE,
        )
        self.assertEqual(
            _git(
                "rev-parse", f"{STAGE_D_CONTINUATION_AUTHORITY_TARGET}^{{tree}}"
            )
            .decode()
            .strip(),
            STAGE_D_CONTINUATION_AUTHORITY_TREE,
        )
        self.assertEqual(
            _git("rev-parse", f"{STAGE_D_CONTINUATION_AUTHORITY_TARGET}^1")
            .decode()
            .strip(),
            STAGE_D_CONTINUATION_ACCEPTED_BASE_COMMIT,
        )
        self.assertEqual(
            _git("rev-parse", f"{STAGE_D_CONTINUATION_AUTHORITY_TARGET}^2")
            .decode()
            .strip(),
            STAGE_D_CONTINUATION_AUTHORITY_CANDIDATE,
        )
        base_entries = _tree_entries(STAGE_D_CONTINUATION_ACCEPTED_BASE_COMMIT)
        candidate_entries = _tree_entries(STAGE_D_CONTINUATION_AUTHORITY_CANDIDATE)
        target_entries = _tree_entries(STAGE_D_CONTINUATION_AUTHORITY_TARGET)
        current_entries = _tree_entries(current_scope["actual_head"])
        candidate_delta = frozenset(
            path
            for path in set(base_entries) | set(candidate_entries)
            if base_entries.get(path) != candidate_entries.get(path)
        )
        self.assertEqual(
            candidate_delta, frozenset(STAGE_D_CONTINUATION_AUTHORITY_PATHS)
        )
        self.assertEqual(candidate_entries, target_entries)
        implementation_delta = frozenset(
            path
            for path in set(target_entries) | set(current_entries)
            if target_entries.get(path) != current_entries.get(path)
        )
        expected_implementation_delta = {
            "tests/framework/test_validation_reachability.py"
        }
        if current_scope["stage_e_phase"] is not None:
            expected_implementation_delta.update(STAGE_E_AUTHORITY_PATHS)
        if current_scope["stage_e_phase"] == "STAGE_E_HARNESS_COMPLETED_IMPLEMENTATION":
            expected_implementation_delta.update(STAGE_E_HARNESS_IMPLEMENTATION_PATHS)
        self.assertEqual(
            implementation_delta,
            frozenset(expected_implementation_delta),
        )

        candidate_archive = _archive_members(STAGE_D_CONTINUATION_AUTHORITY_CANDIDATE)
        target_archive = _archive_members(STAGE_D_CONTINUATION_AUTHORITY_TARGET)
        documents = {}
        raw_by_path = {}
        for path in STAGE_D_CONTINUATION_AUTHORITY_PATHS:
            candidate_row, candidate_raw = _object_row(
                path, candidate_entries, candidate_archive
            )
            target_row, target_raw = _object_row(path, target_entries, target_archive)
            self.assertEqual(candidate_row, target_row, path)
            self.assertEqual(candidate_raw, target_raw, path)
            current_raw = (ROOT / path).read_bytes()
            self.assertEqual(current_raw, candidate_raw, path)
            self.assertEqual(
                _sha256(current_raw),
                STAGE_D_CONTINUATION_AUTHORITY_RAW_SHA256[path],
                path,
            )
            self.assertTrue(
                current_raw.endswith(b"\n") and not current_raw.endswith(b"\n\n"),
                path,
            )
            self.assertNotIn(b"\r", current_raw, path)
            raw_by_path[path] = current_raw
            if path.endswith(".json"):
                documents[path] = _strict_stage_d_json_bytes(current_raw, path)
                canonical = _canonical_json_lf(documents[path])[:-1]
                self.assertEqual(
                    _sha256(canonical),
                    STAGE_D_CONTINUATION_AUTHORITY_CANONICAL_SHA256[path],
                    path,
                )

        contract = documents[
            "stage_d_completion_oriented_continuation_contract.json"
        ]
        schema = documents[
            "stage_d_completion_oriented_continuation_evidence_schema.json"
        ]
        predecessor = documents[
            "stage_d_completion_oriented_continuation_predecessor_manifest.json"
        ]
        validation = documents[
            "stage_d_completion_oriented_continuation_validation_contract.json"
        ]
        self.assertEqual(
            tuple(contract["candidate_files"]),
            STAGE_D_CONTINUATION_AUTHORITY_PATHS,
        )
        self.assertEqual(contract["candidate_file_count"], 5)
        self.assertEqual(
            tuple(validation["candidate_paths"]),
            STAGE_D_CONTINUATION_AUTHORITY_PATHS,
        )
        self.assertEqual(validation["candidate_path_count"], 5)
        self.assertEqual(
            contract["accepted_base"]["commit"],
            STAGE_D_CONTINUATION_ACCEPTED_BASE_COMMIT,
        )
        self.assertEqual(
            contract["accepted_base"]["tree"],
            STAGE_D_CONTINUATION_ACCEPTED_BASE_TREE,
        )
        self.assertEqual(
            predecessor["accepted_base"]["commit"],
            STAGE_D_CONTINUATION_ACCEPTED_BASE_COMMIT,
        )
        self.assertEqual(
            predecessor["accepted_base"]["tree"],
            STAGE_D_CONTINUATION_ACCEPTED_BASE_TREE,
        )

        preserved_stage_d_paths = tuple(
            contract["accepted_stage_d_authority"]["files_preserved_byte_for_byte"]
        )
        self.assertEqual(preserved_stage_d_paths, STAGE_D_AUTHORITY_PATHS)
        base_archive = _archive_members(STAGE_D_CONTINUATION_ACCEPTED_BASE_COMMIT)
        for path in STAGE_D_AUTHORITY_PATHS:
            _, base_raw = _object_row(path, base_entries, base_archive)
            self.assertEqual(base_raw, (ROOT / path).read_bytes(), path)
            self.assertEqual(_sha256(base_raw), STAGE_D_AUTHORITY_RAW_SHA256[path], path)

        self.assertEqual(predecessor["source_count"], 9)
        source_rows = predecessor["source_rows"]
        self.assertEqual(len(source_rows), 9)
        self.assertEqual(len({row["path"] for row in source_rows}), 9)
        for row in source_rows:
            reconstructed, base_raw = _object_row(
                row["path"], base_entries, base_archive
            )
            self.assertEqual(
                {
                    "path": reconstructed["path"],
                    "mode": reconstructed["mode"],
                    "git_object": reconstructed["git_object"],
                    "byte_count": reconstructed["byte_count"],
                    "raw_sha256": reconstructed["raw_sha256"],
                },
                {
                    key: row[key]
                    for key in (
                        "path",
                        "mode",
                        "git_object",
                        "byte_count",
                        "raw_sha256",
                    )
                },
                row["path"],
            )
            stage_e_workflow_change = (
                row["path"] == ".github/workflows/tests.yml"
                and current_scope["stage_e_phase"]
                == "STAGE_E_HARNESS_COMPLETED_IMPLEMENTATION"
            )
            if (
                row["path"] != "tests/framework/test_validation_reachability.py"
                and not stage_e_workflow_change
            ):
                self.assertEqual((ROOT / row["path"]).read_bytes(), base_raw, row["path"])
            if row["path"].endswith(".json"):
                document = _strict_stage_d_json_bytes(base_raw, row["path"])
                canonical = _canonical_json_lf(document)[:-1]
                self.assertEqual(row["canonical_byte_count"], len(canonical), row["path"])
                self.assertEqual(row["canonical_sha256"], _sha256(canonical), row["path"])
            else:
                self.assertIsNone(row["canonical_byte_count"], row["path"])
                self.assertIsNone(row["canonical_sha256"], row["path"])
            self.assertEqual(row["candidate_disposition"], "PRESERVED_BYTE_FOR_BYTE")

        nested_lock = predecessor["accepted_stage_d_nested_predecessor_lock"]
        self.assertEqual(
            nested_lock,
            {
                "path": "stage_d_scientific_validation_predecessor_manifest.json",
                "source_count": 39,
                "all_rows_remain_controlling": True,
                "candidate_may_reconcile_or_exclude_nested_row": False,
            },
        )
        accepted_evidence = contract["accepted_integration_evidence"]
        self.assertEqual(accepted_evidence["ci_run_id"], 33094713851)
        self.assertEqual(
            accepted_evidence["ci_head"], STAGE_D_CONTINUATION_ACCEPTED_BASE_COMMIT
        )
        self.assertEqual(accepted_evidence["ci_conclusion"], "SUCCESS")
        self.assertEqual(accepted_evidence["required_job_count"], 5)
        self.assertEqual(set(accepted_evidence["required_job_conclusions"].values()), {"SUCCESS"})
        self.assertEqual(accepted_evidence["artifact_id"], 9656859745)
        self.assertEqual(accepted_evidence["scientific_execution_count"], 0)

        study_order = tuple(f"SD-{index:02d}" for index in range(1, 15))
        registry = contract["study_registry"]
        self.assertEqual(tuple(registry["ordered_study_ids"]), study_order)
        self.assertEqual(registry["study_count"], 14)
        continuation_partition = (
            set(registry["within_run_checkpoint_continuation"])
            | set(registry["conditional_inherited_continuation"])
            | set(registry["between_atomic_case_continuation_only"])
        )
        self.assertEqual(continuation_partition, set(study_order))
        self.assertEqual(
            sum(
                len(registry[key])
                for key in (
                    "within_run_checkpoint_continuation",
                    "conditional_inherited_continuation",
                    "between_atomic_case_continuation_only",
                )
            ),
            14,
        )
        hierarchy = contract["identity_hierarchy"]
        self.assertEqual(
            tuple(hierarchy["ordered_levels"]),
            ("study_id", "campaign_id", "scientific_run_id", "attempt_id", "checkpoint_id"),
        )
        self.assertEqual(len(hierarchy["campaign_identity_preimage_fields"]), 29)
        self.assertEqual(len(hierarchy["scientific_run_identity_preimage_fields"]), 8)
        self.assertEqual(len(hierarchy["attempt_identity_preimage_fields"]), 5)
        execution_binding = contract["execution_binding_policy"]
        self.assertEqual(execution_binding["campaign_policy_identity_field_count"], 5)
        self.assertEqual(execution_binding["attempt_binding_preimage_field_count"], 12)
        self.assertEqual(execution_binding["process_allocation_preimage_field_count"], 4)
        self.assertEqual(execution_binding["worker_allocation_required_field_count"], 9)
        self.assertIn(
            "must equal",
            execution_binding["policy_conformance_receipt_equality_rule"],
        )
        self.assertEqual(
            contract["cache_and_invalidation"]["accepted_cache_key_field_count"], 29
        )
        self.assertEqual(len(contract["terminal_states"]["attempt_states"]), 10)
        self.assertTrue(contract["cumulative_accounting"]["never_reset"])
        self.assertEqual(
            contract["finite_computation_boundary"]["boolean_mobius_time"],
            "O(n*2^n) transform arithmetic plus 2^n*C_E subset-evaluation cost",
        )
        self.assertEqual(
            contract["finite_computation_boundary"]["boolean_mobius_storage"],
            "O(2^n)",
        )
        self.assertEqual(
            contract["finite_computation_boundary"]["approximation"],
            "SEPARATE_PREREGISTERED_AUTHORITY_REQUIRED",
        )

        checkpoint = contract["checkpoint_binding"]
        deterministic = checkpoint["deterministic_empty_branch"]
        self.assertEqual(deterministic["seed"], 0)
        self.assertEqual(deterministic["ordered_permitted_stream_ids"], [])
        self.assertEqual(deterministic["next_counter_tuples"], [])
        empty_digest = _sha256(_canonical_json_lf([])[:-1])
        self.assertEqual(
            deterministic["canonical_empty_array_sha256"], empty_digest
        )
        tuple_preimage = json.loads(
            deterministic["next_counter_tuple_set_preimage_canonical_json"]
        )
        tuple_digest = _sha256(_canonical_json_lf(tuple_preimage)[:-1])
        self.assertEqual(
            deterministic["next_counter_tuple_set_identity"]["value"], tuple_digest
        )
        self.assertEqual(
            deterministic["next_counter_tuple_set_identity"]["sha256"], tuple_digest
        )
        self.assertFalse(deterministic["dummy_stream_permitted"])
        self.assertEqual(
            contract["stochastic_terminal_rule"]["terminal_rejection_attempt_index"],
            1_000_000,
        )
        self.assertEqual(
            contract["stochastic_terminal_rule"]["continuation_after_terminal"],
            "FORBIDDEN",
        )

        required_definitions = tuple(validation["required_schema_definition_names"])
        self.assertEqual(validation["required_schema_definition_count"], 23)
        self.assertEqual(len(schema["$defs"]), 23)
        self.assertEqual(set(schema["$defs"]), set(required_definitions))
        refs = []

        def collect_refs(value: object) -> None:
            if type(value) is dict:
                for key, item in value.items():
                    if key == "$ref":
                        refs.append(item)
                    collect_refs(item)
            elif type(value) is list:
                for item in value:
                    collect_refs(item)

        collect_refs(schema)
        local_refs = tuple(ref for ref in refs if ref.startswith("#/$defs/"))
        self.assertEqual(len(local_refs), 227)
        self.assertEqual(len(set(local_refs)), 13)
        for ref in local_refs:
            self.assertIn(ref.removeprefix("#/$defs/"), schema["$defs"])
        self.assertEqual(schema["prospective_instance_count"], 0)
        self.assertEqual(
            tuple(row["case_id"] for row in schema["prospective_negative_validation_cases"]),
            tuple(f"CONT-SCHEMA-N{index:02d}" for index in range(1, 36)),
        )
        fixtures = schema["prospective_non_evidence_schema_fixtures"]
        fixture_names = tuple(validation["required_non_evidence_schema_fixture_names"])
        self.assertEqual(set(fixtures) - {"purpose"}, set(fixture_names))
        deterministic_fixture = fixtures["valid_sd01_deterministic_empty_checkpoint"]
        self.assertEqual(deterministic_fixture["study_id"], "SD-01")
        self.assertEqual(deterministic_fixture["counter_state_mode"], "DETERMINISTIC_EMPTY")
        self.assertEqual(deterministic_fixture["stochastic_rule_identity"]["value"], "FORBIDDEN")
        self.assertEqual(deterministic_fixture["seed"], 0)
        self.assertEqual(deterministic_fixture["ordered_permitted_stream_ids"], [])
        self.assertEqual(deterministic_fixture["next_counter_tuples"], [])
        self.assertEqual(
            deterministic_fixture["next_counter_tuple_set_identity"]["sha256"],
            tuple_digest,
        )

        self.assertEqual(validation["required_positive_check_count"], 99)
        self.assertEqual(validation["required_negative_case_count"], 46)
        self.assertEqual(validation["required_predecessor_row_count"], 9)
        self.assertEqual(
            tuple(check.split()[0] for check in validation["positive_checks"]),
            tuple(f"CONT-P{index:03d}" for index in range(1, 100)),
        )
        self.assertEqual(
            tuple(row["id"] for row in validation["negative_cases"]),
            tuple(f"CONT-N{index:02d}" for index in range(1, 47)),
        )
        self.assertIn(
            "policy_conformance_receipt_identity values are exactly equal",
            validation["positive_checks"][-1],
        )
        self.assertEqual(
            schema["prospective_negative_validation_cases"][-1]["required_disposition"],
            "REFUSE_POLICY_CONFORMANCE_RECEIPT_MISMATCH",
        )
        self.assertEqual(
            validation["negative_cases"][-1]["required_disposition"],
            "REFUSE_POLICY_CONFORMANCE_RECEIPT_MISMATCH",
        )
        self.assertEqual(
            validation["required_operation_counts"],
            {"added": 5, "modified": 0, "deleted": 0, "renamed": 0, "mode_changed": 0},
        )
        self.assertEqual(set(contract["evidence_boundary"]["counters"].values()), {0})
        for key, value in validation["global_acceptance"].items():
            if key.endswith("_count"):
                self.assertEqual(value, 0, key)

        marker = contract["completion_marker"]
        self.assertEqual(marker, schema["completion_marker"])
        self.assertEqual(marker, predecessor["completion_marker"])
        self.assertEqual(marker, validation["completion_marker"])
        for path, raw in raw_by_path.items():
            self.assertEqual(raw.count(marker.encode("utf-8")), 1, path)
        self.assertEqual(
            contract["future_stage_boundary"]["durability"],
            "separately authorized one-path reachability change after integration",
        )
        self.assertEqual(
            contract["future_stage_boundary"]["stage_e"],
            "separately authorized harness and conformance only after accepted continuation authority and durability",
        )

    def _audit_stage_e_authority(self, current_scope: dict[str, object]) -> None:
        self.assertEqual(
            _git(
                "rev-parse", "--verify", f"{STAGE_E_ACCEPTED_BASE_COMMIT}^{{commit}}"
            )
            .decode()
            .strip(),
            STAGE_E_ACCEPTED_BASE_COMMIT,
        )
        self.assertEqual(
            _git("rev-parse", f"{STAGE_E_ACCEPTED_BASE_COMMIT}^{{tree}}")
            .decode()
            .strip(),
            STAGE_E_ACCEPTED_BASE_TREE,
        )
        self.assertEqual(
            _git("rev-parse", f"{STAGE_E_AUTHORITY_CANDIDATE}^{{tree}}")
            .decode()
            .strip(),
            STAGE_E_AUTHORITY_TREE,
        )
        self.assertEqual(
            _git("rev-parse", f"{STAGE_E_AUTHORITY_TARGET}^{{tree}}")
            .decode()
            .strip(),
            STAGE_E_AUTHORITY_TREE,
        )
        self.assertEqual(
            _git("rev-parse", f"{STAGE_E_AUTHORITY_TARGET}^1").decode().strip(),
            STAGE_E_ACCEPTED_BASE_COMMIT,
        )
        self.assertEqual(
            _git("rev-parse", f"{STAGE_E_AUTHORITY_TARGET}^2").decode().strip(),
            STAGE_E_AUTHORITY_CANDIDATE,
        )
        self.assertEqual(
            _git("merge-base", STAGE_E_ACCEPTED_BASE_COMMIT, STAGE_E_AUTHORITY_CANDIDATE)
            .decode()
            .strip(),
            STAGE_E_ACCEPTED_BASE_COMMIT,
        )
        history_rows = tuple(
            tuple(line.split())
            for line in _git(
                "rev-list",
                "--reverse",
                "--parents",
                f"{STAGE_E_ACCEPTED_BASE_COMMIT}..{STAGE_E_AUTHORITY_CANDIDATE}",
            )
            .decode()
            .splitlines()
        )
        self.assertEqual(tuple(row[0] for row in history_rows), STAGE_E_AUTHORITY_CHAIN)
        self.assertEqual(history_rows[0][1:], (STAGE_E_ACCEPTED_BASE_COMMIT,))
        for previous, row in zip(STAGE_E_AUTHORITY_CHAIN, history_rows[1:]):
            self.assertEqual(row[1:], (previous,))

        base_entries = _tree_entries(STAGE_E_ACCEPTED_BASE_COMMIT)
        candidate_entries = _tree_entries(STAGE_E_AUTHORITY_CANDIDATE)
        target_entries = _tree_entries(STAGE_E_AUTHORITY_TARGET)
        current_entries = _tree_entries(current_scope["actual_head"])
        candidate_delta = frozenset(
            path
            for path in set(base_entries) | set(candidate_entries)
            if base_entries.get(path) != candidate_entries.get(path)
        )
        self.assertEqual(candidate_delta, frozenset(STAGE_E_AUTHORITY_PATHS))
        self.assertEqual(candidate_entries, target_entries)
        implementation_delta = frozenset(
            path
            for path in set(target_entries) | set(current_entries)
            if target_entries.get(path) != current_entries.get(path)
        )
        expected_implementation_delta = {
            "tests/framework/test_validation_reachability.py"
        }
        if current_scope["stage_e_phase"] == "STAGE_E_HARNESS_COMPLETED_IMPLEMENTATION":
            expected_implementation_delta.update(STAGE_E_HARNESS_IMPLEMENTATION_PATHS)
        self.assertEqual(
            implementation_delta,
            frozenset(expected_implementation_delta),
        )

        candidate_archive = _archive_members(STAGE_E_AUTHORITY_CANDIDATE)
        target_archive = _archive_members(STAGE_E_AUTHORITY_TARGET)
        documents = {}
        raw_by_path = {}
        for path in STAGE_E_AUTHORITY_PATHS:
            candidate_row, candidate_raw = _object_row(
                path, candidate_entries, candidate_archive
            )
            target_row, target_raw = _object_row(path, target_entries, target_archive)
            self.assertEqual(candidate_row, target_row, path)
            self.assertEqual(candidate_raw, target_raw, path)
            current_raw = (ROOT / path).read_bytes()
            self.assertEqual(current_raw, candidate_raw, path)
            self.assertEqual(
                _sha256(current_raw), STAGE_E_AUTHORITY_RAW_SHA256[path], path
            )
            self.assertTrue(
                current_raw.endswith(b"\n") and not current_raw.endswith(b"\n\n"),
                path,
            )
            self.assertNotIn(b"\r", current_raw, path)
            raw_by_path[path] = current_raw
            if path.endswith(".json"):
                documents[path] = _strict_stage_d_json_bytes(current_raw, path)
                canonical = _canonical_json_lf(documents[path])[:-1]
                self.assertEqual(
                    _sha256(canonical),
                    STAGE_E_AUTHORITY_CANONICAL_SHA256[path],
                    path,
                )

        contract = documents["stage_e_scientific_harness_contract.json"]
        schema = documents["stage_e_scientific_harness_evidence_schema.json"]
        implementation = documents[
            "stage_e_scientific_harness_implementation_path_manifest.json"
        ]
        predecessor = documents[
            "stage_e_scientific_harness_predecessor_manifest.json"
        ]
        validation = documents[
            "stage_e_scientific_harness_validation_contract.json"
        ]
        self.assertEqual(tuple(contract["candidate_files"]), STAGE_E_AUTHORITY_PATHS)
        self.assertEqual(contract["candidate_file_count"], 6)
        self.assertEqual(tuple(validation["candidate_paths"]), STAGE_E_AUTHORITY_PATHS)
        self.assertEqual(validation["candidate_path_count"], 6)
        for document in (contract, implementation, predecessor):
            self.assertEqual(
                document["accepted_base"]["commit"], STAGE_E_ACCEPTED_BASE_COMMIT
            )
            self.assertEqual(
                document["accepted_base"]["tree"], STAGE_E_ACCEPTED_BASE_TREE
            )
        self.assertEqual(validation["base_commit"], STAGE_E_ACCEPTED_BASE_COMMIT)
        self.assertEqual(validation["base_tree"], STAGE_E_ACCEPTED_BASE_TREE)

        history_policy = contract["candidate_history_policy"]
        self.assertEqual(history_policy["shape"], "merge-free linear descendant chain")
        self.assertIn("sole parent", history_policy["first_candidate_parent"])
        self.assertIn("sole parent", history_policy["later_candidate_parent"])
        self.assertEqual(
            history_policy["merge_nonlinear_extra_parent_or_detached_commit"],
            "REFUSE_STAGE_E_AUTHORITY",
        )

        self.assertEqual(predecessor["source_count"], 17)
        source_rows = predecessor["source_rows"]
        self.assertEqual(len(source_rows), 17)
        self.assertEqual(len({row["path"] for row in source_rows}), 17)
        base_archive = _archive_members(STAGE_E_ACCEPTED_BASE_COMMIT)
        for row in source_rows:
            reconstructed, base_raw = _object_row(
                row["path"], base_entries, base_archive
            )
            self.assertEqual(
                {
                    key: reconstructed[key]
                    for key in (
                        "path",
                        "mode",
                        "object_type",
                        "git_object",
                        "byte_count",
                        "raw_sha256",
                    )
                },
                {
                    key: row[key]
                    for key in (
                        "path",
                        "mode",
                        "object_type",
                        "git_object",
                        "byte_count",
                        "raw_sha256",
                    )
                },
                row["path"],
            )
            stage_e_workflow_change = (
                row["path"] == ".github/workflows/tests.yml"
                and current_scope["stage_e_phase"]
                == "STAGE_E_HARNESS_COMPLETED_IMPLEMENTATION"
            )
            if (
                row["path"] != "tests/framework/test_validation_reachability.py"
                and not stage_e_workflow_change
            ):
                self.assertEqual((ROOT / row["path"]).read_bytes(), base_raw, row["path"])
            if row["path"].endswith(".json"):
                canonical = _canonical_json_lf(
                    _strict_stage_d_json_bytes(base_raw, row["path"])
                )[:-1]
                self.assertEqual(row["canonical_byte_count"], len(canonical))
                self.assertEqual(row["canonical_sha256"], _sha256(canonical))
            else:
                self.assertIsNone(row["canonical_byte_count"])
                self.assertIsNone(row["canonical_sha256"])

        self.assertEqual(tuple(implementation["authority_paths"]), STAGE_E_AUTHORITY_PATHS)
        self.assertEqual(implementation["authority_path_count"], 6)
        durability = implementation["prospective_durability"]
        self.assertEqual(
            durability["modified_paths"],
            ["tests/framework/test_validation_reachability.py"],
        )
        self.assertEqual(durability["modified_path_count"], 1)
        self.assertEqual(durability["new_paths"], [])
        self.assertEqual(durability["new_path_count"], 0)
        self.assertEqual(durability["required_phase"], "STAGE_E_HARNESS_AUTHORITY_ONLY")
        harness_paths = implementation["prospective_harness_implementation"]
        self.assertEqual(harness_paths["modified_paths"], [".github/workflows/tests.yml"])
        self.assertEqual(harness_paths["modified_path_count"], 1)
        self.assertEqual(
            tuple(harness_paths["new_paths"]),
            STAGE_E_HARNESS_IMPLEMENTATION_PATHS[1:],
        )
        self.assertEqual(harness_paths["new_path_count"], 45)
        self.assertEqual(harness_paths["total_path_count"], 46)
        self.assertEqual(
            len(
                set(STAGE_E_AUTHORITY_PATHS)
                | {"tests/framework/test_validation_reachability.py"}
                | set(STAGE_E_HARNESS_IMPLEMENTATION_PATHS)
            ),
            53,
        )
        self.assertEqual(implementation["unknown_path_disposition"], "REFUSE_STAGE_E_IMPLEMENTATION")
        self.assertEqual(implementation["scope_derived_exclusion"], "FORBIDDEN")
        self.assertEqual(implementation["force_push_or_history_rewrite"], "FORBIDDEN")
        if current_scope["stage_e_phase"] == "STAGE_E_HARNESS_COMPLETED_IMPLEMENTATION":
            workflow_row = next(
                row
                for row in source_rows
                if row["path"] == ".github/workflows/tests.yml"
            )
            _, accepted_workflow_raw = _object_row(
                workflow_row["path"], base_entries, base_archive
            )
            current_workflow_raw = (ROOT / workflow_row["path"]).read_bytes()
            self.assertEqual(
                current_workflow_raw,
                accepted_workflow_raw + STAGE_E_WORKFLOW_APPEND_BLOCK,
                "Stage E workflow must be the exact accepted workflow plus the frozen additive job",
            )
            self.assertEqual(
                current_workflow_raw.count(b"  stage-e-scientific-harness:\n"),
                1,
            )
            self.assertEqual(
                current_workflow_raw.count(
                    b"    needs: [test, framework-t0, framework-t1, framework-t2, packaging-release-candidate]\n"
                ),
                1,
            )
            self.assertEqual(current_workflow_raw.count(b"--network none"), 6)
            self.assertEqual(current_workflow_raw.count(b"--read-only"), 6)
            self.assertEqual(
                current_workflow_raw.count(b"--platform linux/amd64"), 6
            )

        study_order = tuple(f"SD-{index:02d}" for index in range(1, 15))
        registry = contract["study_registry"]
        self.assertEqual(tuple(registry["ordered_study_ids"]), study_order)
        self.assertEqual(registry["study_count"], 14)
        self.assertEqual(registry["first_priority"], "SD-01")
        self.assertEqual(
            tuple(registry["within_run_checkpoint_continuation"]),
            ("SD-01", "SD-08", "SD-09", "SD-10", "SD-11", "SD-12", "SD-13", "SD-14"),
        )
        self.assertEqual(tuple(registry["conditional_inherited_continuation"]), ("SD-02",))
        self.assertEqual(
            tuple(registry["between_atomic_case_continuation_only"]),
            ("SD-03", "SD-04", "SD-05", "SD-06", "SD-07"),
        )

        mobius = contract["mobius_conformance"]
        self.assertEqual(mobius["shared_case_count"], 488)
        self.assertEqual(mobius["complexity_cell_count"], 55)
        self.assertEqual(mobius["declared_time"], "O(n*2^n) transform arithmetic plus 2^n*C_E subset evaluation")
        self.assertEqual(mobius["declared_storage"], "O(2^n)")
        self.assertEqual(mobius["hard_maximum_n"], 18)
        self.assertEqual(mobius["hard_maximum_subsets"], 262_144)
        self.assertEqual(mobius["universal_scalability_claim"], "FORBIDDEN")
        dag = contract["dag_conformance"]
        self.assertEqual(dag["valid_exact_case_count"], 39_467)
        self.assertEqual(dag["invalid_refusal_case_count"], 14)
        self.assertEqual(len(dag["complexity_cells"]), 5)
        self.assertEqual(dag["declared_traversal_time"], "O(V+E)")
        self.assertIn("not part of traversal claim", dag["canonicalization_bound"])
        cache = contract["canonical_cache_conformance"]
        self.assertEqual(cache["complete_cache_key_field_count"], 29)
        self.assertEqual(cache["required_control_count"], 17)
        self.assertEqual(cache["cache_key_omission_mutations"], 29)
        self.assertFalse(cache["runtime_cache_authorized_in_stage_e"])

        schema_profile = contract["schema_profile"]
        expected_keywords = (
            "$defs", "$id", "$ref", "$schema", "additionalProperties", "allOf",
            "const", "description", "else", "enum", "format", "if", "items",
            "maxItems", "maximum", "minItems", "minLength", "minProperties",
            "minimum", "oneOf", "pattern", "prefixItems", "properties",
            "required", "then", "title", "type", "uniqueItems",
        )
        self.assertEqual(tuple(schema_profile["supported_keywords_in_order"]), expected_keywords)
        self.assertEqual(schema_profile["supported_keyword_count"], 28)
        self.assertIn("derive", schema_profile["validator_scope"])
        self.assertEqual(schema_profile["assertion_and_applicator_keyword_mutation_count"], 22)
        self.assertEqual(schema_profile["positive_fixture_counts"]["total"], 19)
        self.assertEqual(schema_profile["frozen_negative_fixture_counts"]["total"], 75)
        self.assertEqual(schema_profile["total_refused_instance_count"], 97)
        schema_documents = (
            _strict_stage_d_json_bytes(
                (ROOT / "stage_d_scientific_validation_evidence_schema.json").read_bytes(),
                "stage_d_scientific_validation_evidence_schema.json",
            ),
            _strict_stage_d_json_bytes(
                (ROOT / "stage_d_completion_oriented_continuation_evidence_schema.json").read_bytes(),
                "stage_d_completion_oriented_continuation_evidence_schema.json",
            ),
            schema,
        )
        derived_keywords = set()

        def collect_keywords(value: object) -> None:
            if type(value) is dict:
                for key, item in value.items():
                    if key in expected_keywords:
                        derived_keywords.add(key)
                    collect_keywords(item)
            elif type(value) is list:
                for item in value:
                    collect_keywords(item)

        for schema_document in schema_documents:
            collect_keywords(schema_document)
        self.assertEqual(derived_keywords, set(expected_keywords))
        self.assertIn(
            b'"minProperties": 1',
            (ROOT / "stage_d_scientific_validation_evidence_schema.json").read_bytes(),
        )

        self.assertEqual(len(schema["$defs"]), 22)
        refs = []

        def collect_refs(value: object) -> None:
            if type(value) is dict:
                for key, item in value.items():
                    if key == "$ref":
                        refs.append(item)
                    collect_refs(item)
            elif type(value) is list:
                for item in value:
                    collect_refs(item)

        collect_refs(schema)
        self.assertEqual(len(refs), 99)
        for ref in refs:
            self.assertTrue(ref.startswith("#/$defs/"), ref)
            self.assertIn(ref.removeprefix("#/$defs/"), schema["$defs"])
        schema_record = schema["$defs"]["schema_record"]["allOf"][1]["properties"]
        self.assertEqual(tuple(schema_record["supported_keywords"]["const"]), expected_keywords)
        self.assertEqual(schema_record["valid_instances"]["const"], 19)
        self.assertEqual(schema_record["refused_instances"]["const"], 97)
        self.assertEqual(schema_record["unresolved_local_refs"]["const"], 0)
        self.assertEqual(len(schema["prospective_non_evidence_schema_fixtures"]), 11)
        self.assertEqual(len(schema["prospective_negative_schema_cases"]), 24)

        positive_groups = validation["positive_check_groups"]
        self.assertEqual(sum(group["count"] for group in positive_groups), 195)
        for group in positive_groups:
            self.assertEqual(group["count"], len(group["checks"]), group["group_id"])
        self.assertEqual(validation["required_positive_check_count"], 195)
        self.assertEqual(len(validation["negative_cases"]), 95)
        self.assertEqual(validation["required_negative_case_count"], 95)
        self.assertTrue(validation["negative_cases"][-1].startswith("SE-N095 "))
        self.assertTrue(
            any(
                "merge-free linear chain" in check
                for check in positive_groups[0]["checks"]
            )
        )
        self.assertTrue(
            any(
                "minProperties" in check
                for group in positive_groups
                for check in group["checks"]
            )
        )
        self.assertEqual(len(validation["required_zero_counters"]), 17)
        scientific_properties = schema["$defs"]["scientific_zero_counters"]["properties"]
        release_properties = schema["$defs"]["release_zero_counters"]["properties"]
        self.assertEqual(
            set(validation["required_zero_counters"]),
            set(scientific_properties) | set(release_properties),
        )
        self.assertEqual(
            {row["const"] for row in scientific_properties.values()}, {0}
        )
        self.assertEqual({row["const"] for row in release_properties.values()}, {0})
        self.assertEqual(schema["scientific_execution_count"], 0)
        self.assertEqual(schema["stage_e_instance_count"], 0)

        environment = contract["reference_environment"]
        self.assertEqual(
            environment["oci_manifest_digest"],
            "sha256:a1f225293efe68c4cb9dddb084b04fa1a21a4d751ad130d0224902e00b1e55ab",
        )
        self.assertEqual(environment["architecture"], "linux/amd64")
        self.assertEqual(environment["cpython"], "3.14.4-final")
        self.assertEqual(environment["sqlite_version"], "3.46.1")
        self.assertEqual(environment["network"], "OFFLINE")
        self.assertEqual(environment["fallback_environment"], "FORBIDDEN")
        artifacts = contract["framework_isolation"]["accepted_artifact_identities"]
        self.assertEqual(artifacts["direct_wheel"]["byte_count"], 4_078_247)
        self.assertEqual(
            artifacts["direct_wheel"]["sha256"],
            "3d11dca3efe1798f02da5faf16e1eeff30b0ddb38cf0a9dccb8ab43193b794c2",
        )
        self.assertEqual(artifacts["direct_wheel"], artifacts["sdist_derived_wheel"])
        self.assertEqual(artifacts["sdist"]["byte_count"], 4_139_346)
        self.assertEqual(
            artifacts["sdist"]["sha256"],
            "0dbf5eeaa3008c038bab55be43eadbcfe667b5f68ef6319285c86770e0fcfe41",
        )

        markers = {
            "STAGE_E_SCIENTIFIC_HARNESS_AUTHORITY.md": contract["completion_marker"],
            "stage_e_scientific_harness_contract.json": contract["completion_marker"],
            "stage_e_scientific_harness_evidence_schema.json": schema["completion_marker"],
            "stage_e_scientific_harness_implementation_path_manifest.json": implementation["completion_marker"],
            "stage_e_scientific_harness_predecessor_manifest.json": predecessor["completion_marker"],
            "stage_e_scientific_harness_validation_contract.json": validation["completion_marker"],
        }
        for path, marker in markers.items():
            self.assertEqual(raw_by_path[path].count(marker.encode("utf-8")), 1, path)
        self.assertEqual(
            tuple(
                name
                for name, value in self.__class__.__dict__.items()
                if name.startswith("test_") and callable(value)
            ),
            (
                "test_historical_i9_reconstruction",
                "test_current_head_durability",
                "test_post_i9_authority_cases",
            ),
        )

    def _audit_validation_ast(self, contract, manifest) -> None:
        path = SOURCE / "validation.py"
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        compile(tree, str(path), "exec")
        assignments = _literal_assignments(tree)
        self.assertEqual(tuple(assignments), CONSTANT_NAMES + ("__all__",))
        self.assertEqual(assignments["__all__"], ())

        groups = tuple(
            (
                row["group_id"],
                row["class"],
                tuple(row["permitted_checks"]),
                tuple(row["explicitly_unreachable"]),
                tuple(row["exact_test_paths"]),
            )
            for row in contract["validation_authority"]["groups"]
        )
        self.assertEqual(assignments["_VALIDATION_GROUPS"], groups)
        self.assertEqual(tuple(row[0] for row in groups), tuple(f"V{i}" for i in range(12)))
        self.assertNotIn("T3", tuple(row[1] for row in groups))
        self.assertEqual(assignments["_I9_IMPLEMENTATION_PATHS"], IMPLEMENTATION_PATHS)
        self.assertEqual(
            assignments["_I9_ROOT_EXPORTS"],
            tuple(contract["accepted_surface"]["root_exports"]["values"]),
        )
        self.assertEqual(
            assignments["_I9_FAILURE_CODES"],
            tuple(contract["accepted_surface"]["failure_codes"]["values"]),
        )
        self.assertEqual(
            assignments["_I9_PUBLIC_SIGNATURES"],
            tuple(tuple(row) for row in contract["accepted_surface"]["public_signature_rows"]["rows"]),
        )
        self.assertEqual(
            assignments["_I9_DIRECT_IMPORTS"],
            tuple(tuple(row) for row in manifest["future_import_graph"]["direct_edges"]),
        )
        self.assertEqual(
            assignments["_I9_AUDIT_REGISTER"],
            tuple(row[1] for row in contract["audit_register"]["combined_rows"]),
        )

        bridge_path = "tests/framework/fixtures/bridge_m1_m9_v1.json"
        dynamic_path = "tests/framework/fixtures/dynamic_static_v1.json"
        bridge = json.loads((ROOT / bridge_path).read_text(encoding="utf-8"))
        dynamic = json.loads((ROOT / dynamic_path).read_text(encoding="utf-8"))
        bridge_hash = _sha256((ROOT / bridge_path).read_bytes())
        dynamic_hash = _sha256((ROOT / dynamic_path).read_bytes())
        expected_allowlist = tuple(
            ("V8", bridge_path, bridge_hash, row["case_id"], row["interface"])
            for row in bridge["positive_interface_vectors"]
        ) + tuple(
            ("V9", dynamic_path, dynamic_hash, row["case_id"], row["owner"])
            for row in dynamic["cases"]
        )
        self.assertEqual(assignments["_I9_T2_ALLOWLIST"], expected_allowlist)
        self.assertEqual(len(expected_allowlist), 42)

        functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
        self.assertEqual(tuple(node.name for node in functions), PRIVATE_NAMES)
        self.assertEqual(
            [["validation", node.name, _signature(node)] for node in functions],
            manifest["private_signature_rows"],
        )
        self.assertFalse(any(isinstance(node, (ast.ClassDef, ast.Lambda)) for node in ast.walk(tree)))
        nested_functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        self.assertEqual(len(nested_functions), 7)

        relative_imports = _direct_imports(
            tree, tuple(manifest["future_import_graph"]["package_module_order"])
        )
        self.assertEqual(
            relative_imports,
            ("canonical", "numeric", "identity", "hashing", "primitives", "capabilities", "errors"),
        )
        forbidden_calls = {
            "__import__",
            "compile",
            "eval",
            "exec",
            "import_module",
            "open",
            "run",
            "Popen",
        }
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = (
                    node.func.id
                    if isinstance(node.func, ast.Name)
                    else node.func.attr
                    if isinstance(node.func, ast.Attribute)
                    else ""
                )
                self.assertNotIn(name, forbidden_calls)

    def _audit_public_surface(self, contract, manifest, clcd_contract) -> None:
        init_tree = ast.parse((SOURCE / "__init__.py").read_text(encoding="utf-8"))
        root_exports = _module_exports(init_tree)
        expected_root = (
            tuple(contract["accepted_surface"]["root_exports"]["values"])
            + tuple(clcd_contract["root_export_suffix"])
        )
        self.assertEqual(root_exports, expected_root)
        self.assertEqual(len(root_exports), 471)
        self.assertEqual(len(set(root_exports)), 471)
        self.assertFalse(any(name.startswith("I9") for name in root_exports))

        errors_tree = ast.parse((SOURCE / "errors.py").read_text(encoding="utf-8"))
        failure_class = next(
            node
            for node in errors_tree.body
            if isinstance(node, ast.ClassDef) and node.name == "FailureCode"
        )
        failure_codes = tuple(
            node.targets[0].id
            for node in failure_class.body
            if isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
        )
        self.assertEqual(
            failure_codes,
            tuple(contract["accepted_surface"]["failure_codes"]["values"])
            + tuple(clcd_contract["failure_suffix"]),
        )
        self.assertEqual(len(failure_codes), 294)
        self.assertFalse(any(code.startswith("I9_") for code in failure_codes))

        expected_exports = dict(manifest["module_exports"])
        expected_exports["validation"] = []
        clcd_suffix = tuple(clcd_contract["root_export_suffix"])
        expected_exports["correction_protocol"] = clcd_suffix[:20]
        expected_exports["correction_diagnostics"] = clcd_suffix[20:]
        for module, expected in expected_exports.items():
            tree = ast.parse((SOURCE / f"{module}.py").read_text(encoding="utf-8"))
            self.assertEqual(_module_exports(tree), tuple(expected), module)
        self.assertEqual(_module_exports(ast.parse((SOURCE / "validation.py").read_text())), ())

        actual_functions = {}
        for path in SOURCE.glob("*.py"):
            if path.stem in {"__init__", "validation"}:
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in tree.body:
                if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                    actual_functions[(path.stem, node.name)] = node
        expected_rows = list(contract["accepted_surface"]["public_signature_rows"]["rows"])
        expected_rows.extend(
            [
                (
                    "correction_protocol"
                    if name == "validate_closed_loop_correction_protocol"
                    else "correction_diagnostics",
                    name,
                    signature,
                )
                for name, signature in clcd_contract["public_callables"]
            ]
        )
        self.assertEqual(len(expected_rows), 162)
        self.assertEqual(len(actual_functions), 162)
        self.assertEqual(
            set(actual_functions), {(row[0], row[1]) for row in expected_rows}
        )
        for module, name, signature in expected_rows:
            expected_node = ast.parse(f"def _expected{signature}:\n    pass\n").body[0]
            actual_node = actual_functions[(module, name)]
            self.assertEqual(
                ast.dump(actual_node.args, include_attributes=False),
                ast.dump(expected_node.args, include_attributes=False),
                f"{module}.{name}",
            )
            self.assertEqual(
                ast.dump(actual_node.returns, include_attributes=False),
                ast.dump(expected_node.returns, include_attributes=False),
                f"{module}.{name}",
            )

        _assert_projection(
            contract["accepted_surface"]["public_signature_rows"]["rows"],
            contract["accepted_surface"]["public_signature_rows"]["projection"],
        )
        _assert_projection(
            contract["accepted_surface"]["module_exports"],
            contract["accepted_surface"]["module_export_projection"],
        )

    def _audit_import_graph(self, manifest, clcd_contract) -> None:
        graph = manifest["future_import_graph"]
        modules = tuple(graph["package_module_order"]) + (
            "correction_protocol",
            "correction_diagnostics",
        )
        self.assertEqual(len(modules), 42)
        actual_imports = {}
        for module in modules:
            tree = ast.parse((SOURCE / f"{module}.py").read_text(encoding="utf-8"))
            actual_imports[module] = _direct_imports(tree, modules)
        expected_imports = {
            module: tuple(values) for module, values in graph["direct_imports"].items()
        }
        expected_imports.update(
            {
                "correction_protocol": ("errors", "identity", "numeric", "primitives"),
                "correction_diagnostics": ("correction_protocol", "errors", "numeric"),
            }
        )
        for module in ("correction_protocol", "correction_diagnostics"):
            self.assertEqual(
                set(expected_imports[module]),
                set(clcd_contract["import_boundary"][module]),
            )
        self.assertEqual(actual_imports, expected_imports)
        edges = tuple(
            (module, dependency)
            for module in modules
            for dependency in actual_imports[module]
        )
        expected_edges = tuple(tuple(row) for row in graph["direct_edges"]) + tuple(
            (module, dependency)
            for module in ("correction_protocol", "correction_diagnostics")
            for dependency in expected_imports[module]
        )
        self.assertEqual(edges, expected_edges)
        self.assertEqual(len(edges), 257)
        self.assertNotIn(("validation", "execution"), edges)
        self.assertFalse(any(target == "validation" and source != "validation" for source, target in edges))

        visiting = set()
        visited = set()

        def visit(module: str) -> None:
            if module in visiting:
                raise AssertionError(f"import cycle reaches {module}")
            if module in visited:
                return
            visiting.add(module)
            for dependency in actual_imports[module]:
                visit(dependency)
            visiting.remove(module)
            visited.add(module)

        for module in modules:
            visit(module)
        self.assertEqual(len(visited), 42)

        reachable = set()
        pending = ["validation"]
        while pending:
            module = pending.pop()
            if module in reachable:
                continue
            reachable.add(module)
            pending.extend(actual_imports[module])
        self.assertNotIn("execution", reachable)
        _assert_projection(graph["direct_edges"], graph["projection"])

    def _audit_tables(self, contract) -> None:
        invariants = contract["audit_register"]["invariants"]
        specification_threats = contract["audit_register"]["specification_threats"]
        implementation_threats = contract["audit_register"]["implementation_plan_threats"]
        open_rows = contract["open_boundaries"]["post_atomic_register_snapshot"]
        self.assertEqual(invariants["count"], 67)
        self.assertEqual(specification_threats["count"], 45)
        self.assertEqual(implementation_threats["count"], 26)
        self.assertEqual(contract["audit_register"]["combined_count"], 138)
        self.assertEqual(open_rows["disposition_row_occurrence_count"], 180)
        _assert_ordered_table_rows(
            ROOT / "UNIFIED_PYTHON_RESEARCH_FRAMEWORK_SPECIFICATION.md",
            invariants["rows"],
        )
        _assert_ordered_table_rows(
            ROOT / "UNIFIED_PYTHON_RESEARCH_FRAMEWORK_SPECIFICATION.md",
            specification_threats["rows"],
        )
        _assert_ordered_table_rows(
            ROOT / "UNIFIED_PYTHON_RESEARCH_FRAMEWORK_IMPLEMENTATION_PLAN.md",
            implementation_threats["rows"],
        )
        _assert_ordered_table_rows(
            ROOT / "POST_ATOMIC_OPEN_PROBLEM_REGISTER.md",
            open_rows["rows_in_document_order"],
        )
        _assert_projection(invariants["rows"], invariants["projection"])
        _assert_projection(specification_threats["rows"], specification_threats["projection"])
        _assert_projection(implementation_threats["rows"], implementation_threats["projection"])
        _assert_projection(open_rows["rows_in_document_order"], open_rows["projection"])
        _assert_projection(
            contract["audit_register"]["combined_rows"],
            contract["audit_register"]["combined_projection"],
        )

    def _audit_safety_and_ci(
        self, manifest, stage_c_phase: str, stage_e_phase: str | None
    ) -> None:
        safety_path = ROOT / "tests/framework/safety.py"
        safety_raw = safety_path.read_bytes()
        self.assertEqual(
            _sha256(_base_candidate_bytes("tests/framework/safety.py")),
            "40346595695d908a575dbc8fe8228564f2e182268a0822b93ce5b0db03246eb6",
        )
        safety_tree = ast.parse(safety_raw.decode("utf-8"), filename=str(safety_path))
        safety_assignments = _literal_assignments(safety_tree)
        self.assertIn("i9_forbidden_observation_guard", _module_exports(safety_tree))
        self.assertEqual(
            safety_assignments["_I9_FORBIDDEN_DYNAMIC_IMPORT_CALLS"],
            ("import_module", "invalidate_caches", "reload"),
        )
        self.assertIn("subprocess", safety_assignments["_I9_FORBIDDEN_PROCESS_MODULE_PREFIXES"])
        self.assertIn("results", safety_assignments["_I9_FORBIDDEN_HISTORICAL_MODULE_PREFIXES"])
        safety_imports = {
            alias.name.split(".", 1)[0]
            for node in safety_tree.body
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        self.assertFalse(safety_imports & {"ebu_framework", "subprocess", "socket", "requests"})

        current_workflow_raw = (ROOT / ".github/workflows/tests.yml").read_bytes()
        if stage_c_phase == "COMPLETED_IMPLEMENTATION":
            workflow_raw = _git(
                "show", f"{STAGE_C_PREDECESSOR_COMMIT}:.github/workflows/tests.yml"
            )
        else:
            workflow_raw = current_workflow_raw
        workflow = workflow_raw.decode("utf-8")
        self.assertEqual(
            _sha256(_base_candidate_projection(".github/workflows/tests.yml", workflow_raw)),
            "4d12f834e52bf92a723ab1e2c9723a9b395344320f3c95482b64d9133c766d23",
        )
        self.assertEqual(workflow_raw.count(WORKFLOW_ROUTING_BLOCK), 1)
        self.assertEqual(workflow_raw.count(WORKFLOW_T1_COMPATIBILITY_BLOCK), 1)
        self.assertEqual(workflow_raw.count(WORKFLOW_T1_RUNNER_BLOCK), 1)
        self.assertEqual(workflow_raw.count(WORKFLOW_CLCD_T0_BLOCK), 1)
        for variable in tuple(COORDINATE_ENV.values()) + (CURRENT_HEAD_ENV,):
            self.assertEqual(workflow.count(f"      {variable}:"), 1, variable)
        self.assertEqual(workflow.count("  workflow_dispatch:\n"), 1)
        self.assertEqual(workflow.count("  framework-t0:\n"), 1)
        self.assertEqual(workflow.count("  framework-t1:\n"), 1)
        self.assertEqual(workflow.count("  framework-t2:\n"), 1)
        self.assertNotIn("framework-t3", workflow.lower())
        self.assertIn("if: github.event_name == 'workflow_dispatch'", workflow)
        self.assertEqual(
            workflow.count("python -m pip install --require-hashes -r requirements-framework.lock"),
            3,
        )
        self.assertEqual(workflow.count('python-version: "3.14"'), 3)
        self.assertEqual(workflow.count('python-version: "3.14.2"'), 0)
        self.assertNotIn("python -m pip install --no-deps .", workflow)
        self.assertNotIn("python -m pip install .", workflow)
        self.assertEqual(workflow.count("or result.skipped"), 5)
        self.assertEqual(workflow.count("or result.expectedFailures"), 5)
        self.assertEqual(workflow.count("or result.unexpectedSuccesses"), 5)

        t0 = workflow.split("  framework-t0:\n", 1)[1].split("  framework-t1:\n", 1)[0]
        t1 = workflow.split("  framework-t1:\n", 1)[1].split("  framework-t2:\n", 1)[0]
        t2 = workflow.split("  framework-t2:\n", 1)[1]
        self.assertNotIn("/private/tmp", t0)
        self.assertEqual(t1.count("/private/tmp"), 4)
        self.assertNotIn("/private/tmp", t2)
        self.assertEqual(t1.count("runs-on: ubuntu-26.04"), 1)
        self.assertNotIn("runs-on: ubuntu-latest", t1)
        pattern = re.compile(r'"(tests/framework/test_[a-z0-9_]+\.py)"')
        self.assertEqual(tuple(pattern.findall(t0)), T0_PATHS)
        for path in CURRENT_T0_PATHS:
            self.assertEqual(t0.count(path.rsplit("/", 1)[1]), 1, path)
        self.assertEqual(tuple(pattern.findall(t1)), T1_PATHS)
        self.assertEqual(tuple(pattern.findall(t2)), T2_PATHS)
        self.assertEqual(
            list(manifest["ci_boundary"]["push_pull_request"]["T0"]), list(T0_PATHS)
        )
        self.assertEqual(
            list(manifest["ci_boundary"]["push_pull_request"]["T1"]), list(T1_PATHS)
        )
        self.assertEqual(
            list(manifest["ci_boundary"]["workflow_dispatch_only"]["T2"]), list(T2_PATHS)
        )
        for required in (
            "2e7848dc495c4b2d5fb2ea09d668f2b240d3ec02",
            "8f570082e40304b156aa18714c65938777126f74",
            "8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af",
            "cacb79a4b52eb714b79424524c12cba9f8a4d2327abe99c2b76260c4621a898d",
            "I9_T2_AUTHORITY_ALLOWLIST=42",
        ):
            self.assertIn(required, t2)
        for region, label in ((t0, "T0"), (t1, "T1"), (t2, "T2")):
            self.assertIn(f"{label}_COMPLETED_TESTS=", region)
            self.assertIn("count <= 0", region)
            self.assertIn(
                'export PYTHONPATH="$compatibility_root/src:'
                '$compatibility_root/tests/framework"',
                region,
            )
        self.assertIn(
            'export PYTHONPATH="$candidate_root/src:'
            '$candidate_root/tests/framework"',
            t0,
        )
        test_source = (ROOT / "tests/framework/test_validation_reachability.py").read_text(
            encoding="utf-8"
        )
        test_tree = ast.parse(test_source)
        subprocess_run_calls = tuple(
            node
            for node in ast.walk(test_tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "run"
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "subprocess"
        )
        self.assertEqual(len(subprocess_run_calls), 1)
        subprocess_popen_calls = tuple(
            node
            for node in ast.walk(test_tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "Popen"
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "subprocess"
        )
        self.assertEqual(subprocess_popen_calls, ())
        forbidden_git_commands = {"fetch", "push"}
        for node in ast.walk(test_tree):
            if not (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "_git"
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
            ):
                continue
            self.assertNotIn(node.args[0].value, forbidden_git_commands)
        skipped_tests = tuple(
            node.name
            for node in ast.walk(test_tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and any("skip" in ast.unparse(item).lower() for item in node.decorator_list)
        )
        self.assertEqual(skipped_tests, ())
        historical_region = test_source.split("    def _historical_reconstruction(", 1)[1].split(
            "    def _audit_documentation_feature(", 1
        )[0]
        self.assertNotIn("from ebu_framework", historical_region)
        self.assertNotIn("import ebu_framework", historical_region)
        if stage_c_phase == "COMPLETED_IMPLEMENTATION":
            stage_c_workflow_raw = current_workflow_raw
            if stage_e_phase == "STAGE_E_HARNESS_COMPLETED_IMPLEMENTATION":
                self.assertTrue(current_workflow_raw.endswith(STAGE_E_WORKFLOW_APPEND_BLOCK))
                stage_c_workflow_raw = current_workflow_raw[
                    : -len(STAGE_E_WORKFLOW_APPEND_BLOCK)
                ]
            self._audit_stage_c_ci(stage_c_workflow_raw.decode("utf-8"))

    def _audit_stage_c_ci(self, workflow: str) -> None:
        self.assertNotIn("ubuntu-26.04", workflow)
        self.assertEqual(workflow.count("runs-on: ubuntu-24.04"), 5)
        for job in (
            "test",
            "framework-t0",
            "framework-t1",
            "framework-t2",
            "packaging-release-candidate",
        ):
            self.assertEqual(workflow.count(f"  {job}:\n"), 1, job)
        self.assertEqual(workflow.count("--network none"), 5)
        self.assertEqual(workflow.count("--platform linux/amd64"), 5)
        self.assertEqual(workflow.count("--read-only"), 5)
        self.assertGreaterEqual(workflow.count(IMAGE_DIGEST := "sha256:a1f225293efe68c4cb9dddb084b04fa1a21a4d751ad130d0224902e00b1e55ab"), 2)
        self.assertIn("docker.io/library/python@" + IMAGE_DIGEST, workflow)
        self.assertIn(
            "framework-t2:\n    if: github.event_name == 'push' || "
            "github.event_name == 'pull_request' || "
            "github.event_name == 'workflow_dispatch'",
            workflow,
        )
        self.assertEqual(
            workflow.count("validate_stage_c_release_candidate.py packaging"), 5
        )
        self.assertEqual(
            workflow.count("validate_stage_c_release_candidate.py static-authority"),
            5,
        )
        self.assertIn("for tier in t0 t1 t2", workflow)
        self.assertIn("for artifact in source direct-wheel sdist-wheel", workflow)
        self.assertIn("validate_stage_c_release_candidate.py emit-manifest", workflow)
        self.assertIn("actions/upload-artifact@v4", workflow)
        self.assertEqual(workflow.count("--require-hashes"), 5)
        self.assertEqual(
            workflow.count("--dest \"$stage_root/conventional-wheelhouse\""), 2
        )
        for requirement in (
            "charset-normalizer==3.5.1",
            "contourpy==1.3.3",
            "cycler==0.12.1",
            "fonttools==4.63.0",
            "kiwisolver==1.5.0",
            "matplotlib==3.11.1",
            "numpy==2.5.2",
            "pillow==12.3.0",
            "pyparsing==3.3.2",
            "python-dateutil==2.9.0.post0",
            "reportlab==5.0.1",
            "six==1.17.0",
        ):
            self.assertEqual(workflow.count(requirement), 2, requirement)
        self.assertEqual(workflow.count("packaging==26.3"), 7)

    def _audit_text_and_markdown(self, contract) -> None:
        for path in (
            IMPLEMENTATION_PATHS
            + tuple(AUTHORITY_RAW_SHA256)
            + CORRECTION_AUTHORITY_FILES
        ):
            raw = (ROOT / path).read_bytes()
            self.assertFalse(raw.startswith(b"\xef\xbb\xbf"), path)
            self.assertNotIn(b"\r", raw, path)
            self.assertTrue(raw.endswith(b"\n"), path)
            raw.decode("utf-8", "strict")
            self.assertFalse(
                any(line.endswith((b" ", b"\t")) for line in raw.splitlines()), path
            )
        for source in (
            "UNIFIED_PYTHON_RESEARCH_FRAMEWORK_SPECIFICATION.md",
            "UNIFIED_PYTHON_RESEARCH_FRAMEWORK_IMPLEMENTATION_PLAN.md",
            "POST_ATOMIC_OPEN_PROBLEM_REGISTER.md",
            "UNIFIED_PYTHON_RESEARCH_FRAMEWORK_I9_AUTHORITY_AMENDMENT.md",
        ):
            text = (ROOT / source).read_text(encoding="utf-8")
            self.assertEqual(text.count("```"), 2 * (text.count("```") // 2), source)
            self.assertEqual(text.count("]("), len(re.findall(r"\]\([^\n)]*\)", text)), source)
        self.assertEqual(contract["future_implementation_boundary"]["path_count"], 4)
        self.assertNotIn(
            "report", tuple(Path(path).name.lower() for path in IMPLEMENTATION_PATHS)
        )

    def _audit_static_vectors(self, validation_contract) -> None:
        vectors = validation_contract["vectors"][69:]
        expected_kinds = (
            "PACKAGE_CARDINALITY",
            "PREDECESSOR_ROUTE_A",
            "PREDECESSOR_ROUTE_B",
            "PREDECESSOR_ROUTE_AGREEMENT",
            "ACCEPTED_TARGET",
            "ROOT_EXPORTS",
            "FAILURE_CODES",
            "PUBLIC_SIGNATURES",
            "MODULE_EXPORTS",
            "IMPORT_GRAPH",
            "NO_EXECUTION_EDGE",
            "IMPLEMENTATION_PATH_CLOSURE",
            "DEPENDENCY_LOCKS",
            "UNICODE_LOCKS",
            "VALIDATION_GROUPS",
            "VECTOR_MATERIALIZATION",
            "FAILURE_IDS",
            "COLLISION_AUDIT",
            "INVARIANT_REGISTER",
            "SPECIFICATION_THREAT_REGISTER",
            "IMPLEMENTATION_PLAN_THREAT_REGISTER",
            "OPEN_PROBLEM_REGISTER",
            "SOURCE_LOCKS",
            "CROSS_DOCUMENT_AGREEMENT",
            "MARKDOWN_INTEGRITY",
            "TEXT_INTEGRITY",
            "GIT_SCOPE",
            "HISTORICAL_SAFETY",
        )
        self.assertEqual(
            tuple(vector["construction"]["static_witness"]["kind"] for vector in vectors),
            expected_kinds,
        )
        for vector in vectors:
            witness = vector["construction"]["static_witness"]
            self.assertEqual(vector["exercise_class"], "AUTHORIZED_STATIC_WITNESS")
            self.assertEqual(vector["owner_interface"], "STATIC_ONLY")
            self.assertEqual(vector["owner_call_count"], 0)
            self.assertEqual(vector["expected"]["outcome"], "STATIC_PASS")
            self.assertEqual(vector["expected"]["result_projection"], witness)
            _assert_projection(
                witness, vector["expected"]["result_projection_identity"]
            )
            self.assertEqual(vector["precedence"]["completed_check_count"], 1)

    def _audit_cross_document(self, contract, validation_contract, predecessor, manifest) -> None:
        self.assertEqual(
            tuple(contract["future_implementation_boundary"]["paths"]), IMPLEMENTATION_PATHS
        )
        self.assertEqual(
            tuple(row[1] for row in manifest["inventory"]["rows"]),
            (
                "src/ebu_framework/validation.py",
                "tests/framework/test_validation_reachability.py",
                "tests/framework/safety.py",
                ".github/workflows/tests.yml",
            ),
        )
        self.assertEqual(
            {row[1] for row in manifest["inventory"]["rows"]},
            set(IMPLEMENTATION_PATHS),
        )
        self.assertEqual(manifest["inventory"]["path_count"], 4)
        self.assertEqual(manifest["inventory"]["modified_count"], 2)
        self.assertEqual(manifest["inventory"]["new_count"], 2)
        self.assertEqual(manifest["future_root_export_suffix"], [])
        self.assertEqual(manifest["future_failure_suffix"], [])
        self.assertEqual(manifest["future_public_signature_rows"], [])
        self.assertFalse(manifest["dependency_drift"]["allowed"])
        self.assertEqual(manifest["ci_boundary"]["T3_job_count"], 0)
        self.assertFalse(contract["validation_authority"]["T3_authorized"])
        self.assertEqual(predecessor["tree_inventory"]["row_count"], 321)
        self.assertEqual(contract["accepted_surface"]["predecessor_tree_row_count"], 321)
        self.assertEqual(contract["audit_register"]["combined_count"], 138)
        self.assertEqual(
            validation_contract["audit_register_contract"]["post_atomic_open_disposition_occurrences"],
            180,
        )

    def _case_baseline(
        self,
        correction: dict[str, object],
        historical: dict[str, object],
        current: dict[str, object],
    ) -> dict[str, object]:
        frozen = correction["validation"]["accepted_i9_frozen_inventory"]
        validation_tree = ast.parse((SOURCE / "validation.py").read_text(encoding="utf-8"))
        assignments = _literal_assignments(validation_tree)
        validators = tuple(
            ("validation", node.name, _signature(node))
            for node in validation_tree.body
            if isinstance(node, ast.FunctionDef)
        )
        constants = tuple((name, assignments[name]) for name in CONSTANT_NAMES)
        init_tree = ast.parse((SOURCE / "__init__.py").read_text(encoding="utf-8"))
        root_exports = _module_exports(init_tree)
        errors_tree = ast.parse((SOURCE / "errors.py").read_text(encoding="utf-8"))
        failure_class = next(
            node
            for node in errors_tree.body
            if isinstance(node, ast.ClassDef) and node.name == "FailureCode"
        )
        failure_codes = tuple(
            node.targets[0].id
            for node in failure_class.body
            if isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
        )
        signatures = tuple(
            tuple(row)
            for row in historical["contract"]["accepted_surface"]["public_signature_rows"]["rows"]
        )
        edges = tuple(
            tuple(row) for row in historical["manifest"]["future_import_graph"]["direct_edges"]
        )
        workflow = current["current_path_bytes"][".github/workflows/tests.yml"].decode("utf-8")
        nonframework = workflow.split("\n  framework-t0:\n", 1)[0].encode("utf-8")
        dependency_rows = tuple(
            (row["path"], row["mode"], row["byte_count"], row["raw_sha256"])
            for row in correction["predecessor"]["rows"]
            if row["path"] == "requirements-framework.lock"
            or row["path"].startswith("tests/framework/fixtures/")
        )
        current_book = next(
            {
                key: row[key]
                for key in ("byte_count", "git_object", "mode", "path", "raw_sha256")
            }
            for row in correction["predecessor"]["rows"]
            if row["path"] == "EBU_FUTURE_BOOKS_STRUCTURE.md"
        )
        baseline = {
            "coordinate_chain": copy.deepcopy(COORDINATE_CHAIN),
            "expected_coordinate_chain": copy.deepcopy(COORDINATE_CHAIN),
            "historical_binding": COORDINATE_CHAIN["accepted_i9_implementation_target"]["commit"],
            "expected_historical_binding": COORDINATE_CHAIN["accepted_i9_implementation_target"]["commit"],
            "current_binding": current["actual_head"],
            "expected_current_binding": current["actual_head"],
            "historical_data_source": "IMMUTABLE_GIT_OBJECTS",
            "tree_route_identity": historical["route_identity"],
            "archive_route_identity": historical["route_identity"],
            "source_locks": tuple(historical["source_lock_rows"].values()),
            "expected_source_locks": tuple(historical["source_lock_rows"].values()),
            "historical_book": copy.deepcopy(historical["historical_book"]),
            "expected_historical_book": copy.deepcopy(historical["historical_book"]),
            "current_book": current_book,
            "historical_delta_paths": tuple(IMPLEMENTATION_PATHS),
            "expected_historical_delta_paths": tuple(IMPLEMENTATION_PATHS),
            "scope_paths": list(POST_I9_AUTHORIZED_PATHS),
            "scope_modes": {path: "100644" for path in POST_I9_AUTHORIZED_PATHS},
            "current_path_bytes": copy.deepcopy(current["current_path_bytes"]),
            "current_path_hashes": {
                path: _sha256(raw) for path, raw in current["current_path_bytes"].items()
            },
            "current_source_identity_valid": True,
            "validators": validators,
            "expected_validators": validators,
            "constants": constants,
            "expected_constants": constants,
            "vector_ids": [
                row["vector_id"] for row in historical["validation_contract"]["vectors"]
            ],
            "expected_vector_ids": tuple(
                row["vector_id"] for row in historical["validation_contract"]["vectors"]
            ),
            "completed_checks": 292,
            "vector_projection": historical["validation_contract"]["projections"]["all_vectors"]["sha256"],
            "expected_vector_projection": historical["validation_contract"]["projections"]["all_vectors"]["sha256"],
            "root_exports": list(root_exports),
            "expected_root_exports": root_exports,
            "failure_codes": list(failure_codes),
            "expected_failure_codes": failure_codes,
            "public_signatures": list(signatures),
            "expected_public_signatures": signatures,
            "hash_domains": list(frozen["hash_and_dependency_boundary"]["hash_domain_suffix"]),
            "direct_edges": list(edges),
            "expected_direct_edges": edges,
            "dependency_rows": list(dependency_rows),
            "expected_dependency_rows": dependency_rows,
            "workflow_events": ["push", "pull_request", "workflow_dispatch"],
            "workflow_t0": list(T0_PATHS),
            "workflow_t1": list(T1_PATHS),
            "workflow_t2": list(T2_PATHS),
            "workflow_t2_event": "workflow_dispatch",
            "workflow_t3": [],
            "nonframework_job_hash": _sha256(nonframework),
            "expected_nonframework_job_hash": _sha256(nonframework),
            "filtering": False,
            "skipped_accepted": False,
            "expected_failure_accepted": False,
            "representative_substitution": False,
            "scientific_entries": [],
        }
        self.assertEqual(validators, tuple(tuple(row) for row in frozen["private_validator_signatures"]))
        self.assertEqual(tuple(name for name, _ in constants), tuple(frozen["private_constants"]))
        return baseline

    def _apply_authority_case_mutation(
        self, candidate: dict[str, object], row: dict[str, object]
    ) -> None:
        operation = row["mutation"]["op"]
        sentinel = f"P9C::{row['case_id']}::{operation}"
        if operation == "APPEND_UTF8_BYTES":
            path = row["mutation"]["path"]
            self.assertEqual(path, row["fixture"]["path"])
            candidate["current_path_bytes"][path] += row["mutation"]["value"].encode("utf-8")
        elif operation == "APPEND_ROOT_EXPORT":
            candidate["root_exports"].append(sentinel)
        elif operation == "APPEND_FAILURE_CODE":
            candidate["failure_codes"].append(sentinel)
        elif operation == "REPLACE_PUBLIC_SIGNATURE":
            module, name, _ = candidate["public_signatures"][0]
            candidate["public_signatures"][0] = (module, name, f"({sentinel}: str) -> None")
        elif operation == "APPEND_HASH_DOMAIN":
            candidate["hash_domains"].append(sentinel)
        elif operation == "REPLACE_PRIVATE_VALIDATOR_SIGNATURE":
            module, name, _ = candidate["validators"][0]
            candidate["validators"] = ((module, name, f"({sentinel}: str) -> None"),) + tuple(candidate["validators"])[1:]
        elif operation == "REPLACE_PRIVATE_CONSTANT":
            name, _ = candidate["constants"][0]
            candidate["constants"] = ((name, (sentinel,)),) + tuple(candidate["constants"])[1:]
        elif operation == "APPEND_DIRECT_EDGE":
            candidate["direct_edges"].append(("validation", sentinel))
        elif operation == "ADD_CYCLE":
            candidate["direct_edges"].append(("canonical", "validation"))
        elif operation == "FILTER_ONE_VECTOR":
            candidate["vector_ids"].pop()
        elif operation == "DECREMENT_COMPLETED_CHECK_COUNT":
            candidate["completed_checks"] -= 1
        elif operation == "REPLACE_PROJECTION_SHA256":
            candidate["vector_projection"] = "0" * 64
        elif operation == "RELABEL_CURRENT_BOOK_LOCK_AS_HISTORICAL":
            replacement = {
                key: candidate["current_book"][key]
                for key in candidate["expected_historical_book"]
            }
            candidate["historical_book"] = replacement
            locks = list(candidate["source_locks"])
            index = next(i for i, value in enumerate(locks) if value["path"] == "EBU_FUTURE_BOOKS_STRUCTURE.md")
            locks[index] = replacement
            candidate["source_locks"] = tuple(locks)
        elif operation == "USE_CURRENT_HEAD_FOR_HISTORICAL_LANE":
            candidate["historical_binding"] = candidate["current_binding"]
        elif operation == "USE_I9_TARGET_FOR_CURRENT_LANE":
            candidate["current_binding"] = candidate["historical_binding"]
        elif operation == "DROP_PUSH_TRIGGER":
            candidate["workflow_events"].remove("push")
        elif operation == "DROP_PULL_REQUEST_TRIGGER":
            candidate["workflow_events"].remove("pull_request")
        elif operation == "DROP_T0_JOB_OR_PATH":
            candidate["workflow_t0"].pop()
        elif operation == "DROP_T1_JOB_OR_PATH":
            candidate["workflow_t1"].pop()
        elif operation == "DROP_MANUAL_T2":
            candidate["workflow_t2"].clear()
        elif operation == "MAKE_T2_AUTOMATIC":
            candidate["workflow_t2_event"] = "push"
        elif operation == "ADD_T3_JOB_OR_PATH":
            candidate["workflow_t3"].append(sentinel)
        elif operation == "FILTER_TEST_OR_VECTOR":
            candidate["filtering"] = True
        elif operation == "ACCEPT_SKIPPED_TEST":
            candidate["skipped_accepted"] = True
        elif operation == "ACCEPT_EXPECTED_FAILURE":
            candidate["expected_failure_accepted"] = True
        elif operation == "SUBSTITUTE_REPRESENTATIVE_INTERFACE":
            candidate["representative_substitution"] = True
        elif operation == "READ_CURRENT_FILES_AS_HISTORICAL_LOCKS":
            candidate["historical_data_source"] = "CURRENT_WORKTREE"
        elif operation == "MODIFY_UNAUTHORIZED_SOURCE_PATH":
            candidate["current_source_identity_valid"] = False
        elif operation == "ADD_LATER_DOC_TO_I9_FOUR_PATH_DELTA":
            candidate["historical_delta_paths"] += (LATER_DOCUMENTATION_PATHS[0],)
        elif operation == "ADD_PRODUCTION_MODULE_PATH":
            candidate["scope_paths"].append("src/ebu_framework/post_i9_unauthorized.py")
        elif operation == "MODIFY_DEPENDENCY_OR_FIXTURE":
            path, mode, byte_count, _ = candidate["dependency_rows"][0]
            candidate["dependency_rows"][0] = (path, mode, byte_count, _sha256(sentinel.encode()))
        elif operation == "MUTATE_SOURCE_LOCK_RAW_IDENTITY":
            locks = list(candidate["source_locks"])
            locks[0] = dict(locks[0], raw_sha256="f" * 64)
            candidate["source_locks"] = tuple(locks)
        elif operation == "DISAGREE_TREE_AND_ARCHIVE_ROUTES":
            candidate["archive_route_identity"] = "f" * 64
        elif operation == "RELABEL_AUTHORITY_COORDINATE":
            candidate["coordinate_chain"]["accepted_i9_authority_target"]["commit"] = IMPLEMENTATION_BASE_COMMIT
        elif operation == "ACCEPT_ZERO_COMPLETED_CHECKS":
            candidate["completed_checks"] = 0
        elif operation == "MODIFY_NONFRAMEWORK_TEST_JOB":
            candidate["nonframework_job_hash"] = _sha256(sentinel.encode())
        elif operation == "ADD_MODEL_POLICY_STATE_RUNNER_OR_NETWORK_ENTRY":
            candidate["scientific_entries"].append("model")
        elif operation == "DELETE_RENAME_OR_MODE_CHANGE_AUTHORIZED_PATH":
            candidate["scope_modes"][POST_I9_AUTHORIZED_PATHS[0]] = "100755"
        else:
            raise AssertionError(f"unknown closed authority mutation: {operation}")

    def _case_graph_has_cycle(self, edges: list[tuple[str, str]]) -> bool:
        graph = {}
        for source, target in edges:
            graph.setdefault(source, []).append(target)
            graph.setdefault(target, [])
        visiting = set()
        visited = set()

        def visit(node: str) -> bool:
            if node in visiting:
                return True
            if node in visited:
                return False
            visiting.add(node)
            if any(visit(target) for target in graph[node]):
                return True
            visiting.remove(node)
            visited.add(node)
            return False

        return any(visit(node) for node in graph)

    def _evaluate_case(self, candidate: dict[str, object]) -> str:
        if candidate["coordinate_chain"] != candidate["expected_coordinate_chain"]:
            return "FAIL_COORDINATE_RELABEL"
        if candidate["historical_binding"] != candidate["expected_historical_binding"]:
            return "FAIL_CURRENT_SUBSTITUTED_FOR_HISTORY"
        if candidate["current_binding"] != candidate["expected_current_binding"]:
            return "FAIL_HISTORY_SUBSTITUTED_FOR_CURRENT"
        if candidate["historical_data_source"] != "IMMUTABLE_GIT_OBJECTS":
            return "FAIL_CURRENT_FILES_AS_HISTORY"
        if candidate["tree_route_identity"] != candidate["archive_route_identity"]:
            return "FAIL_GIT_ROUTE_DISAGREEMENT"
        if candidate["historical_book"] != candidate["expected_historical_book"]:
            return "FAIL_STALE_LOCK_RELABEL"
        if candidate["source_locks"] != candidate["expected_source_locks"]:
            return "FAIL_SOURCE_LOCK_DRIFT"
        if candidate["historical_delta_paths"] != candidate["expected_historical_delta_paths"]:
            return "FAIL_HISTORICAL_DELTA_BROADENING"
        if any(path.startswith("src/") for path in set(candidate["scope_paths"]) - set(POST_I9_AUTHORIZED_PATHS)):
            return "FAIL_SCOPE_BROADENING"
        if tuple(candidate["scope_paths"]) != POST_I9_AUTHORIZED_PATHS or any(
            candidate["scope_modes"].get(path) != "100644" for path in POST_I9_AUTHORIZED_PATHS
        ):
            return "FAIL_PATH_CONSTRUCTION"
        if any(
            _sha256(candidate["current_path_bytes"][path]) != expected
            for path, expected in candidate["current_path_hashes"].items()
        ):
            return "FAIL_UNAUTHORIZED_I9_IMPLEMENTATION_PATH_DRIFT"
        if not candidate["current_source_identity_valid"]:
            return "FAIL_CURRENT_SOURCE_DRIFT"
        if tuple(candidate["validators"]) != candidate["expected_validators"]:
            return "FAIL_VALIDATOR_DRIFT"
        if tuple(candidate["constants"]) != candidate["expected_constants"]:
            return "FAIL_CONSTANT_DRIFT"
        if tuple(candidate["vector_ids"]) != candidate["expected_vector_ids"]:
            return "FAIL_VECTOR_DRIFT"
        if candidate["completed_checks"] == 0:
            return "FAIL_ZERO_CHECK_ACCEPTANCE"
        if candidate["completed_checks"] != 292:
            return "FAIL_COUNT_DRIFT"
        if candidate["vector_projection"] != candidate["expected_vector_projection"]:
            return "FAIL_PROJECTION_DRIFT"
        if tuple(candidate["root_exports"]) != candidate["expected_root_exports"]:
            return "FAIL_ROOT_EXPORT_DRIFT"
        if tuple(candidate["failure_codes"]) != candidate["expected_failure_codes"]:
            return "FAIL_FAILURE_CODE_DRIFT"
        if tuple(candidate["public_signatures"]) != candidate["expected_public_signatures"]:
            return "FAIL_PUBLIC_SIGNATURE_DRIFT"
        if candidate["hash_domains"]:
            return "FAIL_HASH_DOMAIN_DRIFT"
        if self._case_graph_has_cycle(candidate["direct_edges"]):
            return "FAIL_GRAPH_CYCLE"
        if tuple(candidate["direct_edges"]) != candidate["expected_direct_edges"]:
            return "FAIL_GRAPH_DRIFT"
        if tuple(candidate["dependency_rows"]) != candidate["expected_dependency_rows"]:
            return "FAIL_DEPENDENCY_OR_FIXTURE_DRIFT"
        if "push" not in candidate["workflow_events"]:
            return "FAIL_PUSH_TRIGGER_LOSS"
        if "pull_request" not in candidate["workflow_events"]:
            return "FAIL_PULL_REQUEST_TRIGGER_LOSS"
        if tuple(candidate["workflow_t0"]) != T0_PATHS:
            return "FAIL_T0_LOSS"
        if tuple(candidate["workflow_t1"]) != T1_PATHS:
            return "FAIL_T1_LOSS"
        if tuple(candidate["workflow_t2"]) != T2_PATHS:
            return "FAIL_T2_LOSS"
        if candidate["workflow_t2_event"] != "workflow_dispatch":
            return "FAIL_T2_GATE_BROADENING"
        if candidate["workflow_t3"]:
            return "FAIL_T3_INTRODUCTION"
        if candidate["nonframework_job_hash"] != candidate["expected_nonframework_job_hash"]:
            return "FAIL_SCIENTIFIC_SEMANTICS_CHANGE"
        if candidate["filtering"]:
            return "FAIL_FILTERING"
        if candidate["skipped_accepted"]:
            return "FAIL_SKIP_MASKING"
        if candidate["expected_failure_accepted"]:
            return "FAIL_EXPECTED_FAILURE_MASKING"
        if candidate["representative_substitution"]:
            return "FAIL_REPRESENTATIVE_SUBSTITUTION"
        if candidate["scientific_entries"]:
            return "FAIL_FORBIDDEN_REACHABILITY"
        return "PASS"

    def _dynamic_replay(self, validation_contract) -> None:
        source_path = str(ROOT / "src")
        tests_path = str(ROOT / "tests/framework")
        if source_path not in sys.path:
            sys.path.insert(0, source_path)
        if tests_path not in sys.path:
            sys.path.insert(0, tests_path)

        from ebu_framework import capabilities
        from ebu_framework import validation
        from ebu_framework.errors import Applicability, FrameworkError
        from ebu_framework.identity import SourceFileRawSha256
        from safety import i9_forbidden_observation_guard

        owners = {name: getattr(validation, name) for name in PRIVATE_NAMES}
        baselines = validation_contract["construction_baselines"]
        outcomes = {"SUCCESS": 0, "FAILURE": 0}
        owner_calls = {name: 0 for name in PRIVATE_NAMES}
        active_predicates = 0
        completed_checks = 0
        delegated_calls = 0
        failure_coordinates = {}

        real_delegate = capabilities._issue_t2_fixture_capability
        with mock.patch.object(
            capabilities,
            "_issue_t2_fixture_capability",
            wraps=real_delegate,
        ) as delegated:
            for vector in validation_contract["vectors"][:69]:
                construction = vector["construction"]
                baseline = baselines[construction["baseline_id"]]
                materialized = _apply_mutations(
                    baseline, construction["closed_mutation_program"]
                )
                self.assertEqual(materialized, construction["materialized_call"])
                _assert_projection(
                    materialized, construction["materialized_call_identity"]
                )
                owner_name = materialized["owner"]
                self.assertEqual(vector["owner_interface"], f"validation.{owner_name}")
                materializers = materialized["argument_materialization"]
                positional = materialized["positional"]
                self.assertEqual(len(materializers), len(positional))
                arguments = []
                for materializer, value in zip(materializers, positional):
                    if materializer == "str":
                        arguments.append(value)
                    elif materializer == "SourceFileRawSha256('sha256-raw:'+value)":
                        arguments.append(SourceFileRawSha256("sha256-raw:" + value))
                    elif materializer.startswith("tuple["):
                        arguments.append(_recursive_tuple(value))
                    else:
                        raise AssertionError(f"unknown argument materializer: {materializer}")

                before_delegate = delegated.call_count
                owner_calls[owner_name] += 1
                expected = vector["expected"]
                with i9_forbidden_observation_guard():
                    if expected["outcome"] == "SUCCESS":
                        result = owners[owner_name](*arguments)
                    else:
                        with self.assertRaises(FrameworkError) as caught:
                            owners[owner_name](*arguments)
                        result = caught.exception
                delta = delegated.call_count - before_delegate
                delegated_calls += delta
                self.assertEqual(delta, vector["delegated_owner_call_count"])

                if expected["outcome"] == "SUCCESS":
                    outcomes["SUCCESS"] += 1
                    if result is None:
                        projection = {"return": "None"}
                    else:
                        projection = {
                            "authorized_interface": object.__getattribute__(
                                result, "authorized_interface"
                            ),
                            "capability_class": type(result).__name__,
                            "case_id": object.__getattribute__(result, "case_id"),
                            "fixture_path": object.__getattribute__(result, "fixture_path"),
                            "fixture_raw_sha256": object.__getattribute__(
                                result, "fixture_raw_sha256"
                            ).hex_digest,
                        }
                    self.assertEqual(projection, expected["result_projection"])
                    _assert_projection(projection, expected["result_projection_identity"])
                else:
                    outcomes["FAILURE"] += 1
                    envelope = result.envelope
                    precedence = vector["precedence"]
                    ordinal = precedence["first_failure_ordinal"]
                    self.assertEqual(envelope.failure_ordinal, ordinal)
                    self.assertEqual(envelope.failure_code.value, expected["failure_code"])
                    self.assertEqual(envelope.stage.value, "I-9")
                    self.assertEqual(envelope.interface_ref.module, "ebu_framework.validation")
                    self.assertEqual(envelope.interface_ref.qualname, owner_name)
                    self.assertEqual(envelope.interface_ref.interface_version, "1.0.0")
                    self.assertEqual(envelope.object_refs, ())
                    self.assertIs(envelope.event_key, Applicability.NOT_APPLICABLE)
                    failure_id = _derive_i9_failure_id(
                        expected["failure_code"], owner_name, ordinal
                    )
                    self.assertEqual(str(envelope.failure_id), failure_id)
                    self.assertEqual(expected["failure_id"], failure_id)
                    coordinate = (expected["failure_code"], owner_name, ordinal)
                    if failure_id in failure_coordinates:
                        self.assertEqual(failure_coordinates[failure_id], coordinate)
                    failure_coordinates[failure_id] = coordinate

                active_predicates += len(vector["precedence"]["active_predicates"])
                completed_checks += vector["precedence"]["completed_check_count"]

        self.assertEqual(outcomes, {"SUCCESS": 19, "FAILURE": 50})
        self.assertEqual(sum(owner_calls.values()), 69)
        self.assertTrue(all(count > 0 for count in owner_calls.values()))
        self.assertEqual(active_predicates, 50)
        self.assertEqual(completed_checks, 264)
        self.assertEqual(delegated_calls, 2)
        self.assertEqual(len(failure_coordinates), 37)
        self.assertEqual(
            validation_contract["failure_identity_contract"]["collision_audit"][
                "distinct_coordinate_collision_count"
            ],
            0,
        )


if __name__ == "__main__":
    unittest.main()
