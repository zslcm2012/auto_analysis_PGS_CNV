import re
import click
import os
import sys
import glob
import time
from lxml import etree
import subprocess
import zmail


def stat_demultiplex_result(htmlfile, platform, runid, machinecode, demultidir):
    html = etree.parse(htmlfile, etree.HTMLParser())
    demulti_content = html.xpath('//table')[2].xpath('.//tr')
    lane_info_list = []
    for row in demulti_content:
        tmplist = []
        for col in row:
            tmplist.append(col.text)
        lane_info_list.append(tmplist)
    # lane_info_list = [['Lane', 'Project', 'Sample', 'Barcode sequence', 'PF Clusters', '% of the', '% Perfect', '% One mismatch', 'Yield (Mbases)', '% PF', '% >= Q30', 'Mean Quality'],
    # ['1', 'Project_RDSZ_ZSJ_PGD_8_Gene_RD_6_20190219', '0_1_1_190219_01', 'TAGCTT', '403,808', '1.15', '100.00', 'NaN', '65', '100.00', '94.82', '34.59'].....]
    projdict, undemultilist = dict(), list()
    total_reads, total_q30, total_QS = 0, 0, 0
    for item in lane_info_list[1:]:
        readsnum = int(re.sub(",", "", item[4]))
        total_reads += readsnum
        total_q30 += float(item[10])
        total_QS += float(item[11])
        if 'Undetermined' in item:
            undemultilist.append('lane{num}={ratio}'.format(
                num=item[0], ratio=item[5]))
            continue
        projdict.setdefault(item[1], set()).add(item[2])
    projlist = sorted(projdict.keys())
    projstr_list, projstat_list = [], ["Project_Name\tSample_Counts"]
    for key in projlist:
        for sample in projdict[key]:
            projstr_list.append("{proj}\t{platform}\t{runid}\t{machineid}\t{sample}\t{runid}\t{demulti}/Unaligned/{proj}/{sample}".format(
                                proj=key, platform=platform, runid=runid, machineid=machinecode, sample=sample, demulti=demultidir))
        projstat_list.append("{proj}\t{count}".format(
            proj=key, count=str(len(projdict[key]))))
    mean_q30 = str(total_q30 / len(lane_info_list[1:]))
    mean_qs = str(total_QS / len(lane_info_list[1:]))
    statstr_list = ["Total_Cluster={:,}".format(total_reads), "Mean_q30={}".format(mean_q30), "Mean_Quality_Score_PF={}".format(mean_qs), "Undetermined_Ratio\n"]
    print(statstr_list, undemultilist)
    statstr = "\n".join(statstr_list) + "\n".join(undemultilist) + "\n"
    reportstr = "\n".join(projstr_list) + "\n"
    reportstatstr = statstr + "\n" + "\n".join(projstat_list) + "\n"
    return (reportstr, statstr, reportstatstr)

def send_mail(mail, to, cc):
    server = zmail.server("bioinfo_report@yikongenomics.com", "Yikon123456")
    i = 3               
    #mail_struct = eval(mail)
    tomail = to.split(",") if re.findall(",", to) else to
    while i:            
        if cc:
            ccmail = cc.split(",") if re.findall(",", to) else cc
            status = ''
            try:
                status += server.send_mail(tomail, mail, ccmail)
            except Exception as e:
                print(e)
            time.sleep(30)
            if status:
                print("send mail successfully!!!")
                break
            else:       
                print("Failed to send email, please tring again to send later!!!")
                i = i -1
                time.sleep(30)
        else:
            status = ''
            try:
                status += server.send_mail(tomail, mail)
            except Exception as e:
                print(e)
            time.sleep(30)
            if status:
                print("send mail successfully!!!")
                break
            else:       
                print("Failed to send email, please tring again to send later!!!")
                i = i -1
                time.sleep(30)

@click.command()
@click.option('-l', '--logdir', required=True, help="the log dir")
@click.option('-p', '--platform', required=True, help="the sequence platform")
@click.option('-r', '--runid', required=True, help='runid info')
@click.option('-a', '--read', type=click.Choice(['True', 'False']), help='whether or not sending read1 demulti report')
@click.option('-d', '--demultidir', required=True, help='the demultiplex dir')
def main(logdir, platform, runid, demultidir, read):
    tomail = "swxxb@yikongenomics.com"
    ccmail = "baiyuanxiang@yikongenomics.cn,441605661@qq.com"
    i = 0
    while True:
        runfinish, errorDemlti = '', ''
        if os.path.exists(demultidir + "/Demultiplex.error"):
            with open(demultidir + "/Demultiplex.error") as error:
                tailrow = error.read()
                runfinish += "T" if re.findall("Processing completed with 0 errors and", tailrow) else 'F'
                print(runfinish, demultidir)
                errorDemlti += 'True' if re.findall(r"UseBasesMask formatting error. A mask must be specified for each read.", tailrow) else 'False'
        barcodehtml = glob.glob(
            demultidir + "/Unaligned/Reports/html/*/all/all/all/laneBarcode.html")
        if errorDemlti == "True":
            open(demultidir + "/demulti_index_setting_error", "w").writelines("该批次上机数据设置顺序有误，造成数据拆分不出数据，请进行查验排查！！！\n")
            mail1 = {"subject": "TEST:{plat}_{run}_上机测序设置错误！！！".format(
                plat=platform, run=runid), "content_text": "该批次上机数据设置顺序有误，造成数据拆分不出数据，请进行查验排查！！！\n"}
            send_mail(mail1, tomail, ccmail)
            #os.system("python3 {root}/auto_email.py -m {mail} -t {to} -c {cc}".format(root=sys.path[0], mail=mail1, to=tomail, cc=ccmail))
            break
        if barcodehtml and runfinish == "T":
            htmlfile = barcodehtml[0]
            machinecode = htmlfile.split("/")[-5]
            reportstr, statstr, reportstatstr = stat_demultiplex_result(
                htmlfile, platform, runid, machinecode, demultidir)
            open(demultidir + "/Sequencing_report", "w").writelines(reportstr)
            open(demultidir + "/Sequencing_report_Sta","w").writelines(reportstatstr)
            open(demultidir + "/Demulti_email", "w").writelines(statstr)
            subject = "{plat}_{run}_R1".format(plat=platform, run=runid) if read == "True" else "{plat}_{run}".format(plat=platform, run=runid)
            mail2 = {"subject":"TEST:{subj}_Demultiplex_Report".format(subj=subject), "content_text":statstr, 'attachments':[htmlfile],}
            send_mail(mail2, tomail, ccmail)
            os.system("echo \"{dem}\" >> {log}/Demulti_project_result_path.txt".format(dem=demultidir, log=logdir))
            #os.system("python3 {root}/auto_email.py -m {mail} -t {to} -c {cc}".format(root=sys.path[0], mail=mail2, to=tomail, cc=ccmail))
            break
        if i == 35:
            break
        i = i + 1
        time.sleep(300)

if __name__ == '__main__':
    main()
