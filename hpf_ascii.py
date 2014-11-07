# -*- coding: utf-8 -*-
"""
@author: nik | Created on Wed Nov  5 00:48:58 2014
"""


def hpf_ascii(ratio, center, modulation, second_pass, modulation2, tmpfile):
    f = High_Pass_Filter(ratio, center, modulation, second_pass, modulation2)
    asciif = open(tmpfile, 'w')
    asciif.write(f.filter)
    asciif.close()

#        # Construct Filter
#        hpf = High_Pass_Filter(ratio, center, modulation, False, None)
#        hpf_matrix = hpf.filter
#        g.message("Filter Properties: size: %s, center: %s"
#                  % (hpf.size, center), flags='v')
#        modulator = hpf.modulator
#    #    grass.try_remove(tmp_hpf_matrix)
#        asciif = open(tmp_hpf_matrix, 'w')
#        asciif.write(hpf_matrix)
#        asciif.close()
#
#        # 2nd Pass?
#        if second_pass and ratio > 5.5:
#            hpf_2 = High_Pass_Filter(ratio, center, None, True, modulation2)
#            hpf_matrix_2 = hpf_2.filter
#            g.message("Filter Properties: size: %s, center: %s"
#                      % (hpf.size, center), flags='v')
#            modulator_2 = hpf_2.modulator_2
#
#    #        grass.try_remove(tmp_hpf_matrix)
#            asciif = open(tmp_hpf_matrix_2, 'w')
#            asciif.write(hpf_matrix_2)
#            asciif.close()