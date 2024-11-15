#!/bin/bash
set -e
psql -U postgres -c 'ALTER SYSTEM SET shared_preload_libraries = "vectors.so"'
psql -U postgres -c 'ALTER SYSTEM SET search_path TO "$user", public, vectors'
