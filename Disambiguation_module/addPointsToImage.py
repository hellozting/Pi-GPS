import json
import cv2
import os

images_path = "data/geometry3k/Geo3KTest"
save_path = "data/geometry3k/disambiguation"
image_logic_path = "Parser/diagram_parser/PGDP.json"
text_json_path = "Parser/text_parser/text_logic_forms_pred.json"
pre_symbles_path = "Disambiguation_module/symbols.json"

with open(image_logic_path, 'r') as f:
        image_logic = json.load(f)
with open(pre_symbles_path, 'r', encoding='utf-8') as json_file:
        symbols = json.load(json_file)
image_set=[]
text_logic_table = json.load(open(text_json_path, "r"))
for key,value in text_logic_table.items():
        if int(key)<2401:
                continue
        else:
                image_set.append(key)
print(image_set)

for image_id in image_set:
        pre_points=[]
        new_data = {}
        value=symbols[image_id]
        for symbol in value["symbols"]:
                if symbol["text_class"] == "point":
                        pre_points.append(symbol["text_content"])
        if image_id in image_logic:
                point_positions = image_logic[image_id]['point_positions']
                image_file = os.path.join(images_path, f"{image_id}.png")
                image = cv2.imread(image_file)
                if image is None:
                        print(f"无法加载图像: {image_file}")
                        continue
                for point, position in point_positions.items():
                        if point in pre_points:
                                continue
                        x, y = int(position[0]), int(position[1])
                        cv2.circle(image, (x, y), 5, (0, 0, 0), -1)
                        text = point
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        font_scale = 1
                        thickness = 2
                        color = (0, 0, 0)
                        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
                        text_x, text_y = x + 10, y
                        if text_x + text_size[0] > image.shape[1]:
                                text_x = image.shape[1] - text_size[0] - 10
                        if text_y - text_size[1] < 0:
                                text_y = text_size[1] + 10
                        cv2.putText(image, text, (text_x, text_y), font, font_scale, color, thickness)
                        
                save_file = os.path.join(save_path, f"{image_id}.png")
                cv2.imwrite(save_file, image)


file_names = os.listdir(save_path)

file_list = [file_name.replace(".png", "") for file_name in file_names]

print(file_list)