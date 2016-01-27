#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import ConfigParser
import xml.dom.minidom
import codecs
import re
from exceptions import RuntimeError
import time


# Check whether the drawable file name is valid
def isValidDrawableFileName(fileName):
    # The extension of drawable file must be png, xml or jpg.
    # If the file extension is not one of the three, return False
    if not fileName.endswith('.xml') \
            and not fileName.endswith('.png')\
            and not fileName.endswith('jpg'):
        return False
    # Get the dots count in file name
    dotCount = fileName.count('.')
    # The dots count should be 1 or 2
    if dotCount == 0 or dotCount > 2:
        return False
    # If the dots count is 2, the file must be a NinePatch drawable.
    # That means the file name must ends with .9.png
    if dotCount == 2 and not fileName.endswith('.9.png'):
        return False
    # The first character of the file name must be alphabetic or _
    if not fileName[0].isalpha() and fileName[0] != '_':
        return False
    # Remove the file extension
    if dotCount == 1:
        fileName = fileName[0:-4]
    else:
        fileName = fileName[0:-6]
    # The other characters must be _ or alphabetic or numerical
    for ch in fileName:
        if ch != '_' and not ch.isalnum():
            return False
    return True


# Check whether the resource file name is valid (For drawable file, use isValidDrawableFileName())
def isValidResFileName(fileName):
    # The extension of resource file must be xml
    if not fileName.endswith('.xml'):
        return False
    # Get the dots count in file name
    dotCount = fileName.count('.')
    # The dots count should be 1
    if dotCount != 1:
        return False
    # The first character of the file name must be alphabetic or _
    if not fileName[0].isalpha() and fileName[0] != '_':
        return False
    # Remove the file extension
    fileName = fileName[0:-4]
    # The other characters must be _ or alphabetic or numerical
    for ch in fileName:
        if ch != '_' and not ch.isalnum():
            return False
    return True


# Get a config parse
def getConfigParser():
    configFile = os.path.join(os.path.dirname(__file__), 'config.ini')
    if os.path.exists(configFile):
        parser = ConfigParser.ConfigParser()
        parser.read(configFile)
        return parser


# Check whether the project is an Eclipse project
def isEclipseProject(projectDir):
    manifestFile = os.path.join(projectDir, 'AndroidManifest.xml')
    return os.path.exists(manifestFile)


# Check whether the project is an Android Studio project
def isAndroidStudioProject(projectDir):
    manifestFile = os.path.join(projectDir, 'AndroidManifest.xml')
    gradleFile = os.path.join(projectDir, 'build.gradle')
    if os.path.exists(manifestFile):
        return False
    else:
        return os.path.exists(gradleFile)


# Get the resource folder path
def getResPathList(isEclipse, projectDir):
    resPath = []
    if isEclipse:
        resPath.append(os.path.join(projectDir, 'res'))
        return resPath
    else:
        cfgFile = os.path.join(projectDir, 'build.gradle')
        if os.path.exists(cfgFile):
            cfgFp = open(cfgFile, 'r')
            inSourceSetsCfg = False
            braceCount = 0
            for cfgLine in cfgFp:
                stripLine = cfgLine.strip()
                if stripLine.startswith('sourceSets'):
                    inSourceSetsCfg = True
                if inSourceSetsCfg:
                    pos = stripLine.find('resources.srcDirs')
                    if pos != -1:
                        stripLine = stripLine[pos + len('resources.srcDirs'):].lstrip()
                        assert len(stripLine) > 2
                        if stripLine[0:2] == '+=':
                            resPath.append(os.path.join(projectDir, 'src' + os.path.sep + 'main' + os.path.sep + 'res'))
                            stripLine = stripLine[2:]
                        stripLine = stripLine.lstrip(' [=').rstrip(']')
                        splitLine = stripLine.split(',')
                        for splitItem in splitLine:
                            splitItem = splitItem.strip(' \'"')
                            if len(splitItem) != 0:
                                if os.path.sep != '/':
                                    splitItem = splitItem.replace('/', os.path.sep)
                                elif os.path.sep != '\\':
                                    splitItem = splitItem.replace('\\', os.path.sep)
                                resPath.append(os.path.join(projectDir, splitItem))
                        break
                    braceCount += stripLine.count('{')
                    braceCount -= stripLine.count('}')
                    if braceCount <= 0:
                        break
            if len(resPath) == 0:
                resPath.append(os.path.join(projectDir, 'src' + os.path.sep + 'main' + os.path.sep + 'res'))
            return resPath
        else:
            resPath.append(os.path.join(projectDir, 'src' + os.path.sep + 'main' + os.path.sep + 'res'))
            return resPath


