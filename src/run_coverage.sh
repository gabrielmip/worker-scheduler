#!/bin/bash

INCLUDE_E2E=true coverage run --source='.' manage.py test workforce
coverage xml
[[ -e coverage-badge.svg ]] && rm coverage-badge.svg
coverage-badge -o coverage-badge.svg
