#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
@author: Nikos Alexandris | October 2014
"""

"""
Constants for the HPFA Image Fusion Technique:
Kernel Size, Center Value, Modulation Factor (all depend on Resolution Ratio).

Source: "Optimizing the High-Pass Filter Addition Technique for Image Fusion",
Ute G. Gangkofner, Pushkar S. Pradhan, and Derrold W. Holcomb (2008).
"""

RATIO_RANGES = (
    (1, 2.5),
    (2.5, 3.5),
    (3.5, 5.5),
    (5.5, 7.5),
    (7.5, 9.5),
    (9.5, float('inf')))

KERNEL_SIZES = (5, 7, 9, 11, 13, 15)

MATRIX_PROPERTIES = zip(RATIO_RANGES, KERNEL_SIZES)

# Low level center cell values are: (kernel size)^2 - 1
# What about the rest?
CENTER_CELL = {
    'Low': [24, 48, 80, 120, 168, 336],
    'Mid': [28, 56, 96, 150, 210, 392],
    'High': [32, 64, 106, 180, 252, 448]}

MODULATOR = {
    'Min': [0.20, 0.35, 0.35, 0.50, 0.65, 1.00],
    'Mid': [0.25, 0.50, 0.50, 0.65, 1.00, 1.35],
    'Max': [0.30, 0.65, 0.65, 1.00, 1.40, 2.00]}

MODULATOR_2 = {'Min': 0.25, 'Mid': 0.35, 'Max': 0.50}