# Get the source code folder path
def getSrcPathList(isEclipse, projectDir):
    srcPath = []
    if isEclipse:
        cfgFile = os.path.join(projectDir, '.classpath')
        if os.path.exists(cfgFile):
            dom = xml.dom.minidom.parse(cfgFile)
            root = dom.documentElement
            items = root.getElementsByTagName('classpathentry')
            for item in items:
                itemKind = item.getAttribute('kind')
                if itemKind == 'src':
                    itemPath = item.getAttribute('path')
                    if itemPath != 'gen':
                        srcPath.append(os.path.join(projectDir, itemPath))
            return srcPath
        else:
            srcPath.append(os.path.join(projectDir, 'src'))
            return srcPath
    else:
        cfgFile = os.path.join(projectDir, 'build.gradle')
        if os.path.exists(cfgFile):
            cfgFp = open(cfgFile, 'r')
            inSourceSetsCfg = False
            braceCount = 0
            for cfgLine in cfgFp:
                stripLine = cfgLine.strip()
                if stripLine.startswith('sourceSets'):
                    inSourceSetsCfg = True
                if inSourceSetsCfg:
                    pos = stripLine.find('java.srcDirs')
                    if pos != -1:
                        stripLine = stripLine[pos + len('java.srcDirs'):].lstrip()
                        assert len(stripLine) > 2
                        if stripLine[0:2] == '+=':
                            temp = os.path.join(projectDir, 'src' + os.path.sep + 'main' + os.path.sep + 'java')
                            srcPath.append(temp)
                            stripLine = stripLine[2:]
                        stripLine = stripLine.lstrip(' [=').rstrip(']')
                        splitLine = stripLine.split(',')
                        for splitItem in splitLine:
                            splitItem = splitItem.strip(' \'"')
                            if len(splitItem) != 0:
                                if os.path.sep != '/':
                                    splitItem = splitItem.replace('/', os.path.sep)
                                elif os.path.sep != '\\':
                                    splitItem = splitItem.replace('\\', os.path.sep)
                                srcPath.append(os.path.join(projectDir, splitItem))
                        break
                    braceCount += stripLine.count('{')
                    braceCount -= stripLine.count('}')
                    if braceCount <= 0:
                        break
            if len(srcPath) == 0:
                srcPath.append(os.path.join(projectDir, 'src' + os.path.sep + 'main' + os.path.sep + 'java'))
            return srcPath
        else:
            srcPath.append(os.path.join(projectDir, 'src' + os.path.sep + 'main' + os.path.sep + 'java'))
            return srcPath


# Get all configured resources in resources folder
def getConfiguredValueRes(resPathList, resTypes):
    resDic = {resType: [] for resType in resTypes}
    for resPath in resPathList:
        # Iterate through all the files in resources folder.
        for (parent, _, fileNames) in os.walk(resPath):
            for fileName in fileNames:
                # If the file is not an xml file
                if not fileName.endswith('.xml'):
                    continue
                # Parse the xml
                fileFullPath = os.path.join(parent, fileName)
                dom = xml.dom.minidom.parse(fileFullPath)
                root = dom.documentElement
                # Iterate through all resource types. Find the type nodes in the file.
                for resType in resTypes:
                    resTypedList = resDic[resType]
                    items = root.getElementsByTagName(resType)
                    for item in items:
                        itemName = item.getAttribute('name')
                        if itemName is not None and itemName != '':
                            resTypedList.append(itemName)
                    #  Find the item nodes in the file.
                    itemItems = root.getElementsByTagName('item')
                    for item in itemItems:
                        # record the name if the type equals with the resource type
                        if item.getAttribute('type') == resType:
                            itemName = item.getAttribute('name')
                            if itemName is not None and itemName != '':
                                resTypedList.append(itemName)
    return resDic


