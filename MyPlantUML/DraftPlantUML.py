﻿#============================================================================================================================================================
import sys
sys.path.append('../MyLogger/')
sys.path.append('../MyDataBase/')
sys.path.append('../MyBaseSystem/')
from MyLogger import MyLogger
MyLogger = MyLogger.GetInstance()
from MyDataBase import MyDataBase
from MyBaseSystem import *
#============================================================================================================================================================
import re
import os
import glob
from bs4 import BeautifulSoup
import shutil
#============================================================================================================================================================
## @brief MyPlantUMLクラス
class MyPlantUML():
   @MyLogger.deco
   def __init__(self):
      self.samenamecnt = {}
      self.inputbase='./input/'
      self.outputbase='./output/'
      self.db_functions = MyDataBase.GetInstance('plantuml_functions.xlsx')
      self.db_defines = MyDataBase.GetInstance('plantuml_defines.xlsx')
      self.ignore_functions = []
      self.__InitializeColumn()
      self.__LoadFunctionList()
#============================================================================================================================================================
   @MyLogger.deco
   def SetIgnoreFunction(self, functions):
      self.ignore_functions += functions
      MyLogger.sakura(self.ignore_functions)
#============================================================================================================================================================
   @MyLogger.deco
   def __InitializeColumn(self):
      self.db_defines.DBAppendColumn(['compoundname', 'name', 'params', 'initializer', 'bodyfile', 'bodystart', 'bodyend'])
      self.db_defines.DBWrite()
      self.db_functions.DBAppendColumn(['compoundname', 'definition', 'argsstring', 'name', 'samenamecnt', 'bodyfile', 'bodystart', 'bodyend'])
      self.db_functions.DBWrite()
#============================================================================================================================================================
   @MyLogger.deco
   def __LoadFunctionList(self):
      self.db_functions.DBRead()
      self.db_functions.DBDropDuplicates('name')
      self.db_functions.DBFilter('samenamecnt', "1", mode='fullmatch')
      self.unique_functions = self.db_functions.GetDict().values()
      # MyLogger.sakura(self.unique_functions)
      self.db_functions.DBRead()
      self.all_functions = self.db_functions.GetDict()
#============================================================================================================================================================
   @MyLogger.deco
   def AnalyzeDoxygen(self, doxygenpath):
      self.db_functions.DBRead()
      files = [file for file in glob.glob(doxygenpath+'/**/*', recursive=True) if file.find('class_') != -1]
      # files = [file for file in glob.glob(doxygenpath+'/**/*', recursive=True) if file.find('.xml') != -1]
      self.temp_dict = self.db_functions.GetDict()
      MyLogger.SetFraction(len(files))
      for file in files:
         MyLogger.SetNumerator(files.index(file))
         self.__ParseFunctions(file)
         # self.__ParseDefines(file)
      self.db_functions.DBImportDict(self.temp_dict)
      self.__LoadFunctionList()
#============================================================================================================================================================
   @MyLogger.deco
   def __ParseFunctions(self, xmlpath):
      xml = ''.join(myopen(xmlpath, 'r').readlines())
      soup = BeautifulSoup(xml, 'lxml')
      componddef = soup.find('compounddef')
      if not componddef:
         MyLogger.warning('not found compoundname in ', xmlpath)
         return
      compoundname = componddef.find('compoundname').text
      compoundname = compoundname[compoundname.rfind(":")+1:]
      functions = componddef.find_all('memberdef', {'kind':'function'})
      for function in functions:
         definition = function.find('definition').text
         argsstring = function.find('argsstring').text
         name = function.find('name').text
         location = function.find('location')
         if not location.has_attr('bodyfile'):
            MyLogger.warning('not found bodyfile of ', definition)
            continue
         bodyfile = location['bodyfile']
         bodystart = location['bodystart']
         bodyend = location['bodyend']
         if not name in self.samenamecnt:
            self.samenamecnt[name] = 1
         else:
            self.samenamecnt[name] += 1
         self.db_functions.DBAppendRow([compoundname, definition, argsstring, name, self.samenamecnt[name], bodyfile, bodystart, bodyend], self.temp_dict)
