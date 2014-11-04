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
#% description: Level of modulating factor weighting the HPF image in the second pass to determine crispness
#% descriptions: mid;Mid modulating factor (0.35) for the 2nd pass;min;Minimum modulating factor (0.25) for the 2nd pass;max;Maximum modulating factor (0.5) for 2nd pass;
#% options: min,mid,max
#% required: no
#% answer: mid
#% guisection: High Pass Filter Options
#% multiple : no
#%end

import os
import atexit
import grass.script as grass
from grass.pygrass.modules.shortcuts import general as g
from grass.pygrass.modules.shortcuts import raster as r
from grass.pygrass.modules.shortcuts import vector as v
from grass.pygrass.modules.shortcuts import display as d
from grass.pygrass.modules import Module

from high_pass_filter import High_Pass_Filter

if "GISBASE" not in os.environ:
    print "You must be in GRASS GIS to run this program."
    sys.exit(1)


def run(cmd, **kwargs):
    grass.run_command(cmd, quiet=True, **kwargs)

#def cleanup():
#   grass.try_remove(tmp_hpf_matrix)
   
g.message("HPFA Replication for GRASS-GIS in Python", flags='i')


def main():
    global tmp_hpf_matrix
    
    pan = options['pan']
    msx = options['msx']
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
        g.message("Region's North:South (%s) and East:West (%s)"
                  "resolutions do not match!" % (nsr, ewr), flags='w')

    # 1. Compute Ratio ------------------------------------------------------
    g.message("Step 1: Determining ratio of low (Multi-Spectral)"
              "to high (Panchromatic) resolutions)", flags='v')

    # 2D image resolutions
    g.message("* Get resolution of input imagery (pan, msx)", flags='v')

# Write a function for the following? Integrate it in a Class?
    msxinfo = grass.parse_command("r.info", map=msx, flags='g')
    msxres = float(msxinfo['nsres'])

    paninfo = grass.parse_command("r.info", map=pan, flags='g')
    panres = float(paninfo['nsres'])

    # Custom ratio? Skip standard computation method
    if custom_ratio:
        global ratio
        ratio = float(custom_ratio)
        g.message('Using custom ratio, overriding standard method', flags='w')
    else:
        ratio = msxres / panres
        msg_ratio ='Low (%.3f) to high resolution (%.3f) ratio: %.1f'\
            % (msxres, panres, ratio)
        g.message(msg_ratio, flags='v')

    # 2nd Pass requested, yet Ratio < 5.5
    if second_pass and ratio < 5.5:
        g.message("Ratio < 5.5 -- Won't apply a 2nd pass!", flags='i')
        second_pass = bool(0)

    # 2. High Pass Filtering ------------------------------------------------
    g.message('2. High Pass Filtering the Panchromatic Image', flags='v')

    # Respect current region -- Change the resolution
    run('g.region', res=panres)
    g.message("> Region's resolution set to %f" % panres, flags='v')

    # Temporary files =======================================================
    tmpfile = grass.tempfile()
    tmp = grass.basename(tmpfile)

    tmp_pan_hpf = "%s_pan_hpf" % tmp  # HPF image
    tmp_msx_blnr = "%s_msx_blnr" % tmp  # Upsamples MSx
    tmp_msx_hpf = "%s_msx_hpf" % tmp  # Fused image

    tmp_hpf_matrix = grass.tempfile()  # ASCII filter

    if second_pass and ratio > 5.5:  # 2nd Pass?
        tmp_hpf_matrix_2 = grass.tempfile()  # 2nd Pass ASCII filter
        tmp_pan_hpf_2 = "%s_pan_hpf_2" % tmp
    # ============================================= end of Temporary files ==

    # Construct Filter
    hpf = High_Pass_Filter(ratio, center, modulation, False, None)
    hpf_matrix = hpf.filter
    modulator = hpf.modulator
#    grass.try_remove(tmp_hpf_matrix)
    asciif = open(tmp_hpf_matrix, 'w')
    asciif.write(hpf_matrix)
    asciif.close()

    # 2nd Pass?
    if second_pass and ratio > 5.5:
        hpf_2 = High_Pass_Filter(ratio, center, None, True, modulation2)
        hpf_matrix_2 = hpf_2.filter
        modulator_2 = hpf_2.modulator_2
