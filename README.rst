pyproject-validator
====================

Validate Python version declarations in ``pyproject.toml``.

This tiny tool checks that the ``project.requires-python`` specifier in your
``pyproject.toml`` is consistent with the declared Trove
``project.classifiers`` for Python versions (e.g. ``Programming Language :: Python :: 3.12``).

Why this is useful
------------------
It is easy to forget to update ``requires-python`` when you drop support for an
older Python in your classifiers, or vice‑versa. For example, if your
classifiers start from ``3.12`` but your ``requires-python`` is still ``>=3.11``,
users on 3.11 will be told they can install your package even though your
classifiers say otherwise. This tool catches that inconsistency.

What exactly is checked?
------------------------
- The minimal explicit Python version found in ``project.classifiers``
  (e.g. ``Programming Language :: Python :: 3.12``) is detected.
- The previous minor version (e.g. ``3.11``) is then tested against the
  ``project.requires-python`` specifier.
- If that previous version still matches the specifier, the tool exits with a
  non‑zero code and explains how to fix the problem (usually by raising
  ``requires-python`` to ``>= <minimal_classifier_version>``).

.. note::

   Only explicit minor versions like ``3.10``, ``3.11``, ... are considered.
   Generic entries like ``Programming Language :: Python :: 3`` or
   ``... :: 3 :: Only`` are ignored.


- If either ``requires-python`` or the Python version classifiers are missing,
  the tool prints an informational message and exits successfully (0) so it can
  be safely used in CI or pre-commit even for repos that don’t publish packages.


Usage
-----
Run in the repository root (where ``pyproject.toml`` is located):

.. code-block:: bash

   python check_python_versions.py

Exit codes:
- ``0``: Everything is consistent, or required fields are missing (informational skip).
- ``1``: Inconsistency detected, or a runtime error occurred (missing dependencies, etc.).

Example output (consistent):

.. code-block:: text

   ✅ Python versions consistency (`requires-python` and `classifiers` >= 3.12) is verified.

Example output (inconsistent):

.. code-block:: text

   ================================================================================
   !!! INCONSISTENCY IN PYTHON VERSIONS IN PYPROJECT.TOML !!!
     Minimum version in `classifiers`: 3.12
     Oldest versiion still supported in classifiers: 3.11
     `requires-python` setting is: ">=3.11"
     ERROR: 3.11 version (which is not in the classifiers) still fits in `requires-python`.
     RECOMMENDATION: Change`requires-python` into: ">= 3.12"
   ================================================================================

Pre-commit integration
----------------------
You can run this tool as a pre-commit hook to automatically check changes to
``pyproject.toml``.

.. code-block:: yaml

    repos:
    -   repo: https://github.com/fizyk/pyproject-validator
        rev: v0.1.0
        hooks:
        -   id: check-python-version-consistency


Development
-----------
- Set up development dependencies with ``pipenv`` (used by local hooks here):

  .. code-block:: bash

     pip install pipenv
     pipenv install --dev

- Run linters and formatters:

  .. code-block:: bash

     pre-commit run -a

- Run tests:

  .. code-block:: bash

     pipenv run pytest -q

Project metadata
----------------
- Source: https://github.com/fizyk/pyproject-validator
- Issue tracker: https://github.com/fizyk/pyproject-validator/issues
- Changelog: https://github.com/fizyk/pyproject-validator/blob/v0.1.0/CHANGES.rst
- License: MIT (see ``LICENSE``)

License
-------
This project is licensed under the MIT License. See ``LICENSE`` for details.
