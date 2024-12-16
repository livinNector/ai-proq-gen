#!/bin/bash

arg=$1
arg=${arg:-frontend/first_page.py}

PYTHONPATH="$HOME/ai-prog-gen:$PYTHONPATH" gradio "$arg"