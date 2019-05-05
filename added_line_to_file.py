#!usr/bin/python3
# -*- coding:utf-8 -*-
# @Time     :2019/3/28 17:33
# @Author   : zhousai@yikongenomics.com
# @File     : added_line_to_file.py
# @Function :---------

import time

file = "/data/Project/Project_run_log/N_0463_test_test/Demulti_project_result_path.txt"
dem_path_01 = "/data/Illumina_fastq/NextSeq550_1/190324_NB551093_0492_AHMLG3BGX7_R1"
dem_path_02 = "/data/Illumina_fastq/NextSeq550_1/190325_NB551093_0493_AHYNVGBGX7_R1"
dem_path_03 = "/data/Illumina_fastq/NextSeq550_1/190326_NB551093_0494_AHKN2TAFXY_R1"
dem_path_04 = "/data/Illumina_fastq/NextSeq550_1/190327_NB551093_0495_AHKN5JAFXY_R1"
info_01 = open(file,'a')
info_01.writelines(dem_path_01 + '\n')
info_01.close()
time.sleep(600)

info_02 = open(file,'a')
info_02.writelines(dem_path_02 + '\n')
info_02.close()
time.sleep(1200)

info_03 = open(file,'a')
info_03.writelines(dem_path_03 + '\n')
info_03.close()
time.sleep(1800)

info_04 = open(file,'a')
info_04.writelines(dem_path_04 + '\n')
info_04.close()
time.sleep(3600)
