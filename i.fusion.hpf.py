# -*- coding: utf-8 -*-
"""
@author: Nikos Alexandris | Created on Fri Oct 31 20:03:06 2014
"""

############################################################################
#
# MODULE:       i.fusion.hpf
#
# AUTHOR(S):    Nikos Alexandris <nik@nikosalexandris.net>
#               Based on the bash shell script i.fusion.hpf
#
#
# PURPOSE:      HPF Resolution Merge -- Algorithm Replication in GRASS GIS
#
#               Module to combine high-resolution panchromatic data with
#               lower resolution multispectral data, resulting in an output
#               with both excellent detail and a realistic representation of
#               original multispectral scene colors.
#
# 				 The process involves a convolution using a High Pass Filter
# 				 (HPF) on the high resolution data, then combining this with
# 				 the lower resolution multispectral data.
#
#               Optionally, a linear histogram matching technique is performed
#               in a  way that matches the resulting Pan-Sharpened imaged to
#               them statistical mean and standard deviation of the original
#               multi-spectral image. Credits for how to implement this
#               technique go to GRASS-GIS developer Moritz Lennert.
#
#               Source: "Optimizing the High-Pass Filter Addition Technique for
#               Image Fusion", Ute G. Gangkofner, Pushkar S. Pradhan,
#               and Derrold W. Holcomb (2008)
#
# COPYRIGHT:    (C) 2013 by the GRASS Development Team
#
#               This program is free software under the GNU General Public
#               License (>=v2). Read the file COPYING that comes with GRASS
#               for details.
#
#############################################################################

#%Module
#%  description: Fuses a High-Resolution Panchromatic with its corresponding Low Resolution Multi-Spectral image based on the High-Pass Filter Addition technique
#%  keywords: imagery, fusion, HPF, HPFA
#%End
#%flag
#%  key: l
#%  description: Linearly match histograms of the HPF Pan-sharpened output(s) to the Multi-Spectral input(s)
#%end
#%flag
#%  key: 2
#%  description: 2-Pass Processing (recommended) for large Resolution Ratio (>=5.5)
#%end
#%option
#% key: pan
#% type: string
#% gisprompt: old,double,raster
#% description: High resolution panchromatic image
#% required : yes
#%end
#%option
#% key: msx
#% type: string
#% gisprompt: old,double,raster
#% description: Low resolution multi-spectral image(s)
#% required: yes
#% multiple: yes
#%end
#%option
#% key: outputprefix
#% type: string
#% gisprompt: old,double,raster
#% description: Prefix for the Pan-Sharpened Multi-Spectral image(s)
#% required: yes
#% answer: hpf
#%end
#%option
#% key: ratio
#% type: double
#% description: Custom defined ratio to override standard calculation 
#% options: 1.0-10.0
#% guisection: High Pass Filter Options
#% required: no
#%end
#%option
#% key: center
#% type: string
#% description: Center cell value of the High-Pass-Filter 
#% descriptions: Level of center value (low, mid, high)
#% options: low,mid,high
#% required: no
#% answer: low
#% guisection: High Pass Filter Options
#% multiple : no
#%end
#%option
#% key: center2
#% type: string
#% description: Center cell value for the second High-Pass-Filter 
#% descriptions: Level of center value for second pass
#% options: low,mid,high
#% required: no
#% answer: low
#% guisection: High Pass Filter Options
#% multiple : no
#%end
#%option
#% key: modulation
#% type: string
#% description: Level of modulating factor weighting the HPF image to determine crispness
#% descriptions: Levels of modulating factors
#% options: min,mid,max
#% required: no
#% answer: mid
#% guisection: High Pass Filter Options
#% multiple : no
#%end
#%option
#% key: modulation2
#% type: string
#% description: Level of modulating factor weighting the second HPF image to determine crispness
#% descriptions: mid;Mid: 0.35;min;Minimum: 0.25;max;Maximum: 0.5;
#% options: min,mid,max
#% required: no
#% answer: mid
#% guisection: High Pass Filter Options
#% multiple : no
#%end


# required librairies -------------------------------------------------------

import os
import sys
#import atexit

import grass.script as grass
#from grass.pygrass.gis import Mapset
from grass.pygrass.modules.shortcuts import general as g
#from grass.pygrass.modules.shortcuts import raster as r
#from grass.pygrass.modules.shortcuts import vector as v
#from grass.pygrass.modules.shortcuts import display as d
#from grass.pygrass.modules import Module
from grass.pygrass.raster.abstract import Info

