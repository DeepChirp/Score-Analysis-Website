#!/bin/bash
docker compose down
git pull --rebase
docker compose build
docker compose up -d

