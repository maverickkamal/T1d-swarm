#!/bin/bash
conda env export > environment.yml
git add environment.yml
git commit -m "Update environment.yml"
git push
