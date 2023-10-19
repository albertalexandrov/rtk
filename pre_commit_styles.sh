#!/bin/sh
pre-commit run -a autoflake
pre-commit run -a isort
pre-commit run -a black