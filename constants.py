#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""Constants for HPFA Image Fusion Technique:
Kernel Size, Center Value, Modulation Factor
(all depend on Resolution Ratio)"""

RATIO_RANGES = (
    (1, 2.5),
    (2.5, 3.5),
    (3.5, 5.5),
    (5.5, 7.5),
    (7.5, 9.5),
    (9.5, float('inf'))
    )

KERNEL_SIZES = (5, 7, 9, 11, 13, 15)

MATRIX_PROPERTIES = zip(RATIO_RANGES, KERNEL_SIZES)

CENTER_CELL = {
    'Default': [24, 48, 80, 120, 168, 336],
    'Mid': [28, 56, 96, 150, 210, 392],
    'High': [32, 64, 106, 180, 252, 448],
    }

CENTER_CELL_2 = {  # values for 2nd pass
    'Default': 24,
    'Mid': 28,
    'High': 32
    }

MODULATOR = {
    'Min': [0.20, 0.35, 0.35, 0.50, 0.65, 1.00],
    'Default': [0.25, 0.50, 0.50, 0.65, 1.00, 1.35],
    'Max': [0.30, 0.65, 0.65, 1.00, 1.40, 2.00]
    }

MODULATOR_2 = {
    'Min 2': 0.25,
    'Default 2': 0.35,
    'Max 2': 0.50
    }
