# -*- coding: utf-8 -*-
from pathlib import Path
import os
import pandas as pd


def load_df_ori(file_path):
    while True:
        try:
            _file = Path(file_path)
            df_ori = None
            if _file.exists():
                df_ori = pd.read_csv(file_path, sep=",")
            else:     ## if not found input file
                print("Using default file")
            break
        except:
            print("Fail to read original dataset, plz try again.")
    return df_ori

def load_df_ano(file_path):
    while True:
        try:
            _file = Path(file_path)
            df_ano = None
            if _file.exists():
                df_ano = pd.read_csv(file_path, sep=",")
            else:    ## if not found input file
                print("Using default file")
            break
        except:
            print("Fail to read anonymized dataset, plz try again.")
    return df_ano


def load_p(file_path):
    ## load p.txt
    ## index from 1 to n
    while True:
        try:
            _file = Path(file_path)
            file_p = None
            p = None
            if _file.exists():
                file_p = file_path
            else:   ## if not found input file
                file_p = "./p.txt" 
                print("Using default file", file_p)
            with open(file_p, 'r') as f:
                p = f.read()
            p = p.split()
            p = [int(pi) for pi in p]
            break
        except:
            print("Fail to read anonymized dataset, plz try again.")
    return p

def getP(pandas_df):
    df_shuffle = pandas_df.sample(frac=1)  ## Random order
    df_shuffle_index = df_shuffle.index.values + 1   ### index from 1 to n 

    return df_shuffle_index



