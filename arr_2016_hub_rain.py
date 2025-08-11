
import zipfile
import numpy as np
import glob
import os
debug = 1

def decode(l):
    """
    .decode('utf-8').strip('\r\n').split(',')
    """
    if isinstance(l, list):
        return [decode(x) for x in l]
    else:
        return l.decode('utf-8').strip('\r\n').split(',')

class Arr_hub_rain(object):

    def __init__(self, hub_filename, debug=0):

        """
        Open downloaded ARR hub file

        """

        import glob
        import os

        self.hub_filename = hub_filename

        self.open_hubfile()


    def open_hubfile(self):

        hub_filename = self.hub_filename

        lcount = 0
        Hfile = open(hub_filename,'r')
        lines = Hfile.readlines()
        self.lines = lines
        for line in lines:
            if debug > 1:print(line)
            if line.startswith('[INPUTDATA]'):
                self.Loc_Lat = lines[lcount+1].split(',')[1].strip() #,-33.035717
                self.Loc_Lon = lines[lcount+2].split(',')[1].strip() #,151.265069
            elif line.startswith('[RIVREG]'):
                self.Divis = lines[lcount+1].split(',')[1].strip() #,South East Coast (NSW)
                self.RivNum = lines[lcount+2].split(',')[1].strip() # ,10
                self.RivName = lines[lcount+3].split(',')[1].strip() # ,Hunter River
            elif line.startswith('[RIVREG_META]'):
                self.TimeAccessed = lines[lcount+1].split(',')[1].strip()  #,17 September 2019 02:43PM
                self.Version      = lines[lcount+2].split(',')[1].strip()  #,2016_v1
            elif line.startswith('[LONGARF]'):
                self.ARF_a = lines[lcount+2].split(',')[1].strip() 
                self.ARF_b = lines[lcount+3].split(',')[1].strip() 
                self.ARF_c = lines[lcount+4].split(',')[1].strip() 
                self.ARF_d = lines[lcount+5].split(',')[1].strip() 
                self.ARF_e = lines[lcount+6].split(',')[1].strip() 
                self.ARF_f = lines[lcount+7].split(',')[1].strip() 
                self.ARF_g = lines[lcount+8].split(',')[1].strip() 
                self.ARF_h = lines[lcount+9].split(',')[1].strip() 
                self.ARF_i = lines[lcount+10].split(',')[1].strip() 
            elif line.startswith('[LOSSES]'):    
                self.ARR_IL = lines[lcount+2].split(',')[1].strip() 
                self.ARR_CL = lines[lcount+3].split(',')[1].strip() 
            elif line.startswith('[TP]'):
                self.Tpat_code = lines[lcount+1].split(',')[1].strip()  #,17 September 2019 02:43PM
                self.Tpatlabel = lines[lcount+2].split(',')[1].strip() 
            elif line.startswith('[ATP]'):
                self.ATpat_code = lines[lcount+1].split(',')[1].strip()  #,17 September 2019 02:43PM
                self.ATpatlabel = lines[lcount+2].split(',')[1].strip() 

            lcount+=1
        Hfile.close()


    def stats(self):

        print(self.lines)



class ARR_point_rainfall_patterns(object):

    def __init__(self, pattern_zip_file, Tpat_code, debug=0):


        try:# Try to open the Zip File and open the 2 zips inside the HUB zip file
            zip = zipfile.ZipFile(pattern_zip_file)
            if debug>0: print('Files found in the zip file:')
            if debug>0: print (zip.namelist())   # available files in the zip container
            files_inzip_list = zip.namelist()
        except:
            print('PROBLEM FINDING THE MAIN ZIP FILE.... Is it present ?')

        if debug>0: print(Tpat_code+'_AllStats.csv')


        findfile = Tpat_code+'_AllStats.csv'
        if debug>0: print('Look for: %s' %(findfile))

        try:
            if findfile in files_inzip_list:
                AllStat_index = files_inzip_list.index(findfile) # The STATS for the RAINFALL DATA
                fAStat=zip.open(files_inzip_list[AllStat_index],'r')
                linesAStat = fAStat.readlines()
        except:
            print('Problem finding AllStats ZIP part...')


        findfile = Tpat_code+'_Increments.csv'
        if debug>0: print('Look for: %s' %(findfile))

        try:
            if findfile in files_inzip_list:
                Incr_index = files_inzip_list.index(findfile)# THIS IS THE RAINFALL INCREMENTS (PATTERN)
                fInc=zip.open(files_inzip_list[Incr_index],'r')
                linesInc = fInc.readlines()
        except:
            print('Problem finding Increments ZIP part...')


        self.linesAStat = decode(linesAStat)
        self.linesInc = decode(linesInc)

        self.STATS_Labels =  decode(linesAStat[0])
        self.INCS_Labels =  decode(linesInc[0])


           