from high_pass_filter import High_Pass_Filter

if "GISBASE" not in os.environ:
    print "You must be in GRASS GIS to run this program."
    sys.exit(1)


# helper functions ----------------------------------------------------------

def run(cmd, **kwargs):
    """ """
    grass.run_command(cmd, quiet=True, **kwargs)


def hpf_weight(lo_sd, hpf_sd, mod, pss):
    """Function returning an appropriate weighting value for the
    High Pass Filtered image. The required inputs are:
    - StdDev of Low resolution image
    - StdDev of High Pass Filtered image
    - Appropriate Modulating Factor determining image crispness
    - Number of Pass (1st or 2nd)"""
    if pss == 1:
        wgt = lo_sd / hpf_sd * mod  # mod: modulator
        msg = "   >> Weighting = %.2f / %.2f * %.2f = %.2f" % \
            (lo_sd, hpf_sd, mod, wgt)
        g.message(msg, flags='v')

    if pss == 2:
        wgt = lo_sd / hpf_sd * mod  # mod: modulator
        msg = "   >> 2nd Pass Weighting = %.3f / %.3f * %.3f = %.3f" % \
            (lo_sd, hpf_sd, mod, wgt)
        g.message(msg, flags='v')

    return wgt


def export_hpf(center, filter, tmpfile, pss):
    """Function exporting High Pass Filter as a temporary ASCII file"""
    if pss == 1:
        global modulator
        modulator = filter.modulator
#        msg = "   > Filter Properties: size: %s, center: %s" % \
#            (filter.size, center)
        msg_ps2 = ''

    elif pss == 2:
        global modulator_2
        modulator_2 = filter.modulator_2
#        msg = "   > 2nd Pass Filter Properties: size: %s, center: %s" % \
#            (filter.size, center)
        msg_ps2 = '2nd Pass '

    # structure informative message
    msg = "   > %sFilter Properties: size: %s, center: %s" % \
        (msg_ps2, filter.size, center)
    g.message(msg, flags='v')

    # open, write and close file
    asciif = open(tmpfile, 'w')
    asciif.write(filter.filter)
    asciif.close()


#def cleanup():
#   grass.try_remove(tmp_hpf_matrix)


# main program --------------------------------------------------------------

def main():
    global tmp_hpf_matrix

    pan = options['pan']
    msxlst = options['msx'].split(',')
    outputprefix = options['outputprefix']
    custom_ratio = options['ratio']
    center = options['center']
    center2 = options['center2']
    modulation = options['modulation']
    modulation2 = options['modulation2']
    histogram_match = flags['l']
    second_pass = flags['2']

    # Check & warn user about "ns == ew" resolution of current region
    region = grass.region()
    nsr = region['nsres']
    ewr = region['ewres']

    if nsr != ewr:
        g.message(">>> Region's North:South (%s) and East:West (%s)"
                  "resolutions do not match!" % (nsr, ewr), flags='w')

    mapset = grass.gisenv()['MAPSET']  # Current Mapset?

    imglst = [pan]
    imglst.extend(msxlst)  # List of input imagery

    # Retrieving Image Info
    images = {}
    for img in imglst:
        images[img] = Info(img, mapset)
        images[img].read()

    panres = images[pan].nsres  # Panchromatic resolution

    # Respect region extent -- Change region resolution
    run('g.region', res=panres)
    g.message("|  Region's resolution set to %f" % panres, flags='v')

    # Loop over Multi-Spectral images
    for msx in msxlst:

        # Inform
        g.message("\nProcessing image: %s" % msx, flags='v')

        # Tracking command history -- Why don't do this all r.* modules?
        cmd_history = ''

        # -------------------------------------------------------------------
        # 1. Compute Ratio
        # -------------------------------------------------------------------

        g.message("\n|1 Determining ratio of low to high resolution",
                  flags='v')

        # Custom Ratio? Skip standard computation method.
        if custom_ratio:
            global ratio
            ratio = float(custom_ratio)
            g.message('Using custom ratio, overriding standard method!',
                      flags='w')

        # Multi-Spectral resolution(s), multiple
        else:
            # Image resolutions
            g.message("   > Retrieving image resolutions", flags='v')

            msxres = images[msx].nsres
            ratio = msxres / panres
            msg_ratio = '   >> Low (%.3f) to high resolution (%.3f) ratio: %.1f'\
                % (msxres, panres, ratio)
            g.message(msg_ratio, flags='v')

        # 2nd Pass requested, yet Ratio < 5.5
        if second_pass and ratio < 5.5:
            g.message("   >>> Ratio < 5.5 -- WON'T perform 2nd pass! <<<",
                      flags='i')
            second_pass = bool(0)

        # -------------------------------------------------------------------
        # 2. High Pass Filtering
        # -------------------------------------------------------------------

        g.message('\n|2 High Pass Filtering the Panchromatic Image', flags='v')

        # Temporary files ===================================================
        tmpfile = grass.tempfile()  # a Temporary file
        tmp = grass.basename(tmpfile)  # use its basename

        tmp_pan_hpf = "%s_pan_hpf" % tmp  # HPF image
        tmp_msx_blnr = "%s_msx_blnr" % tmp  # Upsamples MSx
        tmp_msx_hpf = "%s_msx_hpf" % tmp  # Fused image

        tmp_hpf_matrix = grass.tempfile()  # ASCII filter

        if second_pass and ratio > 5.5:  # 2nd Pass?
            tmp_hpf_matrix_2 = grass.tempfile()  # 2nd Pass ASCII filter
            tmp_pan_hpf_2 = "%s_pan_hpf_2" % tmp
        # ========================================== end of Temporary files #

        # Construct Filter
        hpf = High_Pass_Filter(ratio, center, modulation, False, None)
