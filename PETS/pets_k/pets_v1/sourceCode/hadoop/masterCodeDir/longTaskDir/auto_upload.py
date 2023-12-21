#!/usr/local/bin/python
# coding:utf-8

import time
import os
import base64
import logging
from MyLib.connect_sql import ConnectSQL
from MyLib.parseData import doCommand


def checkUserList(conn, userName):
    # Query user list
    db = 'DeIdService'
    tbl = 'T_Member'
    sqlCommand = """
    select * from {}.{};
    """.format(db, tbl)
    sqlResult = conn.doSqlCommand(sqlCommand)
    userList = [user["username"] for user in sqlResult["fetchall"]]

    result = dict()
    result["result"] = False

    if userName in userList:
        result["result"] = True
        return result
    else:
        return result


def scanFiles(path_, pri_user=None):
    if pri_user is not None:
        userList = [pri_user]
    else:
        # get user list
        userList = os.listdir(path_)

    totalUserResult = dict()

    for user in userList:

        totalUserResult[user] = dict()
        # Get project without log
        projectList = [file for file in os.listdir(os.path.join(path_, user)) if file != user+".log"]

        for project in projectList:
            totalUserResult[user][project] = dict()
            totalUserResult[user][project]["isFile"] = False

            # Get file
            filesList = [file for file in os.listdir(os.path.join(path_, user, project))]
            if len(filesList) > 0:
                totalUserResult[user][project]["isFile"] = True

                # Get and filter csv file
                csvFiles = list()
                otherFiles = list()
                for file in filesList:
                    if file[-4:] == ".csv":
                        csvFiles.append(file)
                    else:
                        otherFiles.append(file)
                totalUserResult[user][project]["csvFiles"] = csvFiles
                totalUserResult[user][project]["otherFiles"] = otherFiles

    return totalUserResult

def setupLogger(name, log_file, level=logging.INFO):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    handler = logging.FileHandler(log_file, mode='w')
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    if (logger.hasHandlers()):
        logger.handlers.clear()
    logger.addHandler(handler)

    return logger


def main():

    global PATH, sys_logger
    PATH = "/root/data/input_auto_upload"
    sleepTime = 30

    sysLogName = "/root/proj_/longTaskDir/log/auto_upload.log"
    sys_logger = setupLogger('sysadmin', sysLogName)

    checkWarnDict = dict()

    while True:
        # Scan file
        scanResult = scanFiles(PATH)

        # Calculate number of file in each user.
        fileNumber = 0
        userFileList = list()
        for user in scanResult:
            numofFileUser = sum([scanResult[user][project]['isFile'] for project in scanResult[user]])
            if numofFileUser > 0:
                fileNumber += sum([scanResult[user][project]['isFile'] for project in scanResult[user]])
                userFileList.append(user)

        # If there is no new files, then wait 60 sec and continue next loop.
        if fileNumber == 0:
            time.sleep(sleepTime)
            continue
        # For those users who have files, go on next step.
        else:
            for user in userFileList:
                # Create logging for user
                userLogName = os.path.join(PATH, user, user+".log")
                user_logger = setupLogger(user, userLogName)
                msg = "Found new files in user: {}".format(user)
                sys_logger.info(msg)
                user_logger.info(msg)


                # If there is new file, then check user authority
                # Connect mysql
                try:
                    conn = ConnectSQL()
                except Exception as e:
                    msg = 'Connect mysql error: {0}'.format(str(e))
                    sys_logger.debug(msg)
                    continue

                userListResult = checkUserList(conn, user)

                # If checkUserList fail, then continue check next user (next for loop)
                if not userListResult["result"]:
                    msg = "User: {} does not have authority. " \
                          "Please create user or contact admin.".format(user)
                    sys_logger.info(msg)
                    user_logger.info(msg)
                    time.sleep(sleepTime)
                    continue

                for project in scanResult[user]:

                    # Check if there is new file
                    if not scanResult[user][project]['isFile']:
                        msg = "There is no new files in project: {}".format(project)
                        sys_logger.info(msg)
                        user_logger.info(msg)
                        continue

                    # Check if files are csv
                    if len(scanResult[user][project]["otherFiles"]) > 0:
                        msg = "Upload file should be csv, these files in '{0}'can not " \
                              "be uploaded: {1}".format(project, ",".join(scanResult[user][project]['otherFiles']))
                        sys_logger.info(msg)
                        user_logger.info(msg)

                    if len(scanResult[user][project]["csvFiles"]) > 0:
                        msg = "Found csv file in '{0}', which will be " \
                              "uploaded: {1}".format(project, ",".join(scanResult[user][project]['csvFiles']))
                        sys_logger.info(msg)
                        user_logger.info(msg)

                        sparkCode = "/root/proj_/longTaskDir/importAuto.py"

                        for tbl in scanResult[user][project]['csvFiles']:
                            # Upload tbl
                            try:
                                importListEncode = base64.b64encode(tbl.encode())
                                user_logger.debug(importListEncode)
                                commandList = ["spark-submit", sparkCode, PATH, user, project, importListEncode]
                                result = doCommand(commandList)
                                msg = "File upload succeed: (User, Project, File) = " \
                                      "({0},{1},{2}). {3}".format(user, project, tbl, result)
                                sys_logger.info(msg)
                                user_logger.info(msg)
                            except Exception as e:
                                msg = 'Upload table error: {0}'.format(str(e))
                                sys_logger.debug(msg)
                                continue

                            # Delete tbl
                            try:
                                path = os.path.join(PATH, user, project, tbl)
                                result = doCommand(["rm", "-f", path])
                                msg = "File delete succeed: (User, Project, File) = " \
                                  "({0},{1},{2}). {3}".format(user, project, tbl, result)
                                sys_logger.info(msg)
                                user_logger.info(msg)
                            except Exception as e:
                                msg = 'Delete table error: {0}'.format(str(e))
                                sys_logger.debug(msg)
                                continue
            time.sleep(sleepTime)

if __name__ == "__main__":
    main()
