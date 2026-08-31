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
import unicodedata
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
STAGE_D_DYNAMIC_GROWTH_ACCEPTED_BASE_COMMIT = (
    "5a66c674a3a9a23861ac11b986754b2022e277dc"
)
STAGE_D_DYNAMIC_GROWTH_ACCEPTED_BASE_TREE = (
    "ee38ece14a945ddc8d4108f54ff2b813360c8c58"
)
STAGE_D_DYNAMIC_GROWTH_AUTHORITY_CANDIDATE = (
    "295e4a75b5d4e8eacfd203d7dc75b2e49f728964"
)
STAGE_D_DYNAMIC_GROWTH_AUTHORITY_TARGET = (
    "8739e29f8d3762dd755008759d266c7773f4f182"
)
STAGE_D_DYNAMIC_GROWTH_AUTHORITY_TREE = (
    "e0d73434ec16b9142d77ebf4e4459f4ca281eb70"
)
STAGE_D_DYNAMIC_GROWTH_AUTHORITY_CHAIN = (
    "de1269da8cc33d7ca34f51fb7194bc11a1d2da60",
    "78bc26b7ac938b570af0b6f32eaab07b116abd6b",
    "c53ebc4614115e00b72365b0a650becb5dc474b2",
    STAGE_D_DYNAMIC_GROWTH_AUTHORITY_CANDIDATE,
)
STAGE_D_DYNAMIC_GROWTH_AUTHORITY_PATHS = (
    "STAGE_D_DYNAMIC_GROWTH_CAMPAIGN_AUTHORITY_AMENDMENT.md",
    "stage_d_dynamic_growth_campaign_contract.json",
    "stage_d_dynamic_growth_campaign_evidence_schema.json",
    "stage_d_dynamic_growth_campaign_predecessor_manifest.json",
    "stage_d_dynamic_growth_campaign_validation_contract.json",
)
STAGE_D_DYNAMIC_GROWTH_AUTHORITY_RAW_SHA256 = {
    "STAGE_D_DYNAMIC_GROWTH_CAMPAIGN_AUTHORITY_AMENDMENT.md": (
        "5e55617ee5c1f107567685e81377f1a697a4b7d49ce0e844ee1b3dbf72aec0eb"
    ),
    "stage_d_dynamic_growth_campaign_contract.json": (
        "7d9ce96dba89f46771a08747c7c5db7762e94f2072bb83fdf8bcc1e68e6e3c22"
    ),
    "stage_d_dynamic_growth_campaign_evidence_schema.json": (
        "be93bb6ad0abbc8605e293d3bb7f7ec1634cf55e71dff57372b7078810afe8e9"
    ),
    "stage_d_dynamic_growth_campaign_predecessor_manifest.json": (
        "c729fa3b038ba479b6a7651a24e620a36b0bfea6f901a72b7b8c19b1c0b9c312"
    ),
    "stage_d_dynamic_growth_campaign_validation_contract.json": (
        "4c85d28f822558fbabee47cb2b294cf1f9ad85936b4fe388e06243e4d83fa0d2"
    ),
}
STAGE_D_DYNAMIC_GROWTH_AUTHORITY_CANONICAL_SHA256 = {
    "stage_d_dynamic_growth_campaign_contract.json": (
        "3b634d78956d7dbff485fe75bca35aa6f79f61fb14523421b29ba30991f066df"
    ),
    "stage_d_dynamic_growth_campaign_evidence_schema.json": (
        "f1bde9a46f8ddafb9a539e011814bb83e3a41d12dba9b0305037b960eefc698d"
    ),
    "stage_d_dynamic_growth_campaign_predecessor_manifest.json": (
        "1ea6cd84eabb987966f4910bce9b6a20b03eeff0dc4d9cab7181d84c9be1f8a7"
    ),
    "stage_d_dynamic_growth_campaign_validation_contract.json": (
        "04d84cfad9bf7c14d1b7940c87300dc22491871669952f5acd2586f33fbb3634"
    ),
}
STAGE_D_DYNAMIC_GROWTH_AUTHORITY_SCOPE = STAGE_E_AUTHORITY_SCOPE | frozenset(
    STAGE_D_DYNAMIC_GROWTH_AUTHORITY_PATHS
)
STAGE_E_RECONCILIATION_ACCEPTED_BASE_COMMIT = (
    "08cea14d828668413b9156da8f220beec2713c26"
)
STAGE_E_RECONCILIATION_ACCEPTED_BASE_TREE = (
    "a1b690662e14eab7220492dd378fce93b15eb9c7"
)
STAGE_E_RECONCILIATION_AUTHORITY_CANDIDATE = (
    "ff82a5ea1658f86cb3a9b4120583efa575f71ce9"
)
STAGE_E_RECONCILIATION_AUTHORITY_TARGET = (
    "0c8e8d8824b50fcdc5817d1c27ccea1a7c094ae6"
)
STAGE_E_RECONCILIATION_AUTHORITY_TREE = (
    "55387ce0b1009b00b36ad6eb2e46fc6aa6ad69e4"
)
STAGE_E_RECONCILIATION_AUTHORITY_CHAIN = (
    "1191d4d4815a65609b7f55182ef5110b1722583b",
    "2dd1776a4694e2e585030379c48f73ae0de27f66",
    "0add7f1299c18b8a032bf4db3631149012e51477",
    "68a7ec7a4a36a1fa2e4806bf34580b01591df31e",
    "00d15dd0fa048c7e07f2d683b531b74bdf1f1d45",
    STAGE_E_RECONCILIATION_AUTHORITY_CANDIDATE,
)
STAGE_E_RECONCILIATION_AUTHORITY_PATHS = (
    "STAGE_E_DYNAMIC_GROWTH_HARNESS_RECONCILIATION_AUTHORITY_AMENDMENT.md",
    "stage_e_dynamic_growth_harness_reconciliation_contract.json",
    "stage_e_dynamic_growth_harness_reconciliation_evidence_schema.json",
    "stage_e_dynamic_growth_harness_reconciliation_implementation_path_manifest.json",
    "stage_e_dynamic_growth_harness_reconciliation_predecessor_manifest.json",
    "stage_e_dynamic_growth_harness_reconciliation_validation_contract.json",
)
STAGE_E_RECONCILIATION_AUTHORITY_RAW_SHA256 = {
    "STAGE_E_DYNAMIC_GROWTH_HARNESS_RECONCILIATION_AUTHORITY_AMENDMENT.md": (
        "5f791746390ff39ff1b4f730ba37f7c9687ee5a7dd9efda429727a7ef76d5728"
    ),
    "stage_e_dynamic_growth_harness_reconciliation_contract.json": (
        "115268c17fd5fecbb6eccaf71b3317e6915f413bae217da4685fd1fd9f417ad9"
    ),
    "stage_e_dynamic_growth_harness_reconciliation_evidence_schema.json": (
        "7aea36d0a010e849f1490e9e964756a61335804cefefa5d84059bf739ff399ee"
    ),
    "stage_e_dynamic_growth_harness_reconciliation_implementation_path_manifest.json": (
        "bcd88263976eb6ee333b257965f6727dc716793d6d1214642620cdecc10b5b99"
    ),
    "stage_e_dynamic_growth_harness_reconciliation_predecessor_manifest.json": (
        "6d5426dcdeeeed95dbcd32545d47ffb5ad3dbc35070fd8981c0a1a9409758467"
    ),
    "stage_e_dynamic_growth_harness_reconciliation_validation_contract.json": (
        "de108dea3e59ba95301824094dfb2f72652a0a97ffda48e08b2dd7d42c867986"
    ),
}
STAGE_E_RECONCILIATION_AUTHORITY_CANONICAL_SHA256 = {
    "stage_e_dynamic_growth_harness_reconciliation_contract.json": (
        "c3604cec4d9d75779edbd8a24c3061f5f9135816a2be1d49eecf4d7517843f96"
    ),
    "stage_e_dynamic_growth_harness_reconciliation_evidence_schema.json": (
        "4d14b1e980f44f4717d0e47e8eab0ffc88a65eef9f05757d30b9a38e06d5a994"
    ),
    "stage_e_dynamic_growth_harness_reconciliation_implementation_path_manifest.json": (
        "cc9c76ac54de74bdaf6797268e1b8f016fc33026cc29c77980cc88e60f9df077"
    ),
    "stage_e_dynamic_growth_harness_reconciliation_predecessor_manifest.json": (
        "e16a638a586ccc83dcc46e3848f28050658ae47c57848c7e7ca4bfd85253827a"
    ),
    "stage_e_dynamic_growth_harness_reconciliation_validation_contract.json": (
        "7adb3d55b2a2fcf51dbc724443f25e0cffe65abeb0025e7305e5892c1776e791"
    ),
}
STAGE_E_RECONCILIATION_ADDED_HARNESS_PATHS = (
    "stage_e_harness/growth.py",
    "stage_e_harness/recursive.py",
    "stage_e_harness/capacity_population.py",
    "tests/stage_e/test_dynamic_growth_conformance.py",
    "tests/stage_e/test_capacity_population_conformance.py",
)
STAGE_E_RECONCILED_HARNESS_IMPLEMENTATION_PATHS = (
    STAGE_E_HARNESS_IMPLEMENTATION_PATHS[:18]
    + STAGE_E_RECONCILIATION_ADDED_HARNESS_PATHS[:3]
    + STAGE_E_HARNESS_IMPLEMENTATION_PATHS[18:]
    + STAGE_E_RECONCILIATION_ADDED_HARNESS_PATHS[3:]
)
STAGE_E_RECONCILIATION_AUTHORITY_SCOPE = (
    STAGE_D_DYNAMIC_GROWTH_AUTHORITY_SCOPE
    | frozenset(STAGE_E_RECONCILIATION_AUTHORITY_PATHS)
)
STAGE_E_RECONCILED_HARNESS_IMPLEMENTATION_SCOPE = (
    STAGE_E_RECONCILIATION_AUTHORITY_SCOPE
    | frozenset(STAGE_E_RECONCILED_HARNESS_IMPLEMENTATION_PATHS)
)
STAGE_F_LOCAL_BINDING_ACCEPTED_BASE_COMMIT = (
    "c43ead831c3e4021405985134ed564b761bb1aed"
)
STAGE_F_LOCAL_BINDING_ACCEPTED_BASE_TREE = (
    "212777d569af527ce9532ea6c836ff2225465d87"
)
STAGE_F_LOCAL_BINDING_AUTHORITY_CANDIDATE = (
    "c683040869ecbbe439835a8fabd0a6c3d7ea0e3d"
)
STAGE_F_LOCAL_BINDING_AUTHORITY_TARGET = (
    "4ab6a8a8b158e6ff32d06e67d29a3d974a6326be"
)
STAGE_F_LOCAL_BINDING_AUTHORITY_TREE = (
    "46ce30f0c3675836b449bc2fb00ae22a688ca287"
)
STAGE_F_LOCAL_BINDING_AUTHORITY_CHAIN = (
    "0727f59c7f8071724e4661048f0afaa25267b291",
    "6d7f59449d895ad23c02f3cc8eee1d4d4747565e",
    "1357fef2ad3bff2ecc482a108fba7e9063fe81da",
    "ba6002a24696ae780706cc030bebb53df2bd820b",
    "152f809b7cac4dbbdd64d4c006b0bdcc63206a5f",
    "a9a23cf45bcb6ae0831a1d1683921ef092c75f82",
    "b688a3bad48d41b85fd608c306ad8db4919a3271",
    "0c218d5e2b8bb6f43be1c6a0a15b74d89e8b9133",
    "bd08f1e2695b8d4f600858413e05f3960aab9098",
    "5b5cd95d6c7dd34f1e6fd9cdb402c90e5b0f1d8f",
    "4f639decf09594de73558152af91b15884a14de9",
    "f61532d45f9400db4616f250659e0b84fe91a6da",
    "ffae1444e2c9ddac4163294388535275fe5da410",
    "24024beec928bfad6496af9b57fa47ff76310571",
    "c484f8fb3ff23a0a8a1f9de78782581cab67e537",
    "b0917eeaf71fb920a01b752e0f02275563411afc",
    "f3a3219b307d669afa753cfaa3bc68e9cbadf218",
    STAGE_F_LOCAL_BINDING_AUTHORITY_CANDIDATE,
)
STAGE_F_LOCAL_BINDING_AUTHORITY_PATHS = (
    "STAGE_F_LOCAL_EXECUTION_BINDING_AUTHORITY_AMENDMENT.md",
    "stage_f_local_execution_binding_contract.json",
    "stage_f_local_execution_binding_evidence_schema.json",
    "stage_f_local_execution_binding_implementation_path_manifest.json",
    "stage_f_local_execution_binding_predecessor_manifest.json",
    "stage_f_local_execution_binding_validation_contract.json",
)
STAGE_F_LOCAL_BINDING_AUTHORITY_RAW_SHA256 = {
    "STAGE_F_LOCAL_EXECUTION_BINDING_AUTHORITY_AMENDMENT.md": (
        "05b5679e61991c692b8f245d22897665089dafc25d0769590b3b0ad153fecad0"
    ),
    "stage_f_local_execution_binding_contract.json": (
        "74b582fae72216f2234aa7de354586a3ff679147a89b9bad4f7df43082a9d59f"
    ),
    "stage_f_local_execution_binding_evidence_schema.json": (
        "0062377ea1aea416e09e6c149ec3973f5aab632a0b84b438d7e181aee505a396"
    ),
    "stage_f_local_execution_binding_implementation_path_manifest.json": (
        "befdb7b717be75f7b62f6489d053274bad9330f7b8f53f2a5b4c0d4da059ae23"
    ),
    "stage_f_local_execution_binding_predecessor_manifest.json": (
        "28ffee108f64c9b0f0341cdf61b51437ed315ee2b84d9979cbfeb89c6bd6baab"
    ),
    "stage_f_local_execution_binding_validation_contract.json": (
        "6550603ec759580660300d10361cac66ef43b7d657ac1f49672d712ba5de1abf"
    ),
}
STAGE_F_LOCAL_BINDING_AUTHORITY_CANONICAL_SHA256 = {
    "stage_f_local_execution_binding_contract.json": (
        "087b06257389fe726e583b15b41199550eaafec41599988019c0a4b2c77e277c"
    ),
    "stage_f_local_execution_binding_evidence_schema.json": (
        "a38dffe3326cf9d732218a7291be356f10c93af7c50c702a29deb70e8a863452"
    ),
    "stage_f_local_execution_binding_implementation_path_manifest.json": (
        "f51427478cc13145a4fada6ad12d55988ddc43d1db84984067b357d117f603f4"
    ),
    "stage_f_local_execution_binding_predecessor_manifest.json": (
        "d501dd8bf0f70435b67347c5251f0612bfd9a363702a138b61e744fae552c634"
    ),
    "stage_f_local_execution_binding_validation_contract.json": (
        "10da4c6789d370ea4ff013c5fa8ceb41a361115c9e2b52802052c83bcf6cce4a"
    ),
}
STAGE_F_BINDING_EVIDENCE_CORRECTION_REQUIRED_BASE_COMMIT = (
    "1033501b77f7f55ed9aacd9a71cef95f81966e4a"
)
STAGE_F_BINDING_EVIDENCE_CORRECTION_REQUIRED_BASE_TREE = (
    "d8ffbd105eb76cfbb72472772e07f18a11112db3"
)
STAGE_F_BINDING_EVIDENCE_CORRECTION_CANDIDATE = (
    "dd1a38aee4a6c1048122cb2b5a4e7cf542c5e101"
)
STAGE_F_BINDING_EVIDENCE_CORRECTION_TARGET = (
    "db9d305be120e69d00be14f0d07e06999ca77999"
)
STAGE_F_BINDING_EVIDENCE_CORRECTION_TREE = (
    "c5d6e6c53528ae64a90151d286feb2cc62be47be"
)
STAGE_F_BINDING_EVIDENCE_CORRECTION_PATHS = (
    "STAGE_F_LOCAL_EXECUTION_BINDING_EVIDENCE_CORRECTION_AUTHORITY_AMENDMENT.md",
    "stage_f_local_execution_binding_evidence_correction_contract.json",
    "stage_f_local_execution_binding_evidence_correction_schema.json",
    "stage_f_local_execution_binding_evidence_correction_implementation_path_manifest.json",
    "stage_f_local_execution_binding_evidence_correction_predecessor_manifest.json",
    "stage_f_local_execution_binding_evidence_correction_validation_contract.json",
)
STAGE_F_BINDING_EVIDENCE_CORRECTION_ROWS = (
    (
        "STAGE_F_LOCAL_EXECUTION_BINDING_EVIDENCE_CORRECTION_AUTHORITY_AMENDMENT.md",
        "100644",
        "f0506c94553d8240086525e2218077915fde900d",
        63947,
        "4e49bd26a2e28fc8703de447d18e541eb04b64f4856953bf96e1da57fd93e0c4",
    ),
    (
        "stage_f_local_execution_binding_evidence_correction_contract.json",
        "100644",
        "a2204c4e7a8625d4c21e8f7af09c6aeabfd94f34",
        51342,
        "83a0d753bd30ee56af585e9f191e0319f7b2fe6070ff088ea60a9149f859b94f",
    ),
    (
        "stage_f_local_execution_binding_evidence_correction_schema.json",
        "100644",
        "cf1369548d55b6f85d486ac20a6c28f45f46596c",
        654186,
        "9a74d517029a684a0889f1460df253f0757c8e712a961670d888a90dc2389673",
    ),
    (
        "stage_f_local_execution_binding_evidence_correction_implementation_path_manifest.json",
        "100644",
        "ee1c9f57328efc1eac51530822f4c667f1648916",
        5788,
        "734aeef99d900700bc1fea89ea94932b904ff126d5197dd6a01d10fe4aa87919",
    ),
    (
        "stage_f_local_execution_binding_evidence_correction_predecessor_manifest.json",
        "100644",
        "b29e67292febabfd91debe245fd164d0377d6567",
        5270,
        "1e9162e64f9e1d89cdaa87a7701441b76d0d63e7a804d1129b140c52e5ebfc58",
    ),
    (
        "stage_f_local_execution_binding_evidence_correction_validation_contract.json",
        "100644",
        "bd8639ed159953062c844109332895fedae5e990",
        31186,
        "29a53c1fb987f48a7ed89d9344cf715927839fd31f093e6e13c2c612ffe8c050",
    ),
)
STAGE_F_FINAL_EVIDENCE_CLOSURE_REQUIRED_BASE_COMMIT = (
    "f47648320be2054edf51a166b0e7fd7e9ab20594"
)
STAGE_F_FINAL_EVIDENCE_CLOSURE_REQUIRED_BASE_TREE = (
    "382472276e7fbb7b483cc120467f23f83bc25ca3"
)
STAGE_F_FINAL_EVIDENCE_CLOSURE_CANDIDATE = (
    "b6452dcf69cb9ee46ce01b03f86d97a80c348713"
)
STAGE_F_FINAL_EVIDENCE_CLOSURE_TARGET = (
    "1f4650411ea360d82df3e9f0708af32a58608729"
)
STAGE_F_FINAL_EVIDENCE_CLOSURE_TREE = (
    "bd9e8610b70b9f06f15fb18d9045d2cb933e173a"
)
STAGE_F_FINAL_EVIDENCE_CLOSURE_PATHS = (
    "STAGE_F_LOCAL_EXECUTION_BINDING_FINAL_EVIDENCE_CLOSURE_CORRECTION_AUTHORITY_AMENDMENT.md",
    "stage_f_local_execution_binding_final_evidence_closure_correction_contract.json",
    "stage_f_local_execution_binding_final_evidence_closure_correction_schema.json",
    "stage_f_local_execution_binding_final_evidence_closure_correction_implementation_path_manifest.json",
    "stage_f_local_execution_binding_final_evidence_closure_correction_predecessor_manifest.json",
    "stage_f_local_execution_binding_final_evidence_closure_correction_validation_contract.json",
)
STAGE_F_FINAL_EVIDENCE_CLOSURE_ROWS = (
    (
        "STAGE_F_LOCAL_EXECUTION_BINDING_FINAL_EVIDENCE_CLOSURE_CORRECTION_AUTHORITY_AMENDMENT.md",
        "100644",
        "89ef316dda859426e67e610f74eda9713e391a49",
        39038,
        "0e5e91d9e96cc18ab8fa5ecc324c2e1027f432c676f0465ba80991f2b150fd6d",
    ),
    (
        "stage_f_local_execution_binding_final_evidence_closure_correction_contract.json",
        "100644",
        "ac80a0e8d870016b8aaf9044bc51fcd0474527c5",
        33226,
        "f8435c21acb6534bee37a30c27de6f84ecbaa7a7f80c73f7083522d0bff434e1",
    ),
    (
        "stage_f_local_execution_binding_final_evidence_closure_correction_schema.json",
        "100644",
        "db8268a009ed4a20e056f62f236c12d1b0f7c131",
        833194,
        "b3bc610e1e6ded0e75de13ac30c36dafd72d3432fd9517cb80815ecb07396b67",
    ),
    (
        "stage_f_local_execution_binding_final_evidence_closure_correction_implementation_path_manifest.json",
        "100644",
        "6025cd89480de6f93f756cfa6b2e22d8eb26de77",
        7866,
        "6a592444ebcb7991fe19f4bbdbe1f9a2477693bd3655ecf55ddb6de99b2e0d50",
    ),
    (
        "stage_f_local_execution_binding_final_evidence_closure_correction_predecessor_manifest.json",
        "100644",
        "d7912bb26b638e8dbffb24155f4c1c1aff2eac12",
        9025,
        "1daeefbcbcbb8cb2cbc014c04ccac4b509113be787970b10c67e41710ed31c78",
    ),
    (
        "stage_f_local_execution_binding_final_evidence_closure_correction_validation_contract.json",
        "100644",
        "9f1516dc4a629c3ad3b6d427d75944237f3e27f2",
        65712,
        "25ed317603593bcdb3495696deb2db88b4e1e8e2be1ef5ba8a1cb94bb3c3c86c",
    ),
)
STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_REQUIRED_BASE_COMMIT = (
    "06a1b1400d5bd15cdfb50363333602c58b5ac692"
)
STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_REQUIRED_BASE_TREE = (
    "ca0bd70c96c0a6d9542ce9656be78a11465662f3"
)
STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_CANDIDATE = (
    "fcb38eb1acffeb11e4a63f0fc17bd92cf5548d63"
)
STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_TARGET = (
    "be7f180547a144f1a4dbf3f9d88bc6c20af95fcb"
)
STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_TREE = (
    "aeeecb9b0a49a1486adf6e10107e7d9af07d07b3"
)
STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_PATHS = (
    "STAGE_F_LOCAL_EXECUTION_BINDING_ATTEMPT_ROOT_BOOTSTRAP_CORRECTION_AUTHORITY_AMENDMENT.md",
    "stage_f_local_execution_binding_attempt_root_bootstrap_correction_contract.json",
    "stage_f_local_execution_binding_attempt_root_bootstrap_correction_schema.json",
    "stage_f_local_execution_binding_attempt_root_bootstrap_correction_implementation_path_manifest.json",
    "stage_f_local_execution_binding_attempt_root_bootstrap_correction_predecessor_manifest.json",
    "stage_f_local_execution_binding_attempt_root_bootstrap_correction_validation_contract.json",
)
STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_ROWS = (
    (
        "STAGE_F_LOCAL_EXECUTION_BINDING_ATTEMPT_ROOT_BOOTSTRAP_CORRECTION_AUTHORITY_AMENDMENT.md",
        "100644",
        "d91d115da9d9b88b3b0e1371939105d2428f264d",
        15470,
        "2fd8181d4a4b3fb74d12a6f7a94e39ad9dec6c78d012bd1661468bcebfdcb470",
    ),
    (
        "stage_f_local_execution_binding_attempt_root_bootstrap_correction_contract.json",
        "100644",
        "21c5ae1bb46b480121ba811f4e83c5df27e9848b",
        38266,
        "c3fb378f8e40c1a507a2ea97fc44899f915087091788991b8d5fb97457e50693",
    ),
    (
        "stage_f_local_execution_binding_attempt_root_bootstrap_correction_schema.json",
        "100644",
        "ff30f37135d92b00d8c6d238bff9b373f4d0e8f0",
        878634,
        "51e679986ee4122e258075c5aa3d7c1fd088711f9f215c1b93ba54ae44d1a0be",
    ),
    (
        "stage_f_local_execution_binding_attempt_root_bootstrap_correction_implementation_path_manifest.json",
        "100644",
        "5fd765fe17c807e6ec742c82b159ad3ac8ab1a3c",
        8918,
        "1dbc429a4935bbf927b8beafabc03bf281b2d908740ffa9034b0983587fa1f67",
    ),
    (
        "stage_f_local_execution_binding_attempt_root_bootstrap_correction_predecessor_manifest.json",
        "100644",
        "08df778f711c258c085eb1e232b5b4de8310ffd9",
        11622,
        "cae7faee780ae97682791db98aabf80258327459fef2848302809830ebb8cc00",
    ),
    (
        "stage_f_local_execution_binding_attempt_root_bootstrap_correction_validation_contract.json",
        "100644",
        "a7fa65fd2fbac07ef282e226fcdf151de785778c",
        73073,
        "5361b1704c0b1c070493254b595b197f89d04d3913af07bbc400044d11b8e9d7",
    ),
)
STAGE_F_LOCAL_BINDING_MODIFIED_PATHS = (
    ".github/workflows/tests.yml",
    "scripts/validate_stage_e_harness.py",
)
STAGE_F_LOCAL_BINDING_NEW_PATHS = (
    "scripts/build_stage_f_local_binding.py",
    "scripts/validate_stage_f_local_binding.py",
    "stage_f_binding/__init__.py",
    "stage_f_binding/canonical.py",
    "stage_f_binding/binding.py",
    "stage_f_binding/durability.py",
    "stage_f_binding/locked_zipapp_bootstrap.py",
    "tests/stage_f_binding/__init__.py",
    "tests/stage_f_binding/fixtures/negative_cases.json",
    "tests/stage_f_binding/fixtures/synthetic_private_host_manifest.json",
    "tests/stage_f_binding/test_binding_privacy_and_authorization.py",
    "tests/stage_f_binding/test_durability_and_no_science.py",
)
STAGE_F_LOCAL_BINDING_REACHABILITY_PATH = (
    "tests/framework/test_validation_reachability.py"
)
STAGE_F_LOCAL_BINDING_AUTHORITY_SCOPE = (
    STAGE_E_RECONCILED_HARNESS_IMPLEMENTATION_SCOPE
    | frozenset(STAGE_F_LOCAL_BINDING_AUTHORITY_PATHS)
)
STAGE_F_LOCAL_BINDING_COMPLETED_IMPLEMENTATION_SCOPE = (
    STAGE_F_LOCAL_BINDING_AUTHORITY_SCOPE
    | frozenset(STAGE_F_LOCAL_BINDING_NEW_PATHS)
)
STAGE_F_BINDING_EVIDENCE_CORRECTION_AUTHORITY_SCOPE = (
    STAGE_F_LOCAL_BINDING_AUTHORITY_SCOPE
    | frozenset(STAGE_F_BINDING_EVIDENCE_CORRECTION_PATHS)
)
STAGE_F_BINDING_EVIDENCE_CORRECTION_COMPLETED_IMPLEMENTATION_SCOPE = (
    STAGE_F_BINDING_EVIDENCE_CORRECTION_AUTHORITY_SCOPE
    | frozenset(STAGE_F_LOCAL_BINDING_NEW_PATHS)
)
STAGE_F_FINAL_EVIDENCE_CLOSURE_AUTHORITY_SCOPE = (
    STAGE_F_BINDING_EVIDENCE_CORRECTION_AUTHORITY_SCOPE
    | frozenset(STAGE_F_FINAL_EVIDENCE_CLOSURE_PATHS)
)
STAGE_F_FINAL_EVIDENCE_CLOSURE_COMPLETED_IMPLEMENTATION_SCOPE = (
    STAGE_F_FINAL_EVIDENCE_CLOSURE_AUTHORITY_SCOPE
    | frozenset(STAGE_F_LOCAL_BINDING_NEW_PATHS)
)
STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_AUTHORITY_SCOPE = (
    STAGE_F_FINAL_EVIDENCE_CLOSURE_AUTHORITY_SCOPE
    | frozenset(STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_PATHS)
)
STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_COMPLETED_IMPLEMENTATION_SCOPE = (
    STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_AUTHORITY_SCOPE
    | frozenset(STAGE_F_LOCAL_BINDING_NEW_PATHS)
)
STAGE_F_DESCENDANT_PATH_BASE_COMMIT = (
    "b7ebe8615d54ae5e23645734b1a6c7667ce28bce"
)
STAGE_F_DESCENDANT_PATH_BASE_TREE = (
    "24f2693b6d26d42bf9e360b295e3209a16417f74"
)
STAGE_F_LOCAL_BINDING_DESCENDANT_PATHS = (
    STAGE_E_RECONCILED_HARNESS_IMPLEMENTATION_PATHS
    + STAGE_F_LOCAL_BINDING_AUTHORITY_PATHS
    + (STAGE_F_LOCAL_BINDING_REACHABILITY_PATH,)
    + STAGE_F_BINDING_EVIDENCE_CORRECTION_PATHS
    + STAGE_F_FINAL_EVIDENCE_CLOSURE_PATHS
    + STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_PATHS
    + STAGE_F_LOCAL_BINDING_NEW_PATHS
)
STAGE_F_VALIDATOR_AUTHORITY_LANE_SCOPE_BLOCK = """manifest = strict_load(source / "stage_e_dynamic_growth_harness_reconciliation_implementation_path_manifest.json")
scope = manifest["prospective_harness_implementation"]
expected_modified = set(scope["modified_paths"])
expected_added = set(scope["new_paths"])
stage_e_expected = expected_modified | expected_added
if scope["modified_path_count"] != 1 or scope["new_path_count"] != 50 or scope["total_path_count"] != 51:
    raise Refusal("accepted Stage E implementation path manifest count mismatch")
stage_f_v1_manifest = strict_load(source / "stage_f_local_execution_binding_implementation_path_manifest.json")
stage_f_v1_authority_paths = (
    "STAGE_F_LOCAL_EXECUTION_BINDING_AUTHORITY_AMENDMENT.md",
    "stage_f_local_execution_binding_contract.json",
    "stage_f_local_execution_binding_evidence_schema.json",
    "stage_f_local_execution_binding_implementation_path_manifest.json",
    "stage_f_local_execution_binding_predecessor_manifest.json",
    "stage_f_local_execution_binding_validation_contract.json",
)
if tuple(stage_f_v1_manifest["authority_paths"]) != stage_f_v1_authority_paths or stage_f_v1_manifest["authority_path_count"] != 6:
    raise Refusal("Stage F v1 authority path closure mismatch")
stage_f_v2_manifest = strict_load(source / "stage_f_local_execution_binding_evidence_correction_implementation_path_manifest.json")
stage_f_correction_authority_paths = (
    "STAGE_F_LOCAL_EXECUTION_BINDING_EVIDENCE_CORRECTION_AUTHORITY_AMENDMENT.md",
    "stage_f_local_execution_binding_evidence_correction_contract.json",
    "stage_f_local_execution_binding_evidence_correction_schema.json",
    "stage_f_local_execution_binding_evidence_correction_implementation_path_manifest.json",
    "stage_f_local_execution_binding_evidence_correction_predecessor_manifest.json",
    "stage_f_local_execution_binding_evidence_correction_validation_contract.json",
)
if tuple(stage_f_v2_manifest["authority_paths"]) != stage_f_correction_authority_paths or stage_f_v2_manifest["authority_path_count"] != 6:
    raise Refusal("Stage F correction authority path closure mismatch")
stage_f_v3_manifest = strict_load(source / "stage_f_local_execution_binding_final_evidence_closure_correction_implementation_path_manifest.json")
stage_f_final_closure_authority_paths = (
    "STAGE_F_LOCAL_EXECUTION_BINDING_FINAL_EVIDENCE_CLOSURE_CORRECTION_AUTHORITY_AMENDMENT.md",
    "stage_f_local_execution_binding_final_evidence_closure_correction_contract.json",
    "stage_f_local_execution_binding_final_evidence_closure_correction_schema.json",
    "stage_f_local_execution_binding_final_evidence_closure_correction_implementation_path_manifest.json",
    "stage_f_local_execution_binding_final_evidence_closure_correction_predecessor_manifest.json",
    "stage_f_local_execution_binding_final_evidence_closure_correction_validation_contract.json",
)
if tuple(stage_f_v3_manifest["authority_paths"]) != stage_f_final_closure_authority_paths or stage_f_v3_manifest["authority_path_count"] != 6:
    raise Refusal("Stage F final-evidence-closure authority path closure mismatch")
stage_f_manifest = strict_load(source / "stage_f_local_execution_binding_attempt_root_bootstrap_correction_implementation_path_manifest.json")
stage_f_attempt_root_bootstrap_authority_paths = (
    "STAGE_F_LOCAL_EXECUTION_BINDING_ATTEMPT_ROOT_BOOTSTRAP_CORRECTION_AUTHORITY_AMENDMENT.md",
    "stage_f_local_execution_binding_attempt_root_bootstrap_correction_contract.json",
    "stage_f_local_execution_binding_attempt_root_bootstrap_correction_schema.json",
    "stage_f_local_execution_binding_attempt_root_bootstrap_correction_implementation_path_manifest.json",
    "stage_f_local_execution_binding_attempt_root_bootstrap_correction_predecessor_manifest.json",
    "stage_f_local_execution_binding_attempt_root_bootstrap_correction_validation_contract.json",
)
if tuple(stage_f_manifest["authority_paths"]) != stage_f_attempt_root_bootstrap_authority_paths or stage_f_manifest["authority_path_count"] != 6:
    raise Refusal("Stage F attempt-root-bootstrap authority path closure mismatch")
reachability = stage_f_manifest["prospective_reachability_correction"]
reachability_path = "tests/framework/test_validation_reachability.py"
if reachability["modified_paths"] != [reachability_path] or reachability["modified_path_count"] != 1:
    raise Refusal("Stage F attempt-root-bootstrap reachability path closure mismatch")
stage_f_scope = stage_f_manifest["prospective_implementation"]
stage_f_modified = tuple(stage_f_scope["modified_paths"])
stage_f_added = set(stage_f_scope["new_paths"])
if stage_f_modified != (".github/workflows/tests.yml", "scripts/validate_stage_e_harness.py") or stage_f_scope["modified_path_count"] != 2 or len(stage_f_added) != 12 or stage_f_scope["new_path_count"] != 12 or stage_f_scope["total_path_count"] != 14:
    raise Refusal("Stage F attempt-root-bootstrap implementation manifest closure mismatch")
final_closure = stage_f_manifest["final_descendant_path_closure"]
if final_closure["accepted_stage_e_path_count"] != 51 or final_closure["accepted_stage_f_v1_authority_path_count"] != 6 or final_closure["accepted_stage_f_evidence_correction_authority_path_count"] != 6 or final_closure["accepted_stage_f_final_evidence_closure_authority_path_count"] != 6 or final_closure["reachability_unique_path_count"] != 1 or final_closure["attempt_root_bootstrap_correction_authority_added_path_count"] != 6 or final_closure["successor_active_authority_row_count"] != 24 or final_closure["historical_authority_only_unique_path_count"] != 70 or final_closure["historical_completed_implementation_unique_path_count"] != 82 or final_closure["authority_only_unique_path_count"] != 76 or final_closure["stage_f_new_unique_path_count"] != 12 or final_closure["stage_f_modified_paths_overlapping_accepted_stage_e_count"] != 2 or final_closure["final_unique_path_count"] != 88:
    raise Refusal("Stage F attempt-root-bootstrap descendant path arithmetic mismatch")
all_authority_paths = set(stage_f_v1_authority_paths) | set(stage_f_correction_authority_paths) | set(stage_f_final_closure_authority_paths) | set(stage_f_attempt_root_bootstrap_authority_paths)
if set(stage_f_modified) - stage_e_expected or stage_f_added & (stage_e_expected | all_authority_paths | {reachability_path}):
    raise Refusal("Stage F attempt-root-bootstrap implementation path overlap mismatch")
expected = stage_e_expected | all_authority_paths | {reachability_path} | stage_f_added
actual = set(filter(None, _git(source, "diff", "--name-only", f"{IMPLEMENTATION_BASE}..HEAD").splitlines()))
if actual != expected or len(actual) != 88:
    raise Refusal(f"Stage F attempt-root-bootstrap descendant path mismatch: missing={sorted(expected-actual)} extra={sorted(actual-expected)}")
status_rows: dict[str, str] = {}
for row in filter(None, _git(source, "diff", "--name-status", f"{IMPLEMENTATION_BASE}..HEAD").splitlines()):
    fields = row.split("\t")
    if len(fields) != 2 or fields[0] not in {"A", "M"} or fields[1] in status_rows:
        raise Refusal(f"Stage F attempt-root-bootstrap descendant has a forbidden Git operation: {row}")
    status_rows[fields[1]] = fields[0]
expected_status = ({path: "M" for path in expected_modified} | {path: "A" for path in expected_added} | {path: "A" for path in all_authority_paths} | {reachability_path: "M"} | {path: "A" for path in stage_f_added})
if status_rows != expected_status:
    raise Refusal("Stage F attempt-root-bootstrap add/modify classification mismatch")
for relative in expected:
    fields = _git(source, "ls-tree", "HEAD", "--", relative).split()
    if len(fields) < 4 or fields[0] != "100644" or fields[1] != "blob":
        raise Refusal(f"Stage F attempt-root-bootstrap mode/object mismatch: {relative}")
"""
STAGE_E_VALIDATOR_AUTHORITY_LANE_SCOPE_BLOCK = br"""    manifest = strict_load(source / "stage_e_dynamic_growth_harness_reconciliation_implementation_path_manifest.json")
    scope = manifest["prospective_harness_implementation"]
    expected_modified = set(scope["modified_paths"])
    expected_added = set(scope["new_paths"])
    expected = expected_modified | expected_added
    actual = set(filter(None, _git(source, "diff", "--name-only", f"{IMPLEMENTATION_BASE}..HEAD").splitlines()))
    if actual != expected or len(actual) != 51:
        raise Refusal(f"Stage E implementation path closure mismatch: missing={sorted(expected-actual)} extra={sorted(actual-expected)}")
    status_rows: dict[str, str] = {}
    for row in filter(None, _git(source, "diff", "--name-status", f"{IMPLEMENTATION_BASE}..HEAD").splitlines()):
        fields = row.split("\t")
        if len(fields) != 2 or fields[0] not in {"A", "M"} or fields[1] in status_rows:
            raise Refusal(f"Stage E implementation has a forbidden Git operation: {row}")
        status_rows[fields[1]] = fields[0]
    expected_status = {path: "M" for path in expected_modified} | {path: "A" for path in expected_added}
    if status_rows != expected_status:
        raise Refusal("Stage E implementation add/modify classification mismatch")
    for relative in expected:
        fields = _git(source, "ls-tree", "HEAD", "--", relative).split()
        if len(fields) < 4 or fields[0] != "100644" or fields[1] != "blob":
            raise Refusal(f"Stage E implementation mode/object mismatch: {relative}")
"""
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
TEST_SELF_SEAL = "5c1fe07f026cc953c2d8efbb7e89dc1becf76fda8297f5ceeef722d5c1aed70e"
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


