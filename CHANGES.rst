CHANGELOG
=========

.. towncrier release notes start

pyproject-validator 1.0.0 (2026-10-06)
======================================

Breaking changes
----------------

- Drop support for Python 3.10. (`#21 <https://github.com/fizyk/pyproject-validator/issues/21>`__)


Features
--------

- Add support for Python 3.15. (`#21 <https://github.com/fizyk/pyproject-validator/issues/21>`__)
- Validate that ruff's ``tool.ruff.target-version`` points to the lowest Python version declared in classifiers. (`#25 <https://github.com/fizyk/pyproject-validator/issues/25>`__)


Miscellaneous
-------------

- `#23 <https://github.com/fizyk/pyproject-validator/issues/23>`__, `#36 <https://github.com/fizyk/pyproject-validator/issues/36>`__


pyproject-validator 0.1.1 (2026-09-29)
======================================

Miscellaneous
-------------

- `#6 <https://github.com/fizyk/pyproject-validator/issues/6>`__, `#7 <https://github.com/fizyk/pyproject-validator/issues/7>`__, `#8 <https://github.com/fizyk/pyproject-validator/issues/8>`__, `#9 <https://github.com/fizyk/pyproject-validator/issues/9>`__, `#10 <https://github.com/fizyk/pyproject-validator/issues/10>`__, `#11 <https://github.com/fizyk/pyproject-validator/issues/11>`__, `#12 <https://github.com/fizyk/pyproject-validator/issues/12>`__, `#19 <https://github.com/fizyk/pyproject-validator/issues/19>`__


pyproject-validator 0.1.0 (2025-11-05)
======================================

Features
--------

- Created readme for the project
- Script and pre-commit hook to check validity and consistency between classifiers and require-python in pyproject.toml.
