#!/bin/bash
#
# Installs the `i.fusion.hpf` GRASS Addon.

# define variables

GRASS_ADDONS_DIR="$HOME/.grass7/addons"
GITHUB_RAW_URL="https://raw.githubusercontent.com/NikosAlexandris/i.fusion.hpf/master"

# Ensure that the necessary directories exist
mkdir -p $GRASS_ADDONS_DIR/etc/i.fusion.hpf
mkdir -p $GRASS_ADDONS_DIR/scripts
mkdir -p $GRASS_ADDONS_DIR/docs/html

# Download the files
curl $GITHUB_RAW_URL/high_pass_filter.py -o $GRASS_ADDONS_DIR/etc/i.fusion.hpf/high_pass_filter.py
curl $GITHUB_RAW_URL/constants.py -o $GRASS_ADDONS_DIR/etc/i.fusion.hpf/constants.py
curl $GITHUB_RAW_URL/i.fusion.hpf -o $GRASS_ADDONS_DIR/scripts/i.fusion.hpf
curl $GITHUB_RAW_URL/i.fusion.hpf.html -o $GRASS_ADDONS_DIR/docs/html/i.fusion.hpf.html

# set the appropriate permissions
chmod +x $GRASS_ADDONS_DIR/scripts/i.fusion.hpf
