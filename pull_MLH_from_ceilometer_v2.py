# -*- coding: utf-8 -*-
"""
Created on Tue May 22 14:02:20 2018

@author: kweber
"""

from netCDF4 import Dataset
#import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np         #didn't even use numpy!!! HA!
#import seaborn as sns
from tkinter import Tk

from tkinter.filedialog import askdirectory
import os
import xarray as xr

def get_dat():
    root = Tk()
    root.withdraw()
    root.focus_force()
    root.attributes("-topmost", True)      #makes the dialog appear on top
    filename = askdirectory()      # Open single file
    root.destroy()
    root.quit()
    return filename

start=pd.datetime.now()

directory=get_dat()
output_df=pd.DataFrame()
i=0

for filename in os.listdir(directory):     #loop through files in user's dir
    if filename.endswith(".nc"):
        runstart=pd.datetime.now()
        rootgrp3 = Dataset(directory+'/'+filename, "r", format="NETCDF4")
#        print (rootgrp3.dimensions.keys())
        #print (rootgrp3.data_model)
        print(pd.datetime.now()-runstart)
        
        # this is the variable we want!!
        mlh_2 = rootgrp3.variables['Mean_Layer_Height'][:]
        print(pd.datetime.now()-runstart)
        # time: days since 1970-01-01 00:00:00.000
        ml_time = rootgrp3.variables['time'][:]
        print(pd.datetime.now()-runstart)
        
        # close the file after you've had your way with the data you wanted from it
        rootgrp3.close()
        runtime=pd.datetime.now()-runstart
        df=pd.DataFrame([mlh_2[:,0],ml_time],index=['mlh2','ml_time']).T
        df['dt']=pd.to_datetime('1970-01-01 00:00:00.000') +pd.to_timedelta(df['ml_time'], unit='S')-pd.Timedelta('7 hours')
        
        df['dt_trunc']=df['dt'].apply(str).str[:13]
        df=df.drop_duplicates(subset=['dt_trunc','mlh2'])
        output_df=output_df.append(df)
        print("{}. It's working!!! It's working!!! It took {} for this file".format(i,runtime))
        i+=1



output_df['Site']='HW'
output_df['Parameter']='61301'
output_df['Average Interval']='001h'
output_df['Date']=output_df['dt'].dt.strftime("%m/%d/%Y %H")+':00'
output_df['Value']=np.around(output_df['mlh2'],2)
output_df['Raw Value']=output_df['mlh2']
output_df['AQS Null Code']=np.where(output_df['mlh2']<0,'AN','')
output_df['Flags']=np.where(output_df['mlh2']<0,'<-','')
output_df['Qualifier Codes']=''
output_df['AQS Method Code']='128'
output_df['Data Grade']=''
columns=['Site','Parameter','Average Interval','Date','Value','Raw Value',
         'AQS Null Code','Flags','Qualifier Codes','AQS Method Code','Data Grade']
output_df=output_df[columns]
output_df=output_df.sort_values(by=['Date','Value'],ascending=False).drop_duplicates(subset=['Date'],keep='first')
#plt.plot(mlh_2)
output_df.to_csv(directory+'/test_out.csv',index =False)
end=pd.datetime.now()
total=(end-start)

print('runtime: {}'.format(total))