# ---------------------------------------------------------------------------
#        g.message("   > Filter Properties: size: %s, center: %s"
#                  % (hpf.size, center), flags='v')
#        modulator = hpf.modulator
#        asciif = open(tmp_hpf_matrix, 'w')
#        asciif.write(hpf.filter)
#        asciif.close()
# ------------------------------------------------ replaced by export_hpf() -
        export_hpf(center, hpf, tmp_hpf_matrix, 1)

        # Construct 2nd Filter
        if second_pass and ratio > 5.5:
            hpf_2 = High_Pass_Filter(ratio, center2, None, True, modulation2)
# ---------------------------------------------------------------------------
#            g.message("   > 2nd Pass Filter Properties: size: %s, center: %s"
#                      % (hpf.size, center2), flags='v')
#            modulator_2 = hpf_2.modulator_2
#            asciif = open(tmp_hpf_matrix_2, 'w')
#            asciif.write(hpf_2.filter)
#            asciif.close()
# ------------------------------------------------ replaced by export_hpf() -
            export_hpf(center2, hpf_2, tmp_hpf_matrix_2, 2)

        # Filtering
        run('r.mfilter', input=pan, filter=tmp_hpf_matrix,
            output=tmp_pan_hpf,
            title="High Pass Filtered Panchromatic image",
            overwrite=True)

        # 2nd Filtering
        if second_pass and ratio > 5.5:
            run('r.mfilter', input=pan, filter=tmp_hpf_matrix_2,
                output=tmp_pan_hpf_2,
                title="2-High-Pass Filtered Panchromatic Image",
                overwrite=True)

        # -------------------------------------------------------------------
        # 3. Upsampling low resolution image
        # -------------------------------------------------------------------

        g.message("\n|3 Upsampling (bilinearly) low resolution image",
                  flags='v')

        # resample -- named "linear" in G7
        run('r.resamp.interp',
            method='bilinear', input=msx, output=tmp_msx_blnr, overwrite=True)

        # -------------------------------------------------------------------        
        # 4. Weighting the High Pass Filtered image(s)
        # -------------------------------------------------------------------

        g.message("\n|4 Weighting the High-Pass-Filtered image (HPFi)")

        # Compute Weighting(s)
        msg_w = '   > Weighting = StdDev(MSx) / StdDev(HPFi) * Modulating Factor'
        g.message(msg_w, flags='v')

        # StdDev of Multi-Spectral Image(s)
        msx_uni = grass.parse_command("r.univar", map=msx, flags='g')
        msx_avg = float(msx_uni['mean'])
        msx_sd = float(msx_uni['stddev'])

        g.message("   >> StdDev of <%s>: %s" % (msx, msx_sd), flags='v')

        # StdDev of HPF Image
        hpf_uni = grass.parse_command("r.univar", map=tmp_pan_hpf, flags='g')
        hpf_sd = float(hpf_uni['stddev'])

        g.message("   >> StdDev of HPFi: %s"
                  % (hpf_sd), flags='v')

        # Modulating factor
        g.message("   >> Modulating Factor: %f" % modulator,
                  flags='v')


        # weighting HPFi
        weighting = hpf_weight(msx_sd, hpf_sd, modulator, 1)

        # -------------------------------------------------------------------
        # 5. Adding weighted HPF image to upsampled Multi-Spectral band
        # -------------------------------------------------------------------

        g.message("\n|5 Adding weighted HPFi to upsampled image",
                  flags='v')

        fusion = "%s = %s + %s * %f" \
            % (tmp_msx_hpf, tmp_msx_blnr, tmp_pan_hpf, weighting)

        grass.mapcalc(fusion)

        # history
        cmd_history += "Weigthing applied: %s / %s * %s | " \
            % (msx_sd, hpf_sd, modulator)

        # 2nd Pass
        if second_pass and ratio > 5.5:
            
            g.message("\n|4+ Weighting 2nd HPFi")

            # StdDev of HPF Image #2
            hpf_2_uni = grass.parse_command("r.univar", map=tmp_pan_hpf_2,
                                            flags='g')
            hpf_2_sd = float(hpf_2_uni['stddev'])
