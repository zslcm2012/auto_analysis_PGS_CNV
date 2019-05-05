#!/usr/bin/env python
#-*- coding: utf-8 -
'''
ftp自动下载、自动上传脚本，可以递归目录操作
'''
 
#作用： 检查FTP端 目录下的文件;  如果本地端没有，则从下载到本地；
 
from ftplib import FTP
import os
import datetime
import subprocess
import time
import socket
import sys
import glob
import click
import pathlib
import json
import re
import csv
from lxml import etree

            
class MyFtp(object):
    def __init__(self, hostaddr, username, password, monitordir, rootpath, port=21):
        self.hostaddr = hostaddr
        self.username = username
        self.password = password
        self.monitordir = monitordir
        self.rootpath = rootpath
        self.port = port
        self.ftp = FTP()
        self.file_list = []

    def __del__(self):
        self.ftp.close()

    def is_same_size(self, localfile, remotefile):
        try:
            remotefile_size = self.ftp.size(remotefile)
            localfile_size = os.path.getsize(localfile)
            return [0, 1][remotefile_size == localfile_size]
        except:
            return 0

    def upload_files(self, localpath):
        if localpath.is_dir():
            remotepath = re.sub(str(self.rootpath) + '/', '', str(localpath))
            try:
                self.ftp.mkd(remotepath)
            except Exception as e:
                print(">>>> {}".format(e))
            uploadFileList, limsFileList = list(), list()
            uploadFileList.extend([str(filepath) for filepath in localpath.glob("*") if filepath.is_file()])
            limsFileList.extend([str(self.rootpath /remotepath / item[0]) for item in self.ftp.mlsd(remotepath) if item[1]['type'] == 'file'])
            print(uploadFileList, limsFileList)
            print([item for item in uploadFileList if item not in limsFileList])
            for filepath in [item for item in uploadFileList if item not in limsFileList]:
                remotefile = re.sub(str(self.rootpath) + '/', '', filepath)
                try:
                    self.ftp.storbinary("STOR {}".format(remotefile), open(filepath, 'rb'))
                    print('已传送: {}'.format(filepath))
                except Exception as e:
                    print(">>>> {}".format(e))
            [self.upload_files(filepath) for filepath in localpath.glob("*") if filepath.is_dir()]

    def download_files(self, monitorpath):
        try:
            if not monitorpath.exists():
                os.makedirs(str(monitorpath))
            # store all files path
            remotepath = re.sub(str(self.rootpath) + '/', '', str(monitorpath))
            downloadFileList = list()
            downloadFileList.extend([(str(monitorpath / item[0]), str(pathlib.Path(remotepath) / item[0]))
                                     for item in self.ftp.mlsd(remotepath) if item[1]['type'] == 'file'])
            #[self.download_files(pathlib.Path(monitorpath) / item[0]) for item in self.ftp.mlsd(monitorpath) if item[1]['type'] == 'dir']
            # downloads all files
            print(monitorpath)
            print(downloadFileList)
            '''
            for secondarypath in [pathlib.Path(monitorpath) / item[0] for item in self.ftp.mlsd(monitorpath) if item[1]['type'] == 'dir']:
                if not secondarypath.exists():
                    os.makedirs(str(secondarypath))
                downloadFileList.extend([(str(self.rootpath / secondarypath / item[0]), str(secondarypath / item[0])) 
                                     for item in self.ftp.mlsd(secondarypath) if item[1]['type'] == 'file'])
            '''
            for localfile, remotefile in downloadFileList:
                print(localfile, remotefile)
                if self.is_same_size(localfile, remotefile):
                    print('%s 文件大小相同，无需下载' % localfile)
                else:
                    print('>>>>>>>>>>>>下载文件 %s ... ...' % localfile)
                    self.ftp.retrbinary("RETR {}".format(remotefile), open(localfile, 'wb').write)
            [self.download_files(pathlib.Path(monitorpath) / item[0]) for item in self.ftp.mlsd(remotepath) if item[1]['type'] == 'dir']
            # uploads new files
            print(monitorpath)
            self.upload_files(monitorpath)
        except Exception as e:
            print(e)
            #print('目录{}不存在，继续...'.format(monitorpath))

    def deal_error(self, errorinfo):
        timenow = time.localtime()
        datenow = time.strftime('%Y-%m-%d', timenow)
        print("{} 发生错误: {}".format(datenow, errorinfo))
        sys.exit(1)

    def login(self):
        try:
            socket.setdefaulttimeout(60)
            print("开始连接到 {}".format(self.hostaddr))
            self.ftp.connect(self.hostaddr, self.port)
            print("成功连接到 {}".format(self.hostaddr))
            print("开始登录到 {}" .format(self.hostaddr))
            self.ftp.login(self.username, self.password)
            print("成功登录到 {}".format(self.hostaddr))
            print(self.ftp.getwelcome())
        except Exception:
            self.deal_error("连接或登录失败")
        try:
            #self.ftp.delete("SH/ILLUMINA/NextSeq550/0449_SE55_190121_NB551093_0453_AHCTWGBGX9_01/test/test.json")
            #self.ftp.rmd("SH/ILLUMINA/NextSeq550/0449_SE55_190121_NB551093_0453_AHCTWGBGX9_01/test")
            now = int(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
            before = int((datetime.datetime.now() - datetime.timedelta(days=3)).strftime('%Y%m%d%H%M%S'))
            self.ftp.encoding = 'utf-8'
            monitorlist = list()
            for path in self.monitordir:
                if not (self.rootpath / path).exists():
                    os.makedirs(str(self.rootpath / path))
                ftpDirList = [pathlib.Path(path) / item[0] for item in self.ftp.mlsd(path) if item[1]['type'] == 'dir' and before<=int(item[1]['modify'])<=now]
                #tmppath = self.rootpath / path
                #monitorlist.extend([ftppath for ftppath in ftpDirList if self.rootpath / ftppath not in tmppath.iterdir()])
                monitorlist.extend([self.rootpath / path / item[0] for item in self.ftp.mlsd(path) if item[1]['type'] == 'dir' and before<=int(item[1]['modify'])<=now])
                print(ftpDirList)
                print(monitorlist)
            for monitorpath in monitorlist:
                self.download_files(monitorpath)
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                datenow = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
                #logpath = (self.rootpath / monitorpath).parent
                logpath = monitorpath.parent
                open(str(logpath) + '/log.txt', "a").writelines("{}>>>>>>>{}成功执行了备份\n".format(datenow, str(monitorpath)))
            return monitorlist
        except Exception as e:
            print(e)
        finally:
            self.ftp.quit()


class AutoDemutiplex(object):
    def __init__(self, demultiRootPath, illuminaFastqPath, logPath, monitorList):
        self.demuti = demultiRootPath
        self.illfaq = illuminaFastqPath
        self.logpath = logPath
        self.monitorlist = monitorList
    
    def mkdir(self, path):
        path = path.strip()
        if not os.path.exists(path):
            os.makedirs(path)
            return True
        else:
            print("{}已经存在，无需进行拆分任务投递！！！".format(path))
            return False
            #sys.exit(1)

    def get_newest_samplesheet_demultiplex(self):
        newestfilelist, errorinfolist = list(), list()
        errorfilelist = [line.strip() for line in open(self.logpath + "/log.error").readlines()]
        liblist = (['"PCR_free"', '"NIPT_PCR"', '"MALBAC_1_step_lib"', '"MALBAC_2_steps_amp_transposase_lib"', '"MALBAC_2_steps_amp_frag_lib"',
                    '"MALBAC_3_steps_amp_transposase_lib"', '"MALBAC_3_steps_amp_frag_lib"', '"transposase_lib"', '"MDA_amp_frag_lib"'])
        for path in self.monitorlist:
            runinfo = re.sub("_0[0-9]$", "", str(path).split("/")[-1])
            latestfilelist = glob.glob(str(path) + "/" + runinfo + "_[0-9][0-9].csv")
            latestfilelist.sort(key = lambda csvfile: os.path.getctime(csvfile))
            latestfile = latestfilelist[-1]
            #for latestfile in latestfilelist:
            if latestfile not in errorfilelist:
                #newestfilelist.append(latestfile)
                #for samplesheetfile in newestfilelist:
                tmpdict, lanedict = dict(), dict()
                libset, illegalcharset = set(), set()
                i = 0
                with open(latestfile) as ssf:
                    for tmplist in csv.reader(ssf):
                        if i < 2: continue
                        i = i + 1
                        # get the same index of sample
                        tmpdict.setdefault((tmplist[5], tmplist[1]), list()).append(tmplist[3])
                        # get the same sample in the same lane
                        lanedict.setdefault((tmplist[3], tmplist[1]), list()).append(1)
                        # judge CNV's lib_type
                        if re.findall("ONCPGD|PGS|PGD|MaReCs|NICS|CPGD|CNV", tmplist[-1]):
                            if tmplist[6] not in liblist: libset.add(tmplist[3])
                        # judge the illegalchar
                        [ illegalcharset.add(tmplist[3]) for item in tmplist if re.findall('[^a-zA-Z0-9_"]', item) ]
                errorbarcode = ["-".join(list(k)) + "___" + "/".join(v) for k, v in tmpdict.items() if len(v) >= 2]
                errorsample = { k[0] for k, v in lanedict.items() if len(v) >=2 }
                if errorbarcode:
                    errorinfolist.append(runinfo + ":" + "、".join(errorbarcode))
                    open(self.logpath + "/log.error", "a").writelines(latestfile + "\n")
                    runid = str(path).split("/")[6].split("_")[0]
                    mail = {
                        "subject": "TEST:" + runid + ":样本index重复！！！",
                        "content_text": "该批次存在样本index重复错误具体如下：\n  {id}:{error}\n  请在read1测序完成前尽快处理，并按照命名要求重新上传samplesheet文件！！！\n".format(id=runinfo, error="、".join(errorbarcode))
                        }
                    tomail = "bioinfo_report@yikongenomics.com"
                    ccmail = "baiyuanxiang@yikongenomics.cn,441605661@qq.com"
                    demultilog = self.logpath + "/" + runid
                    if not self.mkdir(demultilog): continue
                    shstr = "python3 {root}/auto_email.py -m {mail} -t {to} -c {cc}\n".format(root=sys.path[0], mail=mail, to=tomail, cc=ccmail)
                    open(demultilog + "/indexerro.sh", "w").writelines(shstr)
                    os.system("nohup sh {}/indexerro.sh 1 >> {}/indexerro.out 2>&1 &")
                elif errorsample or libset or illegalcharset or True:
                    tmpinfo = ""
                    tomail = "bioinfo_report@yikongenomics.com"
                    ccmail = "baiyuanxiang@yikongenomics.cn,441605661@qq.com"
                    if errorsample:
                        tmpinfo += "该批次存在单条lane含有相同样本，请再次进行确认！样本名称为：" + \
                            "、".join(list(errorsample)) + "\n"
                    if libset:
                        tmpinfo += "该批次存在样本建库方式书写错误，请再次进行确认！样本名称为：" + \
                            "、".join(list(libset)) + "\n"
                    if illegalcharset:
                        tmpinfo += "该批次存在样本行内容含有非法字符错误，请再次进行确认！样本名称为：" + \
                            "、".join(list(illegalcharset)) + "\n"
                    if tmpinfo:
                        runid = str(path).split("/")[6].split("_")[0]
                        demultilog = self.logpath + "/" + runid
                        self.mkdir(demultilog)
                        mail = {"subject": "TEST:" + runid +
                                ":样本Warning信息！！！", "content_text": tmpinfo}
                        shstr = "python3 {root}/auto_email.py -m {mail} -t {to} -c {cc}\n".format(
                            root=sys.path[0], mail=mail, to=tomail, cc=ccmail)
                        open(demultilog + "/sampleerro.sh","w").writelines(shstr)
                        os.system("nohup sh {}/sampleerro.sh 1 >> {}/sample_lib_char_erro.out 2>&1 &")
                #else:
                    newestfilelist.append(latestfile)
                    # do_demultiplex
                    limsplatform = ['Hiseq2500', 'Miseq', 'BES4000', 'NextSeq550', 'NextSeq550AR', 'MiniSeq']
                    demultiplatform = ['HiSeq2500_1', 'MiSeq_1', 'BioelectronSeq_4000_1', 'NextSeq550_1', 'NextSeq550AR_1', 'MiniSeq_BJ_1']
                    platformdict = dict(zip(limsplatform, demultiplatform))
                    limsfilelist = str(path).split("/")
                    #if len(limsfilelist) != 6:
                    #    print("该批次：{}，lims所在目录不符合设定标准！！！！".format(path))
                    #    sys.exit(1)
                    platform = platformdict[limsfilelist[5]]
                    bclrootpath = pathlib.Path(self.demuti) / platform
                    runindex = limsfilelist[6].split("_")[-2]
                    recipe =  "SE" if re.findall("SE", limsfilelist[6].split("_")[1], re.I) else "PE"
                    #basemask = "Y*,I6n*" if recipe == "SE" else "Y*,I6n*,Y*"
                    basemask = ["Y*,I6n", "Y*,I6n,Y*"][recipe == "PE"]
                    print(recipe, limsfilelist[6].split("_")[1])
                    print("basemask: " + basemask)
                    runid = limsfilelist[6].split("_")[0]
                    for bclpath in bclrootpath.iterdir():
                        bclindex = str(bclpath).split("_")[-1]
                        bclindex1 = bclindex[1:]
                        if runindex == bclindex or runindex == bclindex1:
                            rtacCompleteDir = str(pathlib.Path(self.demuti) / platformdict[limsfilelist[5]] / bclpath)
                            demultipath = str(pathlib.Path(self.illfaq) / platformdict[limsfilelist[5]] / runinfo)
                            demultilog = self.logpath + "/" + runid
                            print(self.illfaq, self.demuti)
                            print(rtacCompleteDir, demultipath)
                            #"#!/bin/bash\n#\n#$ -S /bin/bash\n"
                            configSh = ("cp {bcl}/RunInfo.xml {demulti}\n"
                                        "cp {bcl}/*unParameters.xml {demulti}\n"
                                        "cp -rf {bcl}/InterOp {demulti}\n".format(
                                        bcl=rtacCompleteDir, demulti=demultipath))
                            demutiplexSh = (
                                "/data/software/bcl2fastq2.20w/bin/bcl2fastq --input-dir {bcl}/Data/Intensities/BaseCalls/ "
                                "--output-dir {demulti}/Unaligned --sample-sheet {samplesheet} --runfolder-dir {demulti} --loading-threads 4 "
                                "--processing-threads 12 --writing-threads 8 --use-bases-mask {mask} --ignore-missing-bcl --ignore-missing-filter "
                                "--ignore-missing-positions --ignore-missing-control --barcode-mismatches 0\n")
                            reportSh = ("sleep 1m\n"
                                        "python3 {root}/auto_monitor_demulti_result.py -l {log} -p {platform} -r {runid} -a {read1} -d {dem}\n")
                            summarySh = (
                                "/data/software/bin/python {root}/parse_html_table.py --index {root}/Candidate_barcode_v6.1.txt --demultiplex_dir {dem}/Unaligned --fcid {fcid} --out_dir {locallims} --out_prefix {locallims}/{projid}\n"
                                "/data/software/bin/python {root}/csv2json.py -i {locallims}/{projid}_Lane_Summary.csv -o {locallims}/{projid}_Lane_Summary.json -f pretty\n"
                                "/data/software/bin/python {root}/csv2json.py -i {locallims}/{projid}_Lane_Summary_Overview.csv -o {locallims}/{projid}_Lane_Summary_Overview.json -f pretty\n"
                                "/data/software/bin/python {root}/csv2json.py -i {locallims}/{projid}_Top_Unknown_Barcodes.csv -o {locallims}/{projid}_Top_Unknown_Barcodes.json -f pretty\n")
                            #if recipe == "SE" and os.path.exists(rtacCompleteDir + "/RTAComplete.txt"):
                            if os.path.exists(rtacCompleteDir + "/RTAComplete.txt"):
                                self.mkdir(demultilog)
                                if not self.mkdir(demultipath) and os.path.exists("{}/{}.sh".format(demultipath, runid)): continue
                                #if not self.mkdir(demultilog) and os.path.exists(demultilog + "/Demultiplex.sh"): continue
                                tree = etree.parse(rtacCompleteDir + "/RunInfo.xml")
                                fcid = tree.xpath('.//Flowcell')[0].text
                                locallims, limsfile = os.path.dirname(latestfile), os.path.basename(latestfile)
                                projid = os.path.splitext(limsfile)[0]
                                with open("{}/{}.sh".format(demultipath, runid), "w") as runsh, open("{}/Demultiplex.sh".format(demultilog), "w") as demux:
                                    runsh.writelines(
                                        configSh + demutiplexSh.format(bcl=rtacCompleteDir, demulti=demultipath, samplesheet=latestfile, mask=basemask) + reportSh.format(log=self.logpath,
                                        dem=demultipath, root=sys.path[0], platform=platform, runid=runid, read1="False") + summarySh.format(root=sys.path[0], dem=demultipath, fcid=fcid, locallims=locallims, projid=projid))
                                    demux.writelines(
                                        "qsub -l ncpus=12 -d {dem} -e {dem}/Demultiplex.error -o {dem}/Demultiplex.log {dem}/{id}.sh\n".format(dem=demultipath, id=runid))
                                    print("sh {}/Demultiplex.sh".format(demultilog))
                                '''
                                with open("{}/report.sh".format(demultipath), "w") as report, open("{}/run_report.sh".format(demultipath), "w") as run:
                                    mailinfo1 = open("{}/demulti_index_setting_error".format(demultipath)).read()
                                    mailinfo2 = open("{}/Demulti_email".format(demultipath)).read()
                                    mail1 = {"subject": "TEST:{plat}_{run}_上机测序设置错误！！！".format(plat=platform, run=runid), "content_text": mailinfo1}
                                    attach = subprocess.getstatusoutput(
                                        "ls {}/Unaligned/Reports/html/*/all/all/all/laneBarcode.html".format(demultipath))[1]
                                    mail2 = {"subject": "TEST:{plat}_{run}_Demultiplex_Report".format(plat=platform, run=runid), "content_text": mailinfo2, 'attachments': attach} if attach else {}
                                    locallims, limsfile = os.path.dirname(latestfile), os.path.basename(latestfile)
                                    projid = os.path.splitext(limsfile)[0]
                                    if attach:
                                        fcid = attach.split("/")[-5]
                                        report.writelines(reportSh.format(
                                            q
                                            q
                                            dem=demultipath, root=sys.path[0], mail1=mail1, mail2=mail2, to=tomail, cc=ccmail, platform=platform, runid=runid, logpath=self.logpath) +
                                            summarySh.format(root=sys.path[0], dem=demultipath, fcid=fcid, locallims=locallims, projid=projid))
                                    else:
                                        report.writelines(reportSh.format(
                                            dem=demultipath, root=sys.path[0], mail1=mail1, mail2=mail2, to=tomail, cc=ccmail, platform=platform, runid=runid, logpath=self.logpath))
                                    run.writelines(
                                        "qsub -l ncpus=1 -d {dem} -e {dem}/report.error -o {dem}/report.log {dem}/report.sh\n".format(dem=demultipath))
                                '''
                                try:
                                    #subprocess.Popen("sh {}/Demultiplex.sh".format(demultilog), stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
                                    os.system("chmod 775 {}/Demultiplex.sh".format(demultilog))
                                    #os.system("chmod 775 {}/run_report.sh".format(demultipath))
                                    #time.sleep(10)
                                    subprocess.call("/usr/bin/bash -c {demu}/Demultiplex.sh".format(demu=demultilog), shell=True)
                                    #subprocess.call("/usr/bin/bash -c {demu}/run_report.sh".format(demu=demultipath), shell=True)
                                    #e = subprocess.call(["/usr/bin/bash", "-c", "qsub {dem}/{id}.sh".format(dem=demultipath, id=runid)])
                                    #e = os.system("cd {demu} && sh {demu}/run.sh".format(demu=demultilog))
                                    #e = subprocess.getstatusoutput("sh {demu}/run.sh".format(demu=demultilog))
                                except Exception as e:
                                    print(e)
                            else:
                                deminfolist = list()
                                with open(latestfile) as nsf:
                                    for line in nsf.readlines():
                                        line = line.strip()
                                        if re.findall(r'^"\[Data\]"|^"FCID"', line):
                                            deminfolist.append(line)
                                        elif re.findall("ONCPGD|PGS|PGD|MaReCs|NICS|CPGD|CNV", line):
                                            deminfolist.append(line)
                                if len(deminfolist) >= 3 and (os.path.exists(rtacCompleteDir + "/RTARead2Complete.txt") or os.path.exists(rtacCompleteDir + "/Basecalling_Netcopy_complete_Read2.txt")):
                                    #demultipathR1 = self.demuti + "/R1_" + runinfo
                                    demultipathR1 = self.illfaq + "/" + platformdict[limsfilelist[5]] + "/R1_" + runinfo
                                    if not self.mkdir(demultipathR1) and os.path.exists("{}/{}.sh".format(demultipathR1, runid)): continue
                                    self.mkdir(demultilog)
                                    #if not self.mkdir(demultilog) and os.path.exists(demultilog + "/Demultiplex_R1.sh"): continue
                                    newsamplesheet = demultipathR1 + "/samplesheet.csv"
                                    open(newsamplesheet, "w").writelines("\n".join(deminfolist) + "\n")
                                    # tree = etree.parse(rtacCompleteDir + "/RunInfo.xml")
                                    # get read3 NumCycles ['3', '75', 'N']
                                    # read3NumCycles = int(tree.xpath('.//Read')[2].values()[1]) - 1
                                    # mask = "Y*,I6n,Y{num}n".format(num=str(read3NumCycles))
                                    configShR1 = ("cp {bcl}/RunInfo.xml {demulti}\n"
                                                  "cp {bcl}/*unParameters.xml {demulti}\n"
                                                  "cp -rf {bcl}/InterOp {demulti}\n".format(
                                                   bcl=rtacCompleteDir, demulti=demultipathR1))
                                    with open("{}/{}.sh".format(demultipathR1, runid), "w") as runsh, open("{}/Demultiplex_R1.sh".format(demultilog), "w") as demux:
                                        runsh.writelines(configShR1 + demutiplexSh.format(bcl=rtacCompleteDir, demulti=demultipathR1, samplesheet=newsamplesheet,
                                                mask="Y*,I6n,n*") + reportSh.format(dem=demultipathR1, log=self.logpath, root=sys.path[0], platform=platform, runid=runid, read1="True"))
                                        demux.writelines(
                                            "qsub -l ncpus=12 -d {dem} -e {dem}/Demultiplex.error -o {dem}/Demultiplex.log {dem}/{id}.sh\n".format(dem=demultipathR1, id=runid))
                                    '''
                                    with open("{}/report.sh".format(demultipathR1), "w") as report, open("{}/run_report.sh".format(demultipathR1), "w") as run:
                                        mailinfo2 = open("{}/Demulti_email".format(demultipathR1)).read()
                                        attach = subprocess.getstatusoutput(
                                            "ls {}/Unaligned/Reports/html/*/all/all/all/laneBarcode.html".format(demultipathR1))[1]
                                        mail2 = {"subject": "TEST:{plat}_{run}_R1_Demultiplex_Report".format(plat=platform, run=runid), "content_text": mailinfo2, 'attachments': attach} if attach else {}
                                        report.writelines(reportSh.format(
                                            dem=demultipathR1, root=sys.path[0], mail1={}, mail2=mail2, to=tomail, cc=ccmail,
                                            platform=platform, runid=runid, logpath=self.logpath))
                                        run.writelines(
                                            "qsub -l ncpus=1 -d {dem} -e {dem}/report.error -o {dem}/report.log {dem}/report.sh\n".format(dem=demultipathR1))
                                    '''
                                    try:
                                        os.system("chmod 775 {}/Demultiplex_R1.sh".format(demultilog))
                                        #os.system("chmod 775 {}/run_report.sh".format(demultipathR1))
                                        #time.sleep(10)
                                        subprocess.call("/usr/bin/bash -c {demu}/Demultiplex_R1.sh".format(demu=demultilog), shell=True)
                                        #subprocess.call("/usr/bin/bash -c {demu}/run_report.sh".format(demu=demultipathR1), shell=True)
                                    except Exception as e:
                                        print(e)
                                else:
                                    pass
                                    #if os.path.exists(rtacCompleteDir + "/RTAComplete.txt"):
        return (newestfilelist, errorinfolist)


@click.command()
@click.option("-j", "--jsonfile", required=True, help="The config of AliCloudLIMS file")
@click.option("-l", "--locallims", required=True, help="The local LIMS path")
@click.option("-d", "--localdemutiplex", required=True, help="the demutiplex dir rootpath")
@click.option("-b", "--localbcl", required=True, help="the local bcl dir")
@click.option("-g", "--logdirpath", required=True, help="the project log file path")
#@click.option("--config", "-c", required=True, type='string', help="The config of AliCloudLIMS monitor directory")
def main(jsonfile, locallims, localdemutiplex, localbcl, logdirpath):
    #rootPath = pathlib.Path('/data/LIMS_Data_Interaction')
    rootPath = pathlib.Path(locallims)
    configDict = json.load(open(jsonfile))
    monitorDir = [path for k, v in configDict.items() for path in v]
    print(monitorDir)
    # 配置如下变量
    hostaddr = '114.215.252.175' # ftp地址
    username = 'LIMS_Data_Interaction' # 用户名
    password = 'YkYk1212##' # 密码
    port  =  21   # 端口号
    while True:
        f = MyFtp(hostaddr, username, password, monitorDir, rootPath, port)
        monitorlist = f.login()
        demux = AutoDemutiplex(localbcl, localdemutiplex, logdirpath, monitorlist)
        newestfilelist, errorinfolist = demux.get_newest_samplesheet_demultiplex()
        time.sleep(900)

if __name__ == '__main__':
    main()