#============================================================================================================================================================
   @MyLogger.deco
   def __ParseDefines(self, xmlpath):
      xml = ''.join(myopen(xmlpath, 'r').readlines())
      soup = BeautifulSoup(xml, 'lxml')
      componddef = soup.find('compounddef')
      if not componddef:
         MyLogger.warning('not found compoundname in ', xmlpath)
         return
      compoundname = componddef.find('compoundname').text
      defines = componddef.find_all('memberdef', {'kind':'define'})
      for define in defines:
         name = define.find('name').text
         if (params := define.find_all('param')):
            MyLogger.sakura("name",name)
            for param in params:
               MyLogger.sakura("param",param.text)
         if (initializer := define.find('initializer')):
            initializer = initializer.text
            MyLogger.sakura("initializer",initializer)
         # if not location.has_attr('bodyfile'):
         #    MyLogger.warning('not found bodyfile of ', definition)
         #    continue
         # bodyfile = location['bodyfile']
         # bodystart = location['bodystart']
         # bodyend = location['bodyend']
         # db_defines.DBAppendRow([compoundname, name, params, initializer, bodyfile, bodystart, bodyend])
#============================================================================================================================================================
   @MyLogger.deco
   def DraftUML(self):
      MyLogger.SetFraction(len(self.all_functions.items()))
      for index,values in self.all_functions.items():
         MyLogger.SetNumerator(index)
         compoundname = values['compoundname']
         definition = values['definition']
         argsstring = values['argsstring']
         name = values['name'][values['name'].rfind(":")+1:]
         samenamecnt = str(values['samenamecnt'])
         bodyfile = values['bodyfile']
         bodystart = int(values['bodystart'])-1
         bodyend = int(values['bodyend'])
         inputfile = self.inputbase+bodyfile
         outputfile = self.outputbase+bodyfile+'/'+name+"("+samenamecnt+').pu'
         MyLogger.sakura(outputfile)
         if not os.path.exists(os.path.dirname(outputfile)):
            os.makedirs(os.path.dirname(outputfile))
         if bodyend != -1:
            functionbody = myopen(inputfile, 'r').readlines()[bodystart:bodyend]
         else:
            functionbody = myopen(inputfile, 'r').readlines()[bodystart]
         functionbody = self.__CustomizeFunctionBody(functionbody, compoundname)
         with myopen(outputfile, 'w', encoding='utf-8') as f:
            f.write("' #######################################\n")
            f.write("' definition="+definition+"\n")
            f.write("' bodyfile="+bodyfile+"\n")
            f.write("' bodystart="+str(bodystart)+"\n")
            f.write("' bodyend="+str(bodyend)+"\n")
            f.write("' #######################################\n")
            f.write("@startuml\n")
            f.write("skinparam SequenceDividerFontSize 30\n")
            f.write("skinparam SequenceGroupFontSize 30\n")
            f.write("== " + compoundname + ":" + name + argsstring + " ==\n")
            f.write("activate " + compoundname + "\n")
            f.write("' #######################################\n")
            f.write(''.join(functionbody))
            f.write("' #######################################\n")
            f.write("deactivate " + compoundname + "\n")
            f.write("@enduml\n")
            f.write("' #######################################\n")
