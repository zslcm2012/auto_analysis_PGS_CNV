#!usr/bin/python3
# -*- coding:utf-8 -*-
# @Time     :2019/3/13 14:52
# @Author   : zhousai@yikongenomics.com
# @File     : test_01.py
# @Function :---------

import re
import time
import select
import subprocess
import datetime
import os
import glob
import argparse


def judge_new_dempath(dem_path_file):
    limsplatform = ['Hiseq2500', 'Miseq', 'BES4000', 'NextSeq550', 'NextSeq550AR', 'MiniSeq']
    demultiplatform = ['HiSeq2500_1', 'MiSeq_1', 'BioelectronSeq_4000_1', 'NextSeq550_1', 'NextSeq550AR_1','MiniSeq_BJ_1']
    platformdict = dict(zip(demultiplatform,limsplatform))
    filemt_old= time.localtime(os.stat(dem_path_file).st_mtime)
    file_old_time = time.strftime("%Y%m%d%H%M%S",filemt_old)
    old_dict = {}
    new_dict = {}
    new_dem_path_dict = {}
    new_dem_do_anlysis_path = {}
    old_info = open(dem_path_file,'r')
    for line_old in old_info.readlines():
        line_old = line_old.strip()
        old_dict[line_old] = 1
    old_info.close()

    time.sleep(90)

    filemt_new = time.localtime(os.stat(dem_path_file).st_mtime)
    file_new_time = time.strftime("%Y%m%d%H%M%S",filemt_new)
    new_info = open(dem_path_file,'r')
    for line_new in new_info.readlines():
        line_new = line_new.strip()
        new_dict[line_new] = 2
    new_info.close()

    if file_old_time != file_new_time:
        for ele in new_dict.keys():
            if ele not in old_dict.keys():
                new_dem_path_dict[ele] = 3
    else:
        print('no new dem')



    if len(new_dem_path_dict):
        for dem_01 in new_dem_path_dict.keys():
            if os.path.exists(dem_01):
                if dem_01 not in new_dem_do_anlysis_path:
                    new_dem_do_anlysis_path[dem_01] = {}
                    templist = dem_01.split('/')
                    dem_platform = templist[-2]
                    # run_id = templist[-1].split('_')[-2]
                    lims_paltfrom = platformdict[dem_platform]
                    if dem_01.endswith('_R1'):
                        templist[-1] = templist[-1].replace('_R1','')
                    #limscsv = glob.glob("/data/LIMS_Data_Interaction/SH/ILLUMINA/" + lims_paltfrom + '/' + '*' + templist[-1] + '*/*_[0-9][0-9].csv')[0]
                    limscsv = glob.glob("/data/lims_test/SH/ILLUMINA/" + lims_paltfrom + '/' + '*' + templist[-1] + '*/*_[0-9][0-9].csv')[0]
                    lims_dir = '/'.join(limscsv.split('/')[:-1])

                    if dem_01.endswith('_R1'):
                        for project_dir in os.listdir(lims_dir):
                            if re.search('_CNV_', project_dir):
                                new_dem_do_anlysis_path[dem_01]['dir'] = lims_dir
                                new_dem_do_anlysis_path[dem_01]['platform'] = lims_paltfrom
                                new_dem_do_anlysis_path[dem_01]['csv'] = limscsv
                    else:
                        if re.search('_SE',lims_dir.split('/')[-1]):
                            for project_dir in os.listdir(lims_dir):
                                if re.search('_CNV_',project_dir):
                                    new_dem_do_anlysis_path[dem_01]['dir'] = lims_dir
                                    new_dem_do_anlysis_path[dem_01]['platform'] = lims_paltfrom
                                    new_dem_do_anlysis_path[dem_01]['csv'] = limscsv
                        else:
                            print(dem_01,' is PE dem data,SE analysis is finished!')
                            pass

            else:
                print(dem_01,' dem_dir is not exisist,please confirm')
                pass
    # for i in new_dem_do_anlysis_path.keys():
    #     print(i + '\n' + new_dem_do_anlysis_path[i]['csv'] + '\n' + new_dem_do_anlysis_path[i]['platform'] + '\n' + new_dem_do_anlysis_path[i]['dir'])
    return new_dem_do_anlysis_path
#/data/LIMS_Data_Interaction/SH/ILLUMINA/NextSeq550/0481_PE85_75_190317_NB551093_0485_AHMLFWBGX7_01/
#/data/Illumina_fastq/NextSeq550_1/190325_NB551093_0493_AHYNVGBGX7_R1
#E:/YK_SAMPLESHEET/SH/ILLUMINA/NextSeq550/0489_PE75_85_190325_NB551093_0493_AHYNVGBGX7_01/
#E:/YK_SAMPLESHEET/SH/ILLUMINA/NextSeq550/0485_PE85_75_190321_NB551093_0489_AHKMY5AFXY_01/
#/data/LIMS_Data_Interaction/SH/ILLUMINA/NextSeq550/0481_PE85_75_190317_NB551093_0485_AHMLFWBGX7_01  /0481_PE85_75_190317_NB551093_0485_AHMLFWBGX7_01.csv
#                                                   0485_PE85_75_190321_NB551093_0489_AHKMY5AFXY_01/
#/data/Project/Project_run_log/demultiplexedTest/Illumina_fastq/NextSeq550_1/R1_190320_NB551093_0488_AHJ22FBGX7
#/data/Project/Project_run_log/demultiplexedTest/Illumina_fastq/NextSeq550_1/190320_NB551093_0488_AHJ22FBGX7
#E:/YK_SAMPLESHEET/SH/ILLUMINA/NextSeq550/0485_PE85_75_190321_NB551093_0489_AHKMY5AFXY_01/

