import L5XeTree as L5X

xml_open = 'R08c_Fault_CycleStop.L5X'
xml_write = 'R08c_Fault_CycleStop_2.L5x'

fault_number = [i for i in range(193, 257)]
byte_number = [0 for i in range(32)] + [1 for i in range(32)]
bit_number = [i for i in range(32)] * 2
text_number = range(1, 65)

with L5X.L5XeTree(xml_open, xml_write, remove_blank_text=False) as tree_wrap:
    root = tree_wrap.tree.getroot()