class Single_pattern(object):

    def __init__(self, prp, index=1, Ev_dep=1.0, debug=0):
        """
        
        input 
        
        prp: region rainfall patterns
        l: index 1-720
        """

        assert index>0 and index<=720, f"index = {index} but should be in range [1, 720]"

        self.index = index
        self.prp   = prp

        l = index

        self.bitsAS  = prp.linesAStat[l]
        self.bitsInc = prp.linesInc[l]

        self.Ev_ID  = self.bitsInc[0]
        self.Ev_dur = int(self.bitsInc[1])
        self.Tstep  = int(self.bitsInc[2])
        self.Zone   = self.bitsInc[3]
        self.Ev_Frq = self.bitsInc[4]  

        self.Ev_dep = Ev_dep    
        self.Tstps  = int(self.Ev_dur/self.Tstep)

        if debug>0: print('E_Dur: %i, TStep: %i, TSteps: %i, Zone: %s' %(self.Ev_dur,self.Tstep,self.Tstps,self.Zone))

        Rplot = [0.0]
        Tplot = [0.0]
        tcount = 0

        for t in range(self.Tstps):
            #print(d[5+tcount])
            R = float(self.bitsInc[5+tcount])*Ev_dep/100.0
            Rplot.append(R)
            tcount +=1
            T = self.Tstep*tcount
            Tplot.append(T)

        self.Tplot = np.asarray(Tplot)
        self.Rplot = np.asarray(Rplot)



    def plot(self, title=None, ax=None):

        bitsInc = self.bitsInc 
        Tstep = self.Tstep 
        Tstps = self.Tstps
        Ev_dep = self.Ev_dep

        plot_single_pattern(bitsInc, Tstep, Tstps, Ev_dep=Ev_dep, title=title, ax=None)

 




def plot_single_pattern(bitsInc, Tstep, Tstps, Ev_dep=100.0, title=None, ax=None):
    """
    Plots just one Rainfall Pattern
    
    """
    import matplotlib.pyplot as plt
    import numpy as np
    import matplotlib.ticker as ticker

    if ax is None:
        fig, ax = plt.subplots()


    #print(bitsInc)

    Rplot = [0.0]
    Tplot = [0.0]
    tcount = 0
    #print (i,d)
    #print(i,Tstps)
    Ev_ID = bitsInc[0]
    Ev_Frq = bitsInc[4]


    if title is None:
        Ev_ID+':'+Ev_Frq
    else:
        pass

    for t in range(Tstps):
        #print(d[5+tcount])
        R = float(bitsInc[5+tcount])*Ev_dep/-100.0
        Rplot.append(R)
        tcount +=1
        T = Tstep*tcount
        Tplot.append(T)
    
    inv_Rplot = np.array(Rplot)*-1.0
    cum_pmp = np.cumsum(inv_Rplot) 
    #print(Tplot,Rplot)
    ax.set_title(title,fontsize = 10)
    ax.bar(Tplot[1:], Rplot[1:], -Tstep, edgecolor='blue', color='None', align='edge') # Plot Rainfall Bar Chart  
    ax2 = ax.twinx()     
    ax2.plot(Tplot, cum_pmp, color="red") #,label = 'Accum. All') # Add Cumulative Rain Line Plot
    ax2.yaxis.label.set_color('red')
    ax2.set_ylabel('Tot Rain pct',fontsize = 8)
    ax2.tick_params(axis='y', colors='red')
    ax.set_xlabel('Time Steps (min)',fontsize = 8)
    #max_pre = int(max(inv_Rplot))
    #y_ticks = np.linspace(0, max_pre, max_pre+1)
    #y_ticklabels = [str(i) for i in y_ticks]
    #ax.set_yticks(-1 * y_ticks)
    #ax.set_yticklabels(y_ticklabels)
    ax.tick_params(axis='y', colors='green')
    ax.set_ylabel('Rain pct')
    ax.yaxis.label.set_color('green')

    plt.show()
    plt.close(fig=fig)


#-----------------------------------------------------------------------
def plot_frq_patterns(PatternType,Dur_Incs,Tstep,Tstps,Zone,Ev_dur):
    """
    Create Plot of Multiple Patterns on Single Screen
    
    Such as all 10 Patterns
    
    
    """
    import matplotlib.pyplot as plt
    import numpy as np
    
    #-------------------------- PLOTS ----------------------------------
    fig = plt.figure(figsize=(12, 8))
    Ev_dep = 100.0   #---------------------- REPLACE THIS WITH IFD TOTAL RAIN FROM IFD DATA
    # iterate over the function list and add a subplot for each function
    if len(Dur_Incs) == 30:
        v = 6
        h = 5
    else:
        v = 2
        h = 5

    for i, dur_inc in enumerate(Dur_Incs, start=1): 

        ax = fig.add_subplot(v, 5, i) # plot with 2 rows and 2 columns

        plot_single_pattern(dur_inc,Tstep,Tstps,Ev_dep,ax)


    fig.tight_layout()    
    plt.subplots_adjust(top=0.9)
    stitle = '%s, %s  Rain Proportion Patterns for %sminute Duration' %(PatternType,Zone,Ev_dur)
    fig.suptitle(stitle, fontsize = 16, color = 'red')
    plt.show()
    #--------------- PLOT ACCUMULATED RAIN FOR ALL PATTERNS ------------
    return()



#-----------------------------------------------------------------------
def plot_all_patterns_for_duration(PatternType,STATS_Labels,INCS_Labels,Dur_Astat,Dur_Incs,debug):
    """
    There are 30 Data sets passed here:
     - 10 Frequent Patterns
     - 10 Intermediate Patterns
     - 10 Rare patterns
    These can be plotted as 3 x 10, or 5 x 2 x 3 (5,6)
    
    There is also Value in Plottng just the Patterns associated with the Particular Frequency on its own (10 Patterns)
    
    """

    Ev_dur = int(Dur_Incs[0][1])
    Tstep = int(Dur_Incs[0][2])
    Tstps = int(Ev_dur/Tstep)
    Zone = Dur_Incs[0][3]

    print('E_Dur: %i, TStep: %i, TSteps: %i, Zone: %s' %(Ev_dur,Tstep,Tstps,Zone))

    start = 1
    end = 30

    St = [0,10,20]
    End = [10,20,30]
    for i ,frq in enumerate(['Frequent','Intermediate','Rare']):
        print(frq)
        plot_frq_patterns(PatternType,Dur_Incs[St[i]:End[i]],Tstep,Tstps,Zone,Ev_dur)
    return()