def prepare_do_anlysis(new_dem_do_anlysis_path,email):
    system_platform = ['Hiseq2500',  'Miseq',     'BES4000',   'NextSeq550', 'NextSeq550AR',   'MiniSeq']
    run_dir_index =   [  'H',         'Mi',        'Bio',        'N',           'NAR',         'Mini_BJ']
    platform_index = dict(zip(system_platform,run_dir_index))
    for dem_02 in new_dem_do_anlysis_path.keys():
        #print(dem_02 + '\t' + new_dem_do_anlysis_path[dem_02]['csv'])
        run_id = new_dem_do_anlysis_path[dem_02]['dir'].split('/')[-1].split('_')[0]
        new_dem_do_anlysis_path[dem_02]['run_id'] = run_id
        run_id_CNV_dir = "/data/Project/Project_run_log/" + platform_index[new_dem_do_anlysis_path[dem_02]['platform']] + '_' +  run_id + "_only_CNV"
        remote_lims_dir = "E:/YK_SAMPLESHEET/" + "/".join(new_dem_do_anlysis_path[dem_02]['dir'].split('/')[3:])
        if os.path.exists(run_id_CNV_dir):
            run_id_CNV_dir = run_id_CNV_dir + "_CNV"
        run_id_CNV_project_list = run_id_CNV_dir + "/" + run_id + '_project_CNV_info.list'
        run_id_CNV_sample_json_dir = run_id_CNV_dir + "/" + run_id + '_sample_json'
        run_id_CNV_run_002_sh = run_id_CNV_dir + "/" + "run_002_make_snakefile.sh"
        run_id_CNV_run_chromgo_sh = run_id_CNV_dir + "/" + run_id +  "_run_chromgo_shell.sh"


        os.system("mkdir -p {dir} && cd {dir}".format(dir=run_id_CNV_dir))
        os.system("cd {dir} && python3 /data/Project/Project_run_log/N_0463_test_test/auto_submit_pipeline/bin1/get_project_info_list_for_CNV_V1.4.3.1.py --samplesheet_path {csv}".format(dir=run_id_CNV_dir,csv=str(new_dem_do_anlysis_path[dem_02]['csv'])))
        #os.system("cd {dir} && python3 /data/Project/Project_run_log/N_0463_test_test/auto_submit_pipeline/bin1/get_project_info_list_for_CNV_V1.6.1.py --samplesheet_path {csv}".format(dir=run_id_CNV_dir,csv=str(new_dem_do_anlysis_path[dem_02]['csv'])))
        #os.system("nohup perl /data/Project/Project_run_log/N_0463_test_test/auto_submit_pipeline/bin/automation_run_lims_pipeline_for_online_for_CNV.pl -l {remote_lims_dir} -g {run_id_CNV_dir}/{run_id}_CNV.log -d ~/Project/CNV_test/ -p {run_id_CNV_dir} -f N -s {run_id_CNV_dir}/{run_id}_project_CNV_info.list -j Y -e {email} &".format(
            #remote_lims_dir=remote_lims_dir,run_id_CNV_dir=run_id_CNV_dir,run_id=run_id,email=email))
        os.system("cd {dir} && /data/software/anaconda2/bin/python /data/software/ChromGo/pipeline/prepare_sample/make_sample_v2.0.py --sample_sheet {csv} --demultiplex_dir {dem_02} --out_dir {run_id_CNV_sample_json_dir}".format(
            dir=run_id_CNV_dir,csv=new_dem_do_anlysis_path[dem_02]['csv'],dem_02=dem_02 + "/Unaligned",run_id_CNV_sample_json_dir=run_id_CNV_sample_json_dir))
        os.system("/data/software/bin/perl /data/software/Pipeline/auto_submit_pipeline/bin1/write_chromgo_shell_v5.1.pl {analysis_dir} {run_dir} {run_NO} {local_lims_dir} {Project_info_list} {emailreport}".format(
            analysis_dir="/data/home/zhousai/Project/CNV_test/",run_dir=run_id_CNV_dir,run_NO=run_id,local_lims_dir=new_dem_do_anlysis_path[dem_02]['dir'],Project_info_list=run_id_CNV_project_list,emailreport=email))
        #os.system('wait')
        os.system("nohup sh {run_id_CNV_run_chromgo_sh} &".format(run_id_CNV_run_chromgo_sh=run_id_CNV_run_chromgo_sh))
def main():
    '''make command line interface'''
    parser = argparse.ArgumentParser(prog='auto_analysis_CNV',description='auto_analysis_CNV projects. ')
    parser.add_argument('--dem_path_file','-dem', action="store", required=True, help="Demulti_project_result_path.txt")
    parser.add_argument('--email','-e', action="store", required=True, help="The results to this email")
    args = parser.parse_args()
    dem_path_file = os.path.abspath(args.dem_path_file)
    email = args.email

    while True:
        new_dem_do_anlysis_path = judge_new_dempath(dem_path_file)
        if len(new_dem_do_anlysis_path):
            prepare_do_anlysis(new_dem_do_anlysis_path, email)
        else:
            continue
        time.sleep(300)

if __name__ == '__main__':
    main()