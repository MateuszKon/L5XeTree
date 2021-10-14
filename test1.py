import L5XeTree as L5X
from modules import *
from CSVfile import CSVfile as csv

xml_open = 'unitest\\unitest_file_in.L5X'
xml_write = 'tmp.L5X'


def tmp_tree(name, data_type, value, children, concnatinate="", encoder=None):
    sep = "\t"
    if value is not None:
        print(concnatinate + sep.join([name, data_type, str(value)]))
    else:
        print(concnatinate + sep.join([name, data_type]))
    if children is not None:
        concnatinate += sep
        for child in children:
            name2, data_type2, value2, children2 = child.build_child_structure(name, data_type, encoder=encoder, concatenate_path=True)
            tmp_tree(name2, data_type2, value2, children2, concnatinate)


with L5X.L5XeTree(xml_open, remove_blank_text=True) as tree_wrap:
    xml = """<Rung Use="Target" Number="3" Type="N">
                <Comment>
                </Comment>
                <Text>
                    <![CDATA[[XIC(Out_Y1_UnloadGripper.Open.FaultTimer.DN) ,XIC(Fault_ImmedStop[2].0) XIO(Fault_ResetAll) ]OTE(Fault_ImmedStop[2].0);]]>
                </Text>
             </Rung>"""

    # tmp1 = ET.XML(xml, tree_wrap.parser)
    # tmp1.find(".//Text").ctext = "abcdg"
    # print(tmp1.find(".//Text").ctext)

    root: L5X.L5XRoot = tree_wrap.tree.getroot()

    '''
    # RUNG
    rung = root.find(".//Rung")
    # rung.comment = ""
    print(rung.comment)
    # dekorator komentarza runga
    rung.decor_comment(decorator='*', lines=2, repeat=36, decor_empty=False)
    print(rung.comment)
    # replace code 
    print(rung.code)
    rung.replace_code("Out_Y1_UnloadGripper", "Out_Y2_UnloadGripper")
    print(rung.code)
    '''

    # ALL TAGs
    # print(root.get_tag_all_names("Controller"))

    # TAG
    '''
    # print tag scope and name, rename tag
    # tag = root.find(".//Program//Tag")
    tag = root.find(".//Tag")
    print(tag.scope)
    print(tag.name)
    tag.rename_tag("abcd")
    print(tag.name)  
    # Print and set tag description
    tag = root.tag("ASCII_Scratchpad")
    print(tag.description)
    tag.description = "bbb"
    print(tag.description) 
    # Read and set tag comment (element of tag)
    tag = root.tag("Global_TextArray")
    print(tag.__class__)
    print(tag.description)
    print(tag.get_element_comment('[0,0]'))
    print(len(tag.get_element_comment('[0,0]')))
    tag.set_element_comment("[5,1]", "Constant String: FAIL")
    tag.set_element_comment("[5,0]", "Constant String: PASS")
    tag.set_element_comment("[3,1]", tag.get_element_comment('[3,0]') + "mym hymyhymy")
    '''

    '''tag = root.tag("ASCII_Scratchpad2")
    print(tag.attrib["DataType"])
    print("Dimensions" in tag.attrib)
    print(tag.value)
    tag.value = "ABDEF"'''

    # tag = root.tag("Fault_ImmedStopTextPL")
    # names = tag.get_names()
    # values = tag.get_value(encoder="Windows-1250")
    # print(names)
    # print(values)
    # encoded_values = [RSLogixEncoding.encode_string(fault_string, "UTF-8") for fault_string in values]
    # print(encoded_values)
    # print(csv.tree_representation(names, values))

    # tag = root.tag("CodeReader_Shaft")
    # tag = root.tag("Fault_ImmedStopTextPL")
    # names = tag.get_names()
    # values = tag.get_value(encoder="Windows-1250")
    # print(names)
    # print(values)
    # print(csv.tree_representation(names, values, separation=";"))
    #
    # names2 = tag.get_names(concatenate_path=True, headers=True)
    # # print(names2)
    #
    # name, data_type, value, children = tag.get_tag_structure(encoder="Windows-1250")
    # tmp_tree(name, data_type, value, children, encoder="Windows-1250")


    # encoding = "Windows-1250"  # jak są zakodowane stringi w projekcie (może być windows-1250, UTF-8 itd.)
    # # tag = root.tag("Fault_ImmedStop", scope="OP030_3_STA1")
    # # print(tag.value)
    # tag = root.tag("Global_TextArray")
    # a = tag.get_value(encoding)
    # print(a)
    # # print(len(a[1][0]))
    # # print(a[1][0])
    # b = tag.get_value_element("[1,0]", encoding)
    # # print(b)
    # tag.set_value_element("ABCDĘfghiĄl", "[1,1]", encoding)
    # print(tag.get_value_element("[1,1]", encoding))
    # a[2][0] = "ąłę"
    # tag.set_value(a, encoding)
    # print(tag.get_value(encoding))


    # tag = root.tag("array_2d")
    # print(tag.get_value())
    # new_values = [[11, 22, 33], [44, 55, 66]]
    # tag.set_value(new_values)
    # # tag = root.tag("array_3d")
    # # print(tag.get_value())

    # tag = root.tag("a_simple_nested_arr3d")
    # # print(tag.get_value())
    # new_value = [
    #     [
    #         [[[1, 2], [[3, 4, 'asd', 'zxc'], [5, 6, 'fgh', 'vbn']]],
    #          [[0, 0], [[0, 0, '', ''], [0, 0, '', '']]]],
    #         [[[0, 0], [[0, 0, '', ''],[0, 0, '', '']]],
    #          [[7, 8], [[9, 10, 'qwe', 'rty'], [11, 12, 'uio', 'p[]']]]]
    #     ],
    #     [
    #         [[[0, 0], [[0, 0, '', ''], [0, 0, '', '']]],
    #          [[0, 0], [[0, 0, '', ''], [0, 0, '', '']]]],
    #         [[[0, 0], [[0, 0, '', ''], [0, 0, '', '']]],
    #          [[13, 14], [[15, 16, 'aasd', 'ffgh'],
    #                      [17, 18, 'gghj', 'hhjk']]]]
    #     ]
    # ]
    # tag.set_value(new_value)
    # encoding = "Windows-1250"
    # tag = root.tag("aaa")
    # print(tag.get_value(encoding))
    # print(tag.get_names(1))

    # PROGRAMS
    # programs = root.programs
    # program1 = root.program("OP030_3_STA2")
    # print(root.programs_name)


    # # TAGS WRITING
    encoding = "Windows-1250"  # jak są zakodowane stringi w projekcie (może być windows-1250, UTF-8 itd.)
    # # Write DINT AFTI_ONS
    # tag = root.tag("AFTI_ONS")
    # # print(tag.get_value())
    # tag.set_value(1234)
    # # print(tag.get_value())
    # # Write STRING
    # tag = root.tag("ASCII_Empty")
    # # print(tag.get_value())
    # tag.set_value('1234')
    # # print(tag.get_value())
    # # Write custom STRING
    # tag = root.tag("AFTI_CommandToSend")
    # # print(tag.get_value())
    # tag.set_value('1234')
    # # print(tag.get_value())
    # # Write REAL
    # tag = root.tag("AFTI_ForceValue")
    # # print(tag.get_value())
    # tag.set_value(1234.12)
    # # print(tag.get_value())
    #
    # # 2 DINTs in DINT array
    # tag = root.tag("Fault_TempArrayAOI")
    # list_value = tag.get_value()
    # list_value[2:4] = [34, 89]
    # # print(list_value)
    # tag.set_value(list_value)
    # # print(tag.get_value())
    # # structures a_deeper_str1
    # tag = root.tag("a_deeper_str1")
    # # print(tag.get_value())
    # list_value = [34, 21, '1233', 'Ałępobsf\n']
    # # print(list_value)
    # tag.set_value(list_value, encoding)
    # # print(tag.get_value())
    # # structures a_outer_str1
    # tag = root.tag("a_outer_str1")
    # # print(tag.get_value())
    # list_value = [4543, 213, [11, 12, 'absa', 'łąópe\ttubałdź'], [0, 222, 'asd', 'łą'], 'ałę']
    # tag.set_value(list_value, encoding)
    # # print(tag.get_value(encoding))
    # # structure a_complex_str1
    # tag = root.tag("a_complex_str1")
    # # print(tag.get_value())
    # list_value = [32, [0, 48, 'abc', 'ałę'], [['1', '4', 'aaa', ''],
    #                                           ['2', '0', '', ''],
    #                                           ['3', '321', '', 'ałę'],
    #                                           ['4', '41', 'asd', ''],
    #                                           ['5', '1', '', ''],
    #                                           ['0', '0', '', 'OOOOóóóóOOOO'],
    #                                           ['0', '0', '', '\n\n'],
    #                                           ['0', '0', '', ''],
    #                                           ['0', '0', '', ''],
    #                                           ['0', '21', '123', 'ąąą']],
    #               [0, 3, '', 'ąłę'], [0, 0, [0, 0, '', '\r\n'], [0, 0, 'aaaa\t', ''], 'eee']]
    # tag.set_value(list_value, encoding)
    # # print(tag.get_value(encoding))
    # structure a_complexarr_str1
    # tag = root.tag("a_complexarr_str1")
    # # print(tag.get_value())
    # list_value = [[1, list([2, 3, 'qwe', 'rty']), [[5, 6, 'asd', 'das'],
    #                                         [123, 321, 'asd', 'ąłę'],
    #                                         ['0', '0', '', ''],
    #                                         ['0', '0', '', ''],
    #                                         ['0', '0', '', ''],
    #                                         ['0', '0', '', ''],
    #                                         ['222', 333, 'ąąą', 'ęęę'],
    #                                         ['0', '0', '', ''],
    #                                         ['0', '0', '', ''],
    #                                         ['0', '0', '', '']],
    #                list([3, 5, 'aaa', 'sss']), list([0, 0, [0, 0, 'ddd', 'eee'], [0, 0, 'eee', ''], 'fff'])],
    #               [0, list([0, 0, '', '']), [['0', '0', '', ''],
    #                                          ['0', '0', '', ''],
    #                                          ['3', '2', 'aaa', 'bbb'],
    #                                          ['0', '0', '', ''],
    #                                          ['0', '0', '', ''],
    #                                          ['0', '0', '', ''],
    #                                          ['0', '0', '', ''],
    #                                          ['0', '0', '', ''],
    #                                          ['0', '0', '', ''],
    #                                          ['0', '0', '', '']],
    #                list([0, 0, '', '\n\n']), list([0, 0, [0, 0, 'ęę', ''], [0, 0, '', ''], 'a'])]]
    # tag.set_value(list_value, encoding)
    # # print(tag.get_value(encoding))
    # tag.set_value_element("3333", "[0].structure10[1].str1", encoding)
    # # print(tag.get_value(encoding))

    # NEW TAG
    tag = L5X.L5XTag(root, "hymy", "DINT")
    tag = root.new_tag("hymy", "DINT")
    tag.description = "asdasdasd"

    tag = root.new_tag("aaa_DINT1", "DINT", value=1, description="aaa_DINT1")

    tag = root.new_tag("aaa_DINTarr1", "DINT", dimensions=[2], value=[1, 2], description="aaa", comments=[("[0]", "bbb")])
    tag.set_element_comment("[1]", "poipoiiuyyut")

    tag = root.new_tag("aaa_DINTarr2d", "DINT", dimensions=[2, 2], value=[[1, 2], [3, 4]], description="aaa", comments=[("[0]", "111"), ("[0,0]", "aaa"), ("[1,0]", "33"), ("[1]", "44"), ("[0,1].2", "ąłęmym")])
    # L5X.ET.dump(tag)

    root.new_tag("aaa_string", "STRING", value="abc")

    root.new_tag("aaa_string_40", "u_str_40ch", value="abc")

    # tag = root.tag("a_simple_nested_arr3d")
    tag = root.new_tag("aaa_simple_nested", "a_simple_nested", dimensions=[2, 2, 2])
    new_value = [
        [
            [[[1, 2], [[3, 4, 'asd', 'zxc'], [5, 6, 'fgh', 'vbn']]],
             [[0, 0], [[0, 0, '', ''], [0, 0, '', '']]]],
            [[[0, 0], [[0, 0, '', ''], [0, 0, '', '']]],
             [[7, 8], [[9, 10, 'qwe', 'rty'], [11, 12, 'uio', 'p[]']]]]
        ],
        [
            [[[0, 0], [[0, 0, '', ''], [0, 0, '', '']]],
             [[0, 0], [[0, 0, '', ''], [0, 0, '', '']]]],
            [[[0, 0], [[0, 0, '', ''], [0, 0, '', '']]],
             [[13, 14], [[15, 16, 'aasd', 'ffgh'],
                         [17, 18, 'gghj', 'hhjk']]]]
        ]
    ]
    tag.set_value(new_value)


    tree_wrap.save_file(xml_write)
