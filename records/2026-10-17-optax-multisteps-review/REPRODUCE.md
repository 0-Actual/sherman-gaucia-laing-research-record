# Independent reproduction

This procedure reproduces the selected recorded comparison using public source and synthetic test inputs. It is supplied for readers; the numerical suites were not rerun while packaging this edition.

Use a compatible Linux CPU environment with Python 3.11 (recorded: 3.11.17). JAX/jaxlib 0.7.1 requires supported CPU instructions; the author's laptop failed its AVX guard. Do not bypass that guard. No model API, secret, private dataset, GPU or training service is required.

The original [validation workflow](https://github.com/0-Actual/optax/blob/3938cea8578e901a151f6c70ebcf638c423dda1d/.github/workflows/multisteps-validation.yml) supplies the exact executed procedure. The workflow used a hosted Ubuntu 24.04 runner and installed dependencies before saving an environment artifact. The included environment-observed.txt is reconstructed from its successful-install log, not the complete original pip-freeze artifact. Pinning it narrows version drift but does not guarantee an identical operating system, wheel selection or bitwise environment.

## Prepare a disposable checkout

Place this edition in a directory named packet, then run the following from its parent in a shell. Use a new checkout: the later restore commands intentionally change its production file.

```sh
git clone https://github.com/0-Actual/optax.git optax-replay
cd optax-replay
git checkout 1c7e94b42f47899bd98021ed03fe4e0088be4a41
python3.11 -m venv .venv
. .venv/bin/activate
export JAX_PLATFORMS=cpu OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python -m pip install -c ../packet/environment-observed.txt 'jax==0.7.1' 'jaxlib==0.7.1' 'flax==0.11.2' 'pytest==9.1.1' ruff pyink -e .
python -m pip check
python -c "import jax; print(jax.__version__, jax.devices())"
mkdir -p validation-results
```

## Baseline counterexample

Keep the added tests, but restore only production code to the pinned upstream baseline.

```sh
git restore --source 8589d974e565fbf1bfa1cdf8d94f5ecdf8ebe93c -- optax/transforms/_accumulation.py
python -m pytest optax/transforms/_accumulation_test.py::MultiStepsNonFiniteTest -q --tb=short --junitxml=validation-results/baseline-regressions.xml
```

The recorded result is exit code 1, **30 failed and 4 passed**, with no errors or skips. A failure to import, missing CPU support or collection error is not reproduction of these assertion failures. If automating, explicitly capture this expected nonzero status rather than aborting before the next step.

## Corrected selected suite

```sh
git restore --source 1c7e94b42f47899bd98021ed03fe4e0088be4a41 -- optax/transforms/_accumulation.py
python -m pytest optax/transforms/_accumulation_test.py optax/transforms/_conditionality_test.py -q --tb=short --junitxml=validation-results/corrected-selected-tests.xml
python -m ruff check optax/transforms/_accumulation.py optax/transforms/_accumulation_test.py
python .github/check_license_headers.py
git diff --exit-code
```

The recorded corrected result is exit code 0, **55 tests plus 30 subtests passed**. JUnit records include those subtests. Retain new failures, environment information and outputs if an independent rerun differs.

## Verify the distributed patch independently

In a separate fresh checkout of the pinned upstream baseline, contribution.patch applies to the two named files with git apply --check followed by git apply. Publication preparation performed that check and compared the rebuilt files with the immutable tested fork. The content matches after normalizing CRLF to LF; SOURCE_REFERENCES.json records both identities. A raw byte hash mismatch caused solely by that documented transformation is not a semantic difference.

The patch changes only the two masks and adds the MultiStepsNonFiniteTest family. It does not install a global finite-input filter. The k=1 test deliberately checks that an emitted non-finite update remains visible without a rejection policy.