CRLF_NORMALIZED_TEXT_SUFFIXES = frozenset(
    {
        ".cff",
        ".gitignore",
        ".json",
        ".lock",
        ".md",
        ".py",
        ".toml",
        ".txt",
        ".typed",
        ".yaml",
        ".yml",
    }
)
CRLF_NORMALIZED_TEXT_NAMES = frozenset({".gitignore", "LICENSE"})


def _is_crlf_normalized_text_path(path: Path) -> bool:
    return (
        path.suffix.lower() in CRLF_NORMALIZED_TEXT_SUFFIXES
        or path.name in CRLF_NORMALIZED_TEXT_NAMES
    )


def _normalize_checkout_text_bytes(
    checkout_raw: bytes, path: Path, label: str | None = None
) -> bytes:
    if not _is_crlf_normalized_text_path(path):
        raise AssertionError(
            f"CRLF normalization is forbidden for this path: {label or path}"
        )
    if checkout_raw.count(b"\r") != checkout_raw.count(b"\r\n"):
        raise AssertionError(
            f"checkout contains a non-CRLF carriage return: {label or path}"
        )
    normalized = checkout_raw.replace(b"\r\n", b"\n")
    normalized.decode("utf-8", "strict")
    return normalized


def _checkout_lf_bytes(path: Path, label: str | None = None) -> bytes:
    return _normalize_checkout_text_bytes(path.read_bytes(), path, label)


def _assert_checkout_matches_blob(
    path: Path, blob_raw: bytes, label: str | None = None
) -> bytes:
    checkout_raw = path.read_bytes()
    if checkout_raw == blob_raw:
        return blob_raw
    if b"\r" in blob_raw:
        raise AssertionError(
            f"non-LF immutable blob cannot use checkout normalization: {label or path}"
        )
    blob_raw.decode("utf-8", "strict")
    normalized = _normalize_checkout_text_bytes(checkout_raw, path, label)
    if normalized != blob_raw:
        raise AssertionError(
            f"checkout does not reconcile to the immutable Git blob: {label or path}"
        )
    return blob_raw


