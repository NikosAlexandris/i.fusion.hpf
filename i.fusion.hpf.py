# -*- coding: utf-8 -*-
"""
Created on Fri Oct 31 20:03:06 2014

@author: nik
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
    
    print "Options and flags"
    print pan
    print

    print msx
    print
    
    print outputprefix
    print
    
    print custom_ratio
    print
    
    print center
    print center2
    print
    
    print modulation
    print modulation2
    print
    
    print histogram_match
    print second_pass
    print "--- --- ---"
    print



    # Check & warn user about "ns == ew" resolution of current region

    region = grass.region()
    nsr = region['nsres']
    ewr = region['ewres']

    if nsr != ewr:
        g.message("The region's North:South and East:West resolutions do not \
        match.", flags='w')
        print "Region's resolution: ", 'ns=%f, ew=%f' % (nsr, ewr)

    #
    g.message("Step 1:"
              "Computing ratio of low (Multi-Spectral)"
              "to high (Panchromatic) resolutions)", flags='i')

    # 2D image resolutions
    g.message("* Get resolution of input imagery (pan, msx)", flags='i')

    msxinfo = grass.parse_command("r.info", map=msx, flags='g')
    msxres = float(msxinfo['nsres'])

    paninfo = grass.parse_command("r.info", map=pan, flags='g')
    panres = float(paninfo['nsres'])

    # check for custom ratio, else proceed to standard computation method
    if custom_ratio:
        global ratio
        ratio = float(custom_ratio)
        g.message("Using custom ratio value, overriding standard method",
                  flags='w')
    else:
        ratio = msxres / panres
        msg_ratio ='1 Low (%.3f) to high resolution (%.3f) Ratio: %.1f'\
            % (msxres, panres, ratio)
        g.message(msg_ratio, flags='v')

    # 2nd pass requested but Ratio < 5.5
    if second_pass and ratio < 5.5:
        g.message("* Ratio < 5.5 -- Won't apply a 2nd pass!", flags='i')
        second_pass = bool(0)
#        print "[Turned 2nd pass off!]"  # second_pass

    # 2. construct filter!
    g.message("2.  High Pass Filtering the Panchromatic Image", flags='v')

    # Respect current region -- Change the resolution
    run('g.region', res=panres)
    g.message("> Region's resolution set to %f" % panres, flags='v')

    # temporary files
    tmp = grass.tempfile()
    tmpname = grass.basename(tmp)
    print tmpname
    print

    tmp_pan_hpf = "%s_%s" % (outputprefix, tmpname)
    tmp_msx_blnr = "msx_%s" % tmpname
    tmp_msx_hpf = "msx_hpf_%s" % tmpname

    print tmp_pan_hpf
    print tmp_msx_blnr
    print
    
    print "Pan: ", pan
    print

    # High Pass Filter
    hpf = High_Pass_Filter(ratio, center, modulation, False, None)
    hpf_matrix = hpf.filter
    modulator = hpf.modulator
    print "Matrix: ", hpf_matrix
    print "Modulating Factor: ", modulator
    print

    #    grass.try_remove(tmp_hpf_matrix)
    tmp_hpf_matrix = grass.tempfile()

    outf = open(tmp_hpf_matrix, 'w')
    outf.write(hpf_matrix)
    outf.close()

    # 2nd pass?
    if second_pass and ratio > 5.5:

        hpf_2 = High_Pass_Filter(ratio, center, None, True, modulation2)
        hpf_matrix_2 = hpf_2.filter
        modulator_2 = hpf_2.modulator_2

#        grass.try_remove(tmp_hpf_matrix)
        tmp_hpf_matrix_2 = grass.tempfile()

        outf = open(tmp_hpf_matrix_2, 'w')
        outf.write(hpf_matrix_2)
        outf.close()

        tmp_pan_hpf_2 = "%s_2_%s" % (outputprefix, tmpname)

    print "Run r.mfilter"
    print

    # Apply High Pass Filter
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


    #
    g.message("3. Resampling MSx image to the higher resolution")

    g.message("3 Upsampling the low resolution image ($MSX) to the higher"
              "resolution ($PAN_RESOLUTION)",
              flags='v')

  # resample -- named "linear" in G7
    run("r.resamp.interp",  
        method="bilinear",
        input=msx,
        output=tmp_msx_blnr,
        overwrite=True)


    g.message("4.  Adding weighted High-Pass-Filtered image (HPFi) to the"
              "upsampled MSx image")   
    
# ===========================================================================
#    # 4. Add the HPF image weighted relative to the global standard deviation of
## the Multi-Spectral band.
## ----------------------------------------------------------------------------
#
## The weighting formula is: W = ( SD(MS) / SD(HPF) x M )
#  # where:
#	# SD(MS) and SD(HPF) are the Standard Deviations of the MS and HPF images
#	# M is a Modulator value

#  # compute weighting(s)
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


#    # 2nd pass
    if second_pass and ratio > 5.5:
        print "Second Pass..."
	
        # StdDev of HPF Image #2
        hpf_2_uni = run("r.univar", map=tmp_pan_hpf_2, flags='g')
        hpf_2_sd = hpf_2_uni['stddev']
        g.message("* StdDev of 2nd HPF image: $HPF_StdDev_2",
                  flags='g')

		# Modulating factor #2
        g.message("* 2nd Pass Modulating Factor set to: %f" % modulator_2,
                  flags='v')
                  
        weighting_2 = msx_sd / hpf_2_sd * modulator_2
        g.message("%f = %f / %f * %f" % (weighting_2, msx_sd, hpf_2_sd,
                                         modulator_2),
                  flags='v')
        g.message("* 2nd Pass Weighting = %s" % weighting_2,
                  flags='v')
# ===========================================================================



# ===========================================================================
# create temporary file
#  Temporary_MSHPF="i.fusion.hpf.tmp.MSHPF"
#  if [ $? -ne 0 ] || [ -z "$Temporary_MSHPF" ]
#	then g.message -e "unable to create temporary files"
#	exit 1
#  fi

    g.message("4 Adding weighted HPF image to the upsampled image", flags='v')

    # Add weighted HPF image to the bilinearly upsampled Multi-Spectral band
    fusion = "%s = %s + %s * %f" % (tmp_msx_hpf, tmp_msx_blnr, tmp_pan_hpf, weighting)
    grass.mapcalc(fusion)
    g.message("HPF image added to the bilinearly upsampled MSX image.",
              flags='v')

#    # check if 2nd pass applies
    if second_pass and ratio > 5.5:
        g.message("2nd Pass: adding-back to the fused image"
                  "a small-kernel-based HPF weighted image",
                  flags='i')

        add_back = "%s = %s + %s * %f" \
            % (tmp_msx_hpf, tmp_msx_hpf, tmp_pan_hpf_2, weighting_2)
        grass.mapcalc(add_back)
        g.message("2nd pass performed successfuly!", flags='v')
        
#        run("g.copy", rast=$Temporary_MSHPF, ${GIS_OPT_OUTPUTPREFIX}_${MSX})


#  # write cmd history
    run("r.support", map=tmp_msx_hpf,
        history="Weigthing applied: ${MSX_StdDev} / ${HPF_StdDev} * ${!Modulating_Factor}")
        
    run("r.support", map="${Temporary_MSHPF}",
        history="Weigthing applied: ${MSX_StdDev} / ${HPF_StdDev} * ${!Modulating_Factor}")
  
    # 2nd pass history entry
    if second_pass and ratio > 5.5:
        run("r.support", map=tmp_msx_hpf,
            history="2nd Pass Weigthing applied: ${MSX_StdDev} / ${HPF_StdDev2} * ${!Modulating_Factor2}")

# ===========================================================================
    g.message("Step 5:", flags='i')
    g.message("5. Optionally, matching histogram of Pansharpened image"
           "to the one of the original MSx image")

#
# 5. Stretch linearly the new HPF-Sharpened image to match the mean and
# standard deviation of the input Multi-Sectral image.
# ----------------------------------------------------------------------------

    g.message("5 Linearly matching histogram of the >${GIS_OPT_PAN}< to the >${MSX}< image [Not Implemented!]",
              flags='v')

    if histogram_match:
        pass
        run("g.rename", rast=(tmp_msx_hpf,"%s_%s" % (msx, outputprefix)) )
    else:
        # linear hisogram matching to adapt output StdDev and Mean to the input-ted ones
        g.message("Matching histograms...",
                  flags='i')
        pass
  
  #   # input=${Temporary_MSHPF} \
  #   # output=${GIS_OPT_MSX}_${GIS_OPT_OUTPUTPREFIX} \

#   r.mapcalc "MSHPF_Histomatched = ( $Temporary_MSHPF - $MSHPF_Mean ) / $MSHPF_StdDev * $Reference_StdDev + $Reference_Mean" --o
# fi



    g.message("Step 6:", flags='i')

if __name__ == "__main__":
    options, flags = grass.parser()
#    atexit.register(cleanup)
    main()
