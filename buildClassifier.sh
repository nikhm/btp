#!/bin/bash

for f in ../annotated/*.html; do python test1builder.py $f temp.pkl; done
python listMkaer.py data.pkl
python buildFromTxt.py data.pkl
