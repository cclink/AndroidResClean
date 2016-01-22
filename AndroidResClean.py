#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import ConfigParser
import xml.dom.minidom
import codecs
import re
from exceptions import RuntimeError
import time

# 判断资源文件名是否有效
def isValidDrawableFileName(fileName):
    # 不是指定扩展名的文件（png，xml，jpg），返回False
    if not fileName.endswith('.xml') \
        and not fileName.endswith('.png')\
        and not fileName.endswith('jpg'):
        return False
    dotCount = fileName.count('.')
    # 文件名不符合要求（包含两个以上点，或者没有.），返回False
    if dotCount == 0 or dotCount > 2:
        return False
    # 文件名不符合要求（包含两个点，但不是.9.png的后缀），返回False
    if dotCount == 2 and not fileName.endswith('.9.png'):
        return False
    # 文件名不符合要求（首字母不是_，且不是字母），返回False
    if not fileName[0].isalpha() and fileName[0] != '_':
        return False
    # 去掉文件名后缀
    if dotCount == 1:
        fileName = fileName[0:-4]
    else:
        fileName = fileName[0:-6]
    # 文件名不符合要求（包含不是字母，且不是_的字符），返回False
    for ch in fileName:
        if ch != '_' and not ch.isalnum():
            return False
    return True
    
# 判断资源文件名是否有效
def isValidResFileName(fileName):
    # 不是指定扩展名的文件（xml），返回False
    if not fileName.endswith('.xml'):
        return False
    dotCount = fileName.count('.')
    # 文件名不符合要求（包含一个以上点，或者没有.），返回False
    if dotCount != 1:
        return False
    # 文件名不符合要求（首字母不是_，且不是字母），返回False
    if not fileName[0].isalpha() and fileName[0] != '_':
        return False
    # 去掉文件名后缀
    fileName = fileName[0:-4]
    # 文件名不符合要求（包含不是字母，且不是_的字符），返回False
    for ch in fileName:
        if ch != '_' and not ch.isalnum():
            return False
    return True
    
# 获取配置文件解释器
def getConfigParser() :
    configFile = os.path.join(os.path.dirname(__file__), 'config.ini')
    if os.path.exists(configFile):
        parser = ConfigParser.ConfigParser()
        parser.read(configFile)
        return parser

# 判断是否是Eclipse的工程
def isEclipseProject(projectDir):
    manifestFile = os.path.join(projectDir, 'AndroidManifest.xml')
    return os.path.exists(manifestFile)

# 判断是否是AndroidStudio的工程
def isAndroidStudioProject(projectDir):
    manifestFile = os.path.join(projectDir, 'AndroidManifest.xml')
    gradleFile = os.path.join(projectDir, 'build.gradle')
    if os.path.exists(manifestFile):
        return False
    else:
        return os.path.exists(gradleFile)
    
def getResPath(isEclipse, projectDir):
    if isEclipse:
        path = os.path.join(projectDir, 'res')
        return path
    else:
        path = os.path.join(projectDir, 'src' + os.path.sep + 'main' + os.path.sep + 'res')
        return path

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
                            srcPath.append(os.path.join(projectDir, 'src' + os.path.sep + 'main' + os.path.sep + 'java'))
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

def getResConfiged(resPath, resTypes):
    resDic = {resType:[] for resType in resTypes}
    # 遍历dimensDirctory目录下所有的文件
    for (parent, _, fileNames) in os.walk(resPath):
        for fileName in fileNames:
            # 不是xml文件，不做处理
            if not fileName.endswith('.xml'):
                continue
            # 解析xml文件
            fileFullPath = os.path.join(parent, fileName)
            dom = xml.dom.minidom.parse(fileFullPath)
            root = dom.documentElement
            # 遍历所有类型，找出所有的指定类型的节点
            for resType in resTypes:
                resTypedList = resDic[resType]
                items = root.getElementsByTagName(resType)
                for item in items:
                    itemName = item.getAttribute('name')
                    if itemName != None and itemName != '':
                        resTypedList.append(itemName)
                # 找出所有的指定类型的节点所有的item节点
                itemItems = root.getElementsByTagName('item')
                for item in itemItems:
                    # 如果item节点的type是指定的类型，则需要记录该节点的名字
                    if item.getAttribute('type') == resType:
                        itemName = item.getAttribute('name')
                        if itemName != None and itemName != '':
                            resTypedList.append(itemName)
    return resDic

