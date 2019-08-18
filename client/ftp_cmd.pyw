#!python3
# coding:utf-8

"""
@project:FtpNews
@file:ftp_cmd
@author:zaxtyson
@time:2019/3/8 14:06
"""

import configparser
import ftplib
import os
import shutil
import subprocess
import time
import zipfile

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

FTP_HOST = config.get('ftp', 'host')
FTP_ENCODING = "GBK"
FTP_USER = config.get('ftp', 'username')
FTP_PASSWD = config.get('ftp', 'password')
FTP_HOME = config.get('ftp', 'home')
WEB_DOWN_DIR = config.get('others', 'cmd_dir')
LOG_FILE = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()) + ".log"


def log(info):
    try:
        with open(LOG_FILE, 'a+', encoding="gbk") as f:
            log_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            info = "[%s]    %s" % (log_time, str(info).replace("\\\\", "\\"))
            print(info)
            f.write(info)
            f.write("\n")
    except Exception:
        pass


def upload(local_file, ftp_dir):
    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASSWD)
        file_name = local_file.split("\\")[-1]
        ftp_dir = FTP_HOME + ftp_dir
        try:
            ftp.cwd(ftp_dir)
        except ftplib.error_perm:
            ftp.mkd(ftp_dir)
        fp = open(local_file, "rb")
        ftp.storbinary("STOR " + ftp_dir + "/" + file_name, fp, 1024)
        fp.close()
    except Exception as e:
        log(e)


def download(ftp_file, local_dir):
    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASSWD)
        local_file = local_dir + os.sep + ftp_file.split("/")[-1]
        if not os.path.exists(local_dir):
            os.mkdir(local_dir)
        fp = open(local_file, 'wb')
        ftp.retrbinary("RETR" + FTP_HOME + ftp_file, fp.write, 1024)
        fp.close()
    except Exception as e:
        log(e)


def get_cmd_list():
    try:
        download("/cmd/cmd.txt", WEB_DOWN_DIR)
        with open(WEB_DOWN_DIR + os.sep + "cmd.txt", "r") as f:
            txt = f.read()
        os.remove(WEB_DOWN_DIR + os.sep + "cmd.txt")
        cmd_list = []
        for line in txt.split("\n"):
            if len(line) > 2 and not line.strip().startswith("#"):
                cmd_list.append(line)
        return cmd_list
    except Exception as e:
        log(e)
        return None


def windows_cmd(command):
    try:
        out = open(LOG_FILE, "a+", encoding="gbk")
        p = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=out, stderr=out)
        p.wait()
        out.close()
    except Exception as e:
        log(e)


def unzip(zip_name, dst_dir):
    try:
        if not os.path.exists(dst_dir):
            os.mkdir(dst_dir)
        if zipfile.is_zipfile(zip_name):
            fz = zipfile.ZipFile(zip_name, 'r')
            for file in fz.namelist():
                fz.extract(file, dst_dir)
    except Exception as e:
        log(e)


def run_cmd(command):
    cmd = command.split()[0]
    args = command.split()[1:]

    log(">>> " + command)

    if cmd == "del":
        local_file = args[0]
        log("Delete %s " % local_file)
        if os.path.isdir(local_file):
            shutil.rmtree(local_file)
        elif os.path.isfile(local_file):
            os.remove(local_file)

    if cmd == "download":
        log("Download %s to %s" % (args[0], args[1]))
        download(args[0], args[1])

    if cmd == "unzip":
        log("Upzip %s to %s" % (args[0], args[1]))
        unzip(args[0], args[1])

    if cmd == "upload":
        log("Upload %s to %s" % (args[0], args[1]))
        upload(args[0], args[1])

    if cmd == "cmd":
        windows_cmd(" ".join(args))


for line in get_cmd_list():
    try:
        run_cmd(line)
    except Exception as e:
        log(e)

upload(LOG_FILE, "/cmd/log")
os.remove(LOG_FILE)
