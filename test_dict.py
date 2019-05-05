#!usr/bin/python3
# -*- coding:utf-8 -*-
# @Time     :2019/3/19 14:06
# @Author   : zhousai@yikongenomics.com
# @File     : test_dict.py
# @Function :---------

import re
import glob
import subprocess
import os

# #/data/LIMS_Data_Interaction/SH/ILLUMINA/NextSeq550/0481_PE85_75_190317_NB551093_0485_AHMLFWBGX7_01  /0481_PE85_75_190317_NB551093_0485_AHMLFWBGX7_01.csv
# #/data/LIMS_Data_Interaction/SH/ILLUMINA/NextSeq550/0489_PE75_85_190325_NB551093_0493_AHYNVGBGX7_01/0489_PE75_85_190325_NB551093_0493_AHYNVGBGX7_01.csv
# limscsv = glob.glob("/data/LIMS_Data_Interaction/SH/ILLUMINA/" + "NextSeq550" + '/' + '*' + "190325_NB551093_0493_AHYNVGBGX7" + '*/*_[0-9][0-9].csv')[0]
# lims_dir = '/'.join(limscsv.split('/')[:-1])
# run_id = lims_dir.split('/')[-1].split('_')[0]
# recipe= lims_dir.split('/')[-1]
# print(lims_dir)
# print(run_id)
# print(recipe)

# dem_02 = "/data/LIMS_Data_Interaction/SH/ILLUMINA/NextSeq550/0489_PE75_85_190325_NB551093_0493_AHYNVGBGX7_01"
# run_id = dem_02.split('/')[-1].split('_')[0]
# print(run_id)

# dem_01 = "/data/Illumina_fastq/NextSeq550_1/190325_NB551093_0493_AHYNVGBGX7_R1"
# templist = dem_01.split('/')
# dem_platform = templist[-2]
# print(dem_platform)
# print(templist[-1])

# dem = '/data/Illumina_fastq/NextSeq550_1/190325_NB551093_0493_AHYNVGBGX7_R1'
# dict_01 = {'csv':'/data/LIMS_Data_Interaction/SH/ILLUMINA/NextSeq550/0489_PE75_85_190325_NB551093_0493_AHYNVGBGX7_01/0489_PE75_85_190325_NB551093_0493_AHYNVGBGX7_01.csv',
#            'dir':'/data/LIMS_Data_Interaction/SH/ILLUMINA/NextSeq550/0489_PE75_85_190325_NB551093_0493_AHYNVGBGX7_01/'
#            }
# dict_02 = {}
# dict_02[dem] = dict_01
# for i in dict_02.keys():
#  print(dict_02[i])

# a = "chr1"
# if re.search('"',a):
#     a = a.replace('"',a)
#     print(a)

# tmpdict = {}
# tmplist5 = "ATCACG"
# tmplist1= "1"
# tmplist3="GW000059190324IB_PGS01CE01"
# tmpdict.setdefault((tmplist5, tmplist1), list()).append(tmplist3)
# print(type(tmpdict))

sample_name = "D1M117B190228PGD_JX01SYSH_4_SNP_SMN1_NEW"
gene = '-'.join(sample_name.split('_')[-2:])
print(gene)