# Backend reorganization

- Moved `app/`, `modules/`, `tests/`, and `evaluation/` under `backend/`.
- Moved `requirements.txt` under `backend/`.
- Grouped architecture/audit/verification notes under `docs/`.
- Removed cached pytest state, `__pycache__`, and compiled `.pyc` files from the delivery package.
- No database/authentication/M06 code was added in this reorganization.
- Run tests from `backend/` so Python imports resolve from the backend root.