def getResConfigedNotInValues(resPath, resTypes):
    resDic = {resType:[] for resType in resTypes}
    for resType in resTypes:
        resFolders = []
        (_, folders, _) = os.walk(resPath).next()
        for folder in folders:
            if folder == resType or folder.startswith(resType + '-'):
                resFolders.append(folder)
        # 遍历所有的layout文件夹
        resNameList = resDic[resType]
        for folder in resFolders:
            # 遍历layout文件夹下所有的文件
            (_, _, fileNames) = os.walk(os.path.join(resPath, folder)).next()
            for fileName in fileNames:
                # 不是有效的资源文件名，不做处理(对drawable类型，其文件名规则和其他的略有不同)
                if resType == 'drawable':
                    if not isValidDrawableFileName(fileName):
                        continue
                else:
                    if not isValidResFileName(fileName):
                        continue
                # 去掉文件名后缀
                dotPos = fileName.find('.')
                fileName = fileName[0:dotPos]
                # 将文件名添加到列表中
                resNameList.append(fileName)
    return resDic

def getUsedRes(resPath, srcPathList, resTypes):
    resDic = {resType:[] for resType in resTypes}
    # 遍历resPath目录下所有的文件
    for (parent, _, fileNames) in os.walk(resPath):
        for fileName in fileNames:
            # 不是xml文件，不做处理
            if not fileName.endswith('.xml'):
                continue
            # 读取xml文件
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
                    
    # 遍历srcPath目录下所有的文件
    for srcPath in srcPathList:
        for (parent, _, fileNames) in os.walk(srcPath):
            for fileName in fileNames:
                # 不是java文件，不做处理
                if not fileName.endswith('.java'):
                    continue
                # 读取java文件
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
    
def addUnsedToLog(unusedList, logContent):
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
    
def removeUnused(resPath, unusedDict, logContent):
    # 遍历dimensDirctory目录下所有的文件
    for (parent, _, fileNames) in os.walk(resPath):
        for fileName in fileNames:
            # 不是xml文件，不做处理
            if not fileName.endswith('.xml'):
                continue
            isChanged = False
            # 解析xml文件
            fileFullPath = os.path.join(parent, fileName)
            dom = xml.dom.minidom.parse(fileFullPath)
            root = dom.documentElement
            for (unusedType, unusedList) in unusedDict.items():
                # 找出所有的指定类型的节点
                dimenItems = root.getElementsByTagName(unusedType)
                for item in dimenItems:
                    itemName = item.getAttribute('name')
                    if itemName != None and itemName in unusedList:
                        root.removeChild(item)
                        if not isChanged:
                            logContent.append('processing file ' + fileFullPath[len(resPath)+1:])
                            isChanged = True
                        logContent.append(' remove item ' + itemName)
                # 找出所有的指定类型的节点所有的item节点
                itemItems = root.getElementsByTagName('item')
                for item in itemItems:
                    # 如果item节点的type是指定的类型，则需要记录该节点的名字
                    if item.getAttribute('type') == unusedType:
                        itemName = item.getAttribute('name')
                        if itemName != None and itemName in unusedList:
                            root.removeChild(item)
                            if not isChanged:
                                logContent.append('processing file ' + fileFullPath[len(resPath)+1:])
                                isChanged = True
                            logContent.append(' remove item ' + itemName)
            # 如果文件变化，则需要保存文件
            if isChanged:
                # 保存文件时，先将文件保存到临时文件中，然后对临时文件进行格式化，然后再删除原先的文件，最后将临时文件重命名为原先的文件名
                tempFile = fileFullPath + 'temp'
                destFile = codecs.open(tempFile, 'w', 'utf-8')
                dom.writexml(destFile, encoding='utf-8')
                destFile.close()
                dom.unlink()
                replaceNewline(fileFullPath, tempFile)
                os.remove(fileFullPath)
                os.rename(tempFile, fileFullPath)
                logContent.append(' save file')
                # 删除空白的xml
                if isEmptyXML(fileFullPath):
                    os.remove(fileFullPath)
                    logContent.append(' the file is empty and has been removed')
            else:
                dom.unlink()
                # 删除空白的xml
                if isEmptyXML(fileFullPath):
                    os.remove(fileFullPath)
                    logContent.append('processing file ' + fileFullPath[len(resPath)+1:])
                    logContent.append(' the file is empty and has been removed')

