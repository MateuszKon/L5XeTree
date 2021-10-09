import re

# file = "C:/Users/win10x64/Desktop/Modern_GUI_PyDracula_PySide6_or_PyQt6-master/themes/py_dracula_au.qss"

# with open(file, 'r') as f:
#     text = f.read()
#     pattern = r"rgba?\([0-9,\s]+\)"
#     match = re.findall(pattern, text)
#     print(match)
#     s = set()
#     pattern = r"rgba\(([0-9]+,\s?[0-9]+,\s?[0-9]+),\s?[0-9]+\)"
#     for m in match:
#         match2 = re.search(pattern, m)
#         if match2:
#             m = "rgb(" + match2[1] + ")"
#         s.add(m)
#     print(s)
#     with open("tmp_theme.csv", 'w') as f_w:
#         for element in s:
#             f_w.write(element + ";\n")

file = "tmp_theme_replace.csv"
file_old = "C:/Users/win10x64/Desktop/Modern_GUI_PyDracula_PySide6_or_PyQt6-master/themes/py_dracula_au.qss"
file_new = "C:/Users/win10x64/Desktop/Modern_GUI_PyDracula_PySide6_or_PyQt6-master/themes/py_dracula_au2.qss"

with open(file_old, "r") as f_old:
    old_theme = f_old.read()
    with open(file_new, 'w') as f_w:
        with open(file, 'r') as f_r:
            lines = f_r.readlines()
            print(lines)
            for line in lines:
                pair = line.strip().split(";")
                print(pair)
                old_theme = old_theme.replace(pair[0], pair[1])
        f_w.write(old_theme)

