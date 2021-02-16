#============================================================================================================================================================================================================================================================
import sys
import os
import shutil
BASE = "C:/your/target/directory/"
#============================================================================================================================================================================================================================================================
def getNewOutputPath():
    cnt = 1
    while os.path.exists("output"+str(cnt)+".pu"):
        cnt += 1
    return "output"+str(cnt)+".pu"
#============================================================================================================================================================================================================================================================
def deleteTempFile(path):
    # print("copy",path,"to COMBINE.pu")
    shutil.copyfile(path, "COMBINE.pu")
    cnt = 1
    while os.path.exists("output"+str(cnt)+".pu"):
        # print("delete","output"+str(cnt)+".pu")
        os.remove("output"+str(cnt)+".pu")
        cnt += 1
    # printParticipantInfo("COMBINE.pu")
#============================================================================================================================================================================================================================================================
def splitInputLine(line):
    # ' #PYTHON[mod1->mod2:func,relation/path/to/src/from/base/directory]
    indent = line[:line.find("'")]
    line = line[line.find("[")+1:]
    line = line[:line.find("]")]
    info, relpath = line.split(",")
    func = info[info.find(":")+1:]
    info = info[:info.find(":")]
    modfrom = info[:info.find("-")]
    modto = info[info.find(">")+1:]
    file = relpath + "/" + func + ".pu"
    # print(modfrom,modto,file)
    return indent,modfrom,modto,file
#============================================================================================================================================================================================================================================================
def extract(path):
    isExtract = False
    outputpath = getNewOutputPath()
    #------------------------------------------------------------------------------------------
    with open(outputpath, "w", encoding="utf-8") as output:
        with open(path, "r", encoding="utf-8") as input:
            for line in input:
                #------------------------------------------------------------------------------------------
                # 本スクリプト指定のフォーマットの行の場合、処理。
                if line.find("#PYTHON") != -1:
                    indent,modfrom,modto,file = splitInputLine(line)
                    #------------------------------------------------------------------------------------------
                    # 展開対象のファイルがあれば展開
                    if os.path.exists(BASE+file):
                        isExtract = True
                        with open(BASE+file, "r", encoding="utf-8") as input2:
                            for line2 in input2:
                                if line2.find("@startuml") == -1 and line2.find("@enduml") == -1:
                                    output.write(indent+line2.replace("entrypoint",modfrom))
                    #------------------------------------------------------------------------------------------
                    # 展開対象のファイルがなければ、そのファイル名をnoteとして出力
                    else:
                        print("[ERROR in "+modfrom+"]["+file+" is not exist!]")
                        if not os.path.exists(os.path.dirname(BASE+file)):
                            os.makedirs(os.path.dirname(BASE+file))
                        output.write(indent+"note over "+modto+" #9999ff"+"\n")
                        output.write(indent+file+"省略"+"\n")
                        output.write(indent+"end note"+"\n")
                #------------------------------------------------------------------------------------------
                # 本スクリプト指定のフォーマットの行でない場合、そのまま出力。
                else:
                    output.write(line)
    #------------------------------------------------------------------------------------------
    # 一回でも展開した行があれば、再帰呼び出し
    if isExtract:
        extract(outputpath)
    else:
        deleteTempFile(outputpath)
        print("Complete!!!")
#============================================================================================================================================================================================================================================================
def printParticipantInfo(path):
    modlist = list()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.find("->") != -1:
                if line.find("loop") == -1:
                # workarround
                    line = line.strip()
                    line = line[:line.find(":")]
                    mod1 = line[:line.find("-")]
                    mod2 = line[line.find(">")+1:]
                    if not mod1 in modlist:
                        modlist.append(mod1)
                    if not mod2 in modlist:
                        modlist.append(mod2)
    print("=====================================")
    for item in modlist:
        print("participant "+item)
    print(len(modlist))
    print("=====================================")
#============================================================================================================================================================================================================================================================
def createClassDiagramDraft(path, outpath):
    relations = list()
    classinfo = {}
    with open(path, "r", encoding="utf-8") as input:
        for line in input:
            if line.find("->") != -1 and line.find("-->") == -1:
                if line.find("loop") == -1:
                    line = line.strip()
                    method = line[line.find(":")+1:]
                    if method.find("(") != -1:
                        method = method[:method.find("(")]
                    line = line[:line.find(":")]
                    modfrom = line[:line.find("-")]
                    modto = line[line.find(">")+1:]
                    #--------------------------
                    if modfrom != modto:
                        temp = modfrom+"-->"+modto
                        if not temp in relations:
                            relations.append(temp)
                    #--------------------------
                    if modto not in classinfo:
                        classinfo[modto] = list()
                    if not method in classinfo[modto]:
                        classinfo[modto].append(method)
                    #--------------------------
    #-----------------------------------------------------------------------------------------------
    with open(outpath, "w", encoding="utf-8") as output:
        output.write("@startuml\n")
        for k in classinfo:
            output.write("class "+k+" {\n")
            for method in classinfo[k]:
                output.write("\t"+method+"()\n")
            output.write("}\n")
        for relation in relations:
            output.write(relation+"\n")
        output.write("@enduml\n")
#============================================================================================================================================================================================================================================================
if __name__ == "__main__":
   extract("COMBINE.pu")
#    createClassDiagramDraft("COMBINE.pu", "class.pu")
#============================================================================================================================================================================================================================================================