def _canonical_json_lf(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def _canonical_json_bytes(value: object) -> bytes:
    return _canonical_json_lf(value)[:-1]


def _json_identity(value: object) -> dict[str, object]:
    raw = _canonical_json_bytes(value)
    return {"byte_count": len(raw), "sha256": _sha256(raw)}


def _json_pointer(value: object, raw_pointer: str) -> object:
    if raw_pointer == "":
        return value
    if not raw_pointer.startswith("/"):
        raise AssertionError(f"invalid JSON pointer: {raw_pointer!r}")
    current = value
    for raw_token in raw_pointer[1:].split("/"):
        token = raw_token.replace("~1", "/").replace("~0", "~")
        if type(current) is list:
            current = current[int(token)]
        elif type(current) is dict:
            current = current[token]
        else:
            raise AssertionError(f"JSON pointer enters a scalar: {raw_pointer!r}")
    return current


def _apply_json_patch(value: object, operations: object) -> object:
    if type(operations) is not list:
        raise AssertionError("RFC-6902 patch is not an array")
    result = copy.deepcopy(value)
    for operation in operations:
        if type(operation) is not dict:
            raise AssertionError("RFC-6902 operation is not an object")
        op = operation.get("op")
        raw_pointer = operation.get("path")
        if op not in {"add", "remove", "replace"} or type(raw_pointer) is not str:
            raise AssertionError(f"unsupported RFC-6902 operation: {operation!r}")
        tokens = (
            [
                raw.replace("~1", "/").replace("~0", "~")
                for raw in raw_pointer[1:].split("/")
            ]
            if raw_pointer.startswith("/") and raw_pointer != ""
            else []
        )
        if raw_pointer and not raw_pointer.startswith("/"):
            raise AssertionError(f"invalid RFC-6902 path: {raw_pointer!r}")
        if not tokens:
            if op == "remove":
                raise AssertionError("root removal is forbidden")
            result = copy.deepcopy(operation["value"])
            continue
        parent = result
        for token in tokens[:-1]:
            parent = parent[int(token)] if type(parent) is list else parent[token]
        token = tokens[-1]
        if type(parent) is list:
            if op == "add" and token == "-":
                parent.append(copy.deepcopy(operation["value"]))
            elif op == "add":
                parent.insert(int(token), copy.deepcopy(operation["value"]))
            elif op == "remove":
                del parent[int(token)]
            else:
                parent[int(token)] = copy.deepcopy(operation["value"])
        elif type(parent) is dict:
            if op == "remove":
                del parent[token]
            else:
                parent[token] = copy.deepcopy(operation["value"])
        else:
            raise AssertionError(f"RFC-6902 path enters a scalar: {raw_pointer!r}")
    return result


def _schema_resolve(document: dict[str, object], schema: object) -> object:
    if type(schema) is dict and "$ref" in schema:
        ref = schema["$ref"]
        if type(ref) is not str or not ref.startswith("#/"):
            raise AssertionError(f"non-local schema reference: {ref!r}")
        return _json_pointer(document, ref[1:])
    return schema


def _schema_valid(
    document: dict[str, object], schema: object, instance: object
) -> bool:
    if schema is True:
        return True
    if schema is False:
        return False
    schema = _schema_resolve(document, schema)
    if type(schema) is not dict:
        raise AssertionError(f"schema node is not an object or Boolean: {schema!r}")
    if "$ref" in schema:
        return _schema_valid(document, _schema_resolve(document, schema), instance)
    if "allOf" in schema and not all(
        _schema_valid(document, item, instance) for item in schema["allOf"]
    ):
        return False
    if "oneOf" in schema and sum(
        _schema_valid(document, item, instance) for item in schema["oneOf"]
    ) != 1:
        return False
    if "if" in schema:
        branch = (
            schema.get("then")
            if _schema_valid(document, schema["if"], instance)
            else schema.get("else")
        )
        if branch is not None and not _schema_valid(document, branch, instance):
            return False
    if "const" in schema and instance != schema["const"]:
        return False
    if "enum" in schema and instance not in schema["enum"]:
        return False
    kinds = schema.get("type")
    if kinds is not None:
        if type(kinds) is str:
            kinds = [kinds]
        if type(kinds) is not list:
            raise AssertionError(f"schema type is not a string or array: {kinds!r}")
        matches = {
            "object": type(instance) is dict,
            "array": type(instance) is list,
            "string": type(instance) is str,
            "integer": type(instance) is int,
            "number": type(instance) in (int, float),
            "boolean": type(instance) is bool,
            "null": instance is None,
        }
        if not any(matches.get(kind, False) for kind in kinds):
            return False
    if type(instance) is dict:
        required = schema.get("required", [])
        if any(key not in instance for key in required):
            return False
        properties = schema.get("properties", {})
        for key, item in instance.items():
            if key in properties and not _schema_valid(document, properties[key], item):
                return False
            if key not in properties:
                additional = schema.get("additionalProperties", True)
                if additional is False:
                    return False
                if type(additional) is dict and not _schema_valid(
                    document, additional, item
                ):
                    return False
        if len(instance) < schema.get("minProperties", 0):
            return False
    if type(instance) is list:
        if len(instance) < schema.get("minItems", 0):
            return False
        if len(instance) > schema.get("maxItems", sys.maxsize):
            return False
        if schema.get("uniqueItems") and len(
            {_canonical_json_bytes(item) for item in instance}
        ) != len(instance):
            return False
        prefix = schema.get("prefixItems", [])
        for index, item in enumerate(instance[: len(prefix)]):
            if not _schema_valid(document, prefix[index], item):
                return False
        items = schema.get("items")
        if items is False and len(instance) > len(prefix):
            return False
        if type(items) is dict:
            for item in instance[len(prefix) :]:
                if not _schema_valid(document, items, item):
                    return False
    if type(instance) is str:
        if len(instance) < schema.get("minLength", 0):
            return False
        if "pattern" in schema and re.search(schema["pattern"], instance) is None:
            return False
    if type(instance) is int:
        if instance < schema.get("minimum", -sys.maxsize - 1):
            return False
        if instance > schema.get("maximum", sys.maxsize):
            return False
    return True


def _schema_refs(value: object) -> tuple[str, ...]:
    refs = []
    if type(value) is dict:
        for key, item in value.items():
            if key == "$ref":
                refs.append(item)
            refs.extend(_schema_refs(item))
    elif type(value) is list:
        for item in value:
            refs.extend(_schema_refs(item))
    return tuple(refs)


def _schema_keywords(value: object) -> frozenset[str]:
    found = set()
    if type(value) is dict:
        found.update(value)
        for key in ("$defs", "properties"):
            for item in value.get(key, {}).values():
                found.update(_schema_keywords(item))
        for key in ("items", "if", "then", "else"):
            item = value.get(key)
            if type(item) is dict:
                found.update(_schema_keywords(item))
        for key in ("allOf", "oneOf", "prefixItems"):
            for item in value.get(key, []):
                if type(item) is dict:
                    found.update(_schema_keywords(item))
    return frozenset(found)


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
    raw = _checkout_lf_bytes(path)
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
        or (
            len(args) == 5
            and args[:4]
            == ("-c", "core.autocrlf=false", "archive", "--format=tar")
            and re.fullmatch(r"[0-9a-f]{40}", args[4]) is not None
        )
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
            "merge-base",
            STAGE_D_DYNAMIC_GROWTH_ACCEPTED_BASE_COMMIT,
            STAGE_D_DYNAMIC_GROWTH_AUTHORITY_CANDIDATE,
        )
        or args
        == (
            "rev-list",
            "--reverse",
            "--parents",
            f"{STAGE_D_DYNAMIC_GROWTH_ACCEPTED_BASE_COMMIT}..{STAGE_D_DYNAMIC_GROWTH_AUTHORITY_CANDIDATE}",
        )
        or args
        == (
            "merge-base",
            STAGE_E_RECONCILIATION_ACCEPTED_BASE_COMMIT,
            STAGE_E_RECONCILIATION_AUTHORITY_CANDIDATE,
        )
        or args
        == (
            "rev-list",
            "--reverse",
            "--parents",
            f"{STAGE_E_RECONCILIATION_ACCEPTED_BASE_COMMIT}..{STAGE_E_RECONCILIATION_AUTHORITY_CANDIDATE}",
        )
        or args
        == (
            "merge-base",
            STAGE_F_LOCAL_BINDING_ACCEPTED_BASE_COMMIT,
            STAGE_F_LOCAL_BINDING_AUTHORITY_CANDIDATE,
        )
        or (
            len(args) == 3
            and args[:2]
            == ("merge-base", STAGE_F_LOCAL_BINDING_AUTHORITY_TARGET)
            and re.fullmatch(r"[0-9a-f]{40}", args[2]) is not None
        )
        or args
        == (
            "rev-list",
            "--reverse",
            "--parents",
            f"{STAGE_F_LOCAL_BINDING_ACCEPTED_BASE_COMMIT}..{STAGE_F_LOCAL_BINDING_AUTHORITY_CANDIDATE}",
        )
        or args
        == (
            "merge-base",
            STAGE_F_BINDING_EVIDENCE_CORRECTION_REQUIRED_BASE_COMMIT,
            STAGE_F_BINDING_EVIDENCE_CORRECTION_CANDIDATE,
        )
        or (
            len(args) == 3
            and args[:2]
            == ("merge-base", STAGE_F_BINDING_EVIDENCE_CORRECTION_TARGET)
            and re.fullmatch(r"[0-9a-f]{40}", args[2]) is not None
        )
        or args
        == (
            "merge-base",
            STAGE_F_FINAL_EVIDENCE_CLOSURE_REQUIRED_BASE_COMMIT,
            STAGE_F_FINAL_EVIDENCE_CLOSURE_CANDIDATE,
        )
        or (
            len(args) == 3
            and args[:2]
            == ("merge-base", STAGE_F_FINAL_EVIDENCE_CLOSURE_TARGET)
            and re.fullmatch(r"[0-9a-f]{40}", args[2]) is not None
        )
        or args
        == (
            "merge-base",
            STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_REQUIRED_BASE_COMMIT,
            STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_CANDIDATE,
        )
        or (
            len(args) == 3
            and args[:2]
            == ("merge-base", STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_TARGET)
            and re.fullmatch(r"[0-9a-f]{40}", args[2]) is not None
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
    if re.fullmatch(r"[0-9a-f]{40}", commit) is None:
        raise AssertionError(f"archive coordinate is not an immutable commit: {commit!r}")
    raw = _git("-c", "core.autocrlf=false", "archive", "--format=tar", commit)
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
    return _base_candidate_projection(path, _checkout_lf_bytes(ROOT / path, path))


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
            raw = _checkout_lf_bytes(ROOT / path, path)
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
            self.assertEqual(_sha256(_checkout_lf_bytes(ROOT / path, path)), expected)
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
        if (
            current_scope["stage_d_dynamic_growth_phase"]
            == "STAGE_D_DYNAMIC_GROWTH_AUTHORITY_ONLY"
        ):
            self._audit_stage_d_dynamic_growth_authority(current_scope)
        if current_scope["stage_e_reconciliation_phase"] in (
            "STAGE_E_DYNAMIC_GROWTH_HARNESS_RECONCILIATION_AUTHORITY_ONLY",
            "STAGE_E_DYNAMIC_GROWTH_HARNESS_RECONCILIATION_COMPLETED_IMPLEMENTATION",
        ):
            self._audit_stage_e_reconciliation_authority(current_scope)
        if current_scope["stage_f_local_binding_phase"] in (
            "STAGE_F_LOCAL_BINDING_AUTHORITY_ONLY",
            "STAGE_F_LOCAL_BINDING_COMPLETED_IMPLEMENTATION",
        ):
            self._audit_stage_f_local_binding_authority(current_scope)
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
            current_scope["stage_f_local_binding_phase"],
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
        stage_f_local_binding_phase = None
        if changed_paths == STAGE_C_AUTHORITY_SCOPE:
            stage_c_phase = "AUTHORITY_ONLY"
            stage_d_phase = None
            stage_e_phase = None
            stage_d_dynamic_growth_phase = None
            stage_e_reconciliation_phase = None
        elif changed_paths == STAGE_C_IMPLEMENTATION_SCOPE:
            stage_c_phase = "COMPLETED_IMPLEMENTATION"
            stage_d_phase = None
            stage_e_phase = None
            stage_d_dynamic_growth_phase = None
            stage_e_reconciliation_phase = None
        elif changed_paths == STAGE_D_AUTHORITY_SCOPE:
            stage_c_phase = "COMPLETED_IMPLEMENTATION"
            stage_d_phase = "STAGE_D_AUTHORITY_ONLY"
            stage_e_phase = None
            stage_d_dynamic_growth_phase = None
            stage_e_reconciliation_phase = None
        elif changed_paths == STAGE_D_CONTINUATION_AUTHORITY_SCOPE:
            stage_c_phase = "COMPLETED_IMPLEMENTATION"
            stage_d_phase = "STAGE_D_CONTINUATION_AUTHORITY_ONLY"
            stage_e_phase = None
            stage_d_dynamic_growth_phase = None
            stage_e_reconciliation_phase = None
        elif changed_paths == STAGE_E_AUTHORITY_SCOPE:
            stage_c_phase = "COMPLETED_IMPLEMENTATION"
            stage_d_phase = "STAGE_D_CONTINUATION_AUTHORITY_ONLY"
            stage_e_phase = "STAGE_E_HARNESS_AUTHORITY_ONLY"
            stage_d_dynamic_growth_phase = None
            stage_e_reconciliation_phase = None
        elif changed_paths == STAGE_D_DYNAMIC_GROWTH_AUTHORITY_SCOPE:
            stage_c_phase = "COMPLETED_IMPLEMENTATION"
            stage_d_phase = "STAGE_D_CONTINUATION_AUTHORITY_ONLY"
            stage_e_phase = "STAGE_E_HARNESS_AUTHORITY_ONLY"
            stage_d_dynamic_growth_phase = "STAGE_D_DYNAMIC_GROWTH_AUTHORITY_ONLY"
            stage_e_reconciliation_phase = None
        elif changed_paths == STAGE_E_RECONCILIATION_AUTHORITY_SCOPE:
            stage_c_phase = "COMPLETED_IMPLEMENTATION"
            stage_d_phase = "STAGE_D_CONTINUATION_AUTHORITY_ONLY"
            stage_e_phase = "STAGE_E_HARNESS_AUTHORITY_ONLY"
            stage_d_dynamic_growth_phase = "STAGE_D_DYNAMIC_GROWTH_AUTHORITY_ONLY"
            stage_e_reconciliation_phase = (
                "STAGE_E_DYNAMIC_GROWTH_HARNESS_RECONCILIATION_AUTHORITY_ONLY"
            )
        elif changed_paths == STAGE_E_RECONCILED_HARNESS_IMPLEMENTATION_SCOPE:
            stage_c_phase = "COMPLETED_IMPLEMENTATION"
            stage_d_phase = "STAGE_D_CONTINUATION_AUTHORITY_ONLY"
            stage_e_phase = "STAGE_E_HARNESS_COMPLETED_IMPLEMENTATION"
            stage_d_dynamic_growth_phase = "STAGE_D_DYNAMIC_GROWTH_AUTHORITY_ONLY"
            stage_e_reconciliation_phase = (
                "STAGE_E_DYNAMIC_GROWTH_HARNESS_RECONCILIATION_COMPLETED_IMPLEMENTATION"
            )
        elif changed_paths == STAGE_F_BINDING_EVIDENCE_CORRECTION_AUTHORITY_SCOPE:
            stage_c_phase = "COMPLETED_IMPLEMENTATION"
            stage_d_phase = "STAGE_D_CONTINUATION_AUTHORITY_ONLY"
            stage_e_phase = "STAGE_E_HARNESS_COMPLETED_IMPLEMENTATION"
            stage_d_dynamic_growth_phase = "STAGE_D_DYNAMIC_GROWTH_AUTHORITY_ONLY"
            stage_e_reconciliation_phase = (
                "STAGE_E_DYNAMIC_GROWTH_HARNESS_RECONCILIATION_COMPLETED_IMPLEMENTATION"
            )
            stage_f_local_binding_phase = "STAGE_F_LOCAL_BINDING_AUTHORITY_ONLY"
        elif (
            changed_paths
            == STAGE_F_BINDING_EVIDENCE_CORRECTION_COMPLETED_IMPLEMENTATION_SCOPE
        ):
            stage_c_phase = "COMPLETED_IMPLEMENTATION"
            stage_d_phase = "STAGE_D_CONTINUATION_AUTHORITY_ONLY"
            stage_e_phase = "STAGE_E_HARNESS_COMPLETED_IMPLEMENTATION"
            stage_d_dynamic_growth_phase = "STAGE_D_DYNAMIC_GROWTH_AUTHORITY_ONLY"
            stage_e_reconciliation_phase = (
                "STAGE_E_DYNAMIC_GROWTH_HARNESS_RECONCILIATION_COMPLETED_IMPLEMENTATION"
            )
            stage_f_local_binding_phase = (
                "STAGE_F_LOCAL_BINDING_COMPLETED_IMPLEMENTATION"
            )
        elif changed_paths == STAGE_F_FINAL_EVIDENCE_CLOSURE_AUTHORITY_SCOPE:
            stage_c_phase = "COMPLETED_IMPLEMENTATION"
            stage_d_phase = "STAGE_D_CONTINUATION_AUTHORITY_ONLY"
            stage_e_phase = "STAGE_E_HARNESS_COMPLETED_IMPLEMENTATION"
            stage_d_dynamic_growth_phase = "STAGE_D_DYNAMIC_GROWTH_AUTHORITY_ONLY"
            stage_e_reconciliation_phase = (
                "STAGE_E_DYNAMIC_GROWTH_HARNESS_RECONCILIATION_COMPLETED_IMPLEMENTATION"
            )
            stage_f_local_binding_phase = "STAGE_F_LOCAL_BINDING_AUTHORITY_ONLY"
        elif (
            changed_paths
            == STAGE_F_FINAL_EVIDENCE_CLOSURE_COMPLETED_IMPLEMENTATION_SCOPE
        ):
            stage_c_phase = "COMPLETED_IMPLEMENTATION"
            stage_d_phase = "STAGE_D_CONTINUATION_AUTHORITY_ONLY"
            stage_e_phase = "STAGE_E_HARNESS_COMPLETED_IMPLEMENTATION"
            stage_d_dynamic_growth_phase = "STAGE_D_DYNAMIC_GROWTH_AUTHORITY_ONLY"
            stage_e_reconciliation_phase = (
                "STAGE_E_DYNAMIC_GROWTH_HARNESS_RECONCILIATION_COMPLETED_IMPLEMENTATION"
            )
            stage_f_local_binding_phase = (
                "STAGE_F_LOCAL_BINDING_COMPLETED_IMPLEMENTATION"
            )
        elif changed_paths == STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_AUTHORITY_SCOPE:
            stage_c_phase = "COMPLETED_IMPLEMENTATION"
            stage_d_phase = "STAGE_D_CONTINUATION_AUTHORITY_ONLY"
            stage_e_phase = "STAGE_E_HARNESS_COMPLETED_IMPLEMENTATION"
            stage_d_dynamic_growth_phase = "STAGE_D_DYNAMIC_GROWTH_AUTHORITY_ONLY"
            stage_e_reconciliation_phase = (
                "STAGE_E_DYNAMIC_GROWTH_HARNESS_RECONCILIATION_COMPLETED_IMPLEMENTATION"
            )
            stage_f_local_binding_phase = "STAGE_F_LOCAL_BINDING_AUTHORITY_ONLY"
        elif (
            changed_paths
            == STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_COMPLETED_IMPLEMENTATION_SCOPE
        ):
            stage_c_phase = "COMPLETED_IMPLEMENTATION"
            stage_d_phase = "STAGE_D_CONTINUATION_AUTHORITY_ONLY"
            stage_e_phase = "STAGE_E_HARNESS_COMPLETED_IMPLEMENTATION"
            stage_d_dynamic_growth_phase = "STAGE_D_DYNAMIC_GROWTH_AUTHORITY_ONLY"
            stage_e_reconciliation_phase = (
                "STAGE_E_DYNAMIC_GROWTH_HARNESS_RECONCILIATION_COMPLETED_IMPLEMENTATION"
            )
            stage_f_local_binding_phase = (
                "STAGE_F_LOCAL_BINDING_COMPLETED_IMPLEMENTATION"
            )
        else:
            self.fail(
                "current HEAD is neither the exact Stage C authority phase nor "
                "the exact completed implementation, Stage D authority-only, "
                "Stage D continuation-authority-only, Stage E harness "
                "authority-only, Stage D dynamic-growth authority-only, "
                "Stage E dynamic-growth reconciliation authority-only, or "
                "the reconciled Stage E harness completed-implementation, "
                "Stage F corrected local-binding authority-only, Stage F "
                "corrected local-binding completed-implementation, Stage F "
                "final-evidence-closure authority-only, or Stage F "
                "final-evidence-closure completed-implementation, Stage F "
                "attempt-root-bootstrap authority-only, or Stage F "
                "attempt-root-bootstrap completed-implementation "
                f"phase: {sorted(changed_paths)!r}"
            )
        self.assertEqual(len(STAGE_C_AUTHORITY_SCOPE), 7)
        self.assertEqual(len(STAGE_C_IMPLEMENTATION_SCOPE), 24)
        self.assertEqual(len(STAGE_D_AUTHORITY_SCOPE), 30)
        self.assertEqual(len(STAGE_D_CONTINUATION_AUTHORITY_SCOPE), 35)
        self.assertEqual(len(STAGE_E_AUTHORITY_SCOPE), 41)
        self.assertEqual(len(STAGE_E_HARNESS_IMPLEMENTATION_SCOPE), 86)
        self.assertEqual(len(STAGE_D_DYNAMIC_GROWTH_AUTHORITY_SCOPE), 46)
        self.assertEqual(len(STAGE_E_RECONCILIATION_AUTHORITY_SCOPE), 52)
        self.assertEqual(len(STAGE_E_RECONCILED_HARNESS_IMPLEMENTATION_PATHS), 51)
        self.assertEqual(len(STAGE_E_RECONCILED_HARNESS_IMPLEMENTATION_SCOPE), 102)
        self.assertEqual(len(STAGE_F_LOCAL_BINDING_AUTHORITY_SCOPE), 108)
        self.assertEqual(
            len(STAGE_F_LOCAL_BINDING_COMPLETED_IMPLEMENTATION_SCOPE), 120
        )
        self.assertEqual(
            len(STAGE_F_BINDING_EVIDENCE_CORRECTION_AUTHORITY_SCOPE), 114
        )
        self.assertEqual(
            len(STAGE_F_BINDING_EVIDENCE_CORRECTION_COMPLETED_IMPLEMENTATION_SCOPE),
            126,
        )
        self.assertEqual(len(STAGE_F_FINAL_EVIDENCE_CLOSURE_AUTHORITY_SCOPE), 120)
        self.assertEqual(
            len(STAGE_F_FINAL_EVIDENCE_CLOSURE_COMPLETED_IMPLEMENTATION_SCOPE),
            132,
        )
        self.assertEqual(len(STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_AUTHORITY_SCOPE), 126)
        self.assertEqual(
            len(STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_COMPLETED_IMPLEMENTATION_SCOPE),
            138,
        )
        self.assertEqual(len(STAGE_F_LOCAL_BINDING_DESCENDANT_PATHS), 88)
        self.assertEqual(len(set(STAGE_F_LOCAL_BINDING_DESCENDANT_PATHS)), 88)
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
            reconstructed, predecessor_raw = _object_row(
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
            if path in changed_paths or path in CLCD_AUTHORIZED_PREDECESSOR_MODIFICATIONS:
                continue
            current_entry = head_entries[path]
            self.assertEqual(current_entry["git_object"], row["git_object"], path)
            self.assertEqual(current_entry["mode"], row["mode"], path)
            self.assertEqual(current_entry["object_type"], row["object_type"], path)
            current_git_raw = _git("cat-file", "blob", current_entry["git_object"])
            self.assertEqual(current_git_raw, predecessor_raw, path)
            raw = current_git_raw
            if _is_crlf_normalized_text_path(candidate):
                self.assertEqual(
                    _assert_checkout_matches_blob(candidate, current_git_raw, path),
                    current_git_raw,
                    path,
                )
            self.assertEqual(len(raw), row["byte_count"], path)
            self.assertEqual(_sha256(raw), row["raw_sha256"], path)
            self.assertEqual(_blob_id(raw), row["git_object"], path)

        current_path_bytes = {
            path: _checkout_lf_bytes(ROOT / path, path) for path in IMPLEMENTATION_PATHS
        }
        if stage_c_phase == "AUTHORITY_ONLY":
            self.assertEqual(
                _workflow_without_routing(current_path_bytes[".github/workflows/tests.yml"]),
                historical["implementation_raw"][".github/workflows/tests.yml"],
            )
        self.assertNotEqual(TEST_SELF_SEAL, "0" * 64)
        test_path = "tests/framework/test_validation_reachability.py"
        test_entry = head_entries[test_path]
        test_blob = _git("cat-file", "blob", test_entry["git_object"])
        test_checkout = current_path_bytes[test_path]
        self.assertEqual(test_checkout.count(b"\r"), test_checkout.count(b"\r\n"))
        self.assertEqual(test_checkout.replace(b"\r\n", b"\n"), test_blob)
        self.assertNotIn(b"\r", test_blob)
        self.assertEqual(
            _sha256(_normalized_test_bytes(test_blob)),
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
            "stage_d_dynamic_growth_phase": stage_d_dynamic_growth_phase,
            "stage_e_reconciliation_phase": stage_e_reconciliation_phase,
            "stage_f_local_binding_phase": stage_f_local_binding_phase,
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
            expected_implementation_delta.update(
                STAGE_E_RECONCILED_HARNESS_IMPLEMENTATION_PATHS
            )
        if current_scope["stage_d_dynamic_growth_phase"] is not None:
            expected_implementation_delta.update(
                STAGE_D_DYNAMIC_GROWTH_AUTHORITY_PATHS
            )
        if current_scope["stage_e_reconciliation_phase"] is not None:
            expected_implementation_delta.update(
                STAGE_E_RECONCILIATION_AUTHORITY_PATHS
            )
        if current_scope["stage_f_local_binding_phase"] is not None:
            expected_implementation_delta.update(
                STAGE_F_LOCAL_BINDING_AUTHORITY_PATHS
            )
            expected_implementation_delta.update(
                STAGE_F_BINDING_EVIDENCE_CORRECTION_PATHS
            )
            expected_implementation_delta.update(
                STAGE_F_FINAL_EVIDENCE_CLOSURE_PATHS
            )
            expected_implementation_delta.update(
                STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_PATHS
            )
        if (
            current_scope["stage_f_local_binding_phase"]
            == "STAGE_F_LOCAL_BINDING_COMPLETED_IMPLEMENTATION"
        ):
            expected_implementation_delta.update(STAGE_F_LOCAL_BINDING_NEW_PATHS)
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
            current_raw = _assert_checkout_matches_blob(ROOT / path, candidate_raw, path)
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
            expected_implementation_delta.update(
                STAGE_E_RECONCILED_HARNESS_IMPLEMENTATION_PATHS
            )
        if current_scope["stage_d_dynamic_growth_phase"] is not None:
            expected_implementation_delta.update(
                STAGE_D_DYNAMIC_GROWTH_AUTHORITY_PATHS
            )
        if current_scope["stage_e_reconciliation_phase"] is not None:
            expected_implementation_delta.update(
                STAGE_E_RECONCILIATION_AUTHORITY_PATHS
            )
        if current_scope["stage_f_local_binding_phase"] is not None:
            expected_implementation_delta.update(
                STAGE_F_LOCAL_BINDING_AUTHORITY_PATHS
            )
            expected_implementation_delta.update(
                STAGE_F_BINDING_EVIDENCE_CORRECTION_PATHS
            )
            expected_implementation_delta.update(
                STAGE_F_FINAL_EVIDENCE_CLOSURE_PATHS
            )
            expected_implementation_delta.update(
                STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_PATHS
            )
        if (
            current_scope["stage_f_local_binding_phase"]
            == "STAGE_F_LOCAL_BINDING_COMPLETED_IMPLEMENTATION"
        ):
            expected_implementation_delta.update(STAGE_F_LOCAL_BINDING_NEW_PATHS)
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
            current_raw = _assert_checkout_matches_blob(ROOT / path, candidate_raw, path)
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
            self.assertEqual(
                base_raw,
                _assert_checkout_matches_blob(ROOT / path, base_raw, path),
                path,
            )
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
                self.assertEqual(
                    _assert_checkout_matches_blob(
                        ROOT / row["path"], base_raw, row["path"]
                    ),
                    base_raw,
                    row["path"],
                )
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
            expected_implementation_delta.update(
                STAGE_E_RECONCILED_HARNESS_IMPLEMENTATION_PATHS
            )
        if current_scope["stage_d_dynamic_growth_phase"] is not None:
            expected_implementation_delta.update(
                STAGE_D_DYNAMIC_GROWTH_AUTHORITY_PATHS
            )
        if current_scope["stage_e_reconciliation_phase"] is not None:
            expected_implementation_delta.update(
                STAGE_E_RECONCILIATION_AUTHORITY_PATHS
            )
        if current_scope["stage_f_local_binding_phase"] is not None:
            expected_implementation_delta.update(
                STAGE_F_LOCAL_BINDING_AUTHORITY_PATHS
            )
            expected_implementation_delta.update(
                STAGE_F_BINDING_EVIDENCE_CORRECTION_PATHS
            )
            expected_implementation_delta.update(
                STAGE_F_FINAL_EVIDENCE_CLOSURE_PATHS
            )
            expected_implementation_delta.update(
                STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_PATHS
            )
        if (
            current_scope["stage_f_local_binding_phase"]
            == "STAGE_F_LOCAL_BINDING_COMPLETED_IMPLEMENTATION"
        ):
            expected_implementation_delta.update(STAGE_F_LOCAL_BINDING_NEW_PATHS)
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
            current_raw = _assert_checkout_matches_blob(ROOT / path, candidate_raw, path)
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
                self.assertEqual(
                    _assert_checkout_matches_blob(
                        ROOT / row["path"], base_raw, row["path"]
                    ),
                    base_raw,
                    row["path"],
                )
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
            current_workflow_raw = _checkout_lf_bytes(
                ROOT / workflow_row["path"], workflow_row["path"]
            )
            stage_e_workflow_raw = accepted_workflow_raw + STAGE_E_WORKFLOW_APPEND_BLOCK
            if (
                current_scope["stage_f_local_binding_phase"]
                == "STAGE_F_LOCAL_BINDING_COMPLETED_IMPLEMENTATION"
            ):
                self.assertTrue(
                    current_workflow_raw.startswith(stage_e_workflow_raw),
                    "Stage F workflow must retain every accepted Stage E byte as a prefix",
                )
            else:
                self.assertEqual(
                    current_workflow_raw,
                    stage_e_workflow_raw,
                    "Stage E workflow must be the exact accepted workflow plus the frozen additive job",
                )
            self.assertEqual(
                stage_e_workflow_raw.count(b"  stage-e-scientific-harness:\n"),
                1,
            )
            self.assertEqual(
                stage_e_workflow_raw.count(
                    b"    needs: [test, framework-t0, framework-t1, framework-t2, packaging-release-candidate]\n"
                ),
                1,
            )
            self.assertEqual(stage_e_workflow_raw.count(b"--network none"), 6)
            self.assertEqual(stage_e_workflow_raw.count(b"--read-only"), 6)
            self.assertEqual(
                stage_e_workflow_raw.count(b"--platform linux/amd64"), 6
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
                _checkout_lf_bytes(
                    ROOT / "stage_d_scientific_validation_evidence_schema.json",
                    "stage_d_scientific_validation_evidence_schema.json",
                ),
                "stage_d_scientific_validation_evidence_schema.json",
            ),
            _strict_stage_d_json_bytes(
                _checkout_lf_bytes(
                    ROOT
                    / "stage_d_completion_oriented_continuation_evidence_schema.json",
                    "stage_d_completion_oriented_continuation_evidence_schema.json",
                ),
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
            _checkout_lf_bytes(
                ROOT / "stage_d_scientific_validation_evidence_schema.json",
                "stage_d_scientific_validation_evidence_schema.json",
            ),
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

    def _audit_stage_d_dynamic_growth_authority(
        self, current_scope: dict[str, object]
    ) -> None:
        self.assertEqual(
            current_scope["stage_d_dynamic_growth_phase"],
            "STAGE_D_DYNAMIC_GROWTH_AUTHORITY_ONLY",
        )
        self.assertEqual(
            _git(
                "rev-parse",
                "--verify",
                f"{STAGE_D_DYNAMIC_GROWTH_ACCEPTED_BASE_COMMIT}^{{commit}}",
            )
            .decode()
            .strip(),
            STAGE_D_DYNAMIC_GROWTH_ACCEPTED_BASE_COMMIT,
        )
        self.assertEqual(
            _git(
                "rev-parse",
                f"{STAGE_D_DYNAMIC_GROWTH_ACCEPTED_BASE_COMMIT}^{{tree}}",
            )
            .decode()
            .strip(),
            STAGE_D_DYNAMIC_GROWTH_ACCEPTED_BASE_TREE,
        )
        self.assertEqual(
            _git(
                "rev-parse",
                f"{STAGE_D_DYNAMIC_GROWTH_AUTHORITY_CANDIDATE}^{{tree}}",
            )
            .decode()
            .strip(),
            STAGE_D_DYNAMIC_GROWTH_AUTHORITY_TREE,
        )
        self.assertEqual(
            _git(
                "rev-parse", f"{STAGE_D_DYNAMIC_GROWTH_AUTHORITY_TARGET}^{{tree}}"
            )
            .decode()
            .strip(),
            STAGE_D_DYNAMIC_GROWTH_AUTHORITY_TREE,
        )
        self.assertEqual(
            _git("rev-parse", f"{STAGE_D_DYNAMIC_GROWTH_AUTHORITY_TARGET}^1")
            .decode()
            .strip(),
            STAGE_D_DYNAMIC_GROWTH_ACCEPTED_BASE_COMMIT,
        )
        self.assertEqual(
            _git("rev-parse", f"{STAGE_D_DYNAMIC_GROWTH_AUTHORITY_TARGET}^2")
            .decode()
            .strip(),
            STAGE_D_DYNAMIC_GROWTH_AUTHORITY_CANDIDATE,
        )
        self.assertEqual(
            _git(
                "merge-base",
                STAGE_D_DYNAMIC_GROWTH_ACCEPTED_BASE_COMMIT,
                STAGE_D_DYNAMIC_GROWTH_AUTHORITY_CANDIDATE,
            )
            .decode()
            .strip(),
            STAGE_D_DYNAMIC_GROWTH_ACCEPTED_BASE_COMMIT,
        )
        history_rows = tuple(
            tuple(line.split())
            for line in _git(
                "rev-list",
                "--reverse",
                "--parents",
                f"{STAGE_D_DYNAMIC_GROWTH_ACCEPTED_BASE_COMMIT}..{STAGE_D_DYNAMIC_GROWTH_AUTHORITY_CANDIDATE}",
            )
            .decode()
            .splitlines()
        )
        self.assertEqual(
            tuple(row[0] for row in history_rows),
            STAGE_D_DYNAMIC_GROWTH_AUTHORITY_CHAIN,
        )
        self.assertEqual(
            history_rows[0][1:],
            (STAGE_D_DYNAMIC_GROWTH_ACCEPTED_BASE_COMMIT,),
        )
        for previous, row in zip(
            STAGE_D_DYNAMIC_GROWTH_AUTHORITY_CHAIN, history_rows[1:]
        ):
            self.assertEqual(row[1:], (previous,))

        base_entries = _tree_entries(STAGE_D_DYNAMIC_GROWTH_ACCEPTED_BASE_COMMIT)
        candidate_entries = _tree_entries(STAGE_D_DYNAMIC_GROWTH_AUTHORITY_CANDIDATE)
        target_entries = _tree_entries(STAGE_D_DYNAMIC_GROWTH_AUTHORITY_TARGET)
        current_entries = _tree_entries(current_scope["actual_head"])
        candidate_delta = frozenset(
            path
            for path in set(base_entries) | set(candidate_entries)
            if base_entries.get(path) != candidate_entries.get(path)
        )
        self.assertEqual(
            candidate_delta, frozenset(STAGE_D_DYNAMIC_GROWTH_AUTHORITY_PATHS)
        )
        self.assertEqual(candidate_entries, target_entries)
        for path in STAGE_D_DYNAMIC_GROWTH_AUTHORITY_PATHS:
            self.assertNotIn(path, base_entries)
            self.assertEqual(candidate_entries[path]["mode"], "100644", path)
            self.assertEqual(candidate_entries[path]["object_type"], "blob", path)
        implementation_delta = frozenset(
            path
            for path in set(target_entries) | set(current_entries)
            if target_entries.get(path) != current_entries.get(path)
        )
        expected_implementation_delta = {
            "tests/framework/test_validation_reachability.py"
        }
        if current_scope["stage_e_reconciliation_phase"] is not None:
            expected_implementation_delta.update(
                STAGE_E_RECONCILIATION_AUTHORITY_PATHS
            )
        if (
            current_scope["stage_e_reconciliation_phase"]
            == "STAGE_E_DYNAMIC_GROWTH_HARNESS_RECONCILIATION_COMPLETED_IMPLEMENTATION"
        ):
            expected_implementation_delta.update(
                STAGE_E_RECONCILED_HARNESS_IMPLEMENTATION_PATHS
            )
        if current_scope["stage_f_local_binding_phase"] is not None:
            expected_implementation_delta.update(
                STAGE_F_LOCAL_BINDING_AUTHORITY_PATHS
            )
            expected_implementation_delta.update(
                STAGE_F_BINDING_EVIDENCE_CORRECTION_PATHS
            )
            expected_implementation_delta.update(
                STAGE_F_FINAL_EVIDENCE_CLOSURE_PATHS
            )
            expected_implementation_delta.update(
                STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_PATHS
            )
        if (
            current_scope["stage_f_local_binding_phase"]
            == "STAGE_F_LOCAL_BINDING_COMPLETED_IMPLEMENTATION"
        ):
            expected_implementation_delta.update(STAGE_F_LOCAL_BINDING_NEW_PATHS)
        self.assertEqual(
            implementation_delta,
            frozenset(expected_implementation_delta),
        )

        candidate_archive = _archive_members(
            STAGE_D_DYNAMIC_GROWTH_AUTHORITY_CANDIDATE
        )
        target_archive = _archive_members(STAGE_D_DYNAMIC_GROWTH_AUTHORITY_TARGET)
        documents = {}
        raw_by_path = {}
        for path in STAGE_D_DYNAMIC_GROWTH_AUTHORITY_PATHS:
            candidate_row, candidate_raw = _object_row(
                path, candidate_entries, candidate_archive
            )
            target_row, target_raw = _object_row(
                path, target_entries, target_archive
            )
            self.assertEqual(candidate_row, target_row, path)
            self.assertEqual(candidate_raw, target_raw, path)
            current_raw = _assert_checkout_matches_blob(ROOT / path, candidate_raw, path)
            self.assertEqual(current_raw, candidate_raw, path)
            self.assertEqual(
                _sha256(current_raw),
                STAGE_D_DYNAMIC_GROWTH_AUTHORITY_RAW_SHA256[path],
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
                    STAGE_D_DYNAMIC_GROWTH_AUTHORITY_CANONICAL_SHA256[path],
                    path,
                )

        contract = documents["stage_d_dynamic_growth_campaign_contract.json"]
        schema = documents[
            "stage_d_dynamic_growth_campaign_evidence_schema.json"
        ]
        predecessor = documents[
            "stage_d_dynamic_growth_campaign_predecessor_manifest.json"
        ]
        validation = documents[
            "stage_d_dynamic_growth_campaign_validation_contract.json"
        ]
        self.assertEqual(
            tuple(contract["candidate_files"]),
            STAGE_D_DYNAMIC_GROWTH_AUTHORITY_PATHS,
        )
        self.assertEqual(contract["candidate_file_count"], 5)
        self.assertEqual(
            tuple(validation["candidate_paths"]),
            STAGE_D_DYNAMIC_GROWTH_AUTHORITY_PATHS,
        )
        self.assertEqual(validation["candidate_path_count"], 5)
        for document in (contract, predecessor, validation):
            self.assertEqual(
                document["accepted_base"]["commit"],
                STAGE_D_DYNAMIC_GROWTH_ACCEPTED_BASE_COMMIT,
            )
            self.assertEqual(
                document["accepted_base"]["tree"],
                STAGE_D_DYNAMIC_GROWTH_ACCEPTED_BASE_TREE,
            )

        self.assertEqual(predecessor["source_count"], 19)
        source_rows = predecessor["source_rows"]
        self.assertEqual(len(source_rows), 19)
        self.assertEqual(len({row["path"] for row in source_rows}), 19)
        base_archive = _archive_members(STAGE_D_DYNAMIC_GROWTH_ACCEPTED_BASE_COMMIT)
        for row in source_rows:
            reconstructed, base_raw = _object_row(
                row["path"], base_entries, base_archive
            )
            self.assertEqual(
                {
                    "path": reconstructed["path"],
                    "mode": reconstructed["mode"],
                    "git_object": reconstructed["git_object"],
                    "bytes": reconstructed["byte_count"],
                    "sha256": reconstructed["raw_sha256"],
                },
                row,
                row["path"],
            )
            changed_workflow = (
                row["path"] == ".github/workflows/tests.yml"
                and current_scope["stage_e_reconciliation_phase"]
                == "STAGE_E_DYNAMIC_GROWTH_HARNESS_RECONCILIATION_COMPLETED_IMPLEMENTATION"
            )
            if (
                row["path"] != "tests/framework/test_validation_reachability.py"
                and not changed_workflow
            ):
                self.assertEqual(
                    _assert_checkout_matches_blob(
                        ROOT / row["path"], base_raw, row["path"]
                    ),
                    base_raw,
                    row["path"],
                )

        nested = predecessor["nested_authority_locks"]
        self.assertEqual(nested["stage_d_nested_row_count"], 39)
        self.assertEqual(nested["continuation_direct_row_count"], 9)
        self.assertEqual(nested["stage_e_direct_row_count"], 17)
        self.assertEqual(
            nested["stage_d_predecessor_manifest_path"],
            "stage_d_scientific_validation_predecessor_manifest.json",
        )
        self.assertEqual(
            nested["continuation_predecessor_manifest_path"],
            "stage_d_completion_oriented_continuation_predecessor_manifest.json",
        )
        self.assertEqual(
            nested["stage_e_predecessor_manifest_path"],
            "stage_e_scientific_harness_predecessor_manifest.json",
        )

        study = contract["study_registry_binding"]
        study_order = tuple(f"SD-{index:02d}" for index in range(1, 15))
        self.assertEqual(study["accepted_study_count"], 14)
        self.assertEqual(tuple(study["accepted_order"]), study_order)
        self.assertEqual(study["nested_campaign_id"], "SD-01-GROWTH-v1")
        self.assertEqual(study["parent_study_id"], "SD-01")
        self.assertIn("before SD-02", study["execution_position"])
        self.assertEqual(study["scientific_outcome_dependencies"], [])
        self.assertEqual(
            tuple(contract["user_requirement_ids"]),
            tuple(f"DG-USER-{index:02d}" for index in range(1, 15)),
        )
        self.assertEqual(
            tuple(contract["mathematical_control_ids"]),
            tuple(f"DG-MATH-{index:02d}" for index in range(1, 11)),
        )

        registered = contract["registered_counts"]
        self.assertEqual(registered["demand_driven_scientific_runs"], 336)
        self.assertEqual(registered["topology_capacity_response_scientific_runs"], 30)
        self.assertEqual(registered["bidirectional_feedback_scientific_runs"], 30)
        self.assertEqual(registered["scientific_runs"], 396)
        self.assertEqual(registered["matched_strategy_triplets"], 132)
        self.assertEqual(registered["wrong_equivalence_refusal_fixtures"], 76)
        self.assertEqual(registered["valid_scalar_transport_rows"], 90)
        self.assertEqual(registered["non_scalable_direct_rows"], 15)
        self.assertEqual(registered["transport_correction_cases"], 180)
        self.assertEqual(registered["misscaling_refusal_fixtures"], 150)
        self.assertEqual(registered["misscaled_reuse_trajectories"], 0)

        causal = contract["capacity_population_causal_arm_registry"]
        self.assertEqual(
            tuple(causal["arm_order"]),
            (
                "ARM-1-DEMAND-DRIVES-TOPOLOGY",
                "ARM-2-TOPOLOGY-CAPACITY-PERMITS-DEMOGRAPHY",
                "ARM-3-BIDIRECTIONAL-FEEDBACK",
            ),
        )
        self.assertEqual(len(causal["scenario_order"]), 10)
        self.assertEqual(len(causal["strategy_order"]), 3)
        self.assertEqual(causal["capacity_levels"], list(range(17)))
        self.assertEqual(causal["base_capacity"], {
            "C_0": "2", "C_1": "3", "units": "usable-capacity-unit"
        })
        branches = causal["capacity_reconstruction_branches"]
        self.assertIn("targets m=2..16", branches["DIRECT_HASHED_TARGET_CAPACITY"])
        self.assertIn("preserves C_0=2 and C_1=3", branches["DIRECT_HASHED_TARGET_CAPACITY"])
        self.assertIn("null residuals", branches["DIRECT_HASHED_TARGET_CAPACITY"])
        self.assertIn("exactly one branch", branches["mutual_exclusion"])
        progression = causal["progression_counts"]
        self.assertEqual(progression["total_level_rows"], 900)
        self.assertEqual(progression["arm3_request_receipts"], 450)
        self.assertEqual(progression["completed_campaign_stall_records"], 0)
        self.assertEqual(progression["recovery_event_identities"], 216)
        self.assertIn("60 ordered", causal["capacity_population_run_evidence_rule"])

        time_growth = contract["time_and_growth"]
        self.assertEqual(time_growth["horizon_ticks"], 8192)
        self.assertEqual(time_growth["expansion_epoch_count"], 16)
        self.assertEqual(time_growth["expansion_epoch_index_range"], [0, 15])
        self.assertEqual(
            time_growth["expansion_ticks"],
            [256 * index for index in range(1, 17)],
        )
        self.assertIn("256*(e+1)", time_growth["expansion_epoch_tick_rule"])
        corrections = contract["scheduled_corrections"]
        self.assertEqual(corrections[0]["tick"], 2560)
        self.assertEqual(corrections[0]["epoch"], 9)
        self.assertEqual(corrections[0]["target"], "second B occurrence order-3 coefficient")
        self.assertEqual(corrections[0]["seed_1_witness"], "BAAAABAAAAABBAAA; first two B epochs 0 and 5")
        self.assertEqual(len(contract["same_tick_event_order"]), 10)
        self.assertEqual(
            contract["same_tick_event_order"][-1],
            "SEAL_CHECKPOINT_AFTER_ALL_RECEIPTS_ARE_DURABLE",
        )

        schema_profile = validation["schema_profile"]
        self.assertEqual(schema_profile["definition_count"], 29)
        self.assertEqual(len(schema["$defs"]), 29)
        self.assertEqual(set(schema_profile["definition_names"]), set(schema["$defs"]))
        self.assertEqual(schema_profile["root_record_count"], 20)
        self.assertEqual(len(schema["oneOf"]), 20)
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
        self.assertEqual(len(refs), 340)
        self.assertEqual(len(set(refs)), 29)
        for ref in refs:
            self.assertTrue(ref.startswith("#/$defs/"), ref)
            self.assertIn(ref.removeprefix("#/$defs/"), schema["$defs"])
        self.assertEqual(schema_profile["local_ref_occurrence_count"], 340)
        self.assertEqual(schema_profile["local_ref_unique_target_count"], 29)
        self.assertEqual(schema_profile["supported_keyword_count"], 24)
        self.assertEqual(len(schema_profile["supported_keywords"]), 24)
        self.assertEqual(schema_profile["unknown_keyword_disposition"], "REFUSE_VALIDATOR_BUILD")
        self.assertTrue(schema_profile["all_local_refs_must_resolve"])
        self.assertTrue(schema_profile["all_records_closed"])

        fixtures = validation["schema_fixtures"]
        fixture_rule = validation["schema_fixture_rule"]
        self.assertEqual(len(fixtures), 44)
        self.assertEqual(fixture_rule["required_complete_valid_fixture_count"], 44)
        self.assertEqual(
            {row["fixture_id"] for row in fixtures},
            set(fixture_rule["required_fixture_ids"]),
        )
        schema_negatives = validation["schema_negative_cases"]
        self.assertEqual(len(schema_negatives), 150)
        self.assertEqual(
            tuple(row["id"] for row in schema_negatives),
            tuple(f"DG-SN{index:02d}" for index in range(1, 151)),
        )
        self.assertEqual(
            sum(row["validation_layer"] == "JSON_SCHEMA" for row in schema_negatives),
            116,
        )
        self.assertEqual(
            sum(row["validation_layer"] == "SEMANTIC_RELATION" for row in schema_negatives),
            34,
        )
        self.assertTrue(all(row["patch"] for row in schema_negatives))
        self.assertTrue(
            all(row["required_disposition"] == "REFUSE" for row in schema_negatives)
        )
        self.assertEqual(
            tuple(check.split()[0] for check in validation["positive_checks"]),
            tuple(f"DG-P{index:03d}" for index in range(1, 269)),
        )
        self.assertEqual(
            tuple(row["id"] for row in validation["negative_cases"]),
            tuple(f"DG-N{index:03d}" for index in range(1, 142)),
        )
        self.assertEqual(validation["required_positive_check_count"], 268)
        self.assertEqual(validation["required_negative_case_count"], 141)
        self.assertEqual(validation["required_schema_negative_case_count"], 150)
        self.assertEqual(validation["required_predecessor_row_count"], 19)
        relations = validation["cross_record_semantic_relations"]
        self.assertEqual(len(relations), 44)
        self.assertTrue(any("216 events" in relation for relation in relations))
        self.assertTrue(
            any("DG-SEM-STALL-TERMINAL" in relation for relation in relations)
        )
        self.assertTrue(any("attempt_primary_evaluations <=" in relation for relation in relations))

        zero_counters = contract["required_operation_counts"]
        self.assertEqual(set(zero_counters.values()), {0})
        self.assertEqual(predecessor["required_operation_counts"], zero_counters)
        self.assertEqual(validation["required_operation_counts"], zero_counters)
        self.assertEqual(len(zero_counters), 14)
        marker = contract["completion_marker"]
        self.assertEqual(marker, predecessor["completion_marker"])
        self.assertEqual(marker, validation["completion_marker"])
        for path in STAGE_D_DYNAMIC_GROWTH_AUTHORITY_PATHS:
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

    def _audit_stage_e_reconciliation_authority(
        self, current_scope: dict[str, object]
    ) -> None:
        self.assertIn(
            current_scope["stage_e_reconciliation_phase"],
            (
                "STAGE_E_DYNAMIC_GROWTH_HARNESS_RECONCILIATION_AUTHORITY_ONLY",
                "STAGE_E_DYNAMIC_GROWTH_HARNESS_RECONCILIATION_COMPLETED_IMPLEMENTATION",
            ),
        )
        self.assertEqual(
            _git(
                "rev-parse",
                "--verify",
                f"{STAGE_E_RECONCILIATION_ACCEPTED_BASE_COMMIT}^{{commit}}",
            )
            .decode()
            .strip(),
            STAGE_E_RECONCILIATION_ACCEPTED_BASE_COMMIT,
        )
        self.assertEqual(
            _git(
                "rev-parse",
                f"{STAGE_E_RECONCILIATION_ACCEPTED_BASE_COMMIT}^{{tree}}",
            )
            .decode()
            .strip(),
            STAGE_E_RECONCILIATION_ACCEPTED_BASE_TREE,
        )
        self.assertEqual(
            _git(
                "rev-parse",
                f"{STAGE_E_RECONCILIATION_AUTHORITY_CANDIDATE}^{{tree}}",
            )
            .decode()
            .strip(),
            STAGE_E_RECONCILIATION_AUTHORITY_TREE,
        )
        self.assertEqual(
            _git(
                "rev-parse", f"{STAGE_E_RECONCILIATION_AUTHORITY_TARGET}^{{tree}}"
            )
            .decode()
            .strip(),
            STAGE_E_RECONCILIATION_AUTHORITY_TREE,
        )
        self.assertEqual(
            _git("rev-parse", f"{STAGE_E_RECONCILIATION_AUTHORITY_TARGET}^1")
            .decode()
            .strip(),
            STAGE_E_RECONCILIATION_ACCEPTED_BASE_COMMIT,
        )
        self.assertEqual(
            _git("rev-parse", f"{STAGE_E_RECONCILIATION_AUTHORITY_TARGET}^2")
            .decode()
            .strip(),
            STAGE_E_RECONCILIATION_AUTHORITY_CANDIDATE,
        )
        self.assertEqual(
            _git(
                "merge-base",
                STAGE_E_RECONCILIATION_ACCEPTED_BASE_COMMIT,
                STAGE_E_RECONCILIATION_AUTHORITY_CANDIDATE,
            )
            .decode()
            .strip(),
            STAGE_E_RECONCILIATION_ACCEPTED_BASE_COMMIT,
        )
        history_rows = tuple(
            tuple(line.split())
            for line in _git(
                "rev-list",
                "--reverse",
                "--parents",
                f"{STAGE_E_RECONCILIATION_ACCEPTED_BASE_COMMIT}..{STAGE_E_RECONCILIATION_AUTHORITY_CANDIDATE}",
            )
            .decode()
            .splitlines()
        )
        self.assertEqual(
            tuple(row[0] for row in history_rows),
            STAGE_E_RECONCILIATION_AUTHORITY_CHAIN,
        )
        self.assertEqual(
            history_rows[0][1:],
            (STAGE_E_RECONCILIATION_ACCEPTED_BASE_COMMIT,),
        )
        for previous, row in zip(
            STAGE_E_RECONCILIATION_AUTHORITY_CHAIN, history_rows[1:]
        ):
            self.assertEqual(row[1:], (previous,))

        base_entries = _tree_entries(STAGE_E_RECONCILIATION_ACCEPTED_BASE_COMMIT)
        candidate_entries = _tree_entries(STAGE_E_RECONCILIATION_AUTHORITY_CANDIDATE)
        target_entries = _tree_entries(STAGE_E_RECONCILIATION_AUTHORITY_TARGET)
        current_entries = _tree_entries(current_scope["actual_head"])
        candidate_delta = frozenset(
            path
            for path in set(base_entries) | set(candidate_entries)
            if base_entries.get(path) != candidate_entries.get(path)
        )
        self.assertEqual(
            candidate_delta, frozenset(STAGE_E_RECONCILIATION_AUTHORITY_PATHS)
        )
        self.assertEqual(candidate_entries, target_entries)
        for path in STAGE_E_RECONCILIATION_AUTHORITY_PATHS:
            self.assertNotIn(path, base_entries)
            self.assertEqual(candidate_entries[path]["mode"], "100644", path)
            self.assertEqual(candidate_entries[path]["object_type"], "blob", path)
        implementation_delta = frozenset(
            path
            for path in set(target_entries) | set(current_entries)
            if target_entries.get(path) != current_entries.get(path)
        )
        expected_implementation_delta = {
            "tests/framework/test_validation_reachability.py"
        }
        if (
            current_scope["stage_e_reconciliation_phase"]
            == "STAGE_E_DYNAMIC_GROWTH_HARNESS_RECONCILIATION_COMPLETED_IMPLEMENTATION"
        ):
            expected_implementation_delta.update(
                STAGE_E_RECONCILED_HARNESS_IMPLEMENTATION_PATHS
            )
        if current_scope["stage_f_local_binding_phase"] is not None:
            expected_implementation_delta.update(
                STAGE_F_LOCAL_BINDING_AUTHORITY_PATHS
            )
            expected_implementation_delta.update(
                STAGE_F_BINDING_EVIDENCE_CORRECTION_PATHS
            )
            expected_implementation_delta.update(
                STAGE_F_FINAL_EVIDENCE_CLOSURE_PATHS
            )
            expected_implementation_delta.update(
                STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_PATHS
            )
        if (
            current_scope["stage_f_local_binding_phase"]
            == "STAGE_F_LOCAL_BINDING_COMPLETED_IMPLEMENTATION"
        ):
            expected_implementation_delta.update(STAGE_F_LOCAL_BINDING_NEW_PATHS)
        self.assertEqual(
            implementation_delta,
            frozenset(expected_implementation_delta),
        )

        candidate_archive = _archive_members(
            STAGE_E_RECONCILIATION_AUTHORITY_CANDIDATE
        )
        target_archive = _archive_members(STAGE_E_RECONCILIATION_AUTHORITY_TARGET)
        documents = {}
        raw_by_path = {}
        for path in STAGE_E_RECONCILIATION_AUTHORITY_PATHS:
            candidate_row, candidate_raw = _object_row(
                path, candidate_entries, candidate_archive
            )
            target_row, target_raw = _object_row(
                path, target_entries, target_archive
            )
            self.assertEqual(candidate_row, target_row, path)
            self.assertEqual(candidate_raw, target_raw, path)
            current_raw = _assert_checkout_matches_blob(ROOT / path, candidate_raw, path)
            self.assertEqual(current_raw, candidate_raw, path)
            self.assertEqual(
                _sha256(current_raw),
                STAGE_E_RECONCILIATION_AUTHORITY_RAW_SHA256[path],
                path,
            )
            text = current_raw.decode("utf-8", "strict")
            self.assertEqual(text, unicodedata.normalize("NFC", text), path)
            self.assertTrue(
                current_raw.endswith(b"\n") and not current_raw.endswith(b"\n\n"),
                path,
            )
            self.assertNotIn(b"\xef\xbb\xbf", current_raw, path)
            self.assertNotIn(b"\r", current_raw, path)
            self.assertTrue(
                all(line == line.rstrip(" \t") for line in text.splitlines()),
                path,
            )
            raw_by_path[path] = current_raw
            if path.endswith(".json"):
                documents[path] = _strict_stage_d_json_bytes(current_raw, path)
                canonical = _canonical_json_bytes(documents[path])
                self.assertEqual(
                    _sha256(canonical),
                    STAGE_E_RECONCILIATION_AUTHORITY_CANONICAL_SHA256[path],
                    path,
                )

        contract = documents[
            "stage_e_dynamic_growth_harness_reconciliation_contract.json"
        ]
        schema = documents[
            "stage_e_dynamic_growth_harness_reconciliation_evidence_schema.json"
        ]
        implementation = documents[
            "stage_e_dynamic_growth_harness_reconciliation_implementation_path_manifest.json"
        ]
        predecessor = documents[
            "stage_e_dynamic_growth_harness_reconciliation_predecessor_manifest.json"
        ]
        validation = documents[
            "stage_e_dynamic_growth_harness_reconciliation_validation_contract.json"
        ]
        self.assertEqual(
            tuple(contract["candidate_files"]),
            STAGE_E_RECONCILIATION_AUTHORITY_PATHS,
        )
        self.assertEqual(contract["candidate_file_count"], 6)
        self.assertEqual(
            tuple(validation["candidate_paths"]),
            STAGE_E_RECONCILIATION_AUTHORITY_PATHS,
        )
        self.assertEqual(validation["candidate_path_count"], 6)
        self.assertEqual(
            tuple(implementation["authority_paths"]),
            STAGE_E_RECONCILIATION_AUTHORITY_PATHS,
        )
        self.assertEqual(implementation["authority_path_count"], 6)
        for document in (contract, implementation, predecessor, validation):
            self.assertEqual(
                document["accepted_base"]["commit"],
                STAGE_E_RECONCILIATION_ACCEPTED_BASE_COMMIT,
            )
            self.assertEqual(
                document["accepted_base"]["tree"],
                STAGE_E_RECONCILIATION_ACCEPTED_BASE_TREE,
            )

        self.assertEqual(predecessor["source_count"], 24)
        source_rows = predecessor["source_rows"]
        self.assertEqual(len(source_rows), 24)
        self.assertEqual(len({row["path"] for row in source_rows}), 24)
        base_archive = _archive_members(STAGE_E_RECONCILIATION_ACCEPTED_BASE_COMMIT)
        for row in source_rows:
            reconstructed, base_raw = _object_row(
                row["path"], base_entries, base_archive
            )
            self.assertEqual(
                {
                    "path": reconstructed["path"],
                    "mode": reconstructed["mode"],
                    "git_object": reconstructed["git_object"],
                    "bytes": reconstructed["byte_count"],
                    "sha256": reconstructed["raw_sha256"],
                },
                {
                    key: row[key]
                    for key in ("path", "mode", "git_object", "bytes", "sha256")
                },
                row["path"],
            )
            if row["path"].endswith(".json"):
                canonical = _canonical_json_bytes(
                    _strict_stage_d_json_bytes(base_raw, row["path"])
                )
                self.assertEqual(row["canonical_no_lf_bytes"], len(canonical))
                self.assertEqual(
                    row["canonical_no_lf_sha256"], _sha256(canonical), row["path"]
                )
            else:
                self.assertNotIn("canonical_no_lf_bytes", row)
                self.assertNotIn("canonical_no_lf_sha256", row)
            changed_workflow = (
                row["path"] == ".github/workflows/tests.yml"
                and current_scope["stage_e_reconciliation_phase"]
                == "STAGE_E_DYNAMIC_GROWTH_HARNESS_RECONCILIATION_COMPLETED_IMPLEMENTATION"
            )
            if (
                row["path"] != "tests/framework/test_validation_reachability.py"
                and not changed_workflow
            ):
                self.assertEqual(
                    _assert_checkout_matches_blob(
                        ROOT / row["path"], base_raw, row["path"]
                    ),
                    base_raw,
                    row["path"],
                )
        nested = predecessor["nested_authority_closure"]
        self.assertEqual(nested["stage_d_predecessor_rows"], 39)
        self.assertEqual(nested["continuation_direct_rows"], 9)
        self.assertEqual(nested["stage_e_direct_rows"], 17)
        self.assertEqual(nested["dynamic_growth_direct_rows"], 19)
        self.assertTrue(
            nested["all_nested_rows_reconstruct_at_their_own_accepted_commits"]
        )

        durability = implementation["prospective_durability"]
        self.assertEqual(
            durability["modified_path"],
            "tests/framework/test_validation_reachability.py",
        )
        self.assertEqual(durability["modified_path_count"], 1)
        self.assertTrue(durability["authority_integration_required_first"])
        self.assertTrue(durability["independent_audit_required"])
        harness = implementation["prospective_harness_implementation"]
        self.assertEqual(harness["modified_paths"], [".github/workflows/tests.yml"])
        self.assertEqual(harness["modified_path_count"], 1)
        self.assertEqual(
            tuple(harness["new_paths"]),
            STAGE_E_RECONCILED_HARNESS_IMPLEMENTATION_PATHS[1:],
        )
        self.assertEqual(harness["new_path_count"], 50)
        self.assertEqual(harness["total_path_count"], 51)
        self.assertEqual(implementation["accepted_stage_e_implementation_path_count"], 46)
        self.assertEqual(implementation["reconciliation_added_path_count"], 5)
        self.assertEqual(implementation["unknown_path_disposition"], "REFUSE")
        self.assertEqual(implementation["scope_derived_exclusion"], "FORBIDDEN")
        self.assertEqual(
            implementation["force_push_or_history_rewrite"], "FORBIDDEN"
        )

        def load_document(path: str) -> dict[str, object]:
            if path not in documents:
                documents[path] = _strict_stage_d_json_bytes(
                    _checkout_lf_bytes(ROOT / path, path), path
                )
            return documents[path]

        refs = _schema_refs(schema)
        self.assertEqual(len(schema["$defs"]), 25)
        self.assertEqual(len(schema["oneOf"]), 7)
        self.assertEqual(len(refs), 83)
        self.assertEqual(len(set(refs)), 22)
        for ref in refs:
            self.assertTrue(ref.startswith("#/$defs/"), ref)
            self.assertIn(ref.removeprefix("#/$defs/"), schema["$defs"])
        expected_keywords = tuple(
            contract["schema_replay"]["supported_keywords_in_order"]
        )
        self.assertEqual(len(expected_keywords), 29)
        self.assertEqual(expected_keywords[0], "$comment")
        derived_keywords = set()
        for path in contract["schema_replay"]["controlling_schemas"]:
            derived_keywords.update(_schema_keywords(load_document(path)))
        self.assertEqual(
            derived_keywords.intersection(expected_keywords), set(expected_keywords)
        )
        profile = validation["schema_profile"]
        self.assertEqual(profile["definition_count"], 25)
        self.assertEqual(profile["root_count"], 7)
        self.assertEqual(profile["local_ref_occurrence_count"], 83)
        self.assertEqual(profile["unique_local_ref_target_count"], 22)
        self.assertEqual(profile["supported_keyword_count"], 29)

        positives = validation["positive_fixture_registry"]
        self.assertEqual(len(positives), 61)
        self.assertEqual(
            tuple(row["ordinal"] for row in positives), tuple(range(61))
        )
        self.assertEqual(len({row["fixture_id"] for row in positives}), 61)
        for row in positives:
            source = load_document(row["source_path"])
            instance = _json_pointer(source, row["source_json_pointer"])
            self.assertEqual(
                _json_identity(instance),
                {
                    "byte_count": row["canonical_byte_count"],
                    "sha256": row["canonical_sha256"],
                },
                row["fixture_id"],
            )
            target_document = load_document(row["target_schema_path"])
            target = row["target_definition_or_root"]
            self.assertIn(target, target_document["$defs"], row["fixture_id"])
            self.assertTrue(
                _schema_valid(target_document, target_document["$defs"][target], instance),
                row["fixture_id"],
            )
        self.assertEqual(
            tuple(
                sum(1 for row in positives if row["source_path"] == path)
                for path in (
                    "stage_d_scientific_validation_evidence_schema.json",
                    "stage_d_completion_oriented_continuation_evidence_schema.json",
                    "stage_e_dynamic_growth_harness_reconciliation_validation_contract.json",
                    "stage_d_dynamic_growth_campaign_validation_contract.json",
                )
            ),
            (4, 2, 11, 44),
        )

        bases = {
            row["base_fixture_id"]: row
            for row in validation["refusal_base_fixtures"]
        }
        self.assertEqual(len(bases), 120)
        for row in bases.values():
            self.assertEqual(_json_identity(row["instance"]), row["canonical_identity"])
            source = load_document(row["source_path"])
            source_value = _json_pointer(source, row["source_json_pointer"])
            if (
                type(source_value) is dict
                and source_value.get("base_fixture_id") == row["base_fixture_id"]
                and "instance" in source_value
            ):
                source_value = source_value["instance"]
            elif (
                type(source_value) is dict
                and type(row["instance"]) is dict
                and "case_id" not in row["instance"]
                and set(source_value) == set(row["instance"]) | {"case_id"}
            ):
                self.assertTrue(
                    row["base_fixture_id"].startswith("keyword-")
                    and row["base_fixture_id"].endswith("-base")
                )
                self.assertTrue(source_value["case_id"].startswith("SE-KEYWORD-N"))
                source_value = {
                    key: value
                    for key, value in source_value.items()
                    if key != "case_id"
                }
            self.assertEqual(
                source_value,
                row["instance"],
                row["base_fixture_id"],
            )
        refusals = validation["refusal_registry"]
        self.assertEqual(len(refusals), 249)
        self.assertEqual(
            tuple(row["ordinal"] for row in refusals), tuple(range(249))
        )
        self.assertEqual(len({row["case_id"] for row in refusals}), 249)
        mutated_by_case = {}
        structural_by_case = {}
        for row in refusals:
            base = bases[row["base_fixture_id"]]["instance"]
            self.assertEqual(_json_identity(base), row["base_fixture_identity"])
            self.assertEqual(
                row["base_fixture_sha256"], row["base_fixture_identity"]["sha256"]
            )
            representation = row["mutation_representation"]
            if representation == "RFC6902_PATCH":
                self.assertEqual(
                    row["rfc6902_patch_or_full_instance"], row["rfc6902_patch"]
                )
                self.assertEqual(
                    _json_identity(row["rfc6902_patch"]), row["patch_identity"]
                )
                mutated = _apply_json_patch(base, row["rfc6902_patch"])
            elif representation == "FULL_MUTATED_INSTANCE":
                self.assertEqual(row["rfc6902_patch"], [])
                self.assertEqual(
                    _json_identity(row["rfc6902_patch_or_full_instance"]),
                    row["patch_identity"],
                )
                mutated = row["rfc6902_patch_or_full_instance"]
            else:
                self.assertEqual(representation, "RAW_JSON_TEXT")
                self.assertEqual(row["validation_layer"], "JSON_PARSE")
                self.assertEqual(row["rfc6902_patch"], [])
                raw_text = row["rfc6902_patch_or_full_instance"].encode("utf-8")
                raw_identity = {
                    "byte_count": len(raw_text),
                    "sha256": _sha256(raw_text),
                }
                self.assertEqual(raw_identity, row["patch_identity"])
                self.assertEqual(raw_identity, row["mutated_instance_identity"])

                def reject_float(value: str) -> object:
                    raise ValueError(f"floating JSON number: {value}")

                with self.assertRaises(ValueError):
                    json.loads(
                        row["rfc6902_patch_or_full_instance"],
                        parse_float=reject_float,
                    )
                mutated = None
            if mutated is not None:
                self.assertEqual(
                    _json_identity(mutated), row["mutated_instance_identity"]
                )
                target_document = load_document(row["target_schema_path"])
                target = row["target_definition"]
                self.assertIn(target, target_document["$defs"], row["case_id"])
                if target == "comment_nonreliance_pair":
                    self.assertTrue(
                        _schema_valid(
                            target_document, target_document["$defs"][target], mutated
                        )
                    )
                    outcomes = tuple(
                        _schema_valid(mutated[name], mutated[name], mutated["instance"])
                        for name in (
                            "schema_with_comment",
                            "schema_without_comment",
                            "schema_with_changed_comment",
                        )
                    )
                    self.assertEqual(outcomes, (True, True, True))
                    structural = True
                elif target == "keyword_conformance_pair":
                    self.assertTrue(
                        _schema_valid(
                            target_document, target_document["$defs"][target], mutated
                        )
                    )
                    structural = _schema_valid(
                        mutated["schema"], mutated["schema"], mutated["instance"]
                    )
                else:
                    structural = _schema_valid(
                        target_document, target_document["$defs"][target], mutated
                    )
                self.assertIs(
                    structural,
                    row["expected_structural_validity"],
                    row["case_id"],
                )
                mutated_by_case[row["case_id"]] = mutated
                structural_by_case[row["case_id"]] = structural
            self.assertEqual(
                row["mutated_instance_sha256"],
                row["mutated_instance_identity"]["sha256"],
            )
            self.assertNotEqual(row["required_disposition"], "PASS")
        self.assertEqual(
            tuple(
                sum(1 for row in refusals if row["source_path"] == path)
                for path in (
                    "stage_d_scientific_validation_evidence_schema.json",
                    "stage_d_completion_oriented_continuation_evidence_schema.json",
                    "stage_e_scientific_harness_evidence_schema.json",
                    "stage_d_dynamic_growth_campaign_validation_contract.json",
                    "stage_e_dynamic_growth_harness_reconciliation_validation_contract.json",
                )
            ),
            (16, 35, 24, 150, 24),
        )
        continuation_rows = tuple(
            row
            for row in refusals
            if row["source_path"]
            == "stage_d_completion_oriented_continuation_evidence_schema.json"
        )
        self.assertEqual(
            sum(row["validation_layer"] == "JSON_SCHEMA" for row in continuation_rows),
            31,
        )
        self.assertEqual(
            sum(
                row["validation_layer"] == "SEMANTIC_RELATION"
                for row in continuation_rows
            ),
            4,
        )
        self.assertEqual(
            {
                row["case_id"]
                for row in continuation_rows
                if row["validation_layer"] == "SEMANTIC_RELATION"
            },
            {
                "CONT-SCHEMA-N17",
                "CONT-SCHEMA-N21",
                "CONT-SCHEMA-N25",
                "CONT-SCHEMA-N35",
            },
        )

        n17 = next(
            row for row in continuation_rows if row["case_id"] == "CONT-SCHEMA-N17"
        )
        n17_base = bases["continuation-n17-complete-atomic-case-boundary"]
        expected_n17_context = {
            "study_id": "SD-06",
            "continuation_mode": "BETWEEN_ATOMIC_CASE_CONTINUATION_ONLY",
            "atomic_operation_kind": "DIRECT_BOOLEAN_MOBIUS_ORACLE_CASE",
            "completed_atomic_case_id": "SD-06-BOOLEAN-MOBIUS-DIRECT-CASE-000000",
            "next_absent_atomic_case_id": "SD-06-BOOLEAN-MOBIUS-DIRECT-CASE-000001",
            "continuation_requested": True,
            "base_atomic_case_complete": True,
            "mutation_sets_atomic_case_complete": False,
        }
        self.assertEqual(
            n17_base["atomic_case_continuation_context"], expected_n17_context
        )
        self.assertEqual(n17["atomic_case_continuation_context"], expected_n17_context)
        self.assertEqual(
            _json_identity(n17["rfc6902_patch"]),
            {
                "byte_count": 63,
                "sha256": "eccce0f57ae53e7c0d3c3a4d68320a364c2eecd429deef8456f796bc920c1fe5",
            },
        )
        attempt = n17_base["instance"]
        n17_mutated = mutated_by_case["CONT-SCHEMA-N17"]
        self.assertTrue(attempt["atomic_case_complete"])
        self.assertFalse(n17_mutated["atomic_case_complete"])
        self.assertTrue(attempt["continuation_permitted"])
        self.assertTrue(n17_mutated["continuation_permitted"])
        self.assertEqual(
            n17["semantic_rule_id"], "REFUSE_PARTIAL_ATOMIC_CASE_CONTINUATION"
        )
        binding = attempt["attempt_binding"]
        allocation = binding["process_allocation"]
        allocation_fields = (
            "worker_count",
            "ordered_worker_allocations",
            "scheduler_allocation_identity",
            "policy_conformance_receipt_identity",
        )
        allocation_digest = _json_identity(
            {field: allocation[field] for field in allocation_fields}
        )["sha256"]
        self.assertEqual(
            allocation_digest,
            "a3497dd174e7f9a339586b6ab68607e91872eb4e82af6819f9f719d4939bdd7a",
        )
        self.assertEqual(allocation["allocation_sha256"], allocation_digest)
        self.assertEqual(
            binding["process_allocation_identity"],
            {
                "kind": "process_allocation/v2",
                "value": allocation_digest,
                "sha256": allocation_digest,
            },
        )
        workers = allocation["ordered_worker_allocations"]
        self.assertEqual(allocation["worker_count"], len(workers))
        self.assertEqual(
            tuple(worker["worker_ordinal"] for worker in workers),
            tuple(range(len(workers))),
        )
        self.assertEqual(len({worker["process_index"] for worker in workers}), len(workers))
        self.assertEqual(
            len({_canonical_json_bytes(worker["process_identity"]) for worker in workers}),
            len(workers),
        )
        self.assertEqual(
            binding["policy_conformance_receipt_identity"],
            allocation["policy_conformance_receipt_identity"],
        )
        binding_fields = (
            "campaign_id",
            "scientific_run_id",
            "campaign_execution_binding_identity",
            "attempt_ordinal",
            "incoming_checkpoint_identity",
            "parallelization_boundary_identity",
            "worker_allocation_policy_identity",
            "storage_location_identity",
            "durability_policy_identity",
            "restart_policy_identity",
            "process_allocation_identity",
            "policy_conformance_receipt_identity",
        )
        binding_digest = _json_identity(
            {field: binding[field] for field in binding_fields}
        )["sha256"]
        self.assertEqual(
            binding_digest,
            "0ea5f567da08ac9f38cc8bf33ccba1abab62f9cc2ebe3bbfa6fb5d6c65d0dcec",
        )
        self.assertEqual(binding["binding_sha256"], binding_digest)
        self.assertEqual(
            attempt["attempt_binding_identity"],
            {
                "kind": "attempt_binding/v2",
                "value": binding_digest,
                "sha256": binding_digest,
            },
        )
        for field in (
            "campaign_id",
            "scientific_run_id",
            "attempt_ordinal",
            "incoming_checkpoint_identity",
        ):
            self.assertEqual(attempt[field], binding[field])
        attempt_fields = (
            "campaign_id",
            "scientific_run_id",
            "attempt_ordinal",
            "incoming_checkpoint_identity",
            "attempt_binding_identity",
        )
        self.assertEqual(
            _json_identity({field: attempt[field] for field in attempt_fields})[
                "sha256"
            ],
            "cc255ec085c6be703dd48c59a5d7ed0ef80aad5ea7d09900347b8d372d5371b9",
        )
        self.assertEqual(
            attempt["attempt_id"],
            "cc255ec085c6be703dd48c59a5d7ed0ef80aad5ea7d09900347b8d372d5371b9",
        )
        self.assertEqual(attempt["attempt_ordinal"], 0)
        self.assertIsNone(attempt["predecessor_attempt_identity"])
        self.assertIsNone(attempt["incoming_checkpoint_identity"])
        self.assertIsNone(attempt["scientific_disposition"])
        self.assertIsNotNone(attempt["outgoing_checkpoint_identity"])
        self.assertIsNotNone(attempt["continuation_receipt_identity"])
        self.assertTrue(attempt["identity_checks_passed"])
        self.assertTrue(attempt["watchdogs_respected"])
        self.assertTrue(structural_by_case["CONT-SCHEMA-N17"])
        self.assertTrue(
            all(
                n17_mutated[field] == attempt[field]
                for field in attempt
                if field != "atomic_case_complete"
            )
        )

        n21_base = bases[
            next(
                row["base_fixture_id"]
                for row in continuation_rows
                if row["case_id"] == "CONT-SCHEMA-N21"
            )
        ]["instance"]
        n21_mutated = mutated_by_case["CONT-SCHEMA-N21"]
        self.assertEqual(n21_mutated["campaign_id"], n21_base["campaign_id"])
        self.assertNotEqual(
            n21_mutated["parallelization_boundary_identity"],
            n21_base["parallelization_boundary_identity"],
        )
        n25_mutated = mutated_by_case["CONT-SCHEMA-N25"]
        self.assertNotEqual(
            n25_mutated["worker_count"],
            len(n25_mutated["ordered_worker_allocations"]),
        )
        n35_mutated = mutated_by_case["CONT-SCHEMA-N35"]
        self.assertNotEqual(
            n35_mutated["policy_conformance_receipt_identity"],
            n35_mutated["process_allocation"][
                "policy_conformance_receipt_identity"
            ],
        )

        non_n17_base = bases[
            "reconciliation-non-n17-refusal-ledger-row"
        ]["instance"]
        context_case = next(
            row for row in refusals if row["case_id"] == "SE-RC-CONTEXT-N01"
        )
        context_mutated = mutated_by_case["SE-RC-CONTEXT-N01"]
        self.assertNotIn("atomic_case_continuation_context", non_n17_base)
        self.assertEqual(
            context_mutated["atomic_case_continuation_context"],
            expected_n17_context,
        )
        self.assertFalse(structural_by_case["SE-RC-CONTEXT-N01"])
        self.assertEqual(context_case["validation_layer"], "JSON_SCHEMA")
        self.assertTrue(
            all(
                "atomic_case_continuation_context" not in row
                for row in refusals
                if row["case_id"] != "CONT-SCHEMA-N17"
            )
        )

        outputs = contract["evidence_outputs"]
        self.assertEqual(outputs["accepted_v1_record_count_with_manifest"], 10)
        self.assertEqual(outputs["reconciliation_v2_record_count_with_manifest"], 6)
        self.assertEqual(outputs["total_output_file_count"], 16)
        self.assertTrue(
            set(outputs["accepted_v1_record_names_byte_and_shape_semantics_preserved"])
            .isdisjoint(
                outputs["reconciliation_v2_record_names"]
                + [outputs["reconciliation_v2_manifest_name"]]
            )
        )
        dag = schema["$defs"]["dag_cache_record"]["properties"][
            "dag_complexity_cells"
        ]
        exact_cells = []
        for item in dag["prefixItems"]:
            properties = item["allOf"][1]["properties"]
            exact_cells.append(
                (
                    properties["cell_id"]["const"],
                    properties["vertices"]["const"],
                    properties["edges"]["const"],
                    properties["traversal"]["properties"]["edge_inspections"][
                        "const"
                    ],
                    properties["canonicalization"]["properties"][
                        "input_edge_count"
                    ]["const"],
                )
            )
        self.assertEqual(
            exact_cells,
            [
                ("DAG-128-256", 128, 256, 256, 256),
                ("DAG-1024-4096", 1024, 4096, 4096, 4096),
                ("DAG-10000-50000", 10000, 50000, 50000, 50000),
                ("DAG-100000-500000", 100000, 500000, 500000, 500000),
                ("DAG-512-130816", 512, 130816, 130816, 130816),
            ],
        )
        cache = schema["$defs"]["cache_invalidation_receipt"]
        self.assertTrue(
            cache["properties"]["dependency_edges"]["items"]["$ref"].endswith(
                "/dag_edge"
            )
        )
        self.assertTrue(
            cache["properties"]["alias_edges"]["items"]["$ref"].endswith(
                "/dag_edge"
            )
        )
        for name in (
            "declared_key_universe",
            "expected_affected_key_identities",
            "observed_affected_key_identities",
            "traversal_order_key_identities",
            "invalidated_key_identities",
            "recomputed_key_identities",
            "reused_key_identities",
        ):
            self.assertTrue(
                cache["properties"][name]["items"]["$ref"].endswith("/sha256")
            )
        guard = schema["$defs"]["dynamic_growth_guard_record"]["properties"]
        guarded = tuple(
            item["const"]
            for item in guard["guarded_route_ids_in_order"]["prefixItems"]
        )
        self.assertEqual(
            guarded,
            ("SD-01", "SD-01-GROWTH-v1")
            + tuple(f"SD-{index:02d}" for index in range(2, 15)),
        )
        self.assertEqual(guard["preimport_refusal_count"]["const"], 15)
        pass_manifest = schema["$defs"]["reconciliation_manifest_pass"][
            "properties"
        ]
        bound_manifest = schema["$defs"]["reconciliation_manifest_bound"][
            "properties"
        ]
        for manifest in (pass_manifest, bound_manifest):
            names = tuple(
                item["allOf"][1]["properties"]["name"]["const"]
                for item in manifest["entries"]["prefixItems"]
            )
            self.assertEqual(names, tuple(outputs["reconciliation_v2_record_names"]))
        self.assertEqual(
            pass_manifest["final_status"]["const"],
            "STAGE_E_SCIENTIFIC_HARNESS_VALIDATION_PASS",
        )
        self.assertEqual(
            bound_manifest["final_status"]["const"],
            "STAGE_E_SCIENTIFIC_HARNESS_BOUND_NOT_SUPPORTED",
        )
        self.assertEqual(bound_manifest["stage_f_route"]["const"], "REFUSE")

        mechanical = validation["mechanical_counts"]
        self.assertEqual(mechanical["schema_fixture_count"], 61)
        self.assertEqual(mechanical["refusal_base_fixtures"], 120)
        self.assertEqual(mechanical["schema_refusal_count"], 249)
        self.assertEqual(mechanical["evidence_schema_local_ref_occurrences"], 83)
        self.assertEqual(len(validation["new_schema_semantic_relations"]), 38)
        self.assertEqual(validation["required_positive_check_count"], 161)
        self.assertEqual(len(validation["positive_checks"]), 161)
        self.assertEqual(validation["required_negative_case_count"], 138)
        self.assertEqual(len(validation["negative_cases"]), 138)
        stale_rule = implementation["path_rules"][
            "scripts/validate_stage_e_harness.py"
        ]
        self.assertIn("63 fixtures", stale_rule)
        self.assertIn("247 exact refusal cases", stale_rule)
        correction = contract["preserved_implementation_manifest_count_correction"]
        self.assertEqual(correction["operative_fixture_count"], 61)
        self.assertEqual(correction["operative_refusal_count"], 249)
        zero_counters = contract["required_operation_counts"]
        self.assertEqual(len(zero_counters), 18)
        self.assertEqual(set(zero_counters.values()), {0})
        self.assertEqual(predecessor["required_operation_counts"], zero_counters)
        self.assertEqual(
            validation["required_authority_operation_counts"], zero_counters
        )
        markers = {
            STAGE_E_RECONCILIATION_AUTHORITY_PATHS[0]: contract["completion_marker"],
            STAGE_E_RECONCILIATION_AUTHORITY_PATHS[1]: contract["completion_marker"],
            STAGE_E_RECONCILIATION_AUTHORITY_PATHS[2]: (
                "STAGE_E_DYNAMIC_GROWTH_HARNESS_RECONCILIATION_"
                "EVIDENCE_SCHEMA_COMPLETE"
            ),
            STAGE_E_RECONCILIATION_AUTHORITY_PATHS[3]: implementation[
                "completion_marker"
            ],
            STAGE_E_RECONCILIATION_AUTHORITY_PATHS[4]: predecessor[
                "completion_marker"
            ],
            STAGE_E_RECONCILIATION_AUTHORITY_PATHS[5]: validation[
                "completion_marker"
            ],
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

    def _audit_stage_f_attempt_root_bootstrap(
        self, current_scope: dict[str, object]
    ) -> None:
        actual_head = current_scope["actual_head"]
        for commit in (
            STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_REQUIRED_BASE_COMMIT,
            STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_CANDIDATE,
            STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_TARGET,
        ):
            self.assertEqual(
                _git("rev-parse", "--verify", f"{commit}^{{commit}}")
                .decode()
                .strip(),
                commit,
            )
        self.assertEqual(
            _git(
                "rev-parse",
                f"{STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_REQUIRED_BASE_COMMIT}^{{tree}}",
            )
            .decode()
            .strip(),
            STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_REQUIRED_BASE_TREE,
        )
        for commit in (
            STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_CANDIDATE,
            STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_TARGET,
        ):
            self.assertEqual(
                _git("rev-parse", f"{commit}^{{tree}}").decode().strip(),
                STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_TREE,
            )
        self.assertEqual(
            _git("rev-parse", f"{STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_TARGET}^1")
            .decode()
            .strip(),
            STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_REQUIRED_BASE_COMMIT,
        )
        self.assertEqual(
            _git("rev-parse", f"{STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_TARGET}^2")
            .decode()
            .strip(),
            STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_CANDIDATE,
        )
        self.assertEqual(
            _git(
                "merge-base",
                STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_REQUIRED_BASE_COMMIT,
                STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_CANDIDATE,
            )
            .decode()
            .strip(),
            STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_REQUIRED_BASE_COMMIT,
        )
        self.assertEqual(
            _git(
                "merge-base",
                STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_TARGET,
                actual_head,
            )
            .decode()
            .strip(),
            STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_TARGET,
        )

        base_entries = _tree_entries(STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_REQUIRED_BASE_COMMIT)
        candidate_entries = _tree_entries(STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_CANDIDATE)
        target_entries = _tree_entries(STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_TARGET)
        current_entries = _tree_entries(actual_head)
        candidate_delta = frozenset(
            path
            for path in set(base_entries) | set(candidate_entries)
            if base_entries.get(path) != candidate_entries.get(path)
        )
        self.assertEqual(
            candidate_delta, frozenset(STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_PATHS)
        )
        self.assertEqual(candidate_entries, target_entries)

        base_archive = _archive_members(
            STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_REQUIRED_BASE_COMMIT
        )
        candidate_archive = _archive_members(STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_CANDIDATE)
        target_archive = _archive_members(STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_TARGET)
        current_archive = _archive_members(actual_head)
        documents = {}
        for path, mode, git_object, byte_count, raw_sha256 in (
            STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_ROWS
        ):
            expected_row = {
                "path": path,
                "mode": mode,
                "object_type": "blob",
                "git_object": git_object,
                "byte_count": byte_count,
                "raw_sha256": raw_sha256,
            }
            candidate_row, candidate_raw = _object_row(
                path, candidate_entries, candidate_archive
            )
            target_row, target_raw = _object_row(path, target_entries, target_archive)
            current_row, current_raw = _object_row(
                path, current_entries, current_archive
            )
            self.assertEqual(candidate_row, expected_row, path)
            self.assertEqual(target_row, expected_row, path)
            self.assertEqual(current_row, expected_row, path)
            self.assertEqual(candidate_raw, target_raw, path)
            self.assertEqual(candidate_raw, current_raw, path)
            self.assertEqual(
                _assert_checkout_matches_blob(ROOT / path, candidate_raw, path),
                candidate_raw,
                path,
            )
            text = candidate_raw.decode("utf-8", "strict")
            self.assertEqual(text, unicodedata.normalize("NFC", text), path)
            self.assertTrue(
                candidate_raw.endswith(b"\n") and not candidate_raw.endswith(b"\n\n"),
                path,
            )
            self.assertNotIn(b"\xef\xbb\xbf", candidate_raw, path)
            self.assertNotIn(b"\r", candidate_raw, path)
            self.assertTrue(
                all(line == line.rstrip(" \t") for line in text.splitlines()), path
            )
            if path.endswith(".json"):
                documents[path] = _strict_stage_d_json_bytes(candidate_raw, path)

        contract = documents[
            "stage_f_local_execution_binding_attempt_root_bootstrap_correction_contract.json"
        ]
        schema = documents[
            "stage_f_local_execution_binding_attempt_root_bootstrap_correction_schema.json"
        ]
        implementation = documents[
            "stage_f_local_execution_binding_attempt_root_bootstrap_correction_implementation_path_manifest.json"
        ]
        predecessor = documents[
            "stage_f_local_execution_binding_attempt_root_bootstrap_correction_predecessor_manifest.json"
        ]
        validation = documents[
            "stage_f_local_execution_binding_attempt_root_bootstrap_correction_validation_contract.json"
        ]
        required_target = {
            "commit": STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_REQUIRED_BASE_COMMIT,
            "tree": STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_REQUIRED_BASE_TREE,
        }
        for document in (contract, implementation, validation):
            self.assertEqual(document["required_current_target"], required_target)
        predecessor_target = predecessor["required_current_target"]
        self.assertEqual(
            {key: predecessor_target[key] for key in ("commit", "tree")},
            required_target,
        )
        self.assertEqual(
            predecessor_target,
            {
                "commit": STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_REQUIRED_BASE_COMMIT,
                "tree": STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_REQUIRED_BASE_TREE,
                "recursive_blob_row_count": 454,
                "mode_100644_count": 452,
                "mode_100755_count": 2,
                "symlink_count": 0,
                "submodule_count": 0,
                "total_blob_bytes": 133039592,
                "ordered_path_projection_encoding": "canonical JSON array of Git paths in git ls-tree -r order, UTF-8 NFC, sorted keys, comma-colon separators, no final LF",
                "ordered_path_projection_sha256": "8b1d0bb830b16512fd439c8caa88e44b3bb8eb8f99c290a6451caddd4de96b67",
                "ordered_row_projection_fields": [
                    "path",
                    "mode",
                    "git_object",
                    "byte_count",
                    "raw_sha256",
                ],
                "ordered_row_projection_encoding": "canonical JSON array of closed row objects in git ls-tree -r order, UTF-8 NFC, sorted keys, comma-colon separators, no final LF",
                "ordered_row_projection_sha256": "dd6d520abaec7f6adee77d0dd4e74684dd7db4e09161f7f7fce4bbdb81878350",
            },
        )
        self.assertEqual(
            tuple(contract["authority_files_in_order"]),
            STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_PATHS,
        )
        self.assertEqual(contract["authority_file_count"], 6)
        self.assertEqual(
            tuple(implementation["authority_paths"]),
            STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_PATHS,
        )
        self.assertEqual(implementation["authority_path_count"], 6)
        self.assertEqual(
            validation["authority_candidate"],
            {
                "ordered_paths": list(STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_PATHS),
                "path_count": 6,
                "mode": "100644",
                "additions_only": True,
            },
        )

        accepted_rows = (
            predecessor["accepted_original_authority_rows"]
            + predecessor["accepted_evidence_correction_authority_rows"]
            + predecessor["accepted_final_evidence_closure_authority_rows"]
        )
        self.assertEqual(predecessor["accepted_prior_authority_row_count"], 18)
        self.assertEqual(len(accepted_rows), 18)
        self.assertEqual(
            tuple(row["path"] for row in accepted_rows),
            STAGE_F_LOCAL_BINDING_AUTHORITY_PATHS
            + STAGE_F_BINDING_EVIDENCE_CORRECTION_PATHS
            + STAGE_F_FINAL_EVIDENCE_CLOSURE_PATHS,
        )
        for row in accepted_rows:
            path = row["path"]
            reconstructed, reconstructed_raw = _object_row(
                path, base_entries, base_archive
            )
            projected = {
                key: reconstructed[key]
                for key in ("path", "mode", "git_object", "byte_count", "raw_sha256")
            }
            self.assertEqual(projected, row, path)
            for entries, archive in (
                (candidate_entries, candidate_archive),
                (target_entries, target_archive),
                (current_entries, current_archive),
            ):
                later_row, later_raw = _object_row(path, entries, archive)
                self.assertEqual(later_row, reconstructed, path)
                self.assertEqual(later_raw, reconstructed_raw, path)

        reachability_row = predecessor["accepted_reachability_row"]
        reconstructed_reachability, reachability_raw = _object_row(
            STAGE_F_LOCAL_BINDING_REACHABILITY_PATH, base_entries, base_archive
        )
        self.assertEqual(
            {
                key: reconstructed_reachability[key]
                for key in ("path", "mode", "git_object", "byte_count", "raw_sha256")
            },
            reachability_row,
        )
        self.assertNotEqual(
            _object_row(
                STAGE_F_LOCAL_BINDING_REACHABILITY_PATH,
                current_entries,
                current_archive,
            )[1],
            reachability_raw,
        )

        v1_schema = _strict_stage_d_json_bytes(
            _object_row(
                "stage_f_local_execution_binding_evidence_schema.json",
                current_entries,
                current_archive,
            )[1],
            "stage_f_local_execution_binding_evidence_schema.json",
        )
        v2_schema = _strict_stage_d_json_bytes(
            _object_row(
                "stage_f_local_execution_binding_evidence_correction_schema.json",
                current_entries,
                current_archive,
            )[1],
            "stage_f_local_execution_binding_evidence_correction_schema.json",
        )
        v3_schema = _strict_stage_d_json_bytes(
            _object_row(
                "stage_f_local_execution_binding_final_evidence_closure_correction_schema.json",
                current_entries,
                current_archive,
            )[1],
            "stage_f_local_execution_binding_final_evidence_closure_correction_schema.json",
        )
        v1_definitions = v1_schema["$defs"]
        v2_definitions = v2_schema["$defs"]
        v3_definitions = v3_schema["$defs"]
        v4_definitions = schema["$defs"]

        def definition_delta(
            prior: dict[str, object], successor: dict[str, object]
        ) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
            key = lambda value: unicodedata.normalize("NFC", value).encode("utf-8")
            added = tuple(sorted(set(successor) - set(prior), key=key))
            changed = tuple(
                sorted(
                    (
                        name
                        for name in set(prior) & set(successor)
                        if prior[name] != successor[name]
                    ),
                    key=key,
                )
            )
            removed = tuple(sorted(set(prior) - set(successor), key=key))
            return added, changed, removed

        immediate_added, immediate_changed, immediate_removed = definition_delta(
            v3_definitions, v4_definitions
        )
        historical_added, historical_changed, historical_removed = definition_delta(
            v1_definitions, v4_definitions
        )
        effective = contract["effective_schema"]
        self.assertEqual(
            (
                len(v1_definitions),
                len(v2_definitions),
                len(v3_definitions),
                len(v4_definitions),
            ),
            (143, 220, 228, 243),
        )
        self.assertEqual(
            immediate_added,
            tuple(effective["added_definitions_in_strict_nfc_utf8_order"]),
        )
        self.assertEqual(
            immediate_changed,
            tuple(effective["changed_definitions_in_strict_nfc_utf8_order"]),
        )
        self.assertFalse(immediate_removed)
        self.assertEqual(
            (
                len(immediate_added),
                len(immediate_changed),
                len(immediate_removed),
                len(historical_added),
                len(historical_changed),
                len(historical_removed),
            ),
            (15, 28, 0, 100, 28, 0),
        )
        schema_delta = validation["schema_delta"]
        self.assertEqual(tuple(schema_delta["added_definitions"]), immediate_added)
        self.assertEqual(tuple(schema_delta["changed_definitions"]), immediate_changed)
        self.assertEqual(schema_delta["removed_definitions"], [])
        refs = _schema_refs(schema)
        self.assertEqual(len(refs), 2588)
        for ref in refs:
            self.assertIs(type(ref), str)
            self.assertTrue(ref.startswith("#/$defs/"), ref)
            _json_pointer(schema, ref[1:])
        self.assertEqual(len(schema["oneOf"]), 52)
        root_names = tuple(
            item["$ref"].removeprefix("#/$defs/") for item in schema["oneOf"]
        )
        self.assertEqual(len(root_names), len(set(root_names)))

        prior_validation = _strict_stage_d_json_bytes(
            _object_row(
                "stage_f_local_execution_binding_final_evidence_closure_correction_validation_contract.json",
                current_entries,
                current_archive,
            )[1],
            "stage_f_local_execution_binding_final_evidence_closure_correction_validation_contract.json",
        )
        cases = validation["cases"]
        self.assertEqual(cases[:184], prior_validation["cases"])
        self.assertEqual(
            tuple(row["id"] for row in cases),
            tuple(f"BEC-{index:03d}" for index in range(1, 197)),
        )
        self.assertEqual(
            (
                validation["case_count"],
                validation["positive_case_count"],
                validation["negative_case_count"],
                sum(row["class"] == "POSITIVE" for row in cases),
                sum(row["class"] == "NEGATIVE" for row in cases),
            ),
            (196, 33, 163, 33, 163),
        )
        self.assertEqual(
            cases[-2],
            {
                "id": "BEC-195",
                "class": "POSITIVE",
                "mutation": "VALID_CANONICAL_V4_AUTHORITY_SET_IMPLEMENTATION_AND_VALIDATOR_PREIMAGES_WITH_EXACT_24_AUTHORITY_ROWS_REPEATED_IN_THE_IMPLEMENTATION_PREIMAGE_14_IMPLEMENTATION_ROWS_7_VALIDATOR_SOURCE_ROWS_AND_ALL_SEVEN_DOWNSTREAM_V3_CONSUMERS_DIRECTLY_BINDING_THE_SAME_V4_IDENTITIES",
                "expected": "PASS",
                "falsifier": "CURRENT_V4_AUTHORITY_PROVENANCE_CHAIN_UNREPRESENTABLE",
            },
        )
        self.assertEqual(
            cases[-1],
            {
                "id": "BEC-196",
                "class": "NEGATIVE",
                "mutation": "OMIT_REORDER_DUPLICATE_SUBSTITUTE_OR_ADD_A_V4_AUTHORITY_ROW_MISMATCH_THE_24_ROW_AUTHORITY_PROJECTION_BETWEEN_AUTHORITY_AND_IMPLEMENTATION_PREIMAGES_OR_SPLICE_ANY_V4_AUTHORITY_IMPLEMENTATION_OR_VALIDATOR_IDENTITY_IN_ANY_DOWNSTREAM_V3_CONSUMER",
                "expected": "REFUSE",
                "falsifier": "CURRENT_V4_AUTHORITY_OR_DOWNSTREAM_V3_PROVENANCE_FAIL_OPEN",
            },
        )
        for row in cases:
            if row["class"] == "NEGATIVE":
                self.assertIs(type(row["falsifier"]), str)
                self.assertTrue(row["falsifier"].strip(), row["id"])
                self.assertEqual(row["expected"], "REFUSE", row["id"])
        for row in cases[184:]:
            self.assertIs(type(row["falsifier"]), str)
            self.assertTrue(row["falsifier"].strip(), row["id"])
        validation_text = json.dumps(
            validation, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        self.assertIn(
            "IMMEDIATE_SCHEMA_DELTA_228_TO_243_ADDED15_CHANGED28_REMOVED0",
            validation["static_positive_checks"],
        )
        self.assertNotIn("CHANGED26", validation_text)
        self.assertEqual(
            validation["executable_semantic_recomputations"][:2],
            [
                "RECOMPUTE_CANONICAL_V4_AUTHORITY_IMPLEMENTATION_VALIDATOR_PREIMAGES_IDENTITIES_AND_EXACT_24_24_14_ROW_ORDER",
                "RECOMPUTE_EVERY_DOWNSTREAM_V3_CONSUMER_IDENTITY_EQUALITY_TO_THE_SAME_V4_AUTHORITY_IMPLEMENTATION_AND_VALIDATOR_CHAIN",
            ],
        )

        identity_closure = contract["identity_and_preimage_closure"]
        self.assertEqual(
            identity_closure,
            {
                "successor_authority_set_version": "v4",
                "successor_authority_row_count": 24,
                "authority_rows_order": "six_accepted_v1_then_six_accepted_v2_then_six_accepted_v3_then_six_integrated_v4",
                "unchanged_route_authority_projection_count": 15,
                "binding_implementation_exact_path_row_count": 14,
                "binding_validator_source_member_count": 7,
                "binding_validator_zipapp_member_count": 5,
                "binding_validator_zip_method": "ZIP_STORED",
                "all_authority_rows_equal_in_integrated_authority_and_implementation_trees": True,
                "bundle_readiness_validation_audit_packet_post_packet_receipt_and_campaign_authorization_consumer_identity_kinds_are_v3": True,
                "successor_consumer_identity_kinds_are_v2": False,
                "v2_successor_consumer_identity_in_v3_successor_chain": "REFUSE",
                "future_digest_or_git_coordinate_in_preimage": "REFUSE",
                "identity_graph_acyclic": True,
                "bundle_embeds_complete_v4_authority_implementation_and_validator_preimages": True,
                "bundle_readiness_validation_audit_packet_post_packet_receipt_and_campaign_authorization_directly_bind_v4_identities": True,
                "successor_consumer_identity_kinds_are_v3": True,
                "v3_authority_implementation_or_validator_identity_in_v4_identity_chain": "REFUSE",
                "v4_identity_mismatch_in_any_v3_successor_consumer": "REFUSE",
            },
        )
        authority_preimage = v4_definitions["binding_authority_set_preimage"]
        implementation_preimage = v4_definitions["binding_implementation_preimage"]
        validator_preimage = v4_definitions["binding_validator_preimage"]
        self.assertEqual(
            authority_preimage["properties"]["schema"]["const"],
            "stage_f_binding_authority_set/v4",
        )
        self.assertEqual(
            (
                authority_preimage["properties"]["ordered_local_authority_file_rows"]["minItems"],
                authority_preimage["properties"]["ordered_local_authority_file_rows"]["maxItems"],
                authority_preimage["properties"]["local_authority_file_count"]["const"],
            ),
            (24, 24, 24),
        )
        self.assertEqual(
            implementation_preimage["properties"]["schema"]["const"],
            "stage_f_binding_implementation/v4",
        )
        self.assertEqual(
            (
                implementation_preimage["properties"]["ordered_integrated_authority_file_rows"]["minItems"],
                implementation_preimage["properties"]["ordered_integrated_authority_file_rows"]["maxItems"],
                implementation_preimage["properties"]["integrated_authority_file_count"]["const"],
                implementation_preimage["properties"]["ordered_implementation_file_rows"]["minItems"],
                implementation_preimage["properties"]["ordered_implementation_file_rows"]["maxItems"],
                implementation_preimage["properties"]["implementation_file_count"]["const"],
            ),
            (24, 24, 24, 14, 14, 14),
        )
        self.assertEqual(
            validator_preimage["properties"]["schema"]["const"],
            "stage_f_binding_validator/v4",
        )
        self.assertEqual(
            (
                validator_preimage["properties"]["ordered_validator_source_file_rows"]["minItems"],
                validator_preimage["properties"]["ordered_validator_source_file_rows"]["maxItems"],
                validator_preimage["properties"]["validator_source_file_count"]["const"],
                validator_preimage["properties"]["artifact_build_method"]["const"],
                validator_preimage["properties"]["executable_artifact_build_method"]["const"],
            ),
            (
                7,
                7,
                7,
                "CANONICAL_VALIDATOR_SOURCE_BUNDLE_V1",
                "DETERMINISTIC_LOCKED_VALIDATOR_ZIPAPP_V1",
            ),
        )
        active_authority_paths = (
            tuple(row["path"] for row in accepted_rows)
            + STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_PATHS
        )
        self.assertEqual(len(active_authority_paths), 24)
        self.assertEqual(len(set(active_authority_paths)), 24)
        consumer_kinds = {
            "local_binding_bundle": "stage_f_local_binding_bundle/v3",
            "binding_validation_receipt": "stage_f_binding_validation_receipt/v3",
            "binding_readiness_record": "stage_f_local_binding_readiness/v3",
            "independent_binding_audit_receipt": "stage_f_independent_binding_audit/v3",
            "sealed_campaign_packet_manifest": "stage_f_sealed_campaign_packet/v3",
            "post_packet_user_authorization_receipt": "stage_f_post_packet_user_authorization_receipt/v3",
            "campaign_authorization": "stage_f_campaign_authorization/v3",
        }
        identity_kind_keys = {
            "local_binding_bundle": "local_binding_bundle",
            "binding_validation_receipt": "binding_validation_receipt",
            "binding_readiness_record": "binding_readiness",
            "independent_binding_audit_receipt": "independent_binding_audit",
            "sealed_campaign_packet_manifest": "sealed_campaign_packet",
            "post_packet_user_authorization_receipt": "post_packet_authorization_receipt",
            "campaign_authorization": "campaign_authorization",
        }
        for name, kind in consumer_kinds.items():
            definition = v4_definitions[name]
            self.assertEqual(definition["properties"]["schema"]["const"], kind)
            self.assertEqual(
                contract["successor_identity_kinds"][identity_kind_keys[name]], kind
            )
            self.assertTrue(
                {
                    "authority_set_identity",
                    "binding_implementation_identity",
                    "validator_identity",
                }
                <= set(definition["required"]),
                name,
            )
            self.assertEqual(
                definition["properties"]["authority_set_identity"]["$ref"],
                "#/$defs/binding_authority_set_identity",
            )
            self.assertEqual(
                definition["properties"]["binding_implementation_identity"]["$ref"],
                "#/$defs/binding_implementation_identity",
            )
            self.assertEqual(
                definition["properties"]["validator_identity"]["$ref"],
                "#/$defs/binding_validator_identity",
            )
        self.assertTrue(
            {
                "authority_set_preimage",
                "binding_implementation_preimage",
                "binding_validator_preimage",
            }
            <= set(v4_definitions["local_binding_bundle"]["required"])
        )
        self.assertEqual(
            v4_definitions["nonzero_uint64"],
            {
                "type": "integer",
                "minimum": 1,
                "maximum": 18446744073709551615,
            },
        )
        self.assertEqual(
            v4_definitions["valid_handle_value_uint64"],
            {
                "type": "integer",
                "minimum": 1,
                "maximum": 18446744073709551614,
            },
        )

        bootstrap = contract["attempt_root_bootstrap_correction"]
        self.assertEqual(
            bootstrap["dag_in_order"],
            [
                "BOOTSTRAP_TRANSACTION_PREIMAGE",
                "BOOTSTRAP_PROTECTION_AND_PRECREATE_TICKET",
                "WATCH_OBSERVATION_USN_OBSERVATION_EXECUTION_ATTEMPT_GENESIS_CREATION_OBSERVATION",
                "REALIZED_ROOT_PROTECTION_EPOCH",
                "EVIDENCE_LEDGER_GENESIS",
            ],
        )
        self.assertEqual(
            bootstrap["dag_edges"],
            [
                "TRANSACTION_TO_PROTECTION",
                "PROTECTION_TO_TICKET",
                "PROTECTION_AND_TICKET_TO_WATCH_USN_GENESIS_CREATION",
                "WATCH_USN_GENESIS_CREATION_TO_REALIZED_EPOCH",
                "REALIZED_EPOCH_TO_LEDGER_GENESIS",
            ],
        )
        self.assertTrue(bootstrap["acyclic"])
        self.assertFalse(bootstrap["scientific_write_authorized"])
        ticket = v4_definitions["stage_f_attempt_root_mutation_ticket"]["properties"]
        self.assertEqual(ticket["operation"]["const"], "CREATE_ATTEMPT_ROOT")
        self.assertEqual(ticket["create_api"]["const"], "CreateDirectoryW")
        self.assertEqual(
            ticket["permitted_watch_actions"],
            {
                "type": "array",
                "prefixItems": [{"const": "FILE_ACTION_ADDED"}],
                "items": False,
                "minItems": 1,
                "maxItems": 1,
            },
        )
        self.assertEqual(ticket["required_usn_reason_bits_uint32"]["const"], 0x100)
        self.assertEqual(
            ticket["permitted_usn_reason_mask_uint32"]["const"], 0x80000100
        )
        for field in (
            "future_root_epoch_identity_present",
            "future_ledger_identity_present",
            "future_watch_usn_creation_or_genesis_identity_present",
        ):
            self.assertFalse(ticket[field]["const"])
        self.assertTrue(ticket["single_use_required"]["const"])
        legacy_operations = v4_definitions["stage_f_authorized_mutation_ticket"][
            "properties"
        ]["operation"]["enum"]
        self.assertNotIn("CREATE_ATTEMPT_ROOT", legacy_operations)

        watch_completion = v4_definitions[
            "stage_f_attempt_root_watch_completion_observation"
        ]["properties"]
        self.assertEqual(
            (
                watch_completion["notification_filter"]["const"],
                watch_completion["buffer_capacity"]["const"],
                watch_completion["raw_buffer_capacity"]["const"],
                watch_completion["bootstrap_ticket_match_count"]["const"],
                watch_completion["ordinary_authorized_ticket_match_count"]["const"],
                watch_completion["refused_protected_record_count"]["const"],
            ),
            (351, 65536, 65536, 1, 0, 0),
        )
        self.assertEqual(
            v4_definitions["stage_f_attempt_root_watch_completion_observation"][
                "properties"
            ]["records"]["not"]["contains"]["properties"]["scope_disposition"][
                "enum"
            ],
            ["AUTHORIZED_TICKET_MATCH", "REFUSED_PROTECTED_MUTATION"],
        )
        watch_observation = v4_definitions["stage_f_attempt_root_watch_observation"][
            "properties"
        ]
        self.assertEqual(
            (
                watch_observation["matching_bootstrap_record_count"]["const"],
                watch_observation["ordinary_authorized_ticket_match_count"]["const"],
                watch_observation["refused_protected_record_count"]["const"],
            ),
            (1, 0, 0),
        )
        usn_range = v4_definitions["stage_f_attempt_root_usn_range"]["properties"]
        self.assertEqual(
            (
                usn_range["bootstrap_ticket_match_count"]["const"],
                usn_range["ordinary_authorized_ticket_match_count"]["const"],
                usn_range["refused_protected_record_count"]["const"],
                usn_range["range_complete"]["const"],
                usn_range["wrapped_or_gapped"]["const"],
                usn_range["unknown_record_count"]["const"],
                usn_range["access_errors"]["const"],
            ),
            (1, 0, 0, True, False, 0, 0),
        )
        self.assertEqual(
            usn_range["records"]["not"]["contains"]["properties"][
                "scope_disposition"
            ]["enum"],
            ["AUTHORIZED_TICKET_MATCH", "REFUSED_PROTECTED_MUTATION"],
        )
        bootstrap_scope = "ATTEMPT_ROOT_BOOTSTRAP_TICKET_MATCH"
        for record_name in ("stage_f_file_notify_record", "stage_f_usn_record"):
            record = v4_definitions[record_name]
            self.assertEqual(
                record["properties"]["scope_disposition"]["enum"],
                [
                    "AUTHORIZED_TICKET_MATCH",
                    bootstrap_scope,
                    "OUTSIDE_PROTECTED_SCOPE",
                    "REFUSED_PROTECTED_MUTATION",
                ],
            )
            bootstrap_branches = [
                branch
                for branch in record["allOf"]
                if branch.get("if", {})
                .get("properties", {})
                .get("scope_disposition", {})
                .get("const")
                == bootstrap_scope
            ]
            self.assertEqual(len(bootstrap_branches), 1, record_name)
            bootstrap_fields = bootstrap_branches[0]["then"]["properties"]
            self.assertEqual(
                bootstrap_fields["protected_identity_match_count"], {"const": 1}
            )
            self.assertEqual(
                bootstrap_fields["mutation_ticket_identity"], {"type": "null"}
            )
            self.assertEqual(
                bootstrap_fields["mutation_ticket_match_count"], {"const": 0}
            )
            self.assertEqual(
                bootstrap_fields["mutation_transaction_identity"], {"type": "null"}
            )
            self.assertEqual(
                bootstrap_fields["ledger_mutation_entry_identity"],
                {"type": "null"},
            )
            self.assertEqual(
                bootstrap_fields["bootstrap_transaction_identity"]["$ref"],
                "#/$defs/stage_f_attempt_root_bootstrap_transaction_identity",
            )
            self.assertEqual(
                bootstrap_fields["bootstrap_protection_identity"]["$ref"],
                "#/$defs/stage_f_attempt_root_bootstrap_protection_identity",
            )
            self.assertEqual(
                bootstrap_fields["attempt_root_ticket_identity"]["$ref"],
                "#/$defs/stage_f_attempt_root_mutation_ticket_identity",
            )
        self.assertEqual(
            (
                contract["usn_range_closure"]["query_output_byte_count"],
                contract["usn_range_closure"]["read_input_byte_count"],
                contract["usn_range_closure"]["passing_range_refused_record_count"],
            ),
            (80, 48, 0),
        )
        genesis = v4_definitions["stage_f_execution_attempt_genesis"]["properties"]
        self.assertEqual(
            (
                genesis["attempt_absent_observation"]["const"],
                genesis["create_api"]["const"],
                genesis["create_returned_nonzero"]["const"],
                genesis["created_once"]["const"],
                genesis["ticket_consumed_by_this_create_call"]["const"],
            ),
            (
                "GetFileAttributesW_INVALID_FILE_ATTRIBUTES_ERROR_FILE_NOT_FOUND",
                "CreateDirectoryW",
                True,
                True,
                True,
            ),
        )
        creation = v4_definitions["stage_f_attempt_root_creation_observation"][
            "properties"
        ]
        self.assertEqual(
            (
                creation["create_api"]["const"],
                creation["create_returned_nonzero"]["const"],
                creation["ticket_preceded_create_and_was_consumed_by_only_this_call"][
                    "const"
                ],
            ),
            ("CreateDirectoryW", True, True),
        )
        epoch = v4_definitions["stage_f_root_protection_epoch"]
        self.assertTrue(
            {
                "execution_attempt_genesis",
                "bootstrap_protection",
                "attempt_root_ticket",
                "attempt_root_watch_observation",
                "attempt_root_usn_observation",
                "attempt_root_creation_observation",
            }
            <= set(epoch["required"])
        )
        self.assertTrue(
            epoch["properties"][
                "bootstrap_watch_usn_genesis_creation_and_epoch_bijection_recomputed"
            ]["const"]
        )
        ledger = v4_definitions["stage_f_evidence_ledger_genesis"]
        self.assertTrue(
            {
                "execution_attempt_genesis_identity",
                "root_protection_epoch_identity",
                "bootstrap_transaction_identity",
                "bootstrap_protection_identity",
                "attempt_root_ticket_identity",
                "attempt_root_watch_observation_identity",
                "attempt_root_usn_observation_identity",
                "attempt_root_creation_observation_identity",
            }
            <= set(ledger["required"])
        )
        self.assertEqual(
            (
                ledger["properties"]["entry_type"]["const"],
                ledger["properties"]["ordinal"]["const"],
                ledger["properties"]["bootstrap_ticket_consumed_once"]["const"],
                ledger["properties"][
                    "future_ledger_entry_identity_in_preledger_bootstrap_preimages"
                ]["const"],
            ),
            ("GENESIS", 0, True, False),
        )
        semantic_algorithms = {
            row["name"]: row for row in validation["semantic_recomputation_algorithms"]
        }
        self.assertEqual(
            tuple(
                semantic_algorithms["V4_AUTHORITY_AND_DOWNSTREAM_IDENTITY_CLOSURE"][
                    "inputs"
                ]
            ),
            (
                "binding_authority_set_preimage/v4",
                "binding_authority_set_identity/v4",
                "binding_implementation_preimage/v4",
                "binding_implementation_identity/v4",
                "binding_validator_preimage/v4",
                "binding_validator_identity/v4",
                "local_binding_bundle/v3",
                "binding_validation_receipt/v3",
                "binding_readiness_record/v3",
                "independent_binding_audit_receipt/v3",
                "sealed_campaign_packet_manifest/v3",
                "post_packet_user_authorization_receipt/v3",
                "campaign_authorization/v3",
            ),
        )
        self.assertEqual(
            set(
                semantic_algorithms["V4_AUTHORITY_AND_DOWNSTREAM_IDENTITY_CLOSURE"][
                    "refuse"
                ]
            ),
            {
                "authority row missing, reordered, duplicated, substituted or added",
                "authority rows or identity differ between authority and implementation preimages",
                "implementation row or identity mismatch",
                "validator source row or identity mismatch",
                "v2 consumer kind or v3 authority, implementation or validator identity replay",
                "downstream v3 consumer identity splice",
                "future digest or Git coordinate in any preimage",
            },
        )
        self.assertEqual(
            tuple(semantic_algorithms["ATTEMPT_ROOT_BOOTSTRAP_DAG"]["inputs"]),
            (
                "stage_f_attempt_root_bootstrap_transaction_preimage",
                "stage_f_attempt_root_bootstrap_protection",
                "stage_f_attempt_root_mutation_ticket",
                "stage_f_attempt_root_watch_completion_observation",
                "stage_f_attempt_root_watch_observation",
                "stage_f_attempt_root_usn_range",
                "stage_f_attempt_root_usn_observation",
                "stage_f_execution_attempt_genesis",
                "stage_f_attempt_root_creation_observation",
                "stage_f_root_protection_epoch",
                "stage_f_evidence_ledger_genesis",
            ),
        )

        reachability = implementation["prospective_reachability_correction"]
        self.assertEqual(
            reachability["modified_paths"],
            [STAGE_F_LOCAL_BINDING_REACHABILITY_PATH],
        )
        self.assertEqual(
            (
                reachability["modified_path_count"],
                reachability["new_path_count"],
                reachability["total_path_count"],
            ),
            (1, 0, 1),
        )
        self.assertTrue(reachability["independent_audit_required_before_implementation"])
        self.assertFalse(reachability["counts_as_implementation_path"])
        self.assertEqual(
            reachability["project_import_production_validator_host_probe_or_science"],
            "FORBIDDEN",
        )
        prospective = implementation["prospective_implementation"]
        self.assertEqual(
            tuple(prospective["modified_paths"]), STAGE_F_LOCAL_BINDING_MODIFIED_PATHS
        )
        self.assertEqual(tuple(prospective["new_paths"]), STAGE_F_LOCAL_BINDING_NEW_PATHS)
        self.assertEqual(
            (
                prospective["modified_path_count"],
                prospective["new_path_count"],
                prospective["total_path_count"],
            ),
            (2, 12, 14),
        )
        self.assertEqual(
            implementation["final_descendant_path_closure"],
            {
                "accepted_stage_e_path_count": 51,
                "accepted_stage_f_v1_authority_path_count": 6,
                "accepted_stage_f_evidence_correction_authority_path_count": 6,
                "accepted_stage_f_final_evidence_closure_authority_path_count": 6,
                "reachability_unique_path_count": 1,
                "attempt_root_bootstrap_correction_authority_added_path_count": 6,
                "successor_active_authority_row_count": 24,
                "stage_f_new_unique_path_count": 12,
                "stage_f_modified_paths_overlapping_accepted_stage_e_count": 2,
                "historical_authority_only_unique_path_count": 70,
                "historical_completed_implementation_unique_path_count": 82,
                "authority_only_unique_path_count": 76,
                "final_unique_path_count": 88,
                "missing_extra_duplicate_or_reordered_path_disposition": "REFUSE",
            },
        )
        self.assertEqual(len(STAGE_F_LOCAL_BINDING_DESCENDANT_PATHS), 88)
        self.assertEqual(len(set(STAGE_F_LOCAL_BINDING_DESCENDANT_PATHS)), 88)

        post_integration_delta = frozenset(
            path
            for path in set(target_entries) | set(current_entries)
            if target_entries.get(path) != current_entries.get(path)
        )
        expected_post_integration_delta = {STAGE_F_LOCAL_BINDING_REACHABILITY_PATH}
        expected_status = {STAGE_F_LOCAL_BINDING_REACHABILITY_PATH: "M"}
        if (
            current_scope["stage_f_local_binding_phase"]
            == "STAGE_F_LOCAL_BINDING_COMPLETED_IMPLEMENTATION"
        ):
            expected_post_integration_delta.update(STAGE_F_LOCAL_BINDING_MODIFIED_PATHS)
            expected_post_integration_delta.update(STAGE_F_LOCAL_BINDING_NEW_PATHS)
            expected_status.update(
                {path: "M" for path in STAGE_F_LOCAL_BINDING_MODIFIED_PATHS}
            )
            expected_status.update(
                {path: "A" for path in STAGE_F_LOCAL_BINDING_NEW_PATHS}
            )
        self.assertEqual(
            post_integration_delta, frozenset(expected_post_integration_delta)
        )
        self.assertEqual(
            {
                path: "M" if path in target_entries else "A"
                for path in post_integration_delta
            },
            expected_status,
        )
        self.assertEqual(schema["scientific_execution_count"], 0)
        for document in (contract, implementation, predecessor):
            self.assertEqual(set(document["required_operation_counts"].values()), {0})
        self.assertEqual(
            contract["authority_audit_host_probe_docker_connection_and_stage_g_action_count"],
            0,
        )
        self.assertIn("ZERO_SCIENCE_COUNTERS", validation["static_positive_checks"])
        self.assertIn("LIVE_HOST_PROBE", validation["forbidden_validation_operations"])
        self.assertIn(
            "SCIENTIFIC_RNG_DRAW", validation["forbidden_validation_operations"]
        )
        self.assertFalse(contract["precedence"]["scientific_execution_authorized"])
        self.assertTrue(
            contract["precedence"]["post_packet_user_authorization_still_required"]
        )

    def _audit_stage_f_final_evidence_closure(
        self, current_scope: dict[str, object]
    ) -> None:
        actual_head = current_scope["actual_head"]
        for commit in (
            STAGE_F_FINAL_EVIDENCE_CLOSURE_REQUIRED_BASE_COMMIT,
            STAGE_F_FINAL_EVIDENCE_CLOSURE_CANDIDATE,
            STAGE_F_FINAL_EVIDENCE_CLOSURE_TARGET,
        ):
            self.assertEqual(
                _git("rev-parse", "--verify", f"{commit}^{{commit}}")
                .decode()
                .strip(),
                commit,
            )
        self.assertEqual(
            _git(
                "rev-parse",
                f"{STAGE_F_FINAL_EVIDENCE_CLOSURE_REQUIRED_BASE_COMMIT}^{{tree}}",
            )
            .decode()
            .strip(),
            STAGE_F_FINAL_EVIDENCE_CLOSURE_REQUIRED_BASE_TREE,
        )
        for commit in (
            STAGE_F_FINAL_EVIDENCE_CLOSURE_CANDIDATE,
            STAGE_F_FINAL_EVIDENCE_CLOSURE_TARGET,
        ):
            self.assertEqual(
                _git("rev-parse", f"{commit}^{{tree}}").decode().strip(),
                STAGE_F_FINAL_EVIDENCE_CLOSURE_TREE,
            )
        self.assertEqual(
            _git("rev-parse", f"{STAGE_F_FINAL_EVIDENCE_CLOSURE_TARGET}^1")
            .decode()
            .strip(),
            STAGE_F_FINAL_EVIDENCE_CLOSURE_REQUIRED_BASE_COMMIT,
        )
        self.assertEqual(
            _git("rev-parse", f"{STAGE_F_FINAL_EVIDENCE_CLOSURE_TARGET}^2")
            .decode()
            .strip(),
            STAGE_F_FINAL_EVIDENCE_CLOSURE_CANDIDATE,
        )
        self.assertEqual(
            _git(
                "merge-base",
                STAGE_F_FINAL_EVIDENCE_CLOSURE_REQUIRED_BASE_COMMIT,
                STAGE_F_FINAL_EVIDENCE_CLOSURE_CANDIDATE,
            )
            .decode()
            .strip(),
            STAGE_F_FINAL_EVIDENCE_CLOSURE_REQUIRED_BASE_COMMIT,
        )
        self.assertEqual(
            _git(
                "merge-base",
                STAGE_F_FINAL_EVIDENCE_CLOSURE_TARGET,
                actual_head,
            )
            .decode()
            .strip(),
            STAGE_F_FINAL_EVIDENCE_CLOSURE_TARGET,
        )

        base_entries = _tree_entries(STAGE_F_FINAL_EVIDENCE_CLOSURE_REQUIRED_BASE_COMMIT)
        candidate_entries = _tree_entries(STAGE_F_FINAL_EVIDENCE_CLOSURE_CANDIDATE)
        target_entries = _tree_entries(STAGE_F_FINAL_EVIDENCE_CLOSURE_TARGET)
        current_entries = _tree_entries(actual_head)
        candidate_delta = frozenset(
            path
            for path in set(base_entries) | set(candidate_entries)
            if base_entries.get(path) != candidate_entries.get(path)
        )
        self.assertEqual(
            candidate_delta, frozenset(STAGE_F_FINAL_EVIDENCE_CLOSURE_PATHS)
        )
        self.assertEqual(candidate_entries, target_entries)

        base_archive = _archive_members(STAGE_F_FINAL_EVIDENCE_CLOSURE_REQUIRED_BASE_COMMIT)
        candidate_archive = _archive_members(STAGE_F_FINAL_EVIDENCE_CLOSURE_CANDIDATE)
        target_archive = _archive_members(STAGE_F_FINAL_EVIDENCE_CLOSURE_TARGET)
        current_archive = _archive_members(actual_head)
        documents = {}
        for path, mode, git_object, byte_count, raw_sha256 in (
            STAGE_F_FINAL_EVIDENCE_CLOSURE_ROWS
        ):
            expected_row = {
                "path": path,
                "mode": mode,
                "object_type": "blob",
                "git_object": git_object,
                "byte_count": byte_count,
                "raw_sha256": raw_sha256,
            }
            candidate_row, candidate_raw = _object_row(
                path, candidate_entries, candidate_archive
            )
            target_row, target_raw = _object_row(path, target_entries, target_archive)
            current_row, current_raw = _object_row(
                path, current_entries, current_archive
            )
            self.assertEqual(candidate_row, expected_row, path)
            self.assertEqual(target_row, expected_row, path)
            self.assertEqual(current_row, expected_row, path)
            self.assertEqual(candidate_raw, target_raw, path)
            self.assertEqual(candidate_raw, current_raw, path)
            self.assertEqual(
                _assert_checkout_matches_blob(ROOT / path, candidate_raw, path),
                candidate_raw,
                path,
            )
            text = candidate_raw.decode("utf-8", "strict")
            self.assertEqual(text, unicodedata.normalize("NFC", text), path)
            self.assertTrue(
                candidate_raw.endswith(b"\n") and not candidate_raw.endswith(b"\n\n"),
                path,
            )
            self.assertNotIn(b"\xef\xbb\xbf", candidate_raw, path)
            self.assertNotIn(b"\r", candidate_raw, path)
            self.assertTrue(
                all(line == line.rstrip(" \t") for line in text.splitlines()), path
            )
            if path.endswith(".json"):
                documents[path] = _strict_stage_d_json_bytes(candidate_raw, path)

        contract = documents[
            "stage_f_local_execution_binding_final_evidence_closure_correction_contract.json"
        ]
        schema = documents[
            "stage_f_local_execution_binding_final_evidence_closure_correction_schema.json"
        ]
        implementation = documents[
            "stage_f_local_execution_binding_final_evidence_closure_correction_implementation_path_manifest.json"
        ]
        predecessor = documents[
            "stage_f_local_execution_binding_final_evidence_closure_correction_predecessor_manifest.json"
        ]
        validation = documents[
            "stage_f_local_execution_binding_final_evidence_closure_correction_validation_contract.json"
        ]
        required_target = {
            "commit": STAGE_F_FINAL_EVIDENCE_CLOSURE_REQUIRED_BASE_COMMIT,
            "tree": STAGE_F_FINAL_EVIDENCE_CLOSURE_REQUIRED_BASE_TREE,
        }
        for document in (contract, implementation, validation):
            self.assertEqual(document["required_current_target"], required_target)
        predecessor_target = predecessor["required_current_target"]
        self.assertEqual(
            {key: predecessor_target[key] for key in ("commit", "tree")},
            required_target,
        )
        self.assertEqual(
            predecessor_target,
            {
                "commit": STAGE_F_FINAL_EVIDENCE_CLOSURE_REQUIRED_BASE_COMMIT,
                "tree": STAGE_F_FINAL_EVIDENCE_CLOSURE_REQUIRED_BASE_TREE,
                "recursive_blob_row_count": 448,
                "mode_100644_count": 446,
                "mode_100755_count": 2,
                "symlink_count": 0,
                "submodule_count": 0,
                "total_blob_bytes": 132022530,
                "ordered_path_projection_encoding": "canonical JSON array of Git paths in git ls-tree -r order, UTF-8 NFC, sorted keys, comma-colon separators, no final LF",
                "ordered_path_projection_sha256": "53b11e516d0f6375142eef3d3e951657e601b31fc653e892968c137ed0197d2e",
                "ordered_row_projection_fields": [
                    "path",
                    "mode",
                    "git_object",
                    "byte_count",
                    "raw_sha256",
                ],
                "ordered_row_projection_encoding": "canonical JSON array of closed row objects in git ls-tree -r order, UTF-8 NFC, sorted keys, comma-colon separators, no final LF",
                "ordered_row_projection_sha256": "ae2296219fd012964648f82915181ebb25a3fcc7a0d08e1b6e6f24ae8d138295",
            },
        )
        self.assertEqual(
            tuple(contract["authority_files_in_order"]),
            STAGE_F_FINAL_EVIDENCE_CLOSURE_PATHS,
        )
        self.assertEqual(contract["authority_file_count"], 6)
        self.assertEqual(
            tuple(implementation["authority_paths"]),
            STAGE_F_FINAL_EVIDENCE_CLOSURE_PATHS,
        )
        self.assertEqual(implementation["authority_path_count"], 6)
        self.assertEqual(
            validation["authority_candidate"],
            {
                "ordered_paths": list(STAGE_F_FINAL_EVIDENCE_CLOSURE_PATHS),
                "path_count": 6,
                "mode": "100644",
                "additions_only": True,
            },
        )

        accepted_rows = (
            predecessor["accepted_original_authority_rows"]
            + predecessor["accepted_evidence_correction_authority_rows"]
        )
        self.assertEqual(predecessor["accepted_prior_authority_row_count"], 12)
        self.assertEqual(len(accepted_rows), 12)
        self.assertEqual(
            tuple(row["path"] for row in accepted_rows),
            STAGE_F_LOCAL_BINDING_AUTHORITY_PATHS
            + STAGE_F_BINDING_EVIDENCE_CORRECTION_PATHS,
        )
        for row in accepted_rows:
            path = row["path"]
            reconstructed, reconstructed_raw = _object_row(
                path, base_entries, base_archive
            )
            projected = {
                key: reconstructed[key]
                for key in ("path", "mode", "git_object", "byte_count", "raw_sha256")
            }
            self.assertEqual(projected, row, path)
            for entries, archive in (
                (candidate_entries, candidate_archive),
                (target_entries, target_archive),
                (current_entries, current_archive),
            ):
                later_row, later_raw = _object_row(path, entries, archive)
                self.assertEqual(later_row, reconstructed, path)
                self.assertEqual(later_raw, reconstructed_raw, path)

        reachability_row = predecessor["accepted_reachability_row"]
        reconstructed_reachability, reachability_raw = _object_row(
            STAGE_F_LOCAL_BINDING_REACHABILITY_PATH, base_entries, base_archive
        )
        self.assertEqual(
            {
                key: reconstructed_reachability[key]
                for key in ("path", "mode", "git_object", "byte_count", "raw_sha256")
            },
            reachability_row,
        )
        self.assertNotEqual(
            _object_row(
                STAGE_F_LOCAL_BINDING_REACHABILITY_PATH,
                current_entries,
                current_archive,
            )[1],
            reachability_raw,
        )

        v1_schema = _strict_stage_d_json_bytes(
            _object_row(
                "stage_f_local_execution_binding_evidence_schema.json",
                current_entries,
                current_archive,
            )[1],
            "stage_f_local_execution_binding_evidence_schema.json",
        )
        v2_schema = _strict_stage_d_json_bytes(
            _object_row(
                "stage_f_local_execution_binding_evidence_correction_schema.json",
                current_entries,
                current_archive,
            )[1],
            "stage_f_local_execution_binding_evidence_correction_schema.json",
        )
        v1_definitions = v1_schema["$defs"]
        v2_definitions = v2_schema["$defs"]
        v3_definitions = schema["$defs"]

        def definition_delta(
            prior: dict[str, object], successor: dict[str, object]
        ) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
            key = lambda value: unicodedata.normalize("NFC", value).encode("utf-8")
            added = tuple(sorted(set(successor) - set(prior), key=key))
            changed = tuple(
                sorted(
                    (
                        name
                        for name in set(prior) & set(successor)
                        if prior[name] != successor[name]
                    ),
                    key=key,
                )
            )
            removed = tuple(sorted(set(prior) - set(successor), key=key))
            return added, changed, removed

        immediate_added, immediate_changed, immediate_removed = definition_delta(
            v2_definitions, v3_definitions
        )
        historical_added, historical_changed, historical_removed = definition_delta(
            v1_definitions, v3_definitions
        )
        effective = contract["effective_schema"]
        self.assertEqual((len(v1_definitions), len(v2_definitions), len(v3_definitions)), (143, 220, 228))
        self.assertEqual(
            immediate_added,
            tuple(effective["added_definitions_in_strict_nfc_utf8_order"]),
        )
        self.assertEqual(
            immediate_changed,
            tuple(effective["changed_definitions_in_strict_nfc_utf8_order"]),
        )
        self.assertFalse(immediate_removed)
        self.assertEqual(
            (
                len(immediate_added),
                len(immediate_changed),
                len(immediate_removed),
                len(historical_added),
                len(historical_changed),
                len(historical_removed),
            ),
            (8, 44, 0, 85, 28, 0),
        )
        schema_delta = validation["schema_delta"]
        self.assertEqual(tuple(schema_delta["added_definitions"]), immediate_added)
        self.assertEqual(tuple(schema_delta["changed_definitions"]), immediate_changed)
        self.assertEqual(schema_delta["removed_definitions"], [])
        refs = _schema_refs(schema)
        self.assertEqual(len(refs), 2431)
        for ref in refs:
            self.assertIs(type(ref), str)
            self.assertTrue(ref.startswith("#/$defs/"), ref)
            _json_pointer(schema, ref[1:])
        self.assertEqual(len(schema["oneOf"]), 46)
        root_names = tuple(
            item["$ref"].removeprefix("#/$defs/") for item in schema["oneOf"]
        )
        self.assertEqual(len(root_names), len(set(root_names)))

        prior_validation = _strict_stage_d_json_bytes(
            _object_row(
                "stage_f_local_execution_binding_evidence_correction_validation_contract.json",
                current_entries,
                current_archive,
            )[1],
            "stage_f_local_execution_binding_evidence_correction_validation_contract.json",
        )
        cases = validation["cases"]
        self.assertEqual(cases[:131], prior_validation["cases"])
        self.assertEqual(
            tuple(row["id"] for row in cases),
            tuple(f"BEC-{index:03d}" for index in range(1, 185)),
        )
        self.assertEqual(
            (
                validation["case_count"],
                validation["positive_case_count"],
                validation["negative_case_count"],
                sum(row["class"] == "POSITIVE" for row in cases),
                sum(row["class"] == "NEGATIVE" for row in cases),
            ),
            (184, 31, 153, 31, 153),
        )

        authority_preimage = v3_definitions["binding_authority_set_preimage"]
        implementation_preimage = v3_definitions["binding_implementation_preimage"]
        validator_preimage = v3_definitions["binding_validator_preimage"]
        self.assertEqual(
            (
                authority_preimage["properties"]["ordered_local_authority_file_rows"]["minItems"],
                authority_preimage["properties"]["ordered_local_authority_file_rows"]["maxItems"],
                authority_preimage["properties"]["local_authority_file_count"]["const"],
            ),
            (18, 18, 18),
        )
        self.assertEqual(
            (
                implementation_preimage["properties"]["ordered_implementation_file_rows"]["minItems"],
                implementation_preimage["properties"]["ordered_implementation_file_rows"]["maxItems"],
                implementation_preimage["properties"]["implementation_file_count"]["const"],
            ),
            (14, 14, 14),
        )
        self.assertEqual(
            (
                validator_preimage["properties"]["ordered_validator_source_file_rows"]["minItems"],
                validator_preimage["properties"]["ordered_validator_source_file_rows"]["maxItems"],
                validator_preimage["properties"]["validator_source_file_count"]["const"],
            ),
            (7, 7, 7),
        )
        for name in (
            "local_binding_bundle",
            "binding_validation_receipt",
            "binding_readiness_record",
            "independent_binding_audit_receipt",
            "sealed_campaign_packet_manifest",
            "post_packet_user_authorization_receipt",
            "campaign_authorization",
        ):
            self.assertTrue(
                {
                    "authority_set_identity",
                    "binding_implementation_identity",
                    "validator_identity",
                }
                <= set(v3_definitions[name]["required"]),
                name,
            )

        reachability = implementation["prospective_reachability_correction"]
        self.assertEqual(
            reachability["modified_paths"],
            [STAGE_F_LOCAL_BINDING_REACHABILITY_PATH],
        )
        self.assertEqual(
            (
                reachability["modified_path_count"],
                reachability["new_path_count"],
                reachability["total_path_count"],
            ),
            (1, 0, 1),
        )
        self.assertTrue(reachability["independent_audit_required_before_implementation"])
        self.assertFalse(reachability["counts_as_implementation_path"])
        self.assertEqual(
            reachability["project_import_production_validator_host_probe_or_science"],
            "FORBIDDEN",
        )
        prospective = implementation["prospective_implementation"]
        self.assertEqual(
            tuple(prospective["modified_paths"]), STAGE_F_LOCAL_BINDING_MODIFIED_PATHS
        )
        self.assertEqual(tuple(prospective["new_paths"]), STAGE_F_LOCAL_BINDING_NEW_PATHS)
        self.assertEqual(
            (
                prospective["modified_path_count"],
                prospective["new_path_count"],
                prospective["total_path_count"],
            ),
            (2, 12, 14),
        )
        final_closure = implementation["final_descendant_path_closure"]
        self.assertEqual(
            (
                final_closure["accepted_stage_e_path_count"],
                final_closure["accepted_stage_f_v1_authority_path_count"],
                final_closure["accepted_stage_f_evidence_correction_authority_path_count"],
                final_closure["reachability_durability_unique_path_count"],
                final_closure["final_evidence_closure_correction_authority_added_path_count"],
                final_closure["successor_active_authority_row_count"],
                final_closure["historical_authority_only_unique_path_count"],
                final_closure["historical_completed_implementation_unique_path_count"],
                final_closure["authority_only_unique_path_count"],
                final_closure["final_unique_path_count"],
            ),
            (51, 6, 6, 1, 6, 18, 64, 76, 70, 82),
        )
        self.assertEqual(len(STAGE_F_LOCAL_BINDING_DESCENDANT_PATHS), 88)
        self.assertEqual(len(set(STAGE_F_LOCAL_BINDING_DESCENDANT_PATHS)), 88)

        post_integration_delta = frozenset(
            path
            for path in set(target_entries) | set(current_entries)
            if target_entries.get(path) != current_entries.get(path)
        )
        expected_post_integration_delta = {STAGE_F_LOCAL_BINDING_REACHABILITY_PATH}
        expected_status = {STAGE_F_LOCAL_BINDING_REACHABILITY_PATH: "M"}
        expected_post_integration_delta.update(STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_PATHS)
        expected_status.update(
            {path: "A" for path in STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_PATHS}
        )
        if (
            current_scope["stage_f_local_binding_phase"]
            == "STAGE_F_LOCAL_BINDING_COMPLETED_IMPLEMENTATION"
        ):
            expected_post_integration_delta.update(STAGE_F_LOCAL_BINDING_MODIFIED_PATHS)
            expected_post_integration_delta.update(STAGE_F_LOCAL_BINDING_NEW_PATHS)
            expected_status.update(
                {path: "M" for path in STAGE_F_LOCAL_BINDING_MODIFIED_PATHS}
            )
            expected_status.update(
                {path: "A" for path in STAGE_F_LOCAL_BINDING_NEW_PATHS}
            )
        self.assertEqual(
            post_integration_delta, frozenset(expected_post_integration_delta)
        )
        self.assertEqual(
            {
                path: "M" if path in target_entries else "A"
                for path in post_integration_delta
            },
            expected_status,
        )
        self.assertEqual(schema["scientific_execution_count"], 0)
        self.assertEqual(set(predecessor["required_operation_counts"].values()), {0})
        self.assertEqual(set(contract["required_operation_counts"].values()), {0})
        self.assertIn("ZERO_SCIENCE_COUNTERS", validation["static_positive_checks"])
        self.assertFalse(contract["precedence"]["scientific_execution_authorized"])
        self.assertTrue(
            contract["precedence"]["post_packet_user_authorization_still_required"]
        )

    def _audit_stage_f_binding_evidence_correction(
        self, current_scope: dict[str, object]
    ) -> None:
        actual_head = current_scope["actual_head"]
        for commit in (
            STAGE_F_BINDING_EVIDENCE_CORRECTION_REQUIRED_BASE_COMMIT,
            STAGE_F_BINDING_EVIDENCE_CORRECTION_CANDIDATE,
            STAGE_F_BINDING_EVIDENCE_CORRECTION_TARGET,
        ):
            self.assertEqual(
                _git("rev-parse", "--verify", f"{commit}^{{commit}}")
                .decode()
                .strip(),
                commit,
            )
        self.assertEqual(
            _git(
                "rev-parse",
                f"{STAGE_F_BINDING_EVIDENCE_CORRECTION_REQUIRED_BASE_COMMIT}^{{tree}}",
            )
            .decode()
            .strip(),
            STAGE_F_BINDING_EVIDENCE_CORRECTION_REQUIRED_BASE_TREE,
        )
        for commit in (
            STAGE_F_BINDING_EVIDENCE_CORRECTION_CANDIDATE,
            STAGE_F_BINDING_EVIDENCE_CORRECTION_TARGET,
        ):
            self.assertEqual(
                _git("rev-parse", f"{commit}^{{tree}}").decode().strip(),
                STAGE_F_BINDING_EVIDENCE_CORRECTION_TREE,
            )
        self.assertEqual(
            _git("rev-parse", f"{STAGE_F_BINDING_EVIDENCE_CORRECTION_TARGET}^1")
            .decode()
            .strip(),
            STAGE_F_BINDING_EVIDENCE_CORRECTION_REQUIRED_BASE_COMMIT,
        )
        self.assertEqual(
            _git("rev-parse", f"{STAGE_F_BINDING_EVIDENCE_CORRECTION_TARGET}^2")
            .decode()
            .strip(),
            STAGE_F_BINDING_EVIDENCE_CORRECTION_CANDIDATE,
        )
        self.assertEqual(
            _git(
                "merge-base",
                STAGE_F_BINDING_EVIDENCE_CORRECTION_REQUIRED_BASE_COMMIT,
                STAGE_F_BINDING_EVIDENCE_CORRECTION_CANDIDATE,
            )
            .decode()
            .strip(),
            STAGE_F_BINDING_EVIDENCE_CORRECTION_REQUIRED_BASE_COMMIT,
        )
        self.assertEqual(
            _git(
                "merge-base",
                STAGE_F_BINDING_EVIDENCE_CORRECTION_TARGET,
                actual_head,
            )
            .decode()
            .strip(),
            STAGE_F_BINDING_EVIDENCE_CORRECTION_TARGET,
        )

        base_entries = _tree_entries(
            STAGE_F_BINDING_EVIDENCE_CORRECTION_REQUIRED_BASE_COMMIT
        )
        candidate_entries = _tree_entries(
            STAGE_F_BINDING_EVIDENCE_CORRECTION_CANDIDATE
        )
        target_entries = _tree_entries(STAGE_F_BINDING_EVIDENCE_CORRECTION_TARGET)
        current_entries = _tree_entries(actual_head)
        candidate_delta = frozenset(
            path
            for path in set(base_entries) | set(candidate_entries)
            if base_entries.get(path) != candidate_entries.get(path)
        )
        self.assertEqual(
            candidate_delta,
            frozenset(STAGE_F_BINDING_EVIDENCE_CORRECTION_PATHS),
        )
        self.assertEqual(candidate_entries, target_entries)

        candidate_archive = _archive_members(
            STAGE_F_BINDING_EVIDENCE_CORRECTION_CANDIDATE
        )
        target_archive = _archive_members(STAGE_F_BINDING_EVIDENCE_CORRECTION_TARGET)
        current_archive = _archive_members(actual_head)
        documents = {}
        for path, mode, git_object, byte_count, raw_sha256 in (
            STAGE_F_BINDING_EVIDENCE_CORRECTION_ROWS
        ):
            expected_row = {
                "path": path,
                "mode": mode,
                "object_type": "blob",
                "git_object": git_object,
                "byte_count": byte_count,
                "raw_sha256": raw_sha256,
            }
            candidate_row, candidate_raw = _object_row(
                path, candidate_entries, candidate_archive
            )
            target_row, target_raw = _object_row(
                path, target_entries, target_archive
            )
            current_row, current_raw = _object_row(
                path, current_entries, current_archive
            )
            self.assertEqual(candidate_row, expected_row, path)
            self.assertEqual(target_row, expected_row, path)
            self.assertEqual(current_row, expected_row, path)
            self.assertEqual(candidate_raw, target_raw, path)
            self.assertEqual(candidate_raw, current_raw, path)
            self.assertEqual(
                _assert_checkout_matches_blob(ROOT / path, candidate_raw, path),
                candidate_raw,
                path,
            )
            text = candidate_raw.decode("utf-8", "strict")
            self.assertEqual(text, unicodedata.normalize("NFC", text), path)
            self.assertTrue(
                candidate_raw.endswith(b"\n")
                and not candidate_raw.endswith(b"\n\n"),
                path,
            )
            self.assertNotIn(b"\xef\xbb\xbf", candidate_raw, path)
            self.assertNotIn(b"\r", candidate_raw, path)
            self.assertTrue(
                all(line == line.rstrip(" \t") for line in text.splitlines()),
                path,
            )
            if path.endswith(".json"):
                documents[path] = _strict_stage_d_json_bytes(candidate_raw, path)

        contract = documents[
            "stage_f_local_execution_binding_evidence_correction_contract.json"
        ]
        schema = documents[
            "stage_f_local_execution_binding_evidence_correction_schema.json"
        ]
        implementation = documents[
            "stage_f_local_execution_binding_evidence_correction_implementation_path_manifest.json"
        ]
        predecessor = documents[
            "stage_f_local_execution_binding_evidence_correction_predecessor_manifest.json"
        ]
        validation = documents[
            "stage_f_local_execution_binding_evidence_correction_validation_contract.json"
        ]
        required_target = {
            "commit": STAGE_F_BINDING_EVIDENCE_CORRECTION_REQUIRED_BASE_COMMIT,
            "tree": STAGE_F_BINDING_EVIDENCE_CORRECTION_REQUIRED_BASE_TREE,
        }
        for document in (contract, implementation, predecessor, validation):
            target = document["required_current_target"]
            self.assertEqual(target["commit"], required_target["commit"])
            self.assertEqual(target["tree"], required_target["tree"])
        self.assertEqual(
            tuple(contract["authority_files_in_order"]),
            STAGE_F_BINDING_EVIDENCE_CORRECTION_PATHS,
        )
        self.assertEqual(contract["authority_file_count"], 6)
        self.assertEqual(
            tuple(implementation["authority_paths"]),
            STAGE_F_BINDING_EVIDENCE_CORRECTION_PATHS,
        )
        self.assertEqual(implementation["authority_path_count"], 6)
        self.assertEqual(
            validation["authority_candidate"],
            {
                "ordered_paths": list(STAGE_F_BINDING_EVIDENCE_CORRECTION_PATHS),
                "path_count": 6,
                "mode": "100644",
                "additions_only": True,
            },
        )

        original_target_entries = _tree_entries(STAGE_F_LOCAL_BINDING_AUTHORITY_TARGET)
        original_target_archive = _archive_members(
            STAGE_F_LOCAL_BINDING_AUTHORITY_TARGET
        )
        base_archive = _archive_members(
            STAGE_F_BINDING_EVIDENCE_CORRECTION_REQUIRED_BASE_COMMIT
        )
        original_rows = predecessor["accepted_original_authority_rows"]
        self.assertEqual(len(original_rows), 6)
        self.assertEqual(
            tuple(row["path"] for row in original_rows),
            STAGE_F_LOCAL_BINDING_AUTHORITY_PATHS,
        )
        for row in original_rows:
            path = row["path"]
            rows_and_raw = (
                _object_row(path, original_target_entries, original_target_archive),
                _object_row(path, base_entries, base_archive),
                _object_row(path, candidate_entries, candidate_archive),
                _object_row(path, target_entries, target_archive),
                _object_row(path, current_entries, current_archive),
            )
            projected = {
                key: rows_and_raw[0][0][key]
                for key in ("path", "mode", "git_object", "byte_count", "raw_sha256")
            }
            self.assertEqual(projected, row, path)
            self.assertTrue(all(item[0] == rows_and_raw[0][0] for item in rows_and_raw))
            self.assertTrue(all(item[1] == rows_and_raw[0][1] for item in rows_and_raw))

        reachability_row = predecessor["accepted_reachability_row"]
        reconstructed_reachability, reachability_raw = _object_row(
            STAGE_F_LOCAL_BINDING_REACHABILITY_PATH,
            base_entries,
            base_archive,
        )
        self.assertEqual(
            {
                key: reconstructed_reachability[key]
                for key in ("path", "mode", "git_object", "byte_count", "raw_sha256")
            },
            reachability_row,
        )
        self.assertNotEqual(
            _object_row(
                STAGE_F_LOCAL_BINDING_REACHABILITY_PATH,
                current_entries,
                current_archive,
            )[1],
            reachability_raw,
        )

        historical_schema_raw = _object_row(
            "stage_f_local_execution_binding_evidence_schema.json",
            current_entries,
            current_archive,
        )[1]
        historical_schema = _strict_stage_d_json_bytes(
            historical_schema_raw,
            "stage_f_local_execution_binding_evidence_schema.json",
        )
        historical_definitions = historical_schema["$defs"]
        effective_definitions = schema["$defs"]
        added_names = tuple(
            sorted(
                set(effective_definitions) - set(historical_definitions),
                key=lambda value: unicodedata.normalize("NFC", value).encode("utf-8"),
            )
        )
        changed_names = tuple(
            sorted(
                (
                    name
                    for name in set(historical_definitions) & set(effective_definitions)
                    if historical_definitions[name] != effective_definitions[name]
                ),
                key=lambda value: unicodedata.normalize("NFC", value).encode("utf-8"),
            )
        )
        removed_names = set(historical_definitions) - set(effective_definitions)
        delta = contract["schema_delta_from_historical"]
        self.assertEqual(len(historical_definitions), 143)
        self.assertEqual(len(effective_definitions), 220)
        self.assertEqual(added_names, tuple(delta["added_definitions_in_order"]))
        self.assertEqual(changed_names, tuple(delta["changed_definitions_in_order"]))
        self.assertFalse(removed_names)
        self.assertEqual(
            (
                delta["historical_definition_count"],
                delta["effective_definition_count"],
                delta["added_definition_count"],
                delta["changed_definition_count"],
                delta["removed_definition_count"],
            ),
            (143, 220, 77, 21, 0),
        )
        refs = _schema_refs(schema)
        self.assertEqual(len(refs), 2257)
        for ref in refs:
            self.assertIs(type(ref), str)
            self.assertTrue(ref.startswith("#/$defs/"), ref)
            _json_pointer(schema, ref[1:])
        self.assertEqual(len(schema["oneOf"]), 46)
        root_names = tuple(
            item["$ref"].removeprefix("#/$defs/") for item in schema["oneOf"]
        )
        self.assertEqual(len(root_names), len(set(root_names)))
        for nested_only in delta["removed_nested_only_root_variants_in_order"]:
            self.assertNotIn(nested_only, root_names)

        closed_object_count = 0
        enum_count = 0

        def audit_schema_node(value: object, path: tuple[object, ...] = ()) -> None:
            nonlocal closed_object_count, enum_count
            if type(value) is dict:
                if (
                    value.get("additionalProperties") is False
                    and type(value.get("properties")) is dict
                ):
                    closed_object_count += 1
                    self.assertEqual(
                        set(value.get("required", [])),
                        set(value["properties"]),
                        path,
                    )
                    self.assertEqual(
                        len(value.get("required", [])),
                        len(set(value.get("required", []))),
                        path,
                    )
                if type(value.get("enum")) is list:
                    enum_count += 1
                    enum_rows = tuple(
                        _canonical_json_bytes(item) for item in value["enum"]
                    )
                    self.assertEqual(len(enum_rows), len(set(enum_rows)), path)
                for key, item in value.items():
                    audit_schema_node(item, path + (key,))
            elif type(value) is list:
                for index, item in enumerate(value):
                    audit_schema_node(item, path + (index,))

        audit_schema_node(schema)
        self.assertGreater(closed_object_count, 0)
        self.assertGreater(enum_count, 0)
        create_observation = effective_definitions[
            "stage_f_ledger_create_observation"
        ]
        append_observation = effective_definitions[
            "stage_f_evidence_ledger_append_observation"
        ]
        self.assertEqual(
            (len(create_observation["required"]), len(create_observation["properties"])),
            (76, 76),
        )
        self.assertEqual(
            (len(append_observation["required"]), len(append_observation["properties"])),
            (123, 123),
        )
        self.assertEqual(
            effective_definitions["docker_named_pipe_bounded_response_window_observation"]
            ["properties"]["terminal_read_post_tick_relation_to_deadline"]["enum"],
            ["AT_OR_BEFORE_DEADLINE", "AFTER_DEADLINE"],
        )
        terminal_error_rule = effective_definitions[
            "docker_named_pipe_read_attempt_observation"
        ]["allOf"][2]["then"]["properties"]["last_error"]
        self.assertEqual(terminal_error_rule["allOf"][1]["not"]["enum"], [232, 234])

        cases = validation["cases"]
        self.assertEqual(
            tuple(row["id"] for row in cases),
            tuple(f"BEC-{index:03d}" for index in range(1, 132)),
        )
        self.assertEqual(
            (
                validation["case_count"],
                validation["positive_case_count"],
                validation["negative_case_count"],
            ),
            (131, 15, 116),
        )
        self.assertEqual(
            sum(row["class"] == "POSITIVE" for row in cases), 15
        )
        self.assertEqual(
            sum(row["class"] == "NEGATIVE" for row in cases), 116
        )

        reachability = implementation["prospective_reachability_correction"]
        self.assertEqual(
            reachability["modified_paths"],
            [STAGE_F_LOCAL_BINDING_REACHABILITY_PATH],
        )
        self.assertEqual(reachability["modified_path_count"], 1)
        self.assertTrue(reachability["independent_audit_required_before_implementation"])
        self.assertFalse(reachability["counts_as_implementation_path"])
        self.assertEqual(
            reachability["project_import_production_validator_host_probe_or_science"],
            "FORBIDDEN",
        )
        prospective = implementation["prospective_implementation"]
        self.assertEqual(
            tuple(prospective["modified_paths"]),
            STAGE_F_LOCAL_BINDING_MODIFIED_PATHS,
        )
        self.assertEqual(
            tuple(prospective["new_paths"]), STAGE_F_LOCAL_BINDING_NEW_PATHS
        )
        self.assertEqual(
            (
                prospective["modified_path_count"],
                prospective["new_path_count"],
                prospective["total_path_count"],
            ),
            (2, 12, 14),
        )
        self.assertEqual(
            implementation["final_descendant_path_closure"],
            {
                "accepted_stage_e_path_count": 51,
                "accepted_stage_f_v1_authority_path_count": 6,
                "reachability_durability_unique_path_count": 1,
                "correction_authority_added_path_count": 6,
                "stage_f_new_unique_path_count": 12,
                "stage_f_modified_paths_overlapping_accepted_stage_e_count": 2,
                "final_unique_path_count": 76,
                "missing_extra_duplicate_or_reordered_path_disposition": "REFUSE",
            },
        )
        self.assertEqual(len(STAGE_F_LOCAL_BINDING_DESCENDANT_PATHS), 88)
        self.assertEqual(len(set(STAGE_F_LOCAL_BINDING_DESCENDANT_PATHS)), 88)

        post_integration_delta = frozenset(
            path
            for path in set(target_entries) | set(current_entries)
            if target_entries.get(path) != current_entries.get(path)
        )
        expected_post_integration_delta = {
            STAGE_F_LOCAL_BINDING_REACHABILITY_PATH
        }
        expected_status = {STAGE_F_LOCAL_BINDING_REACHABILITY_PATH: "M"}
        expected_post_integration_delta.update(STAGE_F_FINAL_EVIDENCE_CLOSURE_PATHS)
        expected_status.update(
            {path: "A" for path in STAGE_F_FINAL_EVIDENCE_CLOSURE_PATHS}
        )
        expected_post_integration_delta.update(STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_PATHS)
        expected_status.update(
            {path: "A" for path in STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_PATHS}
        )
        if (
            current_scope["stage_f_local_binding_phase"]
            == "STAGE_F_LOCAL_BINDING_COMPLETED_IMPLEMENTATION"
        ):
            expected_post_integration_delta.update(STAGE_F_LOCAL_BINDING_MODIFIED_PATHS)
            expected_post_integration_delta.update(STAGE_F_LOCAL_BINDING_NEW_PATHS)
            expected_status.update(
                {path: "M" for path in STAGE_F_LOCAL_BINDING_MODIFIED_PATHS}
            )
            expected_status.update(
                {path: "A" for path in STAGE_F_LOCAL_BINDING_NEW_PATHS}
            )
        self.assertEqual(
            post_integration_delta, frozenset(expected_post_integration_delta)
        )
        status_rows = {
            path: "M" if path in target_entries else "A"
            for path in post_integration_delta
        }
        self.assertEqual(status_rows, expected_status)
        self.assertEqual(schema["scientific_execution_count"], 0)
        self.assertEqual(set(predecessor["required_operation_counts"].values()), {0})
        self.assertIn("ZERO_SCIENCE_COUNTERS", validation["static_positive_checks"])

    def _audit_stage_f_local_binding_authority(
        self, current_scope: dict[str, object]
    ) -> None:
        self.assertIn(
            current_scope["stage_f_local_binding_phase"],
            (
                "STAGE_F_LOCAL_BINDING_AUTHORITY_ONLY",
                "STAGE_F_LOCAL_BINDING_COMPLETED_IMPLEMENTATION",
            ),
        )
        self._audit_stage_f_attempt_root_bootstrap(current_scope)
        self._audit_stage_f_final_evidence_closure(current_scope)
        self._audit_stage_f_binding_evidence_correction(current_scope)
        self.assertEqual(
            _git(
                "rev-parse",
                "--verify",
                f"{STAGE_F_LOCAL_BINDING_ACCEPTED_BASE_COMMIT}^{{commit}}",
            )
            .decode()
            .strip(),
            STAGE_F_LOCAL_BINDING_ACCEPTED_BASE_COMMIT,
        )
        self.assertEqual(
            _git(
                "rev-parse",
                f"{STAGE_F_LOCAL_BINDING_ACCEPTED_BASE_COMMIT}^{{tree}}",
            )
            .decode()
            .strip(),
            STAGE_F_LOCAL_BINDING_ACCEPTED_BASE_TREE,
        )
        self.assertEqual(
            _git(
                "rev-parse",
                f"{STAGE_F_LOCAL_BINDING_AUTHORITY_CANDIDATE}^{{tree}}",
            )
            .decode()
            .strip(),
            STAGE_F_LOCAL_BINDING_AUTHORITY_TREE,
        )
        self.assertEqual(
            _git(
                "rev-parse", f"{STAGE_F_LOCAL_BINDING_AUTHORITY_TARGET}^{{tree}}"
            )
            .decode()
            .strip(),
            STAGE_F_LOCAL_BINDING_AUTHORITY_TREE,
        )
        self.assertEqual(
            _git("rev-parse", f"{STAGE_F_LOCAL_BINDING_AUTHORITY_TARGET}^1")
            .decode()
            .strip(),
            STAGE_F_LOCAL_BINDING_ACCEPTED_BASE_COMMIT,
        )
        self.assertEqual(
            _git("rev-parse", f"{STAGE_F_LOCAL_BINDING_AUTHORITY_TARGET}^2")
            .decode()
            .strip(),
            STAGE_F_LOCAL_BINDING_AUTHORITY_CANDIDATE,
        )
        self.assertEqual(
            _git(
                "merge-base",
                STAGE_F_LOCAL_BINDING_ACCEPTED_BASE_COMMIT,
                STAGE_F_LOCAL_BINDING_AUTHORITY_CANDIDATE,
            )
            .decode()
            .strip(),
            STAGE_F_LOCAL_BINDING_ACCEPTED_BASE_COMMIT,
        )
        history_rows = tuple(
            tuple(line.split())
            for line in _git(
                "rev-list",
                "--reverse",
                "--parents",
                f"{STAGE_F_LOCAL_BINDING_ACCEPTED_BASE_COMMIT}..{STAGE_F_LOCAL_BINDING_AUTHORITY_CANDIDATE}",
            )
            .decode()
            .splitlines()
        )
        self.assertEqual(
            tuple(row[0] for row in history_rows),
            STAGE_F_LOCAL_BINDING_AUTHORITY_CHAIN,
        )
        self.assertEqual(
            history_rows[0][1:], (STAGE_F_LOCAL_BINDING_ACCEPTED_BASE_COMMIT,)
        )
        for previous, row in zip(
            STAGE_F_LOCAL_BINDING_AUTHORITY_CHAIN, history_rows[1:]
        ):
            self.assertEqual(row[1:], (previous,))

        base_entries = _tree_entries(STAGE_F_LOCAL_BINDING_ACCEPTED_BASE_COMMIT)
        candidate_entries = _tree_entries(STAGE_F_LOCAL_BINDING_AUTHORITY_CANDIDATE)
        target_entries = _tree_entries(STAGE_F_LOCAL_BINDING_AUTHORITY_TARGET)
        current_entries = _tree_entries(current_scope["actual_head"])
        self.assertEqual(
            _git(
                "merge-base",
                STAGE_F_LOCAL_BINDING_AUTHORITY_TARGET,
                current_scope["actual_head"],
            )
            .decode()
            .strip(),
            STAGE_F_LOCAL_BINDING_AUTHORITY_TARGET,
        )
        candidate_delta = frozenset(
            path
            for path in set(base_entries) | set(candidate_entries)
            if base_entries.get(path) != candidate_entries.get(path)
        )
        self.assertEqual(
            candidate_delta, frozenset(STAGE_F_LOCAL_BINDING_AUTHORITY_PATHS)
        )
        self.assertEqual(candidate_entries, target_entries)
        for path in STAGE_F_LOCAL_BINDING_AUTHORITY_PATHS:
            self.assertNotIn(path, base_entries)
            self.assertEqual(candidate_entries[path]["mode"], "100644", path)
            self.assertEqual(candidate_entries[path]["object_type"], "blob", path)
        implementation_delta = frozenset(
            path
            for path in set(target_entries) | set(current_entries)
            if target_entries.get(path) != current_entries.get(path)
        )
        expected_implementation_delta = {STAGE_F_LOCAL_BINDING_REACHABILITY_PATH}
        expected_implementation_delta.update(
            STAGE_F_BINDING_EVIDENCE_CORRECTION_PATHS
        )
        expected_implementation_delta.update(STAGE_F_FINAL_EVIDENCE_CLOSURE_PATHS)
        expected_implementation_delta.update(STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_PATHS)
        if (
            current_scope["stage_f_local_binding_phase"]
            == "STAGE_F_LOCAL_BINDING_COMPLETED_IMPLEMENTATION"
        ):
            expected_implementation_delta.update(STAGE_F_LOCAL_BINDING_MODIFIED_PATHS)
            expected_implementation_delta.update(STAGE_F_LOCAL_BINDING_NEW_PATHS)
        self.assertEqual(
            implementation_delta, frozenset(expected_implementation_delta)
        )

        candidate_archive = _archive_members(
            STAGE_F_LOCAL_BINDING_AUTHORITY_CANDIDATE
        )
        target_archive = _archive_members(STAGE_F_LOCAL_BINDING_AUTHORITY_TARGET)
        current_archive = _archive_members(current_scope["actual_head"])
        documents = {}
        raw_by_path = {}
        expected_blob_bytes = {
            "STAGE_F_LOCAL_EXECUTION_BINDING_AUTHORITY_AMENDMENT.md": 71550,
            "stage_f_local_execution_binding_contract.json": 68095,
            "stage_f_local_execution_binding_evidence_schema.json": 229992,
            "stage_f_local_execution_binding_implementation_path_manifest.json": 5321,
            "stage_f_local_execution_binding_predecessor_manifest.json": 8318,
            "stage_f_local_execution_binding_validation_contract.json": 71510,
        }
        for path in STAGE_F_LOCAL_BINDING_AUTHORITY_PATHS:
            candidate_row, candidate_raw = _object_row(
                path, candidate_entries, candidate_archive
            )
            target_row, target_raw = _object_row(
                path, target_entries, target_archive
            )
            current_row, current_raw = _object_row(
                path, current_entries, current_archive
            )
            self.assertEqual(candidate_row, target_row, path)
            self.assertEqual(candidate_row, current_row, path)
            self.assertEqual(candidate_raw, target_raw, path)
            self.assertEqual(candidate_raw, current_raw, path)
            self.assertEqual(len(candidate_raw), expected_blob_bytes[path], path)
            self.assertEqual(
                _sha256(candidate_raw),
                STAGE_F_LOCAL_BINDING_AUTHORITY_RAW_SHA256[path],
                path,
            )
            self.assertEqual(
                _assert_checkout_matches_blob(ROOT / path, candidate_raw, path),
                candidate_raw,
                path,
            )
            text = candidate_raw.decode("utf-8", "strict")
            self.assertEqual(text, unicodedata.normalize("NFC", text), path)
            self.assertTrue(
                candidate_raw.endswith(b"\n")
                and not candidate_raw.endswith(b"\n\n"),
                path,
            )
            self.assertNotIn(b"\xef\xbb\xbf", candidate_raw, path)
            self.assertNotIn(b"\r", candidate_raw, path)
            self.assertTrue(
                all(line == line.rstrip(" \t") for line in text.splitlines()),
                path,
            )
            raw_by_path[path] = candidate_raw
            if path.endswith(".json"):
                document = _strict_stage_d_json_bytes(candidate_raw, path)
                documents[path] = document
                canonical = _canonical_json_bytes(document)
                self.assertEqual(
                    _sha256(canonical),
                    STAGE_F_LOCAL_BINDING_AUTHORITY_CANONICAL_SHA256[path],
                    path,
                )

        contract = documents["stage_f_local_execution_binding_contract.json"]
        schema = documents["stage_f_local_execution_binding_evidence_schema.json"]
        implementation = documents[
            "stage_f_local_execution_binding_implementation_path_manifest.json"
        ]
        predecessor = documents[
            "stage_f_local_execution_binding_predecessor_manifest.json"
        ]
        validation = documents[
            "stage_f_local_execution_binding_validation_contract.json"
        ]
        self.assertEqual(
            tuple(contract["authority_files"]),
            STAGE_F_LOCAL_BINDING_AUTHORITY_PATHS,
        )
        self.assertEqual(contract["authority_file_count"], 6)
        self.assertEqual(
            tuple(implementation["authority_paths"]),
            STAGE_F_LOCAL_BINDING_AUTHORITY_PATHS,
        )
        self.assertEqual(implementation["authority_path_count"], 6)
        authority_candidate = validation["authority_candidate"]
        self.assertEqual(
            tuple(authority_candidate["added_paths"]),
            STAGE_F_LOCAL_BINDING_AUTHORITY_PATHS,
        )
        self.assertEqual(
            authority_candidate,
            {
                "added_paths": list(STAGE_F_LOCAL_BINDING_AUTHORITY_PATHS),
                "added_path_count": 6,
                "modified_path_count": 0,
                "deleted_path_count": 0,
                "renamed_path_count": 0,
                "allowed_mode": "100644",
            },
        )
        for document in (contract, implementation, predecessor, validation):
            self.assertEqual(
                document["accepted_base"],
                {
                    "commit": STAGE_F_LOCAL_BINDING_ACCEPTED_BASE_COMMIT,
                    "tree": STAGE_F_LOCAL_BINDING_ACCEPTED_BASE_TREE,
                },
            )

        self.assertEqual(predecessor["source_count"], 28)
        source_rows = predecessor["source_rows"]
        self.assertEqual(len(source_rows), 28)
        self.assertEqual(len({row["path"] for row in source_rows}), 28)
        base_archive = _archive_members(STAGE_F_LOCAL_BINDING_ACCEPTED_BASE_COMMIT)
        for row in source_rows:
            reconstructed, base_raw = _object_row(
                row["path"], base_entries, base_archive
            )
            self.assertEqual(
                {
                    "path": reconstructed["path"],
                    "mode": reconstructed["mode"],
                    "git_object": reconstructed["git_object"],
                    "bytes": reconstructed["byte_count"],
                    "sha256": reconstructed["raw_sha256"],
                },
                row,
                row["path"],
            )
            self.assertEqual(current_entries[row["path"]], base_entries[row["path"]])
            self.assertEqual(
                _object_row(row["path"], current_entries, current_archive)[1],
                base_raw,
                row["path"],
            )

        accepted_stage_e = predecessor["accepted_stage_e_implementation"]
        self.assertEqual(
            accepted_stage_e,
            {
                "integration_commit": STAGE_F_LOCAL_BINDING_ACCEPTED_BASE_COMMIT,
                "integration_tree": STAGE_F_LOCAL_BINDING_ACCEPTED_BASE_TREE,
                "implementation_path_count": 51,
                "path_closure_source": "stage_e_dynamic_growth_harness_reconciliation_implementation_path_manifest.json",
            },
        )
        reconciliation_manifest_raw = _object_row(
            accepted_stage_e["path_closure_source"], base_entries, base_archive
        )[1]
        reconciliation_manifest = _strict_stage_d_json_bytes(
            reconciliation_manifest_raw, accepted_stage_e["path_closure_source"]
        )
        accepted_scope = reconciliation_manifest["prospective_harness_implementation"]
        accepted_stage_e_paths = tuple(accepted_scope["modified_paths"]) + tuple(
            accepted_scope["new_paths"]
        )
        self.assertEqual(
            accepted_stage_e_paths, STAGE_E_RECONCILED_HARNESS_IMPLEMENTATION_PATHS
        )
        self.assertEqual(len(accepted_stage_e_paths), 51)
        self.assertEqual(len(set(accepted_stage_e_paths)), 51)
        for path in accepted_stage_e_paths:
            self.assertEqual(base_entries[path]["mode"], "100644", path)
            self.assertEqual(base_entries[path]["object_type"], "blob", path)
            if (
                current_scope["stage_f_local_binding_phase"]
                != "STAGE_F_LOCAL_BINDING_COMPLETED_IMPLEMENTATION"
                or path not in STAGE_F_LOCAL_BINDING_MODIFIED_PATHS
            ):
                self.assertEqual(current_entries[path], base_entries[path], path)
        self.assertEqual(
            current_entries["stage_e_harness/execution.py"],
            base_entries["stage_e_harness/execution.py"],
        )
        accepted_ci = predecessor["accepted_stage_e_ci"]
        self.assertEqual(
            accepted_ci,
            {
                "run_id": 33231168021,
                "required_job_count": 6,
                "conclusion": "success",
                "artifact_id": 9708926559,
                "artifact_sha256": "2b2b5cc213082392bda715e82b9a23f670b7628b92848ace9455724f903bc345",
            },
        )

        prospective = implementation["prospective_implementation"]
        self.assertEqual(
            tuple(prospective["modified_paths"]),
            STAGE_F_LOCAL_BINDING_MODIFIED_PATHS,
        )
        self.assertEqual(prospective["modified_path_count"], 2)
        self.assertEqual(
            tuple(prospective["new_paths"]), STAGE_F_LOCAL_BINDING_NEW_PATHS
        )
        self.assertEqual(prospective["new_path_count"], 12)
        self.assertEqual(prospective["total_path_count"], 14)
        durability = implementation["prospective_reachability_durability"]
        self.assertEqual(
            durability,
            {
                "modified_path": STAGE_F_LOCAL_BINDING_REACHABILITY_PATH,
                "modified_path_count": 1,
                "authority_integration_required_first": True,
                "independent_audit_required": True,
            },
        )
        final_closure = implementation["final_descendant_path_closure"]
        self.assertEqual(
            final_closure,
            {
                "accepted_stage_e_path_count": 51,
                "authority_added_path_count": 6,
                "reachability_durability_unique_path_count": 1,
                "stage_f_new_unique_path_count": 12,
                "stage_f_modified_paths_overlapping_accepted_stage_e_count": 2,
                "final_unique_path_count": 70,
                "missing_extra_or_duplicate_path_disposition": "REFUSE",
            },
        )
        self.assertEqual(
            set(STAGE_F_LOCAL_BINDING_MODIFIED_PATHS)
            & set(accepted_stage_e_paths),
            set(STAGE_F_LOCAL_BINDING_MODIFIED_PATHS),
        )
        self.assertFalse(
            set(STAGE_F_LOCAL_BINDING_NEW_PATHS)
            & (
                set(accepted_stage_e_paths)
                | set(STAGE_F_LOCAL_BINDING_AUTHORITY_PATHS)
                | {STAGE_F_LOCAL_BINDING_REACHABILITY_PATH}
            )
        )
        self.assertEqual(len(STAGE_F_LOCAL_BINDING_DESCENDANT_PATHS), 88)
        self.assertEqual(len(set(STAGE_F_LOCAL_BINDING_DESCENDANT_PATHS)), 88)
        self.assertEqual(
            _git(
                "rev-parse", f"{STAGE_F_DESCENDANT_PATH_BASE_COMMIT}^{{tree}}"
            )
            .decode()
            .strip(),
            STAGE_F_DESCENDANT_PATH_BASE_TREE,
        )
        descendant_base_entries = _tree_entries(STAGE_F_DESCENDANT_PATH_BASE_COMMIT)
        descendant_delta = frozenset(
            path
            for path in set(descendant_base_entries) | set(current_entries)
            if descendant_base_entries.get(path) != current_entries.get(path)
        )
        expected_descendant_delta = (
            set(accepted_stage_e_paths)
            | set(STAGE_F_LOCAL_BINDING_AUTHORITY_PATHS)
            | {STAGE_F_LOCAL_BINDING_REACHABILITY_PATH}
            | set(STAGE_F_BINDING_EVIDENCE_CORRECTION_PATHS)
            | set(STAGE_F_FINAL_EVIDENCE_CLOSURE_PATHS)
            | set(STAGE_F_ATTEMPT_ROOT_BOOTSTRAP_PATHS)
        )
        if (
            current_scope["stage_f_local_binding_phase"]
            == "STAGE_F_LOCAL_BINDING_COMPLETED_IMPLEMENTATION"
        ):
            expected_descendant_delta.update(STAGE_F_LOCAL_BINDING_NEW_PATHS)
        self.assertEqual(descendant_delta, frozenset(expected_descendant_delta))
        self.assertEqual(
            len(descendant_delta),
            88
            if current_scope["stage_f_local_binding_phase"]
            == "STAGE_F_LOCAL_BINDING_COMPLETED_IMPLEMENTATION"
            else 76,
        )
        self.assertEqual(implementation["unknown_path_disposition"], "REFUSE")
        self.assertEqual(implementation["scope_derived_exclusion"], "FORBIDDEN")
        self.assertEqual(
            implementation["force_push_or_history_rewrite"], "FORBIDDEN"
        )
        self.assertTrue(implementation["authority_integration_required_before_implementation"])
        self.assertTrue(implementation["independent_implementation_audit_required"])

        campaign_order = (
            "SD-01",
            "SD-01-GROWTH-v1",
            *tuple(f"SD-{index:02d}" for index in range(2, 15)),
        )
        self.assertEqual(tuple(contract["campaign_order"]), campaign_order)
        self.assertEqual(
            contract["nested_campaign_rule"],
            {
                "nested_id": "SD-01-GROWTH-v1",
                "parent_study_id": "SD-01",
                "independent_study_count_increment": 0,
            },
        )
        route_projection = contract["route_binding_projection"]
        self.assertTrue(route_projection["ordered_route_ids_equal_campaign_order"])
        self.assertEqual(route_projection["nested_growth_study_id"], "SD-01")
        self.assertEqual(
            route_projection["nested_growth_campaign_id"], "SD-01-GROWTH-v1"
        )
        self.assertTrue(route_projection["all_wrapper_campaign_ids_unique"])
        self.assertTrue(route_projection["ready_bundle_requires_fifteen_distinct_sealed_binding_identities"])

        identity_kinds = contract["identity_kind_registry"]
        identity_preimages = contract["identity_preimage_registry"]
        self.assertEqual(len(identity_kinds), 36)
        self.assertEqual(len(identity_preimages), 36)
        self.assertEqual(len(set(identity_kinds.values())), 36)
        self.assertEqual(set(identity_kinds.values()), set(identity_preimages))
        self.assertEqual(
            identity_kinds["campaign_binding"], "campaign_execution_binding/v2"
        )
        self.assertEqual(
            identity_kinds["binding_implementation"],
            "stage_f_binding_implementation/v1",
        )
        self.assertEqual(
            identity_kinds["binding_authority_set"],
            "stage_f_binding_authority_set/v1",
        )
        self.assertEqual(
            identity_kinds["sealed_campaign_packet"],
            "stage_f_sealed_campaign_packet/v1",
        )
        binding_implementation = contract["binding_implementation_preimage"]
        self.assertEqual(
            tuple(binding_implementation["ordered_integrated_authority_paths"]),
            STAGE_F_LOCAL_BINDING_AUTHORITY_PATHS,
        )
        self.assertEqual(
            tuple(binding_implementation["ordered_paths"]),
            STAGE_F_LOCAL_BINDING_MODIFIED_PATHS
            + STAGE_F_LOCAL_BINDING_NEW_PATHS,
        )
        self.assertEqual(binding_implementation["path_count"], 14)
        self.assertEqual(binding_implementation["integrated_authority_file_count"], 6)
        self.assertEqual(
            tuple(binding_implementation["row_fields_in_order"]),
            ("path", "mode", "git_object", "byte_count", "raw_sha256"),
        )
        authority_set = contract["binding_authority_set_preimage"]
        self.assertEqual(
            tuple(authority_set["ordered_local_authority_paths"]),
            STAGE_F_LOCAL_BINDING_AUTHORITY_PATHS,
        )
        self.assertEqual(authority_set["local_authority_file_count"], 6)
        self.assertEqual(authority_set["route_authority_projection_count"], 15)
        validator_preimage = contract["binding_validator_preimage"]
        self.assertEqual(validator_preimage["validator_source_file_count"], 7)
        self.assertEqual(
            tuple(validator_preimage["ordered_validator_source_paths"]),
            STAGE_F_LOCAL_BINDING_NEW_PATHS[:7],
        )
        stage_e_preimage = contract["stage_e_integration_preimage"]
        self.assertEqual(
            stage_e_preimage["integration_commit"],
            STAGE_F_LOCAL_BINDING_ACCEPTED_BASE_COMMIT,
        )
        self.assertEqual(
            stage_e_preimage["integration_tree"],
            STAGE_F_LOCAL_BINDING_ACCEPTED_BASE_TREE,
        )
        self.assertEqual(stage_e_preimage["implementation_path_count"], 51)
        self.assertEqual(stage_e_preimage["ci_run_id"], 33231168021)
        self.assertEqual(stage_e_preimage["artifact_id"], 9708926559)
        self.assertEqual(
            stage_e_preimage["artifact_sha256"], accepted_ci["artifact_sha256"]
        )
        self.assertTrue(
            contract["scientific_code_preimage"][
                "ordered_rows_equal_complete_recursive_git_tree_blob_inventory"
            ]
        )
        self.assertTrue(
            contract["scientific_implementation_preimage"][
                "stage_e_harness_execution_guard_remains_byte_identical"
            ]
        )
        self.assertTrue(
            contract["verifier_implementation_preimage"][
                "all_fifteen_routes_have_static_verifier_coverage"
            ]
        )
        linkage = contract["bundle_identity_linkage"]
        self.assertEqual(linkage["mixed_individually_valid_chain"], "REFUSE")
        self.assertTrue(
            all(value is True for key, value in linkage.items() if key != "mixed_individually_valid_chain")
        )

        refs = _schema_refs(schema)
        self.assertEqual(len(schema["$defs"]), 143)
        self.assertEqual(len(schema["oneOf"]), 27)
        self.assertEqual(len(refs), 990)
        self.assertEqual(len(set(refs)), 135)
        for ref in refs:
            self.assertIs(type(ref), str)
            self.assertTrue(ref.startswith("#/$defs/"), ref)
            _json_pointer(schema, ref[1:])
        expected_root_names = (
            "private_execution_host_manifest",
            "storage_capacity_snapshot",
            "power_snapshot",
            "public_execution_host_binding",
            "host_validation_runtime_preimage",
            "host_runtime_lock_acquisition_preimage",
            "host_runtime_lock_release_observation",
            "binding_implementation_preimage",
            "binding_validator_preimage",
            "validator_source_bundle_artifact",
            "validator_executable_zipapp_manifest",
            "durability_probe_invocation_preimage",
            "validator_artifact_lock_observation",
            "binding_authority_set_preimage",
            "scientific_code_preimage",
            "scientific_implementation_preimage",
            "verifier_implementation_preimage",
            "stage_e_integration_preimage",
            "local_binding_bundle",
            "binding_readiness_record",
            "binding_validation_receipt",
            "durability_probe_receipt",
            "private_durability_bundle",
            "independent_binding_audit_receipt",
            "sealed_campaign_packet_manifest",
            "post_packet_user_authorization_receipt",
            "campaign_authorization",
        )
        self.assertEqual(
            tuple(item["$ref"].removeprefix("#/$defs/") for item in schema["oneOf"]),
            expected_root_names,
        )
        object_nodes = []

        def collect_object_nodes(value: object, path: tuple[object, ...] = ()) -> None:
            if type(value) is dict:
                if value.get("type") == "object":
                    object_nodes.append((path, value))
                for key, item in value.items():
                    collect_object_nodes(item, path + (key,))
            elif type(value) is list:
                for index, item in enumerate(value):
                    collect_object_nodes(item, path + (index,))

        collect_object_nodes(schema)
        self.assertEqual(len(object_nodes), 125)
        closed_objects = tuple(
            (path, node)
            for path, node in object_nodes
            if node.get("additionalProperties") is False
        )
        refinements = tuple(
            (path, node)
            for path, node in object_nodes
            if "additionalProperties" not in node
        )
        self.assertEqual(len(closed_objects), 89)
        self.assertEqual(len(refinements), 36)
        for path, node in closed_objects:
            self.assertEqual(set(node.get("required", [])), set(node["properties"]), path)
        for path, node in refinements:
            self.assertEqual(path[-2:], ("allOf", 1), path)
            self.assertNotIn("required", node, path)
            self.assertTrue(node["properties"], path)
        self.assertEqual(schema["scientific_execution_count"], 0)

        self.assertEqual(len(validation["static_positive_checks"]), 28)
        self.assertEqual(
            tuple(validation["semantic_relations"]),
            (
                "identity",
                "local_preimages",
                "private_public",
                "binding",
                "readiness",
                "validation_receipt",
                "storage",
                "power",
                "durability",
                "authorization",
            ),
        )
        self.assertEqual(
            sum(len(rows) for rows in validation["semantic_relations"].values()),
            144,
        )
        negatives = validation["negative_cases"]
        self.assertEqual(validation["negative_case_count"], 67)
        self.assertEqual(len(negatives), 67)
        self.assertEqual(
            tuple(row["case_id"] for row in negatives),
            tuple(f"SF-BIND-N{index:02d}" for index in range(1, 68)),
        )
        self.assertEqual({row["disposition"] for row in negatives}, {"REFUSE"})
        zero_counters = contract["prohibited_counters"]
        self.assertEqual(len(zero_counters), 15)
        self.assertEqual(set(zero_counters.values()), {0})
        self.assertEqual(predecessor["required_operation_counts"], zero_counters)
        self.assertEqual(schema["scientific_execution_count"], 0)
        self.assertEqual(
            validation["allowed_validation_operations"],
            [
                "Git object and byte inspection",
                "strict UTF-8 and JSON parsing",
                "canonical JSON serialization",
                "SHA-256 hashing",
                "closed-set and ordered-list comparison",
                "JSON Schema inspection and synthetic validation",
                "deterministic ZIP_STORED archive construction parsing and byte-for-byte rebuild",
                "outcome-blind host-runtime inventory and named Win32 identity storage power and durability observations",
                "integer-only storage arithmetic",
                "static source inspection",
            ],
        )
        self.assertEqual(
            validation["forbidden_validation_operations"],
            [
                "project runner import",
                "model or state transition",
                "registered configuration",
                "trajectory or simulation",
                "Gate or scientific transform",
                "benchmark used as scientific evidence",
                "scientific RNG draw",
                "outcome inspection",
                "result figure book release or publication",
            ],
        )

        self.assertEqual(
            contract["accepted_base_readiness"]["binding_sealable"], False
        )
        self.assertEqual(
            contract["accepted_base_readiness"]["required_disposition"],
            "BINDING_NOT_SEALABLE",
        )
        readiness_gaps = contract["accepted_base_readiness"]["gap_registry"]
        self.assertEqual(len(readiness_gaps), 15)
        self.assertEqual(
            tuple(row["route_id"] for row in readiness_gaps), campaign_order
        )
        self.assertTrue(
            all(
                row["gap_class"]
                in {
                    "IMPLEMENTATION_AUTHORITY",
                    "SCIENTIFIC_AUTHORITY",
                    "INSTITUTIONAL_AUTHORITY",
                    "INSTITUTIONAL_AND_DEPENDENCY_AUTHORITY",
                }
                and row["gap_ids"]
                and len(set(row["gap_ids"])) == len(row["gap_ids"])
                for row in readiness_gaps
            )
        )
        self.assertEqual(
            tuple(contract["readiness_dispositions"]),
            (
                "NOT_READY_AUTHORITY_GAPS",
                "READY_FOR_INDEPENDENT_BINDING_AUDIT",
                "INDEPENDENT_BINDING_PASS",
                "INDEPENDENT_BINDING_FAIL",
            ),
        )
        self.assertEqual(
            tuple(contract["bundle_dispositions"]),
            ("BINDING_NOT_SEALABLE", "READY_FOR_INDEPENDENT_BINDING_AUDIT"),
        )

        public_privacy = contract["privacy_tiers"]["public"]
        private_privacy = contract["privacy_tiers"]["private"]
        self.assertEqual(public_privacy["host_alias"], "EXECUTION-HOST-01")
        self.assertFalse(public_privacy["personal_identifiers_permitted"])
        self.assertFalse(public_privacy["absolute_paths_permitted"])
        self.assertFalse(public_privacy["private_manifest_bytes_permitted"])
        self.assertTrue(public_privacy["private_manifest_digest_identity_required"])
        self.assertTrue(public_privacy["logical_directory_roles_required"])
        self.assertTrue(private_privacy["retained_canonical_bytes_required"])
        self.assertTrue(private_privacy["non_scientific_privacy_nonce_required"])
        self.assertTrue(private_privacy["independent_local_auditor_access_required"])
        self.assertFalse(private_privacy["public_digest_alone_is_proof"])
        self.assertFalse(private_privacy["git_worktree_storage_permitted"])

        storage = contract["storage_envelope"]
        gib = 1073741824
        component_gib = (
            storage["primary_logical_output_gib"],
            storage["independent_audit_copy_gib"],
            storage["dynamic_growth_physical_writes_gib"],
            storage["checkpoint_and_write_overhead_gib"],
            storage["temporary_archives_gib"],
            storage["retained_evidence_gib"],
        )
        self.assertEqual(storage["bytes_per_gib"], gib)
        self.assertEqual(component_gib, (253, 253, 80, 64, 8, 8))
        self.assertEqual(sum(component_gib), storage["total_gib"])
        self.assertEqual(storage["total_gib"], 666)
        self.assertEqual(storage["minimum_free_after_existing_data_gib"], 350)
        self.assertEqual(storage["retained_evidence_bytes_predebited"], 8 * gib)
        self.assertEqual(
            storage["remaining_envelope_formula"],
            "715112054784 - current_envelope_usage.total_envelope_usage_bytes",
        )
        self.assertEqual(
            storage["free_space_rule"],
            "observed_free_bytes >= max(375809638400, remaining_reserved_envelope_bytes)",
        )
        self.assertTrue(storage["component_usage_record_required"])
        self.assertTrue(storage["cumulative_accounting_nonresetting"])
        self.assertEqual(
            contract["stage_e_descendant_path_closure"],
            {
                "accepted_stage_e_unique_paths": 51,
                "authority_added_paths": 6,
                "reachability_durability_unique_paths": 1,
                "stage_f_new_unique_paths": 12,
                "stage_f_modified_paths_already_in_stage_e_closure": 2,
                "final_unique_paths_relative_to_stage_e_implementation_base": 70,
                "extra_missing_or_duplicate_path_disposition": "REFUSE",
            },
        )

        packet = contract["sealed_campaign_packet_authorization_projection"]
        self.assertTrue(packet["canonical_self_contained_manifest_required"])
        self.assertEqual(
            packet["identity_preimage"],
            "complete canonical sealed_campaign_packet_manifest object",
        )
        self.assertEqual(packet["additional_fields"], "REFUSE")
        self.assertFalse(packet["private_bytes_embedded"])
        self.assertEqual(packet["sensitive_field_disclosure_count"], 0)
        self.assertTrue(
            packet[
                "packet_created_not_before_bound_validation_audit_and_final_pass_readiness"
            ]
        )
        self.assertEqual(
            tuple(packet["required_identity_fields"]),
            (
                "local_binding_bundle_identity",
                "independent_binding_pass_readiness_identity",
                "independent_binding_audit_identity",
                "binding_validation_receipt_identity",
                "public_host_binding_identity",
                "private_host_manifest_identity",
                "storage_capacity_snapshot_identity",
                "power_snapshot_identity",
                "scientific_code_identity",
                "scientific_implementation_identity",
                "installed_artifact_identity",
                "verifier_identity",
                "binding_implementation_identity",
                "authority_set_identity",
                "stage_e_integration_identity",
                "stage_e_evidence_identity",
                "validator_identity",
            ),
        )
        self.assertEqual(
            tuple(packet["required_ordered_fields"]),
            (
                "ordered_route_ids",
                "ordered_campaign_execution_binding_identities",
            ),
        )
        self.assertTrue(packet["all_identity_preimages_retained_and_recomputed"])
        self.assertEqual(packet["projection_mismatch"], "REFUSE")

        self.assertEqual(
            contract["independent_audit_sequence"],
            {
                "audited_bundle_disposition": "READY_FOR_INDEPENDENT_BINDING_AUDIT",
                "audited_readiness_disposition": "READY_FOR_INDEPENDENT_BINDING_AUDIT",
                "audited_readiness_independent_audit_identity": None,
                "audit_receipt_schema": "stage_f_independent_binding_audit/v1",
                "final_readiness_binds_exact_audit_receipt": True,
                "bundle_mutation_after_audit": "REFUSE",
            },
        )
        authorization = contract["authorization"]
        self.assertEqual(
            authorization["schema"], "stage_f_campaign_authorization/v1"
        )
        self.assertTrue(authorization["independent_binding_pass_required"])
        self.assertTrue(
            authorization[
                "final_independent_binding_pass_readiness_identity_required"
            ]
        )
        self.assertTrue(
            authorization["all_referenced_records_resolved_from_retained_canonical_bytes"]
        )
        self.assertTrue(
            authorization[
                "bundle_identity_equal_across_authorization_packet_pass_readiness_audit_and_validation"
            ]
        )
        self.assertTrue(
            authorization["audit_identity_equals_pass_readiness_audit_identity"]
        )
        self.assertEqual(authorization["audit_disposition"], "INDEPENDENT_BINDING_PASS")
        self.assertEqual(
            authorization["audit_pre_audit_readiness_disposition"],
            "READY_FOR_INDEPENDENT_BINDING_AUDIT",
        )
        self.assertTrue(
            authorization[
                "route_campaign_binding_code_artifact_implementation_authority_stage_e_and_validator_projections_equal_packet_and_bundle"
            ]
        )
        self.assertTrue(
            authorization[
                "private_public_host_and_current_snapshot_projections_equal_validation_audit_pass_readiness_packet_and_public_binding"
            ]
        )
        self.assertEqual(authorization["mixed_record_composition_or_replay"], "REFUSE")
        self.assertTrue(authorization["later_explicit_user_statement_required"])
        self.assertTrue(authorization["user_statement_received_not_before_packet_created"])
        self.assertFalse(authorization["controller_self_authorization_permitted"])
        self.assertFalse(authorization["dictionary_presence_is_authorization"])
        self.assertTrue(authorization["preimport_guard_required"])

        marker = "STAGE_F_LOCAL_EXECUTION_BINDING_AUTHORITY_COMPLETE"
        for document in (contract, schema, implementation, predecessor, validation):
            self.assertEqual(document["completion_marker"], marker)
        for path, raw in raw_by_path.items():
            self.assertEqual(raw.count(marker.encode("utf-8")), 1, path)

        if (
            current_scope["stage_f_local_binding_phase"]
            == "STAGE_F_LOCAL_BINDING_COMPLETED_IMPLEMENTATION"
        ):
            accepted_workflow_raw = _object_row(
                ".github/workflows/tests.yml", base_entries, base_archive
            )[1]
            current_workflow_raw = _object_row(
                ".github/workflows/tests.yml", current_entries, current_archive
            )[1]
            self.assertTrue(current_workflow_raw.startswith(accepted_workflow_raw))
            workflow_suffix = current_workflow_raw[len(accepted_workflow_raw) :]
            self.assertTrue(workflow_suffix.startswith(b"\n"))
            self.assertTrue(workflow_suffix.endswith(b"\n"))
            self.assertNotIn(b"\r", workflow_suffix)
            suffix_text = workflow_suffix.decode("utf-8", "strict")
            self.assertEqual(
                tuple(suffix_text[:-1].split("\n")),
                (
                    "",
                    "  stage-f-binding-foundation:",
                    "    if: github.event_name == 'push' || github.event_name == 'pull_request' || github.event_name == 'workflow_dispatch'",
                    "    needs: [stage-e-scientific-harness]",
                    "    runs-on: ubuntu-24.04",
                    "    steps:",
                    "      - uses: actions/checkout@v4",
                    "        with:",
                    "          fetch-depth: 0",
                    "      - uses: actions/setup-python@v5",
                    "        with:",
                    '          python-version: "3.14"',
                    "      - name: Build deterministic Stage F binding-foundation artifacts",
                    "        run: |",
                    "          set -euo pipefail",
                    '          stage_root="$RUNNER_TEMP/stage-f-${GITHUB_JOB}"',
                    '          mkdir -p "$stage_root/first" "$stage_root/second"',
                    '          python -I scripts/build_stage_f_local_binding.py --source "$GITHUB_WORKSPACE" --output "$stage_root/first"',
                    '          python -I scripts/build_stage_f_local_binding.py --source "$GITHUB_WORKSPACE" --output "$stage_root/second"',
                    '          cmp -- "$stage_root/first/stage-f-binding-validator-source-bundle.json" "$stage_root/second/stage-f-binding-validator-source-bundle.json"',
                    '          cmp -- "$stage_root/first/stage-f-binding-validator.pyz" "$stage_root/second/stage-f-binding-validator.pyz"',
                    "      - name: Run outcome-blind Stage F binding-foundation synthetic controls",
                    "        run: |",
                    "          set -euo pipefail",
                    "          python -I -c 'import os,sys,unittest; sys.path.insert(0,os.environ[\"GITHUB_WORKSPACE\"]); names=(\"tests.stage_f_binding.test_binding_privacy_and_authorization\",\"tests.stage_f_binding.test_durability_and_no_science\"); suite=unittest.defaultTestLoader.loadTestsFromNames(names); count=suite.countTestCases(); result=unittest.TextTestRunner(verbosity=2).run(suite); raise SystemExit(0 if count > 0 and result.testsRun == count and result.wasSuccessful() and not result.skipped and not result.expectedFailures and not result.unexpectedSuccesses else 1)'",
                ),
            )
            top_level_jobs = tuple(
                re.findall(r"(?m)^  ([a-z0-9][a-z0-9-]*):\n", suffix_text)
            )
            self.assertEqual(top_level_jobs, ("stage-f-binding-foundation",))
            self.assertEqual(
                suffix_text.count(
                    "    if: github.event_name == 'push' || github.event_name == 'pull_request' || github.event_name == 'workflow_dispatch'\n"
                ),
                1,
            )
            self.assertEqual(
                suffix_text.count("    needs: [stage-e-scientific-harness]\n"), 1
            )
            self.assertEqual(suffix_text.count("    runs-on: ubuntu-24.04\n"), 1)
            self.assertEqual(suffix_text.count("    steps:\n"), 1)
            self.assertEqual(
                tuple(re.findall(r"(?m)^      - uses: ([^\n]+)$", suffix_text)),
                ("actions/checkout@v4", "actions/setup-python@v5"),
            )
            self.assertEqual(
                tuple(re.findall(r"(?m)^      - name: ([^\n]+)$", suffix_text)),
                (
                    "Build deterministic Stage F binding-foundation artifacts",
                    "Run outcome-blind Stage F binding-foundation synthetic controls",
                ),
            )
            self.assertEqual(suffix_text.count("        with:\n"), 2)
            self.assertEqual(suffix_text.count("        run: |\n"), 2)
            self.assertEqual(suffix_text.count("          fetch-depth: 0\n"), 1)
            self.assertEqual(
                suffix_text.count('          python-version: "3.14"\n'), 1
            )
            for forbidden in (
                "${{",
                "secrets.",
                "upload-artifact",
                "download-artifact",
                "actions/cache",
                "continue-on-error",
                "permissions:",
                "environment:",
                "services:",
                "container:",
                "curl ",
                "wget ",
                "pip ",
                "gh ",
                "stage_e_harness/execution.py",
                "scripts/validate_stage_f_local_binding.py",
                "ebu_framework",
                "results/",
                "figures/",
                "books/",
                "..",
            ):
                self.assertNotIn(forbidden, suffix_text)

            run_commands = []
            for line in suffix_text[:-1].split("\n"):
                if not line:
                    continue
                indent = len(line) - len(line.lstrip(" "))
                stripped = line.strip()
                if indent == 2:
                    self.assertEqual(stripped, "stage-f-binding-foundation:")
                elif indent == 4:
                    self.assertIn(
                        stripped,
                        (
                            "if: github.event_name == 'push' || github.event_name == 'pull_request' || github.event_name == 'workflow_dispatch'",
                            "needs: [stage-e-scientific-harness]",
                            "runs-on: ubuntu-24.04",
                            "steps:",
                        ),
                        line,
                    )
                elif indent == 6:
                    self.assertIn(
                        stripped,
                        (
                            "- uses: actions/checkout@v4",
                            "- uses: actions/setup-python@v5",
                            "- name: Build deterministic Stage F binding-foundation artifacts",
                            "- name: Run outcome-blind Stage F binding-foundation synthetic controls",
                        ),
                        line,
                    )
                elif indent == 8:
                    self.assertIn(stripped, ("with:", "run: |"), line)
                elif indent == 10:
                    if stripped not in ("fetch-depth: 0", 'python-version: "3.14"'):
                        run_commands.append(stripped)
                else:
                    self.fail(f"forbidden Stage F workflow indentation or field: {line!r}")

            allowed_commands = (
                re.compile(r"set -euo pipefail"),
                re.compile(r'stage_root="\$RUNNER_TEMP/stage-f-\$\{GITHUB_JOB\}"'),
                re.compile(r'mkdir -p(?: "\$stage_root/[a-z0-9._/-]+")+'),
                re.compile(
                    r'python -I scripts/build_stage_f_local_binding\.py(?: --[a-z][a-z-]* (?:"(?:\$GITHUB_WORKSPACE|\$stage_root/[a-z0-9._/-]+)"|[A-Za-z0-9._/-]+))+'
                ),
                re.compile(
                    r'cmp -- "\$stage_root/[a-z0-9._/-]+" "\$stage_root/[a-z0-9._/-]+"'
                ),
                re.compile(
                    r"python -I -m unittest -v tests\.stage_f_binding\.test_binding_privacy_and_authorization tests\.stage_f_binding\.test_durability_and_no_science"
                ),
            )
            self.assertEqual(
                tuple(run_commands),
                (
                    "set -euo pipefail",
                    'stage_root="$RUNNER_TEMP/stage-f-${GITHUB_JOB}"',
                    'mkdir -p "$stage_root/first" "$stage_root/second"',
                    'python -I scripts/build_stage_f_local_binding.py --source "$GITHUB_WORKSPACE" --output "$stage_root/first"',
                    'python -I scripts/build_stage_f_local_binding.py --source "$GITHUB_WORKSPACE" --output "$stage_root/second"',
                    'cmp -- "$stage_root/first/stage-f-binding-validator-source-bundle.json" "$stage_root/second/stage-f-binding-validator-source-bundle.json"',
                    'cmp -- "$stage_root/first/stage-f-binding-validator.pyz" "$stage_root/second/stage-f-binding-validator.pyz"',
                    "set -euo pipefail",
                    "python -I -c 'import os,sys,unittest; sys.path.insert(0,os.environ[\"GITHUB_WORKSPACE\"]); names=(\"tests.stage_f_binding.test_binding_privacy_and_authorization\",\"tests.stage_f_binding.test_durability_and_no_science\"); suite=unittest.defaultTestLoader.loadTestsFromNames(names); count=suite.countTestCases(); result=unittest.TextTestRunner(verbosity=2).run(suite); raise SystemExit(0 if count > 0 and result.testsRun == count and result.wasSuccessful() and not result.skipped and not result.expectedFailures and not result.unexpectedSuccesses else 1)'",
                ),
            )
            self.assertEqual(
                sum(
                    "scripts/build_stage_f_local_binding.py" in command
                    for command in run_commands
                ),
                2,
            )
            self.assertEqual(sum(command.startswith("cmp -- ") for command in run_commands), 2)
            self.assertEqual(
                sum(command.startswith("python -I -c ") for command in run_commands),
                1,
            )

            accepted_validator_raw = _object_row(
                "scripts/validate_stage_e_harness.py", base_entries, base_archive
            )[1]
            current_validator_raw = _object_row(
                "scripts/validate_stage_e_harness.py", current_entries, current_archive
            )[1]
            self.assertEqual(
                accepted_validator_raw.count(
                    STAGE_E_VALIDATOR_AUTHORITY_LANE_SCOPE_BLOCK
                ),
                1,
            )
            stage_f_scope_raw = STAGE_F_VALIDATOR_AUTHORITY_LANE_SCOPE_BLOCK.encode(
                "utf-8", "strict"
            )
            self.assertTrue(stage_f_scope_raw.endswith(b"\n"))
            indented_stage_f_scope_raw = b"\n".join(
                b"    " + line for line in stage_f_scope_raw[:-1].split(b"\n")
            ) + b"\n"
            expected_validator_raw = accepted_validator_raw.replace(
                STAGE_E_VALIDATOR_AUTHORITY_LANE_SCOPE_BLOCK,
                indented_stage_f_scope_raw,
                1,
            )
            self.assertEqual(current_validator_raw, expected_validator_raw)
            accepted_validator_tree = ast.parse(
                accepted_validator_raw.decode("utf-8", "strict")
            )
            current_validator_tree = ast.parse(
                current_validator_raw.decode("utf-8", "strict")
            )

            def without_authority_lane(tree: ast.Module) -> tuple[str, ...]:
                return tuple(
                    ast.dump(node, include_attributes=False)
                    for node in tree.body
                    if not (
                        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                        and node.name == "_authority_lane"
                    )
                )

            self.assertEqual(
                without_authority_lane(current_validator_tree),
                without_authority_lane(accepted_validator_tree),
            )
            def authority_lane(tree: ast.Module) -> ast.FunctionDef:
                lanes = tuple(
                    node
                    for node in tree.body
                    if isinstance(node, ast.FunctionDef)
                    and node.name == "_authority_lane"
                )
                self.assertEqual(len(lanes), 1)
                return lanes[0]

            accepted_lane = authority_lane(accepted_validator_tree)
            current_lane = authority_lane(current_validator_tree)
            self.assertEqual(
                ast.dump(current_lane.args, include_attributes=False),
                ast.dump(accepted_lane.args, include_attributes=False),
            )
            self.assertEqual(current_lane.decorator_list, accepted_lane.decorator_list)
            self.assertEqual(
                ast.dump(current_lane.returns, include_attributes=False),
                ast.dump(accepted_lane.returns, include_attributes=False),
            )

            def contains_string(node: ast.AST, value: str) -> bool:
                return any(
                    isinstance(child, ast.Constant) and child.value == value
                    for child in ast.walk(node)
                )

            def assigned_name(node: ast.AST) -> str | None:
                if (
                    isinstance(node, ast.Assign)
                    and len(node.targets) == 1
                    and isinstance(node.targets[0], ast.Name)
                ):
                    return node.targets[0].id
                return None

            stage_e_manifest_name = (
                "stage_e_dynamic_growth_harness_reconciliation_implementation_path_manifest.json"
            )
            accepted_start = next(
                index
                for index, node in enumerate(accepted_lane.body)
                if contains_string(node, stage_e_manifest_name)
            )
            current_start = next(
                index
                for index, node in enumerate(current_lane.body)
                if contains_string(node, stage_e_manifest_name)
            )
            accepted_end = next(
                index
                for index, node in enumerate(accepted_lane.body)
                if assigned_name(node) == "harness_sources"
            )
            current_end = next(
                index
                for index, node in enumerate(current_lane.body)
                if assigned_name(node) == "harness_sources"
            )
            self.assertEqual(
                tuple(
                    ast.dump(node, include_attributes=False)
                    for node in current_lane.body[:current_start]
                ),
                tuple(
                    ast.dump(node, include_attributes=False)
                    for node in accepted_lane.body[:accepted_start]
                ),
            )
            self.assertEqual(
                tuple(
                    ast.dump(node, include_attributes=False)
                    for node in current_lane.body[current_end:]
                ),
                tuple(
                    ast.dump(node, include_attributes=False)
                    for node in accepted_lane.body[accepted_end:]
                ),
            )
            changed_lane_nodes = current_lane.body[current_start:current_end]
            expected_changed_lane_nodes = ast.parse(
                STAGE_F_VALIDATOR_AUTHORITY_LANE_SCOPE_BLOCK
            ).body
            self.assertEqual(
                tuple(
                    ast.dump(node, include_attributes=False)
                    for node in changed_lane_nodes
                ),
                tuple(
                    ast.dump(node, include_attributes=False)
                    for node in expected_changed_lane_nodes
                ),
            )
            lane_source = "\n".join(
                ast.get_source_segment(
                    current_validator_raw.decode("utf-8", "strict"), node
                )
                or ""
                for node in changed_lane_nodes
            )
            for required in (
                stage_e_manifest_name,
                "stage_f_local_execution_binding_implementation_path_manifest.json",
                "stage_f_local_execution_binding_evidence_correction_implementation_path_manifest.json",
                "stage_f_local_execution_binding_final_evidence_closure_correction_implementation_path_manifest.json",
                "stage_f_local_execution_binding_attempt_root_bootstrap_correction_implementation_path_manifest.json",
                "authority_paths",
                "prospective_reachability_correction",
                "prospective_implementation",
                "modified_paths",
                "new_paths",
                "final_descendant_path_closure",
                "final_unique_path_count",
                "accepted_stage_f_v1_authority_path_count",
                "accepted_stage_f_evidence_correction_authority_path_count",
                "accepted_stage_f_final_evidence_closure_authority_path_count",
                "attempt_root_bootstrap_correction_authority_added_path_count",
                "successor_active_authority_row_count",
                "historical_authority_only_unique_path_count",
                "historical_completed_implementation_unique_path_count",
                "authority_only_unique_path_count",
                STAGE_F_LOCAL_BINDING_REACHABILITY_PATH,
                '"diff", "--name-only"',
                '"diff", "--name-status"',
                '"ls-tree"',
                '"100644"',
                '"blob"',
                "actual != expected",
                "len(actual) != 88",
                "status_rows != expected_status",
                "for relative in expected:",
            ):
                self.assertIn(required, lane_source)
            changed_lane_tree = ast.Module(
                body=list(changed_lane_nodes), type_ignores=[]
            )
            self.assertTrue(
                all(
                    isinstance(node, (ast.Assign, ast.AnnAssign, ast.If, ast.For))
                    for node in changed_lane_nodes
                )
            )
            self.assertEqual(
                sum(isinstance(node, ast.For) for node in ast.walk(changed_lane_tree)),
                2,
            )
            self.assertFalse(
                any(
                    isinstance(
                        node,
                        (
                            ast.AsyncFor,
                            ast.AsyncFunctionDef,
                            ast.ClassDef,
                            ast.FunctionDef,
                            ast.Import,
                            ast.ImportFrom,
                            ast.Lambda,
                            ast.Break,
                            ast.Continue,
                            ast.Pass,
                            ast.Return,
                            ast.Try,
                            ast.While,
                            ast.With,
                            ast.AsyncWith,
                            ast.Yield,
                            ast.YieldFrom,
                        ),
                    )
                    for node in ast.walk(changed_lane_tree)
                )
            )
            for guard in (
                node for node in ast.walk(changed_lane_tree) if isinstance(node, ast.If)
            ):
                self.assertFalse(isinstance(guard.test, ast.Constant))
                self.assertFalse(
                    any(
                        isinstance(node, (ast.And, ast.IfExp, ast.NamedExpr))
                        or (
                            isinstance(node, ast.Constant)
                            and type(node.value) is bool
                        )
                        for node in ast.walk(guard.test)
                    )
                )
                self.assertEqual(len(guard.body), 1)
                self.assertIsInstance(guard.body[0], ast.Raise)
                self.assertEqual(guard.orelse, [])
            for refusal in (
                node
                for node in ast.walk(changed_lane_tree)
                if isinstance(node, ast.Raise)
            ):
                self.assertIsNone(refusal.cause)
                self.assertIsInstance(refusal.exc, ast.Call)
                self.assertIsInstance(refusal.exc.func, ast.Name)
                self.assertEqual(refusal.exc.func.id, "Refusal")
            call_names = tuple(
                node.func.id
                if isinstance(node.func, ast.Name)
                else node.func.attr
                if isinstance(node.func, ast.Attribute)
                else "<dynamic>"
                for node in ast.walk(changed_lane_tree)
                if isinstance(node, ast.Call)
            )
            self.assertTrue(
                set(call_names)
                <= {
                    "_git",
                    "Refusal",
                    "filter",
                    "len",
                    "set",
                    "sorted",
                    "split",
                    "splitlines",
                    "strict_load",
                    "tuple",
                },
                call_names,
            )
            self.assertEqual(call_names.count("strict_load"), 5)
            self.assertEqual(call_names.count("_git"), 3)
            self.assertEqual(
                call_names.count("Refusal"),
                sum(
                    isinstance(node, ast.If)
                    for node in ast.walk(changed_lane_tree)
                ),
            )
            for forbidden in (
                "subprocess",
                "ebu_framework",
                "stage_e_harness/execution.py",
                "trajectory",
                "simulation",
                "random",
                "result",
                "figure",
                "book",
            ):
                self.assertNotIn(forbidden, lane_source)
            lane_integer_constants = {
                node.value
                for node in ast.walk(changed_lane_tree)
                if isinstance(node, ast.Constant) and type(node.value) is int
            }
            for count in (70, 76, 82, 88):
                self.assertIn(count, lane_integer_constants)

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
        bridge_hash = _sha256(_checkout_lf_bytes(ROOT / bridge_path, bridge_path))
        dynamic_hash = _sha256(_checkout_lf_bytes(ROOT / dynamic_path, dynamic_path))
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
        self,
        manifest,
        stage_c_phase: str,
        stage_e_phase: str | None,
        stage_f_local_binding_phase: str | None,
    ) -> None:
        safety_path = ROOT / "tests/framework/safety.py"
        safety_raw = _checkout_lf_bytes(safety_path, "tests/framework/safety.py")
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

        current_workflow_raw = _checkout_lf_bytes(
            ROOT / ".github/workflows/tests.yml", ".github/workflows/tests.yml"
        )
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
            stage_e_current_workflow_raw = current_workflow_raw
            if (
                stage_f_local_binding_phase
                == "STAGE_F_LOCAL_BINDING_COMPLETED_IMPLEMENTATION"
            ):
                stage_f_base_entries = _tree_entries(
                    STAGE_F_LOCAL_BINDING_ACCEPTED_BASE_COMMIT
                )
                stage_f_base_archive = _archive_members(
                    STAGE_F_LOCAL_BINDING_ACCEPTED_BASE_COMMIT
                )
                _, accepted_stage_e_workflow_raw = _object_row(
                    ".github/workflows/tests.yml",
                    stage_f_base_entries,
                    stage_f_base_archive,
                )
                self.assertTrue(
                    current_workflow_raw.startswith(accepted_stage_e_workflow_raw)
                )
                stage_e_current_workflow_raw = accepted_stage_e_workflow_raw
            stage_c_workflow_raw = stage_e_current_workflow_raw
            if stage_e_phase == "STAGE_E_HARNESS_COMPLETED_IMPLEMENTATION":
                self.assertTrue(
                    stage_e_current_workflow_raw.endswith(STAGE_E_WORKFLOW_APPEND_BLOCK)
                )
                stage_c_workflow_raw = stage_e_current_workflow_raw[
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
            raw = _checkout_lf_bytes(ROOT / path, path)
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