def getConfiguredFileRes(resPathList, resTypes):
    resDic = {resType: [] for resType in resTypes}
    for resType in resTypes:
        resFolders = []
        for resPath in resPathList:
            (_, folders, _) = os.walk(resPath).next()
            for folder in folders:
                if folder == resType or folder.startswith(resType + '-'):
                    resFolders.append(os.path.join(resPath, folder))
        # Iterate through all folders
        resNameList = resDic[resType]
        for folder in resFolders:
            # Iterate through all files in the folder
            (_, _, fileNames) = os.walk(folder).next()
            for fileName in fileNames:
                # Check whether the file name is valid
                if resType == 'drawable':
                    if not isValidDrawableFileName(fileName):
                        continue
                else:
                    if not isValidResFileName(fileName):
                        continue
                # remove file extension
                dotPos = fileName.find('.')
                fileName = fileName[0:dotPos]
                # add the file name to the list
                resNameList.append(fileName)
    return resDic


def getUsedRes(resPathList, srcPathList, resTypes):
    resDic = {resType: [] for resType in resTypes}
    # Iterate through all resource folders
    for resPath in resPathList:
        for (parent, _, fileNames) in os.walk(resPath):
            for fileName in fileNames:
                # Ignore non xml file
                if not fileName.endswith('.xml'):
                    continue
                # Parser xml file
                fileFullPath = os.path.join(parent, fileName)
                fp = open(fileFullPath, 'r')
                fileContent = fp.read()
                fp.close()
                for resType in resTypes:
                    resUsedList = resDic[resType]
                    regex = re.compile(r'"@([\w.]+:)?%s/(\S+)"|>@([\w.]+:)?%s/(\S+)<' % (resType, resType))
                    findResults = regex.findall(fileContent)
                    for findItem in findResults:
                        if findItem[1] != '':
                            resUsedList.append(findItem[1])
                        if findItem[3] != '':
                            resUsedList.append(findItem[3])

    # Iterate through all source code folders
    for srcPath in srcPathList:
        for (parent, _, fileNames) in os.walk(srcPath):
            for fileName in fileNames:
                # Ignore non java code
                if not fileName.endswith('.java'):
                    continue
                # read java code to find used resource
                fileFullPath = os.path.join(parent, fileName)
                fp = open(fileFullPath, 'r')
                fileContent = fp.read()
                fp.close()
                for resType in resTypes:
                    resUsedList = resDic[resType]
                    regex = re.compile(r'[(+,=]\s*R\.%s\.(\S+?)\s*[+),;]' % resType)
                    findResults = regex.findall(fileContent)
                    for findItem in findResults:
                        if findItem != '':
                            resUsedList.append(findItem)
    return resDic


def addUnsedToLog(unusedList):
    for (resType, resList) in unusedList.items():
        logContent.append('unused %s :' % resType)
        for item in resList:
            logContent.append('  ' + item)


def getReadableTime():
    curTime = time.localtime()
    year = curTime[0]
    month = curTime[1]
    day = curTime[2]
    hour = curTime[3]
    minute = curTime[4]
    second = curTime[5]
    readableTime = '%d-%d-%d %d:%d:%d' % (year, month, day, hour, minute, second)
    return readableTime