#            hpf_avg = float(hpf_uni['mean'])

            g.message("   >> StdDev of 2nd HPFi: %.3f" % hpf_2_sd,
                      flags='v')

            # Modulating factor #2
            g.message("   >> 2nd Pass Modulating Factor: %f"
                      % modulator_2, flags='v')

            # 2nd Pass, weighting already weighted HPFi
            weighting_2 = hpf_weight(msx_sd, hpf_2_sd, modulator_2, 2)

            g.message("\n|5+ Adding small-kernel-based weighted 2nd HPFi "
                      "back to fused image", flags='v')

            add_back = "%s = %s + %s * %f" \
                % (tmp_msx_hpf, tmp_msx_hpf, tmp_pan_hpf_2, weighting_2)

            grass.mapcalc(add_back)

    #        run("g.rename",
    #            rast=(tmp_msx_hpf,("%s_%s" % msx)))

            # 2nd Pass history entry
            cmd_history += "2nd Pass Weighting: %s / %s * %s | " \
                % (msx_sd, hpf_2_sd, modulator_2)

        # -------------------------------------------------------------------
        # 6. Stretching linearly the HPF-Sharpened image(s) to match the Mean
        #     and Standard Deviation of the input Multi-Sectral image(s)
        # -------------------------------------------------------------------

        if histogram_match:

            # adapt output StdDev and Mean to the input(ted) ones
            g.message("\n|  Matching histogram of Pansharpened image"
                      "to %s"
                      % (msx), flags='v')

            # Collect stats for linear histogram matching
            msx_hpf_uni = grass.parse_command("r.univar", map=tmp_msx_hpf,
                                              flags='g')
            msx_hpf_avg = float(msx_hpf_uni['mean'])
            msx_hpf_sd = float(msx_hpf_uni['stddev'])


#            tmp_msx_lhm = "%s_msx_lhm" % tmp

            #    input=${Temporary_MSHPF} \
            #    output=${GIS_OPT_MSX}_${GIS_OPT_OUTPUTPREFIX} \

            lhm = "%s = (%s - %f) / %f * %f + %f" \
                % (tmp_msx_hpf,
                   tmp_msx_hpf, msx_hpf_avg,
                   msx_hpf_sd, msx_sd, msx_avg)
            grass.mapcalc(lhm, quiet=True, overwrite=True)
            cmd_history += "Linear Histogram Matching: %s |" % lhm 
        else:
            pass

        # Rename end product
        run("r.support", map=tmp_msx_hpf, history=cmd_history)
        run("g.rename", rast=(tmp_msx_hpf, "%s_%s" % (msx, outputprefix)))

    # Need to clean up!

    # visualising output
    g.message("\n>>> Note, It is probably required to rebalance colors "
              "(e.g. via i.colors.enhance) before working on RGB composites.",
              flags='i')

if __name__ == "__main__":
    options, flags = grass.parser()
#    atexit.register(cleanup)
    main()
