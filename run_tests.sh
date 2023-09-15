#!/bin/bash

export TEST=1

pip install -r requirements.txt
alembic upgrade head
pytest
