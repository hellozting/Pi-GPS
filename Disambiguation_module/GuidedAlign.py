import os
import re
import json
import time
import random
import warnings


from numpy.random import seed
from Solver.extended_definition import ExtendedDefinition
from Solver.logic_parser import LogicParser
from align import find_dollar_list
from align import align
from collections import defaultdict
warnings.filterwarnings('ignore')

seed(0)
random.seed(0)
EPSILON = 1e-5

invalid_actions = [0] + list(range(24,30))

def isLetter(ch):
    return ch.upper() and len(ch) == 1

if __name__ == '__main__':
    Verify = True
    MultiType = True
    log_text=""
    #Geometry3k
    image_path=r"data/disambiguation/"
    text_logic_form_path = r"Parser\text_parser\text_logic_forms_pred.json"
    diagram_logic_form_path = r"Parser\diagram_parser\PGDP.json"
    updated_text_logic_form_path = r"Disambiguation_module\disambiguated_text_logic_forms_pred.json"
    ## Load files
    text_logic_table = json.load(open(text_logic_form_path, "r"))
    diagram_logic_table = json.load(open(diagram_logic_form_path, "r"))
    lst = list(range(2401, 3002)) # range(2401, 3002)

    ## Read logic forms and predicated theorem orders
    para_lst = []
    classes=defaultdict(int)
    image_list=set()
    shaded_list=set()
    for index in lst[:]:
        str_index = str(index)
        data_json_path = f"\data\geometry3k\test\{str_index}\data.json"
        if os.path.exists(data_json_path):
            with open(data_json_path, 'r') as data_file:
                data_dict = json.load(data_file)
                ques = data_dict.get("problem_text")
        text_parser = text_logic_table.get(str_index)
        diagram_index = str_index
        diagram_parser = diagram_logic_table.get(str_index)
        parser = LogicParser(ExtendedDefinition(debug=False))

        ## Parse diagram logic forms
        lines = diagram_parser['line_instances']
        point_positions = diagram_parser['point_positions']
        diagram_logic_forms = diagram_parser['diagram_logic_forms']

        ## Parse text logic forms
        text_logic_forms = text_parser["text_logic_forms"]
        
        for i, text in enumerate(text_logic_forms):
            while 'Circle($)' in text and len(diagram_parser['circle_instances']) == 1:
                log_text+="\n"+str_index+"\n"+ques+"\n"
                log_text+=text+"\n"
                log_text+="replace:Circle($) to Circle("+diagram_parser['circle_instances'][0]+')'+"\n"
                text = text.replace('Circle($)', 'Circle('+diagram_parser['circle_instances'][0]+')', 1)
            
            # angel special
            angle_matches = re.findall(r'Angle\([a-z0-9]\)', text)
            for match in angle_matches:
                if not any("angle "+match.replace(")","").split("(")[1] in form for form in diagram_logic_forms):
                    text = text.replace(match, 'Angle($)')
                else:
                    print("keep:"+match)
            
            text = re.sub(r'Line\([a-z0-9]\)', 'Line($)', text)
            text = re.sub(r'Shaded\(.*?\)', 'Shaded($', text) 
            text = text.replace("Polygon","Shape")
            text = text.replace("$1","$")
            text = text.replace("$2","$")
            text = text.replace("$3","$")

            count = text.count('$')+2
            round=0
            while round < count and '$' in text:
                print(index)
                print(text)
                log_text+="\n"+str_index+"\n"+ques+"\n"
                log_text+=text+"\n"
                round+=1
                res=parser.parse(text)
                unknown_form=find_dollar_list(eval(str(res)))
                image_list.add(str_index)
                classes[unknown_form[0]]+=1
                #LLM align
                aligned_form=align(MultiType,Verify,image_path,diagram_index,ques,unknown_form,point_positions,lines,diagram_logic_forms,text,diagram_parser['circle_instances'])
                if MultiType:
                    #Shaded($)
                    if unknown_form[0]=="Shaded" and 'AreaOf(Shaded($))' in text:
                            print("replace:AreaOf(Shaded($)) to "+aligned_form+"\n")
                            log_text+="replace:AreaOf(Shaded($)) to "+aligned_form+"\n"
                            text=text.replace("AreaOf(Shaded($))",aligned_form, 1)
                    #Shape($)
                    elif unknown_form[0]=="Shape":
                        if isinstance(aligned_form[1], str):
                            print("replace:Shape($) to "+aligned_form[0]+"("+aligned_form[1]+")")
                            log_text+="LLM same with guide "
                            log_text+="replace:Shape($) to "+aligned_form[0]+"("+aligned_form[1]+")\n"
                            text=text.replace("Shape($)",aligned_form[0]+"("+aligned_form[1]+")", 1)
                        else:
                            print("replace:Shape($) to "+aligned_form[0]+"("+aligned_form[1][1]+")\n But LLM :"+aligned_form[1][0]+"\n")
                            log_text+="LLM not same with guide "
                            log_text+="replace:Shape($) to "+aligned_form[0]+"("+aligned_form[1][1]+")\n"
                            log_text+="But LLM output "+aligned_form[1][0]+"\n"
                            text=text.replace("Shape($)",aligned_form[0]+"("+aligned_form[1][1]+")", 1)
                    else:
                        if isinstance(aligned_form, str):
                            print("replace:"+unknown_form[0]+"($) to "+unknown_form[0]+"("+aligned_form+")")
                            log_text+="LLM same with guide "
                            log_text+="replace:"+unknown_form[0]+"($) to "+unknown_form[0]+"("+aligned_form+")\n"
                            text=text.replace(unknown_form[0]+"("+unknown_form[1]+")",unknown_form[0]+"("+aligned_form+")", 1)
                        else:
                            if aligned_form[1]=="@":
                                print("replace: Tangent sentence removed")
                                log_text+="replace: Tangent sentence removed\n"
                                text=""
                            else:
                                print("replace:"+unknown_form[0]+"($) to "+unknown_form[0]+"("+aligned_form[1]+")\n But LLM "+aligned_form[0]+"\n")
                                log_text+="LLM not same with guide "
                                log_text+="replace:"+unknown_form[0]+"($) to "+unknown_form[0]+"("+aligned_form[1]+")\n"
                                log_text+="But LLM output"+aligned_form[0]+"\n"
                                text=text.replace(unknown_form[0]+"("+unknown_form[1]+")",unknown_form[0]+"("+aligned_form[1]+")", 1)
                else:
                    print("simple align")
                    print(aligned_form)
                    text=aligned_form
                    break
            if 'Circle' in text and len(diagram_parser['circle_instances']) == 1:
                log_text+="\n"+str_index+"\n"+ques+"\n"
                log_text+=text+"\n"
                log_text+="replace:Circle($) to Circle("+diagram_parser['circle_instances'][0]+')'+"\n"
                pattern = r'Circle\([A-Z]\)'
                replacement = 'Circle('+diagram_parser['circle_instances'][0]+')'
                text = re.sub(pattern, replacement, text)
            text_logic_forms[i] = text
        if "" in text_logic_forms:
            text_logic_forms.remove("")
        text_parser["text_logic_forms"] = text_logic_forms
        text_logic_table[str_index] = text_parser
        ## Save updated text_logic_table to file
        with open(updated_text_logic_form_path, 'w') as updated_file:
            json.dump(text_logic_table, updated_file, indent=4)
    print(len(image_list))
    print(sorted(image_list))
    print(sorted(shaded_list))
    print(classes)
    print(log_text)