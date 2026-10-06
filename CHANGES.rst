CHANGELOG
=========

.. towncrier release notes start

pyproject-validator 1.0.0 (2026-10-06)
======================================

Breaking changes
----------------

- Drop support for Python 3.10. (`#21 <https://github.com/fizyk/pyproject-validator/issues/21>`_)


Features
--------

- Add support for Python 3.15. (`#21 <https://github.com/fizyk/pyproject-validator/issues/21>`_)
- Validate that ruff's ``tool.ruff.target-version`` points to the lowest Python version declared in classifiers. (`#25 <https://github.com/fizyk/pyproject-validator/issues/25>`_)


Miscellaneus
------------

- `#23 <https://github.com/fizyk/pyproject-validator/issues/23>`_, `#36 <https://github.com/fizyk/pyproject-validator/issues/36>`_


pyproject-validator 0.1.1 (2026-09-29)
======================================

Miscellaneus
------------

- `#6 <https://github.com/fizyk/pyproject-validator/issues/6>`_, `#7 <https://github.com/fizyk/pyproject-validator/issues/7>`_, `#8 <https://github.com/fizyk/pyproject-validator/issues/8>`_, `#9 <https://github.com/fizyk/pyproject-validator/issues/9>`_, `#10 <https://github.com/fizyk/pyproject-validator/issues/10>`_, `#11 <https://github.com/fizyk/pyproject-validator/issues/11>`_, `#12 <https://github.com/fizyk/pyproject-validator/issues/12>`_, `#19 <https://github.com/fizyk/pyproject-validator/issues/19>`_


pyproject-validator 0.1.0 (2025-11-05)
======================================

Features
--------

- Created readme for the project
- Script and pre-commit hook to check validity and consistency between classifiers and require-python in pyproject.toml.
