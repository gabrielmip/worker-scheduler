#!/bin/bash

CHROME_BIN=/usr/bin/chromium find . -name '*.py' | INCLUDE_E2E=true entr ./manage.py test
