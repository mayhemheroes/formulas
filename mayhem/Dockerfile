# syntax=docker/dockerfile:1.7
#
# Commit-image Dockerfile (SMALL form) — builds ON TOP of the org base image
# (ghcr.io/mayhemheroes/base). The base provides debian + clang/llvm + libFuzzer + Python 3 + the
# identities + the build-contract ENV. formulas (vinci1it2000/formulas) is a PURE-PYTHON package, so
# this image installs the Atheris harness's Python deps (atheris, formulas + its runtime deps, ddt
# for the unittest oracle) into the base's system Python as root, then (as the non-root `mayhem` user)
# compiles the ELF launcher shims and runs the real unittest suite via build.sh / test.sh.
#
# Build (from the repo root):
#   DOCKER_BUILDKIT=1 docker build -f mayhem/Dockerfile \
#       --build-arg COMMIT=$(git rev-parse HEAD) \
#       [--build-arg SOURCE_DATE_EPOCH=$(date +%s)] \
#       -t formulas-commit:test .

FROM ghcr.io/mayhemheroes/base:20260621

ARG COMMIT
ARG REPO_URL
# SOURCE_DATE_EPOCH stays an ARG (available to build.sh); never bake it as ENV — an empty value
# breaks clang. build.sh unsets it when empty.
ARG SOURCE_DATE_EPOCH
# Declared for parity with the build contract; formulas has no native code to sanitize.
ARG SANITIZER_FLAGS

# Atheris (the libFuzzer harness engine — a prebuilt cp313 wheel against the base's clang/libFuzzer)
# and ddt (the unittest data-driven decorator the known-answer suite uses) go into the base's SYSTEM
# Python. PEP 668 marks that interpreter externally-managed, so --break-system-packages. This is the
# (networked) install step; build.sh deliberately does NOT pip-install, so its offline PATCH-tier
# re-run stays air-gapped.
USER root
RUN pip install --no-cache-dir --break-system-packages "atheris==3.1.0" ddt dill

# Source enters from the build CONTEXT (the CI checkout): the FULL repo (incl. .git history)
# is copied to /mayhem as `mayhem`; build.sh builds in place.
WORKDIR /mayhem
COPY --chown=2000:2000 . /mayhem

# Install formulas itself (pulls its runtime deps: schedula, numpy, scipy, regex, python-dateutil,
# numpy-financial, tqdm) so the harness/oracle can `import formulas`.
RUN pip install --no-cache-dir --break-system-packages .

USER mayhem

# Compile the ELF launcher shims (Mayhem needs an ELF target, not a .py).
RUN bash mayhem/build.sh

# Run formulas' real unittest known-answer suite at build time; a failing suite fails the build.
RUN if [ -f mayhem/test.sh ]; then bash mayhem/test.sh; else echo "no mayhem/test.sh"; fi

LABEL org.opencontainers.image.source="${REPO_URL}" \
      org.opencontainers.image.revision="${COMMIT}" \
      rlenv.tier="commit" \
      rlenv.source_date_epoch="${SOURCE_DATE_EPOCH}" \
      rlenv.user="mayhem"

USER mayhem
WORKDIR /mayhem
