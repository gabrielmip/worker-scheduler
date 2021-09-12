#!/bin/bash

RUN_END_TO_END=${INCLUDE_E2E:-false}

CHROME_BIN=/usr/bin/chromium find . -name '*.py' | INCLUDE_E2E=RUN_END_TO_END entr ./manage.py test "$@"
