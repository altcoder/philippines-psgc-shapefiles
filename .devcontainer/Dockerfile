FROM mcr.microsoft.com/devcontainers/python:3

RUN sudo apt-get update \
    && sudo apt-get install -y --no-install-recommends libgdal-dev

RUN python -m pip install --upgrade pip \
    && python -m pip install 'flit>=3.8.0'

ENV FLIT_ROOT_INSTALL=1

COPY pyproject.toml .
RUN touch README.md \
    && mkdir -p src/ph_psgc_shape \
    && python -m flit install --only-deps --deps develop \
    && rm -r pyproject.toml README.md src