def removeUnusedValueRes(resPathList, unusedDict):
    # Iterate through all resource folders
    for resPath in resPathList:
        for (parent, _, fileNames) in os.walk(resPath):
            for fileName in fileNames:
                # Ignore non xml file
                if not fileName.endswith('.xml'):
                    continue
                isChanged = False
                # Parser xml file
                fileFullPath = os.path.join(parent, fileName)
                dom = xml.dom.minidom.parse(fileFullPath)
                root = dom.documentElement
                for (unusedType, unusedList) in unusedDict.items():
                    # Find all nodes in xml with specific types
                    dimenItems = root.getElementsByTagName(unusedType)
                    for item in dimenItems:
                        itemName = item.getAttribute('name')
                        if itemName is not None and itemName in unusedList:
                            root.removeChild(item)
                            if not isChanged:
                                logContent.append('processing file ' + fileFullPath[len(resPath)+1:])
                                isChanged = True
                            logContent.append(' remove item ' + itemName)
                    # Find all item nodes in xml
                    itemItems = root.getElementsByTagName('item')
                    for item in itemItems:
                        # record the name if the type equals with the resource type
                        if item.getAttribute('type') == unusedType:
                            itemName = item.getAttribute('name')
                            if itemName is not None and itemName in unusedList:
                                root.removeChild(item)
                                if not isChanged:
                                    logContent.append('processing file ' + fileFullPath[len(resPath)+1:])
                                    isChanged = True
                                logContent.append(' remove item ' + itemName)
                # If the file is changed, we should save it.
                if isChanged:
                    # Three steps:
                    # 1. save the changed xml to a temp file
                    # 2. format the temp file
                    # 3. rename the temp file to orginal file
                    tempFile = fileFullPath + 'temp'
                    destFile = codecs.open(tempFile, 'w', 'utf-8')
                    dom.writexml(destFile, encoding='utf-8')
                    destFile.close()
                    dom.unlink()
                    replaceNewline(fileFullPath, tempFile)
                    os.remove(fileFullPath)
                    os.rename(tempFile, fileFullPath)
                    logContent.append(' save file')
                else:
                    dom.unlink()
                # If the file is empty, remove the file
                if isEmptyXML(fileFullPath):
                    os.remove(fileFullPath)
                    logContent.append(fileFullPath[len(resPath)+1:] + ' is empty and has been removed')


def removeUnusedFileRes(resPathList, unusedDict):
    for (unusedType, unusedList) in unusedDict.items():
        typedFolders = []
        for resPath in resPathList:
            (_, folders, _) = os.walk(resPath).next()
            # find all folders that matched the type
            for folder in folders:
                if folder == unusedType or folder.startswith(unusedType + '-'):
                    typedFolders.append(folder)
            # Iterate through all folders
            for folder in typedFolders:
                # Iterate through all files in the folder
                (parent, _, fileNames) = os.walk(os.path.join(resPath, folder)).next()
                for fileName in fileNames:
                    # Check whether the file name is valid
                    if unusedType == 'drawable':
                        isValidFile = isValidDrawableFileName(fileName)
                    else:
                        isValidFile = isValidResFileName(fileName)

                    if not isValidFile:
                            os.remove(os.path.join(parent, fileName))
                            logContent.append(fileName + ' is invalid ' + unusedType + ', and has been removed')
                            continue
                    # Remove the file extension
                    dotPos = fileName.find('.')
                    striptFileName = fileName[0:dotPos]
                    # Remove if the file is unused
                    if striptFileName in unusedList:
                        os.remove(os.path.join(parent, fileName))
                        logContent.append(fileName + ' is unused drawable, and has been removed')