#============================================================================================================================================================
   @MyLogger.deco
   def __CustomizeFunctionBody(self, functionbody, compoundname):
      #============================================================================================================================================================
      def __RemoveEmpty(functionbody, compoundname):
         ret = []
         for line in functionbody:
            line = line.strip(' ')
            line = line.strip('\t')
            ret.append(line)
         return ret
      #============================================================================================================================================================
      def __FirstFormat(functionbody, compoundname):
         ret = []
         buf = ''
         for char in ''.join(functionbody):
            buf += char
            # bufは必ず空白文字以外で始まるようにする
            buf = buf.lstrip()
            if buf == "":
               continue
            # ラムダ式で引っ掛からないようにする
            elif len(re.findall("\(", buf))-len(re.findall("\)", buf)) != 0:
               continue
            # elseマッチャー # コメントとかforとかよりも優先度高めにする必要あり
            elif (result := re.fullmatch("(else.*{)", buf, re.S)):
               index = -1
               while ret[index] != "}\n":
                  index -= 1
               ret[index] = ret[index].replace("\n","") + " " + result.group(1).replace("\n", "") + "\n"
            # 関数宣言マッチャー # ifとかforもマッチするはず
            elif (result := re.fullmatch("(.*\(.*\).*\{)", buf, re.S)):
               ret.append(result.group(1).replace("\n", "") + "\n")
            # switch文caseマッチャー
            elif (result := re.fullmatch("(case.*:\n)", buf, re.S)):
               ret.append(result.group(1).replace("\n", "") + "\n")
            # 処理マッチャー
            elif (result := re.fullmatch("(.*;)", buf, re.S)):
               ret.append(result.group(1).replace("\n", "") + "\n")
            # 一行コメントマッチャー
            elif (result := re.fullmatch("(//.*\n)", buf, re.S)):
               ret.append(result.group(1).replace("\n", "") + "\n")
            # 複数行コメントマッチャー
            elif (result := re.fullmatch("(\/\*.*\*\/)", buf, re.S)):
               ret.append(result.group(1).replace("\n", "") + "\n")
            # ブロック終端マッチャー
            elif (result := re.fullmatch("(})", buf, re.S)):
               ret.append(result.group(1).replace("\n", "") + "\n")
            # プリプロセッサーマッチャー
            elif (result := re.fullmatch("(#.*\n)", buf, re.S)):
               ret.append(result.group(1).replace("\n", "") + "\n")
            else:
               continue
            # どこかでマッチしてたらbuf初期化
            buf = ''
         return ret
      #============================================================================================================================================================
      def __RemoveFunctionBlock(functionbody, compoundname):
         ret = []
         blockcnt = 0
         for line in functionbody:
            blockcnt -= len(re.findall("}", line))
            if blockcnt > 0:
               ret.append(line)
            blockcnt += len(re.findall("{", line))
         return ret
      #============================================================================================================================================================
      def __AddCallDependency(functionbody, compoundname):
         def __SearchFunctionInfo(function):
            info = [info for info in self.unique_functions if info['name'] == function]
            return info[0] if info else {'compoundname':'', 'samenamecnt':''}
         ret = []
         for line in functionbody:
            if (results := re.findall("\w+\(", line, re.S)):
               for function in [result[:result.find("(")] for result in results]:
                  info = __SearchFunctionInfo(function)
                  if info['compoundname'] != '':
                     ret.append(compoundname+"->"+info['compoundname']+":"+function+"\n")
                  ret.append("' MyPlantUML["+compoundname+"->"+info['compoundname']+":"+function+"("+str(info['samenamecnt'])+")]\n")
            ret.append(line)
         return ret
      #============================================================================================================================================================
      def __AddPlantUMLSentence(functionbody, compoundname):
         ret = []
         for line in functionbody:
            # プリプロセッサ系
            if re.fullmatch("(#if.*\n)", line, re.S):
               ret.append("alt "+line)
            elif re.fullmatch("(#else.*\n)", line, re.S):
               ret.append("else "+line)
            elif re.fullmatch("(#endif.*\n)", line, re.S):
               ret.append("end "+line)
            # ブロック系
            elif re.fullmatch("(}.*else.*\{\n)", line, re.S):
               ret.append("else "+line)
            elif re.fullmatch("(.*\(.*\).*\{\n)", line, re.S):
               ret.append("alt "+line)
            elif re.fullmatch("(case.*:\n)", line, re.S):
               ret.append("else "+line)
            elif re.fullmatch("(}\n)", line, re.S):
               ret.append("end "+line)
            # コメント
            elif re.fullmatch("(//.*\n)", line, re.S):
               ret.append("note right "+compoundname+": "+line)
            elif re.fullmatch("(\/\*.*\*\/\n)", line, re.S):
               ret.append("note right "+compoundname+": "+line)
            # plantuml comment
            elif re.fullmatch("('.*\n)", line, re.S):
               ret.append(line)
            elif re.fullmatch("([\w.]+->[\w.]*:[\w]+\n)", line, re.S):
               ret.append(line)
            # return
            elif re.fullmatch("(return.*;\n)", line, re.S):
               ret.append(compoundname+"-->entrypoint: "+line)
            # その他
            else:
               ret.append("note right "+compoundname+"#00ffff: "+line)
         return ret
      #============================================================================================================================================================
      def __SecondFormat(functionbody, compoundname):
         def __Nest(nest):
            return ("  "*nest)
         ret = []
         nest = 0
         for line in functionbody:
            if (result := re.fullmatch("(alt )(.*\n)", line, re.S)) != None:
               ret.append(__Nest(nest)+line)
               nest += 1
            elif (result := re.fullmatch("(else )(.*\n)", line, re.S)) != None:
               nest -= 1
               ret.append(__Nest(nest)+line)
               nest += 1
            elif (result := re.fullmatch("(end )(.*\n)", line, re.S)) != None:
               nest -= 1
               ret.append(__Nest(nest)+line)
            elif (result := re.fullmatch("([^:]*: )(.*\n)", line, re.S)) != None:
               ret.append(__Nest(nest)+line)
            elif re.fullmatch("('.*\n)", line, re.S):
               ret.append(__Nest(nest)+line)
            elif re.fullmatch("([\w.]+->[\w.]*:[\w]+\n)", line, re.S):
               ret.append(__Nest(nest)+line)
         return ret
      #============================================================================================================================================================
      functionbody = __RemoveEmpty(functionbody, compoundname)
      functionbody = __FirstFormat(functionbody, compoundname)
      functionbody = __RemoveFunctionBlock(functionbody, compoundname)
      functionbody = __AddCallDependency(functionbody, compoundname)
      functionbody = __AddPlantUMLSentence(functionbody, compoundname)
      functionbody = __SecondFormat(functionbody, compoundname)
      functionbody = '' if functionbody == [] else functionbody
      return functionbody
