MODULE_TOPDIR = ../..

PGM = i.fusion.hpf

ETCFILES = high_pass_filter constants

include $(MODULE_TOPDIR)/include/Make/Script.make
include $(MODULE_TOPDIR)/include/Make/Python.make

default: script
