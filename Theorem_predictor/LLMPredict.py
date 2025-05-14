from openai import OpenAI
import json
import os
import re
if __name__ == '__main__':
    ### Complete the miss information
    model="o3-mini"
    client = OpenAI(
        api_key="",
        base_url=""
        )
    result={}
    #Geometry3k
    image_path=r"data/geometry3k/disambiguation"
    text_logic_form_path = r"Parser\text_parser\text_logic_forms_pred.json"
    diagram_logic_form_path = r"Parser\diagram_parser\PGDP.json"
    ## Load files
    text_logic_table = json.load(open(text_logic_form_path, "r"))
    diagram_logic_table = json.load(open(diagram_logic_form_path, "r"))
    lst = list(range(2401, 3002)) # range(2401, 3002)

    for index in lst[:]:
        str_index = str(index)
        #get ques text
        data_json_path = f"\data\geometry3k\test\{str_index}\data.json"
        if os.path.exists(data_json_path):
            with open(data_json_path, 'r') as data_file:
                data_dict = json.load(data_file)
                ques = data_dict.get("problem_text")
                value_list = data_dict.get("precise_value") # [5.0, 12.0, 13.0, 26.0]
                gt_id = ord(data_dict.get("answer")) - 65  # 0
        text_parser = text_logic_table.get(str_index)
        diagram_index = str_index
        diagram_parser = diagram_logic_table.get(str_index)

        ## Parse diagram logic forms
        lines = diagram_parser['line_instances']
        point_positions = diagram_parser['point_positions']
        diagram_logic_forms = diagram_parser['diagram_logic_forms']
        
        ## Parse text logic forms
        text_logic_forms = text_parser["text_logic_forms"]

        #forms
        text_forms=""
        for i in text_logic_forms:
            text_forms = text_forms+" "+i
        diagram_forms=""
        for i in diagram_logic_forms:
            diagram_forms = diagram_forms+" "+i
        print(ques,text_forms,diagram_forms)
        
        client = client
        user_content=[{"type":"text","text":"Here is a geometry's question and the formal language to discribe its diagram.\
                        Please provide your answer as numbers separated by commas only. (e.g. 1,4,6)\
                        Do not include any additional text or explanations.question:"+ques+"\
                        text_logic_forms:"+text_forms+"diagram logic forms"+diagram_forms}]
        messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant.You will think step by step to find the correct answer.You will try to solve a geometry problem \
                        Instead of giving me the answer directly, you should tell me the sequence of the theorems in numbers that should be used to solve this plane geometry problem.\
                        For example,if you use 2: thales_theorem,4:parallel_lines_theorem and 5: triangle_anglesum_theorem, \
                        you just need to answer (2,4,5).You can not answer any other information.\
                        Solve the problem using as few theorems as possible!\
                        But ensure that the problem can definitely be solved after applying these theorems.\
                        here are the theorems list you can use:\
                        1:circle_definition,\
                        2: thales_theorem,\
                        3: inscribed_angle_theorem,\
                        4:parallel_lines_theorem,\
                        5: triangle_anglesum_theorem,\
                        6:isosceles_triangle_theorem_side,\
                        7: isosceles_triangle_theorem_angle,\
                        8:equilateral_triangle_theorem,\
                        9: pythagoras_theorem,\
                        10: triangle_center_of_gravity_theorem,\
                        11: congruent_triangles_proving_theorem,\
                        12: congruent_triangles_theorem,\
                        13: law_of_sines,\
                        14: tangent_secant_theorem,\
                        15: chord_theorem,\
                        16: angle_bisector_theorem,\
                        17: similar_triangle_proving_theorem,\
                        18: similar_triangle_theorem,\
                        19: similar_polygon_theorem,\
                        20: median_line_theorem,\
                        21: area_equation_theorem,\
                        22: polygon_anglesum_theorem,\
                        23: law_of_cosines",
        },
        {
            "role": "user", 
            "content": user_content
        },
        ]
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.2,
        )
        ans=completion.choices[0].message.content
        ans.replace(" ","")
        ans.replace("[","")
        ans.replace("]","")
        ans.replace("(","")
        ans.replace(")","")
        print(ans)
        if re.match(r'^(\d+,)*\d+$', ans):
            num_seqs = list(map(int, ans.split(',')))
        else:
            print("ans err")
            print(ans)
        print(str_index, num_seqs)
        result[str_index] = {
            "id": str_index,
            "num_seqs":num_seqs,
        }
        with open("LLM_pred_seq.json", "w") as outfile:
            json.dump(result, outfile, indent=4)