#============================================================================================================================================================
   @MyLogger.deco
   def CombineUML(self, plantumlpath):
      #============================================================================================================================================================
      def __FindPlantUML(compoundname, name, samenamecnt):
         MyLogger.sakura(compoundname," ", name," ", samenamecnt)
         for index,value in self.all_functions.items():
            if value['compoundname'] == compoundname and value['name'] == name and str(value['samenamecnt']) == samenamecnt:
               # MyLogger.sakura(value)
               bodyfile = value['bodyfile']
               return self.outputbase+bodyfile+'/'+name+"("+samenamecnt+').pu'
         return ''
      #============================================================================================================================================================
      def __ExtractPlantUML(inputfile, outputfile):
         isExtract = False
         with myopen(outputfile, 'w', encoding='utf-8') as output:
            # inputfileをループ
            input_lines = myopen(inputfile, 'r').readlines()
            for input_line in input_lines:
               # フォーマットに当てはまるコメントがあればumlを展開できるか確認
               if (result := re.fullmatch("(\s*)' MyPlantUML\[([\w.]+)->([\w.]*):([\w]+)\(([\d]*)\)\]\n", input_line, re.S)) != None:
                  indent = result.group(1)
                  modfrom = result.group(2)
                  modto = result.group(3)
                  function = result.group(4)
                  number = result.group(5)
                  if modto == '':
                     output.write(input_line)
                     continue
                  if function in self.ignore_functions:
                     output.write(input_line)
                     continue
                  umlpath = __FindPlantUML(modto, function, number)
                  if umlpath == '' or not os.path.exists(umlpath):
                     MyLogger.warning('plantuml not found for : ',input_line.replace("\n",""))
                     output.write(input_line)
                     continue
                  # umlを展開
                  isExtract = True
                  extract_lines = myopen(umlpath, 'r').readlines()
                  for extract_line in extract_lines:
                     if extract_line == "@startuml\n" or extract_line == "@enduml\n":
                        continue
                     extract_line = indent+extract_line
                     extract_line = extract_line.replace("entrypoint", modfrom)
                     MyLogger.sakura(extract_line.replace("\n",""))
                     output.write(extract_line)
               else:
                  MyLogger.sakura(input_line.replace("\n",""))
                  output.write(input_line)
         return isExtract
      inputfile = "./input.pu"
      outputfile = "./output.pu"
      # shutil.copy2(plantumlpath, outputfile)
      shutil.copy2(plantumlpath, inputfile)
      while __ExtractPlantUML(inputfile, outputfile) == True:
         shutil.copy2(outputfile, inputfile)
#============================================================================================================================================================
if __name__ == '__main__':
   uml = MyPlantUML()
   uml.AnalyzeDoxygen('./docs/xml/')
   uml.DraftUML()
   # uml.SetIgnoreFunction(['begin'])
   # uml.CombineUML(path)
#============================================================================================================================================================
