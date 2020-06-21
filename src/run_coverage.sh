#!/bin/bash

coverage run --source='.' manage.py test workforce
coverage xml
[[ -e coverage-badge.svg ]] && rm coverage-badge.svg
coverage-badge -o coverage-badge.svg