# minidom have three problems after removeChild and writexml
# 1. the file encoding statement and the first item are at the same line
# 2. the file newline would be \n, no matter what the original file newline is
# 3. the position at the remove node would retain an empty line
# this function is used to solve the three problems
def replaceNewline(srcFile, destFile):
    if os.path.exists(srcFile) and os.path.exists(destFile):
        srcfp = open(srcFile, 'rU')
        srcLines = srcfp.readlines()
        srcNewl = srcfp.newlines
        srcfp.close()

        destfp = open(destFile, 'rU')
        destLines = destfp.readlines()
        destNewl = destfp.newlines
        destfp.close()
        # split the first line at ?> to two lines，or remove the encoding part if the original file haven't this
        if len(destLines) != 0:
            line0 = destLines[0]
            index = line0.find('?>')
            if index != -1 and index != len(line0) - 2:
                assert len(srcLines) != 0
                if srcLines[0].strip().startswith('<?xml version'):
                    destLines[0] = line0[:index+2] + destNewl
                    destLines.insert(1, line0[index+2:])
                else:
                    destLines[0] = line0[index+2:]
        srcLineCount = len(srcLines)
        destLineCount = len(destLines)
        removedLines = []
        if srcLineCount == destLineCount:
            for index in range(srcLineCount):
                srcLine = srcLines[index].strip()
                destLine = destLines[index].strip()
                if destLine == "" and srcLine != "":
                    removedLines.append(index)
        elif srcLineCount > destLineCount:
            srcIndex = 0
            destIndex = 0
            while True:
                if srcIndex >= srcLineCount or destIndex >= destLineCount:
                    break
                srcLine = srcLines[srcIndex].strip()
                destLine = destLines[destIndex].strip()
                # line equals, continue to next line
                if srcLine == destLine:
                    srcIndex += 1
                    destIndex += 1
                    continue
                # If the lines are not equal, check whether the dest line is empty,
                # if so, this is an empty line in dest file, caused by removeChild
                if destLine != "":
                    # 分别获取两个文件此行中的name字段，并判断name是否相等，如果name相等，则表示此行仍然是相等的
                    # minidom有一个bug，如果一个item有多个参数，保存的时候会自动按照字典顺序来保存，这样就和原先行不一样了
                    regex = re.compile('\s+name\s*=\s*"(\w+)"')
                    srcSearch = regex.search(srcLine)
                    destSearch = regex.search(destLine)
                    if srcSearch is not None and destSearch is not None:
                        srcName = srcSearch.group()[0]
                        destName = destSearch.group()[0]
                        if srcName == destName:
                            srcIndex += 1
                            destIndex += 1
                            continue
                    # names are not equals, raise exception
                    raise RuntimeError('destination file have unexpected differences with the original file')
                # find the first not empty line in the dest file after the current line
                for endEmptyLine in range(destIndex, destLineCount):
                    if destLines[endEmptyLine].strip() != "":
                        break
                # the no empty line number must be greate than the current dest line number
                if endEmptyLine == destIndex:
                    raise RuntimeError('this should not be happened')
                if endEmptyLine == destLineCount - 1 and destLines[endEmptyLine].strip() == "":
                    raise RuntimeError('this should not be happened')

                # get the line number in original file that equals the line in the next not empty line of dest file
                thisDestLine = destLines[endEmptyLine]
                for nextEqualLine in range(srcIndex, srcLineCount):
                    if srcLines[nextEqualLine] == thisDestLine:
                        break
                # the next equal line number must greate than the current line number
                if nextEqualLine == srcIndex:
                    raise RuntimeError('this should not be happened')
                # the next equal line number must less than the original file line count
                if nextEqualLine == srcLineCount - 1 and srcLines[nextEqualLine].strip() != thisDestLine:
                    raise RuntimeError('this should not be happened')
                # find the empty line in the original file and record the count
                srcEmptyCount = 0
                for tempLine in srcLines[nextEqualLine-1:srcIndex-1:-1]:
                    if tempLine.strip() != "":
                        break
                    srcEmptyCount += 1

                # record the line that should be removed
                for tempLineNum in range(destIndex, endEmptyLine - srcEmptyCount):
                    removedLines.append(tempLineNum)

                destIndex = endEmptyLine
                srcIndex = nextEqualLine
        else:
            raise RuntimeError('destination file have more lines than the original file')

        for lineNum in removedLines[::-1]:
            del destLines[lineNum]

        if srcNewl is not None and destNewl is not None and srcNewl != destNewl:
            for lineStr in destLines:
                lineStr = lineStr.rstrip(destNewl) + srcNewl

        destfp = open(destFile, 'w')
        destfp.writelines(destLines)
        destfp.close()


def isEmptyXML(xmlFileName):
    fp = open(xmlFileName, 'r')
    isEmpty = True
    for fileLine in fp:
        stripedLine = fileLine.strip()
        if stripedLine != "" \
                and not stripedLine.startswith('<?xml version')\
                and not stripedLine.startswith('<resources')\
                and not stripedLine.startswith('</resources>')\
                and not stripedLine.startswith('<!--'):
            isEmpty = False
            break
    return isEmpty


