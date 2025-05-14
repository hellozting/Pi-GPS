import itertools
from pathlib import Path
from openai import OpenAI
import math
import os
import base64
from mimetypes import guess_type
from collections import defaultdict
import itertools
import numpy as np
import re

### Complete the miss information

def create_client():
    client = OpenAI(
    api_key="complete",
    base_url="complete"
    )
    model="complete"
    return model,client

def local_image_to_data_url(image_path):
    mime_type, _ = guess_type(image_path)
    if mime_type is None:
        mime_type = 'application/octet-stream' 
    with open(image_path, "rb") as image_file:
        base64_encoded_data = base64.b64encode(image_file.read()).decode('utf-8')
    return f"data:{mime_type};base64,{base64_encoded_data}"

def is_connected(graph):
    visited = {node: False for node in graph}
    def dfs(node):
        visited[node] = True
        for neighbor in graph[node]:
            if not visited[neighbor]:
                dfs(neighbor)
    dfs(next(iter(graph)))
    return all(visited.values())

def is_cyclic(graph):
    visited = {node: False for node in graph}
    parent = {node: None for node in graph}
    
    def dfs(node):
        visited[node] = True
        for neighbor in graph[node]:
            if not visited[neighbor]:
                parent[neighbor] = node
                if dfs(neighbor):
                    return True
            elif parent[node] != neighbor:
                return True
        return False
    for node in graph:
        if not visited[node]:
            if dfs(node):
                return True
    return False

def has_degree_two(graph):
    for node in graph:
        if len(graph[node]) != 2:
            return False
    return True

def find_closed_polygons(edges, n):
    result = set()
    for combination in itertools.combinations(edges, n):
        subgraph = defaultdict(list)
        nodes = set()
        for edge in combination:
            u, v = edge[0], edge[1]
            subgraph[u].append(v)
            subgraph[v].append(u)
            nodes.add(u)
            nodes.add(v)
        if is_connected(subgraph) and is_cyclic(subgraph) and has_degree_two(subgraph):
            sorted_polygon = sorted(combination)
            sorted_polygon = find_polygon_sequence(sorted_polygon)
            result.add(sorted_polygon)
    return result

def polygon_area(points):
    n = len(points)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += points[i][0] * points[j][1]
        area -= points[j][0] * points[i][1]
    area = abs(area) / 2.0
    return area

def find_polygon_sequence(edges):
    # Create a dictionary to store adjacent vertices
    adj = {}
    # Get all unique vertices
    vertices = set()
    
    # Build adjacency list
    for edge in edges:
        v1, v2 = edge[0], edge[1]
        vertices.add(v1)
        vertices.add(v2)
        adj[v1] = adj.get(v1, []) + [v2]
        adj[v2] = adj.get(v2, []) + [v1]
    
    # Start with the first vertex from the first edge
    start = edges[0][0]
    result = [start]
    current = start
    used_edges = set()
    
    # Build the path
    while len(result) < len(vertices):
        for next_vertex in adj[current]:
            edge = ''.join(sorted([current, next_vertex]))
            if edge not in used_edges:
                result.append(next_vertex)
                used_edges.add(edge)
                current = next_vertex
                break
    
    return ''.join(result)

def max_polygon_area(point_positions, edges, n, middle_points):
    max_area = 0
    max_polygon = ""
    closed_polygons = []
    if not middle_points:
        closed_polygons += (find_closed_polygons(edges, n))
    for middle_points,middle_points_edges in middle_points.items():
        closed_polygons += (find_closed_polygons([edge for edge in edges if middle_points not in edge], n))
        print(closed_polygons)
        closed_polygons += (find_closed_polygons([edge for edge in edges if middle_points_edges not in edge], n))
    print(closed_polygons)
    for polygon in closed_polygons:
        area = polygon_area([point_positions[vertex] for vertex in polygon])
        print(polygon, area)
        if area > max_area:
            max_area = area
            max_polygon = polygon
    return max_polygon

def get_target_positions(target, point_positions):
    target_positions = []
    for char in target:
        if char in point_positions:
            target_positions.append(point_positions[char])
    return target_positions

