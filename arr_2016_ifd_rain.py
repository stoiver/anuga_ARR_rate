"""


                                                PYTHON 3.xx
                                
arr_2016_ifd_rain.py                         
                                                
- Need a routine to Download the IFD Grid DATA

Then a routine to get IFD data limited to a Catchment Polygon
- Then perform statistics on the data sets for the Catchment Extent

A routine to extract the IFD at a Point from the Zip File


"""

def decode(l):
    """
    .decode('utf-8').strip('\r\n').split(',')
    This decodes a list that is identified as bytes
    """
    if isinstance(l, list):
        return [decode(x) for x in l]
    else:
        return l.decode('utf-8').strip('\r\n').split(',')


class Arr_ifd_rain(object):

    def __init__(self, IFD_DIR, Lat, Lon,
                       debug=0):

        """
        Structure of Names in the Grid IFD Rainfall ZIP file is as follows:
        
        catchment_depth_1min_99999aep.txt.asc
        
        Durations can be found by min, and frequency by aep


        What are the choices of Frq and Dur?

        """

        import zipfile
        import glob
        import os
        import numpy as np

        # Directory containing the ARR IFD Data
        self.IFD_DIR = IFD_DIR 

        # Location of point of interest
        self.Lat = Lat
        self.Lon = Lon

        # Frequency and Duration of model
        #self.Frq = Frq
        #self.Dur = Dur

        # self.SiteLabel = SiteLabel

        self.debug = debug

        # Search through IFD directory for appropriate map
        # and read in ascii file and then convert to array


        dur_list  = []
        frq_list  = []
        file_list = []
        zip_list  = []

        for Zip_file in glob.glob(os.path.join(IFD_DIR, '*IFD*.zip')): # just get the IFD files only
            zip = zipfile.ZipFile(Zip_file)

            # available files in the container
            files_in_zip_list = zip.namelist()
            if debug > 0: print (zip.namelist())  

            for file_in_zip in files_in_zip_list: # 
                if 'epsg' in file_in_zip:
                    pass # Not the File we want
                else:
                    if debug > 0 : print (file_in_zip)

                    # CHECK DURATION
                    # pull out integer sitting in front of 'min'
                    Dur_R = file_in_zip.split('min')[0].split('_')[2] 
                    if debug > 0 : print (Dur_R,Dur)

                    Frq_R = file_in_zip.split('aep')[0].split('_')[3] 
                    if debug > 0 : print (Frq_R,Frq)

                    if not Dur_R.isdigit():
                        print ('NOT DIGIT....')
                        print (Dur_R,Dur)

                    if not Frq_R.isdigit():
                        print ('NOT DIGIT....')
                        print (Frq_R,Frq)

                    dur_list.append(Dur_R)
                    frq_list.append(Frq_R)
                    file_list.append(file_in_zip)
                    zip_list.append(Zip_file)

        self.dur_list = np.asarray(dur_list, dtype=int)
        self.frq_list = np.asarray(frq_list, dtype=int)
        self.file_list = file_list
        self.zip_list = zip_list

        # self.open_ifd_grd_file()
        # self.lines_2_array()

    def open_grd(self, Dur, Frq):
        """
        Search through *IFD*.zip files for those corresponding to the 
        specified frequency (Frq) and duration (Dur)

        Structure of Names in the Grid IFD Rainfall ZIP files is as follows:
        catchment_depth_1min_99999aep.txt.asc

        So Dur is the integer before 'min' and Frq is the integer before 'aep' in the 
        filename

        """


        import glob
        import zipfile
        import os
        import numpy as np


        OPENZIP = True

        debug   = self.debug
        IFD_DIR = self.IFD_DIR
        dur_list = self.dur_list
        frq_list = self.frq_list
        file_list = self.file_list
        zip_list = self.zip_list

        found_ifd_file = False

        for Dur_R, Frq_R, file_in_zip, zip_name in zip(self.dur_list, self.frq_list, self.file_list, self.zip_list):

            # Get Specific Frq-Dur File
            if Dur == int(Dur_R) and Frq == int(Frq_R) and OPENZIP:
                # extract a specific file from zip

                found_ifd_file = True

                arr_grd = Arr_grd(Dur_R,Frq_R, file_in_zip, zip_name, IFD_DIR)


        if not found_ifd_file:
            msg  = f"""
No file associated with duration {Dur} and Frequency {Frq} found.

Check dur_list and frq_list for possible pairs of Duration and Frequency.
"""

            print('WARNING: '+msg)

            return

        return arr_grd



