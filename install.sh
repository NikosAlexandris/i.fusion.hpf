#!/bin/bash
#
# Installs the `i.fusion.hpf` GRASS Addon.

# Ensure that the necessary directories exist
mkdir -p ~/.grass7/addons/etc/i.fusion.hpf
mkdir -p ~/.grass7/addons/scripts
mkdir -p ~/.grass7/addons/docs/html

# Download the files
curl https://raw.githubusercontent.com/NikosAlexandris/i.fusion.hpf/master/high_pass_filter.py -o ~/.grass7/addons/etc/i.fusion.hpf/high_pass_filter.py
curl https://raw.githubusercontent.com/NikosAlexandris/i.fusion.hpf/master/constants.py -o ~/.grass7/addons/etc/i.fusion.hpf/constants.py
curl https://raw.githubusercontent.com/NikosAlexandris/i.fusion.hpf/master/i.fusion.hpf -o ~/.grass7/addons/scripts/i.fusion.hpf
curl https://raw.githubusercontent.com/NikosAlexandris/i.fusion.hpf/master/i.fusion.hpf.html -o ~/.grass7/addons/docs/html/i.fusion.hpf.html

# set the appropriate permissions
chmod +x ~/.grass7/addons/scripts/i.fusion.hpf