#        grass.try_remove(tmp_hpf_matrix)
        asciif = open(tmp_hpf_matrix_2, 'w')
        asciif.write(hpf_matrix_2)
        asciif.close()

    # Filtering
    run('r.mfilter',
        input=pan,
        filter=tmp_hpf_matrix,
        output=tmp_pan_hpf,
        title="High Pass Filtered Panchromatic image",
        overwrite=True)

    # 2nd Pass
    if second_pass and ratio > 5.5:
        run('r.mfilter',
            input=tmp_pan_hpf,
            filter=tmp_hpf_matrix_2,
            output=tmp_pan_hpf_2,
            title="2-High-Pass Filtered Panchromatic Image",
            overwrite=True)

    # 3. Upsampling low resolution image ------------------------------------

    g.message("3. Resampling MSx image to the higher resolution")
    g.message("3 Upsampling the low resolution image ($MSX) to the higher"
              "resolution ($PAN_RESOLUTION)",
              flags='v')

    # resample -- named "linear" in G7
    run('r.resamp.interp',
        method='bilinear',
        input=msx,
        output=tmp_msx_blnr,
        overwrite=True)

    # 4. Check Terminology again! -----------------------------------------

    g.message("4. Adding weighted High-Pass-Filtered image (HPFi) to the"
              "upsampled MSx image")

    ### Weighting formula: W = ( SD(MS) / SD(HPF) x M )
        # where:
        # SD(MS), SD(HPF) are the Standard Deviations of the MS and HPF images
        # M is a Modulation Factor

    # Compute Weighting(s)
    g.message("* Weighting = StdDev (MSX) / StdDev (HPF) * Modulating Factor",
              flags='v')

    # StdDev of Multi-Spectral Image(s)
    msx_uni = grass.parse_command("r.univar", map=msx, flags='g')
    msx_sd = float(msx_uni['stddev'])
    g.message("* StdDev of Multi-Spectral input: %s" % msx_sd,
              flags='v')

    # StdDev of HPF Image
    hpf_uni = grass.parse_command("r.univar", map=tmp_pan_hpf, flags='g')
    hpf_sd = float(hpf_uni['stddev'])
    g.message("* StdDev of Multi-Spectral input: %s" % hpf_sd,
              flags='v')

    # Modulating factor
    g.message("* Modulating Factor set to: %f" % modulator,
              flags='v')

    weighting = msx_sd / hpf_sd * modulator
    g.message("%f = %f / %f * %f" % (weighting, msx_sd, hpf_sd, modulator),
              flags='v')

    g.message("* Weighting = %s" % weighting,
              flags='v')

    # 2nd Pass
    if second_pass and ratio > 5.5:
        print "Second Pass..."

        # StdDev of HPF Image #2
        hpf_2_uni = grass.parse_command("r.univar", map=tmp_pan_hpf_2, flags='g')
        hpf_2_sd = float(hpf_2_uni['stddev'])
        g.message("* StdDev of 2nd HPF image: $HPF_StdDev_2",
                  flags='v')

        # Modulating factor #2
        g.message("* 2nd Pass Modulating Factor set to: %f" % modulator_2,
                  flags='v')

        weighting_2 = msx_sd / hpf_2_sd * modulator_2
        g.message("%f = %f / %f * %f" % (weighting_2, msx_sd, hpf_2_sd,
                                         modulator_2),
                  flags='v')
        g.message("* 2nd Pass Weighting = %s" % weighting_2,
                  flags='v')

    # Add weighted HPF image to upsampled Multi-Spectral band
    g.message("4 Adding weighted HPF image to the upsampled image", flags='v')

    fusion = "%s = %s + %s * %f" \
        % (tmp_msx_hpf, tmp_msx_blnr, tmp_pan_hpf, weighting)

    grass.mapcalc(fusion)

    g.message("HPF image added to the bilinearly upsampled MSX image.",
              flags='v')

    # history
    cmd_history = "Weigthing applied: %s / %s * %s" \
        % (msx_sd, hpf_sd, modulator)
    run("r.support", map=tmp_msx_hpf, history=cmd_history)

    # 2nd Pass
    if second_pass and ratio > 5.5:

        g.message("2nd Pass: adding small-kernel-based HPF weighted image"
                  "back to fused image", flags='i')

        add_back = "%s = %s + %s * %f" \
            % (tmp_msx_hpf, tmp_msx_hpf, tmp_pan_hpf_2, weighting_2)

        grass.mapcalc(add_back)

        g.message("2nd pass performed successfuly!", flags='v')

#        run("g.rename",
#            rast=(tmp_msx_hpf,("%s_%s" % msx)))

        # 2nd Pass history entry
        cmd_history_2 = "2nd Pass Weigthing: %s / %s * %s" \
            % (msx_sd, hpf_2_sd, modulator_2)
        run("r.support", map=tmp_msx_hpf,
            history=cmd_history_2)


# ---------------------------------------------------------------------------
# 5. Stretching linearly the HPF-Sharpened image(s) to match the Mean and
#    Standard Deviation of the input Multi-Sectral image(s)
# ----------------------------------------------------------------------------

    if histogram_match:
        # adapt output StdDev and Mean to the input(ted) ones
        g.message("Linear Histogram Matching", flags='i')
        g.message("Linearly matching histogram of Pansharpened image (%s)"
                  "to the one of the original MSx image (%s)"
                  "[Not Implemented!]" % (tmp_msx_hpf, msx), flags='v')

        tmp_msx_lhm = "%s_msx_lhm" % tmp

        #    input=${Temporary_MSHPF} \
        #    output=${GIS_OPT_MSX}_${GIS_OPT_OUTPUTPREFIX} \

#        lhm = "%s = (%s - %f) / %f * %f + %f" \
#            % (tmp_msx_lhm,
#               tmp_msx_hpf, msx_hpf_avg,
#               msx_hpf_sd, ref_sd, ref_avg)
#        grass.mapcalc(lhm, overwrite=True)
#
#        run("g.rename", rast=(tmp_msx_hpf, "%s_%s" % (msx, outputprefix)))
    else:
        pass

    # visualising output
    g.message("Note, It is probably required to rebalance colors"
              "(using i.colors.enhance) before working on RGB composites.",
              flags='i')

if __name__ == "__main__":
    options, flags = grass.parser()
#    atexit.register(cleanup)
    main()