def distance(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

def midpoint(p1, p2):
    return (np.array(p1) + np.array(p2)) / 2

def check_is_Parallelogram(target, point_positions, tolerance=3):
    if len(target) != 4:
        return False
    points = get_target_positions(target, point_positions)
    d1 = distance(points[0], points[1])
    d2 = distance(points[1], points[2])
    d3 = distance(points[2], points[3])
    d4 = distance(points[3], points[0])
    if not (abs(d1 - d3) < tolerance and abs(d2 - d4) < tolerance):
        return False
    mid1 = midpoint(points[0], points[2])
    mid2 = midpoint(points[1], points[3])
    return distance(mid1, mid2) < tolerance

def check_is_Square(target, point_positions, tolerance=1):
    if len(target) != 4:
        return False
    points = get_target_positions(target, point_positions)
    d1 = distance(points[0], points[1])
    d2 = distance(points[1], points[2])
    d3 = distance(points[2], points[3])
    d4 = distance(points[3], points[0])
    d5 = distance(points[0], points[2])
    d6 = distance(points[1], points[3])
    return abs(d1 - d3) < tolerance and abs(d2 - d4) < tolerance and abs(d5 - d6) < tolerance

def check_is_Rectangle(target, point_positions, tolerance=3):
    if len(target) != 4:
        return False
    points = get_target_positions(target, point_positions)

    d01 = distance(points[0], points[1])
    d12 = distance(points[1], points[2])
    d23 = distance(points[2], points[3])
    d30 = distance(points[3], points[0])

    diag02 = distance(points[0], points[2])
    diag13 = distance(points[1], points[3])

    opposite_sides_equal_pair1 = abs(d01 - d23) < tolerance
    opposite_sides_equal_pair2 = abs(d12 - d30) < tolerance

    if not (opposite_sides_equal_pair1 and opposite_sides_equal_pair2):
        return False

    diagonals_equal = abs(diag02 - diag13) < tolerance
    
    return diagonals_equal

def check_is_Rhombus(target, point_positions, tolerance=3):
    if len(target) != 4:
        return False
    points = get_target_positions(target, point_positions) # P0, P1, P2, P3

    d01 = distance(points[0], points[1])
    d12 = distance(points[1], points[2])
    d23 = distance(points[2], points[3])
    d30 = distance(points[3], points[0])

    side1_eq_side2 = abs(d01 - d12) < tolerance
    side2_eq_side3 = abs(d12 - d23) < tolerance
    side3_eq_side4 = abs(d23 - d30) < tolerance
    side4_eq_side1 = abs(d30 - d01) < tolerance

    all_sides_equal = side1_eq_side2 and side2_eq_side3 and side3_eq_side4 and side4_eq_side1
    return all_sides_equal


def check_is_Trapezoid(target, point_positions, tolerance=3):
    if len(target) != 4:
        return False
    points = get_target_positions(target, point_positions)

    d01 = distance(points[0], points[1])
    d12 = distance(points[1], points[2])
    d23 = distance(points[2], points[3])
    d30 = distance(points[3], points[0])

    diag02 = distance(points[0], points[2])
    diag13 = distance(points[1], points[3])

    if not (abs(diag02 - diag13) < tolerance):
        return False

    opposite_pair1_equal = abs(d01 - d23) < tolerance
    opposite_pair2_equal = abs(d12 - d30) < tolerance
    if not (opposite_pair1_equal ^ opposite_pair2_equal):
        return False
        
    return True


def check_is_Kite(target, point_positions, tolerance=3):
    if len(target) != 4:
        return False
    points = get_target_positions(target, point_positions) # P0, P1, P2, P3

    d01 = distance(points[0], points[1])
    d12 = distance(points[1], points[2])
    d23 = distance(points[2], points[3])
    d30 = distance(points[3], points[0])

    config1 = (abs(d01 - d12) < tolerance and abs(d23 - d30) < tolerance)

    config2 = (abs(d12 - d23) < tolerance and abs(d30 - d01) < tolerance)

    return config1 or config2

def check_is_Pentagon(target, point_positions, tolerance=3):
    if len(target) != 5:
        return False
    return True

def check_is_Hexagon(target, point_positions, tolerance=3):
    if len(target) != 6:
        return False
    return True


def check_specific_shape(shape, target, point_positions):
    print("check"+shape)
    if shape == 'Parallelogram':
        result=check_is_Parallelogram(target, point_positions)
        print(result)
        return result
    elif shape == 'Square':
        result=check_is_Square(target, point_positions)
        print(result)
        return result
    #and so on to be tested
    return True

#convert ABCD to A,B,C,D
def convert(target):
    if target=="$": 
        return target
    target=target.replace(" ","")
    text = ""
    for i in list(target):
        if i.isalpha():
            text += i
            text += ","
    text = text[:-1]
    return str(text)

def check_shape(Verify,shape, target, point_positions, edges, middle_points, circle_instances):
    if not Verify:
        return convert(target)
    #不能判断的 值判断字符数
    if shape=="Circle":
        if len(target)==1 and target in circle_instances:
            return convert(target)
        else:
            return [convert(target),"$"]
    if shape=="Line":
        if len(target)==2 and (target in edges or target[::-1] in edges):
            return convert(target)
        else:
            return [convert(target),"$"]
    if shape=="Angle" :
        if len(target)==3 and (target[:2] in edges or target[:2][::-1] in edges)and (target[1:] in edges or target[1:][::-1] in edges):
            return convert(target)
        else:
            return [convert(target),"$"]
    if shape=="Sector":
        if len(target)==3:
            return convert(target)
        else:
            return [convert(target),"$"]
    #根据类型决定点的多少
    if shape=="Triangle":
        n=3
    elif shape=="Parallelogram" or shape=="Square" or shape=="Rectangle" or shape=="Rhombus" or shape=="Trapezoid" or shape=="Kite":
        n=4
    elif shape=="Pentagon":
        n=5
    elif shape=="Hexagon":
        n=6
    elif shape=="Heptagon":
        n=7
    elif shape=="Octagon":
        n=8
    else:
        n=len(target)
    max_area = 0
    max_polygon = "$"
    closed_polygons = set()
    #找到n边的闭合图形
    if not middle_points:
        closed_polygons |= (find_closed_polygons(edges, n))
    for middle_point,middle_point_edges in middle_points.items():
        if n>3:
        #防止交叉导致闭合图形有误   可改进
            if len(middle_point_edges)>=2:
                remove_edges=set()
                for edge in edges:
                    if middle_point in edge or edge in middle_point_edges:
                        remove_edges.add(edge)
                for edge in remove_edges:
                    edges.remove(edge)
        closed_polygons |= (find_closed_polygons([edge for edge in edges if middle_point not in edge], n))
        closed_polygons |= (find_closed_polygons([edge for edge in edges if edge not in middle_point_edges], n))
    for polygon in closed_polygons:
        print(polygon)
        if n>=3 and n<=8:#如果可以算最大面积
            area = polygon_area([point_positions[vertex] for vertex in polygon])
            if area > max_area:
                max_area = area
                max_polygon = polygon
        if set(polygon) == set(target):#检测是否为闭合图形
            if check_specific_shape(shape, polygon, point_positions):
                return convert(polygon)
    return [convert(target), convert(max_polygon)]

def is_right_angle(positions, tolerance=1000):
    A, B, C = positions
    
    # 计算向量 AB 和 BC
    AB = (B[0] - A[0], B[1] - A[1])
    BC = (C[0] - B[0], C[1] - B[1])
    
    # 计算向量 AB 和 BC 的点积
    dot_product = AB[0] * BC[0] + AB[1] * BC[1]
    # print(f"{positions} Dot product: {dot_product}")
    return math.isclose(dot_product, 0, abs_tol=tolerance)

def check_tangent(ans,edges,point_positions,diagram_logic_forms):
    points_on_circle = []
    tangent = []
    for form in diagram_logic_forms:
        if "PointLiesOnCircle(" in form:
            point = form.replace("PointLiesOnCircle(","").split(",")[0]
            circle = form.split(", Circle(")[1].split(",")[0]
            points_on_circle.append((point, circle))
    for edge in edges:
        for point, circle in points_on_circle:
            if point in edge and circle not in edge:
                otherpoint=edge.replace(point,"")
                target=str(otherpoint)+str(point)+str(circle)
                #print(target)
                # print(is_right_angle(get_target_positions(target, point_positions)))
                if is_right_angle(get_target_positions(target, point_positions)):
                    tangent.append(edge)
    if ans in tangent:
        return convert(ans)
    elif len(tangent)!=0:
        return [convert(ans),convert(tangent[0])]
    else:
        return [convert(ans),"@"]

def find_dollar_list(nested_list):
    # Check if the current element is a list
    if isinstance(nested_list, list):
        # If the list contains '$', return this list
        if '$' in nested_list or '$1' in nested_list or '$2' in nested_list:
            return nested_list
        # Otherwise, recursively search each element in the list
        for element in nested_list:
            result = find_dollar_list(element)
            if result is not None:
                return result
    # If no list containing '$' is found, return None
    return None

def tangent_LLM(image_path,str_index):
    model,client = create_client()
    user_content=[{"type":"text","text":"Does the circle in this diagram have a tangent line? Only answer me in True or False."}]
    user_content.append(
        {
            "type":"image_url",
            "image_url": {
                "url": local_image_to_data_url(os.path.join(image_path, f"{str_index}.png")),
            }
        }
    )
    messages=[
    {
        "role": "system",
        "content": "You are a helpful assistant.You will help me answer some questions about the geometric shapes in a plane geometry diagram.",
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
    return ans

def simple_LLM(image_path,str_index,ques,text_logic_form):
    model,client = create_client()
    user_content=[{"type":"text","text":"According to the question:"+ques+", what is the right form in "+text_logic_form+" refer to in the diagram ? \
                you should replace the unclear form which have $ sign with the right form.\
                For example, Find(AreaOf(Shape($))). According to the problem statement, Shape($) in the figure refers to triangle ABC.\
                Therefore, you need to output Find(AreaOf(Triangle(A, B, C))),Here are more exapmles:\
                Find(PerimeterOf(Parallelogram($))) Parallelogram($) refers to Parallelogram(A,B,E,D) output Find(PerimeterOf(Parallelogram(A,B,E,D)))\
                Find(MeasureOf(Angle($))) Angle($) refers to Angle(A,B,C) output Find(MeasureOf(Angle(A,B,C)))\
                No additional information should be output! just answer me the correct form\
                if you cannot answer, please just answer me the original form!\
                the forms of how to describe shapes are as follows:\
                Triangle Triangle(A,B,C) \
                Parallelogram Parallelogram(A,B,C,D) \
                Square Square(A,B,C,D) \
                Rectangle Rectangle(A,B,C,D) \
                Rhombus Rhombus(A,B,C,D) \
                Trapezoid Trapezoid(A,B,C,D) \
                Kite Kite(A,B,C,D) \
                Pentagon Pentagon(A,B,C,D,E) \
                Hexagon Hexagon(A,B,C,D,E,F) \
                Heptagon Heptagon(A,B,C,D,E,F,G) \
                Octagon Octagon(A,B,C,D,E,F,G,H) \
                Circle Circle(A)"}]
    user_content.append(
        {
            "type":"image_url",
            "image_url": {
                "url": local_image_to_data_url(os.path.join(image_path, f"{str_index}.png")),
            }
        }
    )
    messages=[
    {
        "role": "system",
        "content": "You are a helpful assistant.You will help me answer some questions about the geometric shapes in a plane geometry diagram.Think step by step to find the correct answer.",
    },
    {
        "role": "user", 
        "content": user_content
    },
    ]
    # 然后调用 chat-completion, 获取 kimi 的回答
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.2,
    )
    ans=completion.choices[0].message.content
    return ans

def regular_LLM(image_path,str_index,unknown_form,ques,text_logic_form ,additional_prompt):
    model,client = create_client()
    user_content=[{"type":"text","text":"According to the question:"+ques+", what is the "+unknown_form[0]+" in "+text_logic_form+" refer to in the diagram ? \
                answer me only in capital letters(eg. ABCD) no more information should be answer. if there is no answer, please answer me $\
                if there are multiple "+unknown_form[0]+"in my ask, please only answer me the first one! Do not answer me a list!\
                Represent a circle only by its center point,eg. Circle(O) Represent a Line by its end point,eg. Line(AB) Represent a Angle by three letters,eg. Angle(ABC)"}]
    if additional_prompt != "" :
        user_content.append(
            {
                "type":"text",
                "text":"Attention! The answer "+additional_prompt+" is not correct. Please think deeply and answer me the right answer."
            }
        )
    user_content.append(
        {
            "type":"image_url",
            "image_url": {
                "url": local_image_to_data_url(os.path.join(image_path, f"{str_index}.png")),
            }
        }
    )
    messages=[
    {
        "role": "system",
        "content": "You are a helpful assistant.You will help me answer some questions about the geometric shapes in a plane geometry diagram.Think step by step to find the correct answer.",
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
    return ans

def shape_LLM(image_path,str_index, unknown_form, ques,text_logic_form, additional_prompt=""):
    model,client = create_client()
    user_content=user_content=[{"type":"text","text":"According to the question:"+ques+", what is the first Shape($) in "+text_logic_form+" refers to in the diagram"}]
    if additional_prompt != "" :
        user_content.append(
            {
                "type":"text",
                "text":"Attention! The answer "+additional_prompt+" is not correct. Please think deeply and answer me the right answer."
            }
        )
    user_content.append(
        {
            "type":"image_url",
            "image_url": {
                "url": local_image_to_data_url(os.path.join(image_path, f"{str_index}.png")),
            }
        }
    )
    messages=[
    {
        "role": "system",
        "content": "You are a helpful assistant.You will help me answer some questions about the geometric shapes in a plane geometry diagram.\
        Your task is to provide the correct formal language that describes the problem statement based on the text and diagram of a geometry math problem. \
        First, analyze the diagram to identify all the shapes and their corresponding points, then understand the problem statement to determine the specific shapes it refers to\
        For example, I will ask what is the Shape($) in Find(AreaOf(Shape($))) refers to, \
        and according to the text and diagram in the problem, Shape($) refers to triangle ABC, so you need to output Triangle(A,B,C)\
        No additional information should be output.if there are multiple Shape($) in my ask, please only answer me the first one.\
        if you can not answer, please answer me Shape($)\
        the forms of the shapes are as follows:\
        Triangle Triangle(A,B,C) \
        Parallelogram Parallelogram(A,B,C,D) \
        Square Square(A,B,C,D) \
        Rectangle Rectangle(A,B,C,D) \
        Rhombus Rhombus(A,B,C,D) \
        Trapezoid Trapezoid(A,B,C,D) \
        Kite Kite(A,B,C,D) \
        Pentagon Pentagon(A,B,C,D,E) \
        Hexagon Hexagon(A,B,C,D,E,F) \
        Heptagon Heptagon(A,B,C,D,E,F,G) \
        Octagon Octagon(A,B,C,D,E,F,G,H) \
        Circle Circle(A)",
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
    return ans

def shaded_LLM(image_path,str_index, unknown_form, ques,text_logic_form, additional_prompt=""):
    model,client = create_client()
    user_content=user_content=[{"type":"text","text":"According to the question:"+ques+", what is the first Shaded($) in "+text_logic_form+" refers to in the diagram"}]
    if additional_prompt != "" :
        user_content.append(
            {
                "type":"text",
                "text":"Attention! The answer "+additional_prompt+" is not correct. Please think deeply and answer me the right answer."
            }
        )
    user_content.append(
        {
            "type":"image_url",
            "image_url": {
                "url": local_image_to_data_url(os.path.join(image_path, f"{str_index}.png")),
            }
        }
    )
    messages=[
    {
        "role": "system",
        "content": "You are a helpful assistant.You will help me find the shaded area in a plane geometry diagram.\
        Your task is to provide the correct formal language that describes the problem statement based on the text and diagram of a geometry math problem. \
        First, analyze the diagram to identify all the shapes and their corresponding points, then understand the problem statement to determine the specific shapes it refers to\
        For example, I will ask what is the Shaded($) in Find(AreaOf(Shaded($))) refers to, \
        if the shaded area is a complete shape, you answer me the shape.Such as Shaped($) area refers to triangle ABC, so you need to output Triangle(A,B,C)\
        if the shaded area is not a complete shape and it is two shape combined, you can use Minus(Shape(),Shape()) or Add(Shape(),Shape()) to discribe the area.\
        such as the shaded area is obtained by subtracting the area of the circle D from the area of the triangle AEG, you should answer me Minus(Triangle(A,E,G), Circle(D))\
        you can Combine the two expressions together, such as Minus(Rectangle(A,B,C,D), Add(Circle(D),Circle(E)))\
        No additional information should be output.if there are multiple Shaped($) in my ask, please only answer me the first one.\
        if you can not answer, please just answer me Shaded($)\
        the forms of the shapes are as follows:\
        Triangle Triangle(A,B,C) \
        Parallelogram Parallelogram(A,B,C,D) \
        Square Square(A,B,C,D) \
        Rectangle Rectangle(A,B,C,D) \
        Rhombus Rhombus(A,B,C,D) \
        Trapezoid Trapezoid(A,B,C,D) \
        Kite Kite(A,B,C,D) \
        Pentagon Pentagon(A,B,C,D,E) \
        Hexagon Hexagon(A,B,C,D,E,F) \
        Heptagon Heptagon(A,B,C,D,E,F,G) \
        Octagon Octagon(A,B,C,D,E,F,G,H) \
        Sector Sector(O,A,B)\
        Circle Circle(A)",
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
    return ans

def align(MultiType,Verify,image_path,str_index, ques, unknown_form, point_positions, edges,diagram_logic_forms,text_logic_form,circle_instances):
    
    middle_points = {}
    for form in diagram_logic_forms:
        if "PointLiesOnLine(" in form:
            point = form.replace("PointLiesOnLine(","").split(",")[0]
            line = form.split(", Line(")[1].split(")")[0].replace(", ","")
            if point in middle_points:
                middle_points[point].append(line)
            else:
                middle_points[point] = [line]
    expr = unknown_form[0]
    if MultiType:
        if expr == 'Shaded' and 'AreaOf(Shaded($))' in text_logic_form:
            print("Shaded")
            try:
                ans = shaded_LLM(image_path,str_index, unknown_form, ques,text_logic_form)
                print(ans)
                if not Verify:
                            return ans
                if "Minus" in ans or "Add" in ans:
                    #split result
                    pattern = r"\b\w+\([A-Z](?:,[A-Z])*\)"
                    shapes = re.findall(pattern, ans)
                    for shape in shapes:
                        #formalize LLM output
                        form_shape=shape.replace(",","")
                        form_shape=form_shape.replace(" ","")
                        form_shape=form_shape.replace("\n","")
                        form_shape=form_shape.replace(")","").split("(")# ans[0] shape ans[1] point eg. ans[0] Triangle ans[1] ABC 
                        guide=check_shape(Verify,form_shape[0],form_shape[1],point_positions,edges,middle_points,circle_instances)
                        if not isinstance(guide, str):#replace ans with guide
                            ans=ans.replace(shape,"AreaOf("+form_shape[0]+"("+guide[1]+"))")
                        else:
                            ans=ans.replace(shape,"AreaOf("+form_shape[0]+"("+guide+"))")
                else:
                    #shaded area is a complete shape
                    shape=ans
                    #formalize LLM output
                    form_shape=shape.replace(",","")
                    form_shape=form_shape.replace(" ","")
                    form_shape=form_shape.replace("\n","")
                    form_shape=form_shape.replace(")","").split("(")# ans[0] shape ans[1] point eg. ans[0] Triangle ans[1] ABC 
                    guide=check_shape(Verify,form_shape[0],form_shape[1],point_positions,edges,middle_points,circle_instances)
                    if not isinstance(guide, str):#replace ans with guide
                        ans=ans.replace(shape,"AreaOf("+form_shape[0]+"("+guide[1]+"))")
                    else:
                        ans=ans.replace(shape,"AreaOf("+form_shape[0]+"("+guide+"))")
                return ans
            except Exception as e:
                print(e)
                return ["Shaded","$"]
        #deal with shape($)
        elif expr == 'Shape':
            print("Shape($)")
            step=0
            additional_prompt=""
            try:
                while step<2:
                    step+=1
                    ans = shape_LLM(image_path,str_index, unknown_form, ques,text_logic_form,additional_prompt)
                    #formalize LLM output
                    ans=ans.replace(",","")
                    ans=ans.replace(" ","")
                    ans=ans.replace("\n","")
                    ans=ans.replace(")","").split("(")# ans[0] shape ans[1] point eg. ans[0] Triangle ans[1] ABC 
                    print("\nLLM output:",ans)
                    if not Verify:
                        return [ans[0],convert(ans[1])]
                    guide=check_shape(Verify,ans[0],ans[1],point_positions,edges,middle_points,circle_instances)
                    print("Guided result:",guide,type(guide))
                    if isinstance(guide, str) and "("+guide+")" not in text_logic_form:
                        return [ans[0],guide]
                    additional_prompt=ans[1] #提示上一次的答案错误
                    print("additional_prompt",additional_prompt)
                return [ans[0],guide]
            except Exception as e:
                print(e)
                return ["Shape","$"]
        
        # sure about the shape
        else:
            print("Regular")
            try:
                step=0
                additional_prompt=""
                while step<2:
                    step+=1
                    ans = regular_LLM(image_path,str_index, unknown_form, ques,text_logic_form, additional_prompt)
                    if "," in ans: #multiple lines
                        ans = ans.split(",")
                    #防止输出额外信息
                    for extra in [unknown_form[0],unknown_form[0].upper(),unknown_form[0].lower(),"(",")",","]:
                        if extra in ans:
                            ans=ans.replace(extra,"")
                    ans=ans.replace(" ","")
                    ans=ans.replace(",","")
                    ans=ans.replace("\n","")
                    print("LLM output:",ans)
                    if not Verify:
                        return convert(ans)
                    if "Tangent" in text_logic_form and "Assume" in ques:
                        guide=check_tangent(ans,edges,point_positions,diagram_logic_forms)
                    else:
                        guide=check_shape(Verify,unknown_form[0],ans,point_positions,edges,middle_points,circle_instances)
                    print("Guided result:",guide,type(guide))
                    if isinstance(guide, str) and "("+guide+")" not in text_logic_form:
                        return guide
                    additional_prompt=ans #提示上一次的答案错误
                    print("additional_prompt",additional_prompt)
                return guide
            except Exception as e:
                print(e)
                return "$"
    else:
        try:
            print("in simple align")
            ans = simple_LLM(image_path,str_index,ques,text_logic_form)
            print("simple align finish")
            return ans
        except Exception as e:
                print(e)
                return text_logic_form

if __name__ == '__main__':
    print("test")
    points= {
            "A": [
                132.76698113207547,
                30.779047619047617
            ],
            "B": [
                311.6716981132075,
                30.994285714285713
            ],
            "C": [
                189.5031154014919,
                116.22857142857143
            ],
            "D": [
                244.62092624356774,
                201.34545454545454
            ],
            "E": [
                65.8188679245283,
                202.10857142857142
            ]
        }
    lines=[
            "EC",
            "CB",
            "AC",
            "CD",
            "AE",
            "BD",
            "AB",
            "ED"
        ]
    target="WXZA"
    middle_points={"C":["AD","BE"]}
    # print(middle_points["C"])
    # print(check_shape("Rhombus","ADBE",points,lines,middle_points))
    # # print("\n")
    # print(max_polygon_area(points,lines,4,middle_points)) 
    #print(check_is_Parallelogram(target, points, tolerance=3))

    #test tangent
    line_instances = [
            "VA",
            "VT",
            "AT",
            "UT",
            "VU"
        ]
    diagram_logic_forms = [
            "PointLiesOnLine(A, Line(V, T))",
            "PointLiesOnCircle(A, Circle(T, radius_0_0))",
            "PointLiesOnCircle(U, Circle(T, radius_0_0))",
            "Equals(LengthOf(Line(V, U)), 7)",
            "Equals(LengthOf(Line(T, U)), x)",
            "Equals(LengthOf(Line(V, T)), 11)"
        ]
    point_positions = {
            "V": [
                67.11557788944724,
                137.10857142857145
            ],
            "T": [
                237.5678391959799,
                188.58122448979591
            ],
            "U": [
                109.97448782373405,
                241.51384615384617
            ],
            "A": [
                105.46733668341707,
                148.8
            ]
        }
    print(check_tangent("UV",line_instances,point_positions,diagram_logic_forms))
    print(check_tangent("VA",line_instances,point_positions,diagram_logic_forms))