def process():
    configParser = getConfigParser()
    if configParser is None:
        return
    # Get the configurations
    projectDir = configParser.get('Dir', 'ProjectDir')
    isRemove = configParser.get('AndroidClean', 'RemoveUnused')
    isBackup = configParser.get('AndroidClean', 'Backup')
    if isRemove.lower() == 'true':
        isRemove = True
    else:
        isRemove = False
    if isBackup.lower() == 'true':
        isBackup = True
    else:
        isBackup = False

    # project dir is not exist, raise exception
    if not os.path.exists(projectDir):
        raise RuntimeError('Invalid project directory')
    # Check whether the project is Eclipse or Android Studio
    isEclipse = isEclipseProject(projectDir)
    isAndroidStudio = isAndroidStudioProject(projectDir)
    # not Eclipse project，and not Android Studio project, raise exception
    if not isEclipse and not isAndroidStudio:
        raise RuntimeError('Unknown project type')

    # get the resource folder and source code folder in the project
    resPathList = getResPathList(isEclipse, projectDir)
    srcPathList = getSrcPathList(isEclipse, projectDir)
    for resPath in resPathList:
        if not os.path.exists(resPath):
            raise RuntimeError('Cannot find resPath ' + resPath)
    for srcPath in srcPathList:
        if not os.path.exists(srcPath):
            raise RuntimeError('Cannot find src path ' + srcPath)

    logContent.append('Project dir: ' + projectDir)
    for resPath in resPathList:
        logContent.append('res dir: ' + resPath)
    for srcPath in srcPathList:
        logContent.append('src dir: ' + srcPath)

    # get configed resource
    valueTypes = ('dimen', 'string', 'color', 'style', 'array', 'bool', 'integer', 'string-array', 'integer-array')
    fileTypes = ('drawable', 'layout', 'anim', 'animator')
    configuredValueRes = getConfiguredValueRes(resPathList, valueTypes)
    configuredFileRes = getConfiguredFileRes(resPathList, fileTypes)

    # merge integer-array list and string-array list with array list
    configuredValueRes['array'] = configuredValueRes['array'] + configuredValueRes['string-array'] + configuredValueRes['integer-array']
    del configuredValueRes['string-array']
    del configuredValueRes['integer-array']

    # get use resource
    allTypes = tuple(set(valueTypes + fileTypes) - {'string-array', 'integer-array'})
    usedResDict = getUsedRes(resPathList, srcPathList, allTypes)

    # get unused resources
    unusedValueResDict = {}
    for (resType, typeList) in configuredValueRes.items():
        unusedValueResDict[resType] = list(set(typeList) - set(usedResDict[resType]))
    unusedFileResDict = {}
    for (resType, typeList) in configuredFileRes.items():
        unusedFileResDict[resType] = list(set(typeList) - set(usedResDict[resType]))

    # append the unused resources to log
    addUnsedToLog(unusedValueResDict)
    addUnsedToLog(unusedFileResDict)

    # remove unused resources in the project
    if isRemove:
        tempDict = {}
        for (unusedType, unusedList) in unusedValueResDict.items():
            if len(unusedList) != 0:
                tempDict[unusedType] = unusedList
        if len(tempDict) != 0:
            removeUnusedValueRes(resPathList, unusedValueResDict)

        tempDict.clear()
        for (unusedType, unusedList) in unusedFileResDict.items():
            if len(unusedList) != 0:
                tempDict[unusedType] = unusedList
        if len(tempDict) != 0:
            removeUnusedFileRes(resPathList, unusedFileResDict)


def saveToLog():
    logFile = 'AndroidResCleaner.log'
    # log file exists and not empty, open file with append mode
    if os.path.exists(logFile) and os.path.getsize(logFile) != 0:
        logFp = open(logFile, 'a+')
        logFp.write('\n')   # 追加模式下需要一个额外的换行，和上方的log分隔开
        logFp.writelines([i + '\n' for i in logContent])
    # log file does not exist or empty, open file with write mode
    else:
        logFp = open(logFile, 'w+')
        logFp.writelines([i + '\n' for i in logContent])
    logFp.close()

if __name__ == '__main__':
    logContent = []
    try:
        # start clean process
        logContent.append('------------------------------ ' + getReadableTime() + ' ------------------------------')
        process()
    except Exception, e:
        # append the exception message to log
        logContent.append(e.message)
    finally:
        # save log to file
        saveToLog()
        print 'done'
