#!usr/bin/python3
# -*- coding:utf-8 -*-
# @Time     :2019/3/6 11:09
# @Author   : zhousai@yikongenomics.com
# @File     : md5sum_for_Miseq_GW000059.py
# @Function : GW000059 raw_data_dir include MD5.txt,after copy these raw_data to our service,need to make new MD5SUM

import os
import re
import sys
import subprocess
import argparse

def read_old_MD5_value(old_value_dir):
    line_number_MD5 = {}
    MD5_raw_name = {}
    MD5_new_name = {}
    MD5_old_file = old_value_dir + '/MD5.txt'
    line_num = 0
    with open(MD5_old_file,'r',encoding='gbk') as OLD:
        for line in OLD.readlines():
            line = line.strip()
            line_num += 1
            line_number_MD5[line_num] = line

    for number_MD5 in line_number_MD5.keys():
        if re.search('.fastq.gz',line_number_MD5[number_MD5]):
            #print(number_MD5)
            temp_list = line_number_MD5[number_MD5].split('\\')
            fastq_name = temp_list[-1]
            fastq_name = fastq_name.replace('):','')
            temp_list_Md5 = line_number_MD5[number_MD5 + 1].split(' ')
            Md5_raw_value = "".join(temp_list_Md5)
            MD5_raw_name[fastq_name] = Md5_raw_value

    all_files = os.listdir(old_value_dir)
    pwd_dir = os.getcwd()
    new_MD5_file = pwd_dir + "/new_MD5.txt"
    before_MD5_file = pwd_dir + "/before_MD5.txt"
    if os.path.exists(new_MD5_file):
        mv_sh = 'mv '  + new_MD5_file + ' ' + before_MD5_file
        subprocess.call(mv_sh,shell=True)

    for file in all_files:
        if file.endswith('.fastq.gz'):
            file_path = old_value_dir + '/' + file
            file_MD5_sh = 'md5sum ' + file_path + ">>" + new_MD5_file
            subprocess.call(file_MD5_sh,shell=True)

    new_MD5_info = open(new_MD5_file,'r')
    for line_02 in new_MD5_info.readlines():
        line_02 = line_02.strip()
        temp_list_Md5_new = line_02.split('  ')
        fastq_name_new = temp_list_Md5_new[1].split('/')[-1]
        MD5_new_name[fastq_name_new] = temp_list_Md5_new[0]


    for fastq_name_last in MD5_raw_name.keys():
        if fastq_name_last in MD5_new_name.keys():
            if MD5_raw_name[fastq_name_last] == MD5_new_name[fastq_name_last]:
                pass
            else:
                print(fastq_name_last + ' need to copy the file again')
        else:
            if re.match('Undetermined',fastq_name_last):
                pass
            else:
                print(fastq_name_last + ' need to md5sum for raw_data ')

def main():
    parser = argparse.ArgumentParser(description="confirm the md5sum value the file of dir.")
    parser.add_argument('--old_value_dir', action="store", required=True,help="The dir of raw MD5 value.")
    args = parser.parse_args()
    old_value_dir = args.old_value_dir
    read_old_MD5_value(old_value_dir)

if __name__ == '__main__':
    main()




# old_value_dir = "/data/Project/result_backup/ALL_upload/zhuwai_miSeq_GW000059/GW000059_190305_003"
# read_old_MD5_value(old_value_dir)