def removeUnusedNotInValues(resPath, unusedDict, logContent):
    for (unusedType, unusedList) in unusedDict.items():
        drawableFolders = []
        (_, folders, _) = os.walk(resPath).next()
        # 查找所有的drawable文件夹
        for folder in folders:
            if folder == unusedType or folder.startswith(unusedType + '-'):
                drawableFolders.append(folder)
        # 遍历所有的drawable文件夹
        for folder in drawableFolders:
            # 遍历drawable文件夹下所有的文件
            (parent, _, fileNames) = os.walk(os.path.join(resPath, folder)).next()
            for fileName in fileNames:
                # 不是有效的资源文件名，不做处理(对drawable类型，其文件名规则和其他的略有不同)
                if unusedType == 'drawable':
                    if not isValidDrawableFileName(fileName):
                        os.remove(os.path.join(parent, fileName))
                        logContent.append(fileName + ' is invalid drawable, and has been removed')
                        continue
                else:
                    if not isValidResFileName(fileName):
                        os.remove(os.path.join(parent, fileName))
                        logContent.append(fileName + ' is invalid ' + unusedType + ', and has been removed')
                        continue

                # 去掉文件名后缀
                dotPos = fileName.find('.')
                striptFileName = fileName[0:dotPos]
                # 如果文件名在无用的资源列表中，删除该文件
                if striptFileName in unusedList:
                    os.remove(os.path.join(parent, fileName))
                    logContent.append(fileName + ' is unused drawable, and has been removed')
                
# minidom 在removeChild然后writexml后有三个问题
# 1. 文件头的编码声明会和第一个Item合并到同一行
# 2. 文件的换行符会统一变成\n，无论原先的换行符是什么
# 3. 文件中被删除的child位置上会留下一个空行
# 此函数就是用来对生成的xml进行格式化，让其可以保持原先xml的换行和格式
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
        # 将第一行从?>处拆分成两行，或者删除前面的xml编码信息
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
            srcIndex = 0;
            destIndex = 0;
            while True:
                if srcIndex >= srcLineCount or destIndex >= destLineCount:
                    break
                srcLine = srcLines[srcIndex].strip()
                destLine = destLines[destIndex].strip()
                # 相等行，继续下一行
                if srcLine == destLine:
                    srcIndex += 1
                    destIndex += 1
                    continue
                # 不相等，判断目标文件此行是否为空，如果不为空，说明两个文件之间存在非空行的差异
                if destLine != "":
                    # 分别获取两个文件此行中的name字段，并判断name是否相等，如果name相等，则表示此行仍然是相等的
                    # minidom有一个bug，如果一个item有多个参数，保存的时候会自动按照字典顺序来保存，这样就和原先行不一样了
                    regex = re.compile('\s+name\s*=\s*"(\w+)"')
                    srcSearch = regex.search(srcLine)
                    destSearch = regex.search(destLine)
                    if srcSearch != None and destSearch != None:
                        srcName = srcSearch.group()[0]
                        destName = destSearch.group()[0]
                        if srcName == destName:
                            srcIndex += 1
                            destIndex += 1
                            continue
                    # name不相等，raise异常
                    raise RuntimeError,'destination file have unexpected differences with the original file'
                # 从目标文件找到空行后面第一个非空行
                for endEmptyLine in range(destIndex, destLineCount):
                    if destLines[endEmptyLine].strip() != "":
                        break
                # 空行后的非空行行号必须大于空行行号，且小于目标文件最后一行
                if endEmptyLine == destIndex:
                    raise RuntimeError,'this should not be happened'
                if endEmptyLine == destLineCount - 1 and destLines[endEmptyLine].strip() == "":
                    raise RuntimeError,'this should not be happened'
                
                # 从源文件中查找和目标文件中空行后面的第一个非空行相等的行
                thisDestLine = destLines[endEmptyLine]
                for nextEqualLine in range(srcIndex, srcLineCount):
                    if srcLines[nextEqualLine] == thisDestLine:
                        break
                # 这个相等的行必须大于当前不等的行，小于源文件最后一行
                if nextEqualLine == srcIndex:
                    raise RuntimeError,'this should not be happened'
                if nextEqualLine == srcLineCount - 1 and srcLines[nextEqualLine].strip() != thisDestLine:
                    raise RuntimeError,'this should not be happened'
                # 由于源文件可能也存在有空白行，从后往前遍历，找出这些空白行，记录其数量
                srcEmptyCount = 0;
                for tempLine in srcLines[nextEqualLine-1:srcIndex-1:-1]:
                    if tempLine.strip() != "":
                        break
                    srcEmptyCount += 1

                # 添加需要删除的行号
                for tempLineNum in range(destIndex, endEmptyLine - srcEmptyCount):
                    removedLines.append(tempLineNum)
                
                destIndex = endEmptyLine
                srcIndex = nextEqualLine
        else:
            raise RuntimeError,'destination file have more lines than the original file'
            
        for lineNum in removedLines[::-1]:
            del destLines[lineNum]
            
        if srcNewl != None and destNewl != None and srcNewl != destNewl:
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
    
