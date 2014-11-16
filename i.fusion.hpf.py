#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 MODULE:       i.fusion.hpf

 AUTHOR(S):    Nikos Alexandris <nik@nikosalexandris.net>
               Converted from a bash shell script | Trikala, Nov. 2014


 PURPOSE:      HPF Resolution Merge -- Algorithm Replication in GRASS GIS

               Module to combine high-resolution panchromatic data with
               lower resolution multispectral data, resulting in an output
               with both excellent detail and a realistic representation of
               original multispectral scene colors.

               The process involves a convolution using a High Pass Filter
               (HPF) on the high resolution data, then combining this with
               the lower resolution multispectral data.

               Optionally, a linear histogram matching technique is performed
               in a  way that matches the resulting Pan-Sharpened imaged to
               them statistical mean and standard deviation of the original
               multi-spectral image. Credits for how to implement this
               technique go to GRASS-GIS developer Moritz Lennert.


               Source: "Optimizing the High-Pass Filter Addition Technique for
               Image Fusion", Ute G. Gangkofner, Pushkar S. Pradhan,
               and Derrold W. Holcomb (2008)

               Figure 1:

+-----------------------------------------------------------------------------+
|  Pan Img ->  High Pass Filter  ->  HP Img                                   |
|                                       |                                     |
|                                       v                                     |
|  MSx Img ->  Weighting Factors ->  Weighted HP Img                          |
|        |                              |                                     |
|        |                              v                                     |
|        +------------------------>  Addition to MSx Img  =>  Fused MSx Image |
+-----------------------------------------------------------------------------+

 COPYRIGHT:    (C) 2013 by the GRASS Development Team

               This program is free software under the GNU General Public
               License (>=v2). Read the file COPYING that comes with GRASS
               for details.
"""

#%Module
#%  description: Fusing high resolution Panchromatic and low resolution Multi-Spectral data based on the High-Pass Filter Addition technique (Gangkofner, 2008)
#%  keywords: imagery, fusion, HPF, HPFA
#%End

#%flag
#%  key: l
#%  description: Linearly match histogram of Pan-sharpened output to Multi-Spectral input
#%end

#%flag
#%  key: 2
#%  description: 2-Pass Processing (recommended) for large resolution ratio (>=5.5)
#%end

#%flag
#%  key: c
#%  description: Match color table of Pan-Sharpened output to Multi-Spectral input
#%end

#%option G_OPT_R_INPUT
#% key: pan
#% key_desc: filename
#% description: High resolution Panchromatic image
#% required : yes
#%end

#%option G_OPT_R_INPUTS
#% key: msx
#% key_desc: filename(s)
#% description: Low resolution Multi-Spectral image(s)
#% required: yes
#% multiple: yes
#%end

#%option G_OPT_R_BASENAME_OUTPUT
#% key: outputsuffix
#% key_desc: suffix string
#% type: string
#% label: Suffix for output image(s)
#% description: Names of Pan-Sharpened image(s) will end with this suffix
#% required: yes
#% answer: hpf
#%end

#%option
#% key: ratio
#% key_desc: rational number
#% type: double
#% label: Custom ratio
#% description: Custom ratio overriding standard calculation
#% options: 1.0-10.0
#% guisection: High Pass Filter
#% required: no
#%end

#%option
#% key: center
#% key_desc: string
#% type: string
#% label: Center cell value
#% description: Center cell value of the High-Pass-Filter
#% descriptions: Level of center value (low, mid, high)
#% options: low,mid,high
#% required: no
#% answer: low
#% guisection: High Pass Filter
#% multiple : no
#%end

#%option
#% key: center2
#% key_desc: string
#% type: string
#% label: 2nd Pass center cell value
#% description: Center cell value for the second High-Pass-Filter (use -2 flag)
#% descriptions: Level of center value for second pass
#% options: low,mid,high
#% required: no
#% answer: low
#% guisection: High Pass Filter
#% multiple : no
#%end

#%option
#% key: modulation
#% key_desc: string
#% type: string
#% label: Modulation level
#% description: Modulation level weighting the HPF image determining crispness
#% descriptions: Levels of modulating factors
#% options: min,mid,max
#% required: no
#% answer: mid
#% guisection: Crispness
#% multiple : no
#%end

#%option
#% key: modulation2
#% key_desc: string
#% type: string
#% label: 2nd Pass modulation level (use -2 flag)
#% description: Modulation level weighting the second HPF image determining crispness (use -2 flag)
#% descriptions: mid;Mid: 0.35;min;Minimum: 0.25;max;Maximum: 0.5;
#% options: min,mid,max
#% required: no
#% answer: mid
#% guisection: Crispness
#% multiple : no
#%end


# required librairies -------------------------------------------------------

import os
import sys
sys.path.insert(1, os.path.join(os.path.dirname(sys.path[0]),
                                'etc', 'i.fusion.hpf'))
import atexit

import grass.script as grass
from grass.pygrass.modules.shortcuts import general as g
from grass.pygrass.raster.abstract import Info

from high_pass_filter import High_Pass_Filter

if "GISBASE" not in os.environ:
    print "You must be in GRASS GIS to run this program."
    sys.exit(1)


# globals -------------------------------------------------------------------
ratio = float()
tmp = ''
tmp_hpf_matrix = ''
modulator = float()
modulator_2 = float()


# helper functions ----------------------------------------------------------
def cleanup():
    """Clean up temporary maps"""
    grass.run_command('g.remove', flags='f', type="rast",
                      pattern='tmp.%s*' % os.getpid(), quiet=True)


def run(cmd, **kwargs):
    """Pass quiet flag to grass commands"""
    grass.run_command(cmd, quiet=True, **kwargs)


def avg(img):
    """Retrieving Average (or name it: Mean) of input image"""
    uni = grass.parse_command("r.univar", map=img, flags='g')
    avg = float(uni['mean'])
    return avg


def stddev(img):
    """Retrieving Standard Deviation of input image"""
    uni = grass.parse_command("r.univar", map=img, flags='g')
    sd = float(uni['stddev'])
    return sd


def hpf_weight(lo_sd, hpf_sd, mod, pss):
    """Returning an appropriate weighting value for the
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


