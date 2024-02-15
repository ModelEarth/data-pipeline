
# To run: python automateRF.py "../input"

import warnings
warnings.simplefilter(action='ignore')
import sys
import os
import subprocess
import numpy as np
import pandas as pd
import runOneFile
def getOneFileOutput(inFile):
    outFile=os.path.join("/".join(inFile.split("/")[:-1]),inFile.split("/")[-1].split("_")[0]+"_random_forest_poverty.csv")
    command="python runOneFile.py {} > temp.txt && sed 's/\s* /,/' temp.txt > {}".format(inFile,outFile)
    subprocess.call(command,shell=True)
    df=pd.read_csv(outFile)
    l=df.shape[0]
    df.index=range(1,l+1)
    #df.reset_index(level=0,inplace=True)
    #df.index=np.arange(1,l+1)
    df.rename(columns={'Unnamed: 0':'features'},inplace=True)
    df.to_csv(outFile,index=True)
    print("OutFile Generated: " + outFile)
def main():
    inDir=sys.argv[1]
    dir_list=[d for d in os.listdir(inDir)]
    #dir_list.remove('2017')
    dir_list.remove('2012')
    for subDir in dir_list:#2013,2014,2015,2016
        for file in os.listdir(os.path.join(inDir,subDir)):
            if 'zcta_sm.csv' in file:
                file=os.path.abspath(os.path.join(inDir,subDir,file))
                getOneFileOutput(file)
if __name__ == "__main__":
    main()   