def process(logContent):
    configParser = getConfigParser()
    if configParser == None:
        return
    # 获取配置文件中配置的工程目录
    projectDir = configParser.get('Dir', 'ProjectDir')

    # 没有相应配置，返回
    if projectDir == None:
        raise RuntimeError,'Unknown parameters'
    if not os.path.exists(projectDir):
        raise RuntimeError,'Invalid parameters'
    # 判断工程是Eclipse还是Android Studio
    isEclipse = isEclipseProject(projectDir)
    isAndroidStudio = isAndroidStudioProject(projectDir)
    # 既不是Eclipse，也不是Android Studio
    if not isEclipse and not isAndroidStudio:
        raise RuntimeError,'Unknown project type'

    # 获取项目中res文件夹路径
    resPath = getResPath(isEclipse, projectDir)
    srcPathList = getSrcPathList(isEclipse, projectDir)
    if not os.path.exists(resPath):
        raise RuntimeError,'Cannot find resPath ' + resPath
    for srcPath in srcPathList:
        if not os.path.exists(srcPath):
            raise RuntimeError,'Cannot find src path ' + srcPath

    logContent.append('Project dir: ' + projectDir)
    logContent.append('res dir: ' + resPath)
    for srcPath in srcPathList:
        logContent.append('src dir: ' + srcPath)
    
    # 获取工程资源文件夹下配置的各项资源列表
    resConfigedInValues = getResConfiged(resPath, ('dimen', 'string','color', 'style', 'array', 'string-array', 'integer-array'))
    resConfigedNotValues = getResConfigedNotInValues(resPath, ('drawable', 'layout','anim', 'animator'))
    
    # 将integer-array和string-array合并到array中
    resConfigedInValues['array'] = resConfigedInValues['array'] + resConfigedInValues['string-array'] + resConfigedInValues['integer-array'] 
    del resConfigedInValues['string-array']
    del resConfigedInValues['integer-array']
    
    # 获取工程资源文件夹和代码文件夹下的已经使用的各项资源列表
    resUsedDict = getUsedRes(resPath, srcPathList, ('dimen', 'string','color', 'style', 'array', 'drawable', 'layout','anim', 'animator'))

    # 计算得到未使用的各项资源列表
    unusedInValuesDict = {}
    for (resType, typeList) in resConfigedInValues.items():
        unusedInValuesDict[resType] = list(set(typeList) - set(resUsedDict[resType]))
    unusedNotValuesDict = {}
    for (resType, typeList) in resConfigedNotValues.items():
        unusedNotValuesDict[resType] = list(set(typeList) - set(resUsedDict[resType]))
    
    # 将未使用的资源列表保存到log中
    addUnsedToLog(unusedInValuesDict, logContent)
    addUnsedToLog(unusedNotValuesDict, logContent)
    
    # 判断是否要删除不用的资源
    if configParser.has_option('AndroidClean', 'RemoveUnused'):
        isRemove = configParser.get('AndroidClean', 'RemoveUnused')
        if isRemove.lower() == 'true':
            tempDict = {}
            for (unusedType, unusedList) in unusedInValuesDict.items():
                if len(unusedList) != 0:
                    tempDict[unusedType] = unusedList
            if len(tempDict) != 0:
                removeUnused(resPath, unusedInValuesDict, logContent)
                
            tempDict.clear()
            for (unusedType, unusedList) in unusedNotValuesDict.items():
                if len(unusedList) != 0:
                    tempDict[unusedType] = unusedList
            if len(tempDict) != 0:
                removeUnusedNotInValues(resPath, unusedNotValuesDict, logContent)

def saveToLog(logContent):
    logFile = 'AndroidResClean.log'
    # 文件存在且不为空，用追加模式
    if os.path.exists(logFile) and os.path.getsize(logFile) != 0:
        logFp = open(logFile, 'a+')
        logFp.write('\n')   # 追加模式下需要一个额外的换行，和上方的log分隔开
        logFp.writelines([i + '\n' for i in logContent])
    # 文件不存在，或者为空，用覆盖模式
    else:
        logFp = open(logFile, 'w+')
        logFp.writelines([i + '\n' for i in logContent])
    logFp.close()
    
if  __name__ == '__main__':
    logContent = []
    try:
        # 开始清理
        logContent.append('------------------------------ ' + getReadableTime() + ' ------------------------------')
        process(logContent)
    except Exception,e:
        # 保存异常信息
        logContent.append(e.message)
    finally:
        # 保存log日志
        saveToLog(logContent)
        print 'done'