def hpf_ascii(center, filter, tmpfile, pss):
    """Exporting a High Pass Filter in a temporary ASCII file"""
    if pss == 1:
        global modulator
        modulator = filter.modulator
        msg_ps2 = ''

    elif pss == 2:
        global modulator_2
        modulator_2 = filter.modulator_2
        msg_ps2 = '2nd Pass '

    # structure informative message
    msg = "   > %sFilter Properties: size: %s, center: %s" % \
        (msg_ps2, filter.size, center)
    g.message(msg, flags='v')

    # open, write and close file
    asciif = open(tmpfile, 'w')
    asciif.write(filter.filter)
    asciif.close()


# main program

def main():

    global tmp_hpf_matrix

    pan = options['pan']
    msxlst = options['msx'].split(',')
    outputsuffix = options['outputsuffix']
    custom_ratio = options['ratio']
    center = options['center']
    center2 = options['center2']
    modulation = options['modulation']
    modulation2 = options['modulation2']
    histogram_match = flags['l']
    second_pass = flags['2']
    color_match = flags['c']

#    # Check & warn user about "ns == ew" resolution of current region ======
#    region = grass.region()
#    nsr = region['nsres']
#    ewr = region['ewres']
#
#    if nsr != ewr:
#        g.message(">>> Region's North:South (%s) and East:West (%s)"
#                  "resolutions do not match!" % (nsr, ewr), flags='w')
#    # ======================================================================

    mapset = grass.gisenv()['MAPSET']  # Current Mapset?

    imglst = [pan]
    imglst.extend(msxlst)  # List of input imagery

    images = {}
    for img in imglst:  # Retrieving Image Info
        images[img] = Info(img, mapset)
        images[img].read()

    panres = images[pan].nsres  # Panchromatic resolution

    grass.use_temp_region()  # to safely modify the region
    run('g.region', res=panres)  # Respect extent, change resolution
    g.message("|! Region's resolution matched to Pan's (%f)" % panres)

    # -----------------------------------------------------------------------
    # Loop Algorithm over Multi-Spectral images ////////////////////////////
    # -----------------------------------------------------------------------
    
    for msx in msxlst:

        global tmp

        # Inform
        g.message("\nProcessing image: %s" % msx)

        # Tracking command history -- Why don't do this all r.* modules?
        cmd_history = ''

        # -------------------------------------------------------------------
        # 1. Compute Ratio
        # -------------------------------------------------------------------

        g.message("\n|1 Determining ratio of low to high resolution")

        # Custom Ratio? Skip standard computation method.
        if custom_ratio:
            global ratio
            ratio = float(custom_ratio)
            g.message('Using custom ratio, overriding standard method!',
                      flags='w')

        # Multi-Spectral resolution(s), multiple
        else:
            # Image resolutions
            g.message("   > Retrieving image resolutions")

            msxres = images[msx].nsres
            if panres == msxres:
                grass.fatal(_("The Panchromatic's image resolution (%s) "
                              "equals to the Multi-Spectral's one (%s). "
                              "Obviously, something isn't right! "
                              "Please check your input images."
                              % (panres, msxres)))
            ratio = msxres / panres
            msg_ratio = '   >> Low (%.3f) to high resolution (%.3f) ratio: %.1f'\
                % (msxres, panres, ratio)
            g.message(msg_ratio)

        # 2nd Pass requested, yet Ratio < 5.5
        if second_pass and ratio < 5.5:
            g.message("   >>> Ratio < 5.5 -- WON'T perform 2nd pass! "
                      "Use <ratio> option to override.",
                      flags='i')
            second_pass = bool(0)

        # -------------------------------------------------------------------
        # 2. High Pass Filtering
        # -------------------------------------------------------------------

        g.message('\n|2 High Pass Filtering the Panchromatic Image')

        # ========================================== Temporary files ========
        tmpfile = grass.tempfile()  # Temporary file - replace with os.getpid?
        tmp = "tmp." + grass.basename(tmpfile)  # use its basenam
        tmp_pan_hpf = "%s_pan_hpf" % tmp  # HPF image
        tmp_msx_blnr = "%s_msx_blnr" % tmp  # Upsampled MSx
        tmp_msx_hpf = "%s_msx_hpf" % tmp  # Fused image

        tmp_hpf_matrix = grass.tempfile()  # ASCII filter

        if second_pass and ratio > 5.5:  # 2nd Pass?
            tmp_pan_hpf_2 = "%s_pan_hpf_2" % tmp  # 2nd Pass HPF image
            tmp_hpf_matrix_2 = grass.tempfile()  # 2nd Pass ASCII filter

        # Temporary files ===================================================

        # Construct Filter
        hpf = High_Pass_Filter(ratio, center, modulation, False, None)
        hpf_ascii(center, hpf, tmp_hpf_matrix, 1)

        # Construct 2nd Filter
        if second_pass and ratio > 5.5:
            hpf_2 = High_Pass_Filter(ratio, center2, None, True, modulation2)
            hpf_ascii(center2, hpf_2, tmp_hpf_matrix_2, 2)

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

        g.message("\n|3 Upsampling (bilinearly) low resolution image")

        run('r.resamp.interp',
            method='bilinear', input=msx, output=tmp_msx_blnr, overwrite=True)

        # -------------------------------------------------------------------
        # 4. Weighting the High Pass Filtered image(s)
        # -------------------------------------------------------------------

        g.message("\n|4 Weighting the High-Pass-Filtered image (HPFi)")

        # Compute (1st Pass) Weighting
        msg_w = "   > Weighting = StdDev(MSx) / StdDev(HPFi) * " \
            "Modulating Factor"
        g.message(msg_w)

        # StdDev of Multi-Spectral Image(s)
        msx_avg = avg(msx)
        msx_sd = stddev(msx)
        g.message("   >> StdDev of <%s>: %.3f" % (msx, msx_sd))

        # StdDev of HPF Image
        hpf_sd = stddev(tmp_pan_hpf)
        g.message("   >> StdDev of HPFi: %.3f" % hpf_sd)

        # Modulating factor
        g.message("   >> Modulating Factor: %.2f" % modulator)

        # weighting HPFi
        weighting = hpf_weight(msx_sd, hpf_sd, modulator, 1)

        # -------------------------------------------------------------------
        # 5. Adding weighted HPF image to upsampled Multi-Spectral band
        # -------------------------------------------------------------------

        g.message("\n|5 Adding weighted HPFi to upsampled image")

        fusion = "%s = %s + %s * %f" \
            % (tmp_msx_hpf, tmp_msx_blnr, tmp_pan_hpf, weighting)
        grass.mapcalc(fusion)

        # history ***********************************************************
        cmd_history += "Weigthing applied: %.3f / %.3f * %.3f | " \
            % (msx_sd, hpf_sd, modulator)

        if second_pass and ratio > 5.5:
            # ---------------------------------------------------------------
            # 4+ 2nd Pass Weighting the High Pass Filtered image
            # ---------------------------------------------------------------
            g.message("\n|4+ 2nd Pass Weighting the HPFi")

            # Compute 2nd Pass Weighting
            # Formula? Don't inform again...

            # StdDev of HPF Image #2
            hpf_2_sd = stddev(tmp_pan_hpf_2)
            g.message("   >> StdDev of 2nd HPFi: %.3f" % hpf_2_sd)

            # Modulating factor #2
            g.message("   >> 2nd Pass Modulating Factor: %.2f" % modulator_2)

            # 2nd Pass weighting
            weighting_2 = hpf_weight(msx_sd, hpf_2_sd, modulator_2, 2)

            # ---------------------------------------------------------------
            # 5+ Adding weighted HPF image to upsampled Multi-Spectral band
            # ---------------------------------------------------------------

            g.message("\n|5+ Adding small-kernel-based weighted 2nd HPFi "
                      "back to fused image")

            add_back = "%s = %s + %s * %f" \
                % (tmp_msx_hpf, tmp_msx_hpf, tmp_pan_hpf_2, weighting_2)
            grass.mapcalc(add_back)

            # 2nd Pass history entry ****************************************
            cmd_history += "2nd Pass Weighting: %s / %s * %s | " \
                % (msx_sd, hpf_2_sd, modulator_2)

        if color_match:
            g.message("\n|* Matching output's to input's color table")

            run('r.colors',
                map=tmp_msx_hpf, rast=msx)

        # -------------------------------------------------------------------
        # 6. Stretching linearly the HPF-Sharpened image(s) to match the Mean
        #     and Standard Deviation of the input Multi-Sectral image(s)
        # -------------------------------------------------------------------

        if histogram_match:

            # adapt output StdDev and Mean to the input(ted) ones
            g.message("\n|+ Matching histogram of Pansharpened image "
                      "to %s" % (msx), flags='v')

            # Collect stats for linear histogram matching
            msx_hpf_avg = avg(tmp_msx_hpf)
            msx_hpf_sd = stddev(tmp_msx_hpf)

            # expression for mapcalc
            lhm = "%s = (%s - %f) / %f * %f + %f" \
                % (tmp_msx_hpf,
                   tmp_msx_hpf, msx_hpf_avg,
                   msx_hpf_sd, msx_sd, msx_avg)

            # compute
            grass.mapcalc(lhm, quiet=True, overwrite=True)

            # update history string *****************************************
            cmd_history += "Linear Histogram Matching: %s |" % lhm

        # -------------------------------------------------------------------
        # End of Algorithm \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
        # -------------------------------------------------------------------

        # history entry
        run("r.support", map=tmp_msx_hpf, history=cmd_history)

        # add suffix to basename & rename end product
        msx_nam = ("%s.%s" % (msx.split('@')[0], outputsuffix))
        run("g.rename", rast=(tmp_msx_hpf, msx_nam))

    # visualising-related information
    grass.del_temp_region()  # restoring previous region settings
    g.message("\n|! Region's resolution restored!")
    g.message("\n>>> Rebalancing colors "
              "(i.colors.enhance) may improve appearance of RGB composites!",
              flags='i')

if __name__ == "__main__":
    options, flags = grass.parser()
    atexit.register(cleanup)
    sys.exit(main())