class Arr_grd(object):

    def __init__(self, Dur, Frq, file_in_zip, zip_name, IFD_DIR, debug=0):

        self.debug = debug

        import zipfile
        import numpy as np

        self.dur = Dur
        self.frq = Frq
        self.IFD_DIR = IFD_DIR

        zip_file = zipfile.ZipFile(zip_name)
        f=zip_file.open(file_in_zip)
        lines = f.readlines()
        # format of Grid IFD data
        """
        ncols         27
        nrows         23
        xllcorner     150.975   # lon
        yllcorner     -33.6     # lat
        cellsize      0.025
        NODATA_value  -9999

        Note that
        lon=(0:-1:-(nrows-1)).*cellsize + yllcorner + cellsize/2   ## Check this
        lat=(0:ncols).*celsize + xllcorner + cellsize/2
        """
        # Get cols,rows,xllcorner,yllcorner,cellsiize,NODATA_value
        for line in lines:
            line = decode(line)
            if debug > 2: print (line)
            line = ' '.join(line[0].split()) # Get Rid of all but one space
            if line.startswith('ncols'):
                cols =int(line.split('ncols')[1].strip())
                if debug > 2:print (cols)
            if line.startswith('nrows'):
                rows =int(line.split('nrows')[1].strip())
                if debug > 2:print (rows)
            if line.startswith('xllcorner'):
                xllcorner =float(line.split('xllcorner')[1].strip())
                if debug > 2:print (xllcorner)
            if line.startswith('yllcorner'):
                yllcorner =float(line.split('yllcorner')[1].strip())
                if debug > 2:print (yllcorner)
            if line.startswith('cellsize'):
                cellsize =float(line.split('cellsize')[1].strip())
                if debug > 2:print (cellsize)
            if line.startswith('NODATA_value'):
                NODATA_value =line.split('NODATA_value')[1].strip()
                xurcorner = float(xllcorner) + int(cols)*float(cellsize) # Upper Right Lon
                yurcorner = float(yllcorner) + int(rows)*float(cellsize)  # Upper Right Lat
                if debug > 2:
                    print (NODATA_value)
                    print (xurcorner)
                    print (yurcorner)


        IFD_lines = decode(lines)

        IFD_Data = []
        for l in IFD_lines[6:]:
            l[0] = l[0].rstrip(' ')
            IFD_Data.append([float(s) for s in l[0].split(' ')])

        self.IFD_Data = np.asarray(IFD_Data, dtype=float)

        if debug>0: print(IFD_Data)

        self.lons   = xllcorner + np.arange(cols)*cellsize
        lats_r = yllcorner + np.arange(rows)*cellsize
        self.lats   = lats_r[::-1] # keep in mind to flip up-down latitude.

        self.cols = cols
        self.rows = rows
        self.xllcorner = xllcorner
        self.yllcorner = yllcorner
        self.cellsize = cellsize
        self.NODATA_value = NODATA_value

    def __repr__(self):

        msg = f"""
        cols         {self.cols}
        rows         {self.rows}
        xllcorner    {self.xllcorner}
        yllcorner    {self.yllcorner}
        cellsize     {self.cellsize}
        NODATA_value {self.NODATA_value}
        """

        return msg

    def get_rain_at_point(self, Lon=151, Lat=31.5):

        xllcorner = self.xllcorner
        yllcorner = self.yllcorner
        cellsize = self.cellsize
        rows = self.rows
        cols = self.cols
        debug = self.debug

        Tar_col = round(float((Lon - xllcorner) / cellsize))
        Tar_row = round(float((Lat - yllcorner) / cellsize))
        if debug > 0:
            print("Target Location: %i,%i" % (Tar_col, Tar_row))

        Tar_row = int(rows) - Tar_row
        if debug > 0:
            print("Inverted Tar_row : %i " % (Tar_row))

        # Check the Location is correct !!!!!!
        Tar_Rain = self.IFD_Data[Tar_row, Tar_col]

        if debug > 0:
            print("Rain at Target: %.1fmm" % (Tar_Rain))

        return Tar_Rain  

    def plot(self, Lon = None, Lat = None, SiteLabel = 'SiteLabel', ax=None, close_plot=False):
        """
        PLOT the IFD Grid for a specified FREQ & DUR,
        plot a Reference Polyline (Catchment)
        plot a Reference Location PT and label the Rainfall at that point
        """

        import numpy as np
        import matplotlib.pyplot as plt
        import cmaps as nclcmaps
        import glob
        import os

        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 6))
        else:
            fig = plt.gcf()


        IFD_Data = self.IFD_Data
        IFD_DIR  = self.IFD_DIR

        Frq = self.frq
        Dur = self.dur

        plot_marker = True
        if Lon is None or Lat is None: 
            plot_marker = False
        else:
            LLRain = self.get_rain_at_point(Lon=Lon, Lat=Lat)

        lons = self.lons
        lats = self.lats

        debug = self.debug

        mask = IFD_Data > 0.0
        vmax = np.max(IFD_Data)
        vmin = np.min(IFD_Data[mask])

        if debug > 0: print(vmin,vmax)

        # norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
        cs = ax.pcolormesh(lons, lats,IFD_Data, cmap='hsv', vmin=vmin, vmax=vmax)  #  nclcmaps.MPL_plasma_r, 'inferno'
        fig.colorbar(cs)
        # ax.axis('off')

        # ---------- PLOT Poly Lines --------------------------------------------
        # File *.ply
        for poly_file in glob.glob(os.path.join(IFD_DIR, '*.ply')):
            xp = []
            yp = []
            if debug > 0 : print('Plot: '+poly_file)
            with open(poly_file, 'r') as f:
                lines = f.readlines()
                for l in lines:
                    xp.append(float(l.split(',')[0]))
                    yp.append(float(l.split(',')[1]))
            plt.plot(xp,yp,c = 'white',linestyle = '--',linewidth = 1.5)

        # -------------- PLOT IFD LOCATION --------------------------------------
        # PLOT THE POINT OF ENQUIRY
        if plot_marker:
            plt.scatter(Lon, Lat, marker='+',color = 'white', s=10, zorder=10)

        # ------- Titles --------------
        st_txt = '2016 IFD Grd for %f frq; %i Mins' %(Frq,Dur)
        fig.suptitle(st_txt, color='red')

        if plot_marker:
            t_txt = '%s Lat: %.4f, Lon: %.4f Rainfall: %.1fmm' %(SiteLabel,Lat,Lon,LLRain)
        else:
            t_txt = SiteLabel
        
        _ = ax.set_title(t_txt,color = 'blue')

        plt.show()

        if close_plot: 
            plt.close(fig=fig)

        return ax


