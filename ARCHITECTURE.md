# Architecture decisions

1. Single ownership: actual implementations live under their owning module, not duplicated under `app/services`.
2. API thinness: `app/api/routes.py` performs transport validation and coordinates M1–M5; document parsing and analysis logic remain in modules.
3. Explicit dependency direction: API -> modules; M2 depends on M1 and shared cleaning from M3; M3 JD extraction uses M3 resume skill model; M5 consumes M4 results.
4. Tests live in the top-level test suite and can be moved into per-module `tests/` as they become module-specific; module folders include local tests directories for new focused tests.
5. Models are lazy-loaded by existing extractor implementations. Keep pretrained model reuse; don't instantiate a model per request.
