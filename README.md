# AndroidResCleaner

## Description
As an Android developer, we must be familiar with the Android res folder in the project. In the development process, many kinds of resources are added into this folder. drawables, layouts, anims, animators etc. are added as independent files, other resources such as styles, strings, styles are added in xml files. With the development of the project, some resources may become deprecated and useless. These resources should be removed from the project, but somehow we may be forget to to this. One day, we may want to do something to make our project more cleaner and more smaller. But you will soon find that it's a truly tiresome and time-consuming work to identify and remove these useless resources.
This AndroidResCleaner tool can finish this work in a few seconds. It can find various useless resources and help you to remove them from your project.

## Features
1. It can identify the resources that are not used in any of the xmls or java source codes.
2. It can remove these useless resources from your project, if you set 'RemoveUnused' to true.
3. It can remove these useless resources from your project, and backup these files that have been changed for future review, if you set 'RemoveUnused' and 'backup' to true. The backup files have a .bk extension.
4. It can be applied to both Eclipse and Android Studio project. If your project is an Android Studio project, the 'ProjectDir' should be set to module path, not the project path.
5. Supported resource types: array integer-array string-array string style dimen bool integer color   drawable layout anim animator
6. All operations are logged into AndroidResCleaner.log. You can retrieve this file for more information. Especially, when you don't want AndroidResCleaner to remove useless resources automatically, by unset 'RemoveUnused' option, you should view this file to get the useless resources lists.

## Usage
1. AndroidResCleaner run with python 2.7 environment. Get python if you don't have. https://www.python.org/downloads/
2. Set the options in config.ini.
3. Run AndroidResCleaner with 'python AndroidResCleaner.py' in the command line. 

## Attentions
1. These resource types are unsupported: stylable attr id   transition menu xml raw
2. AndroidResCleaner cannot be applied to complied project. It cannot decompile jars, at present.
3. AndroidResCleaner doesn't support deep search for unused resources.
For example: dimen A is only referenced by dimen B, dimen B is unused. So diemn B will be removed, but dimen A won't. In order to remove dimen A, you can run AndroidResCleaner once again.
 