import unittest
import L5XeTree as L5X
from CSVfile import CSVfile as csv
import os
import numpy as np


class TestL5XeTreeMethods(unittest.TestCase):

    XML_READ_FILE = "unitest_file_in.L5X"
    XML_WRITE_FILE = "unitest_file_out.L5X"
    folder_path = os.path.dirname(os.path.abspath(__file__))
    TREE = L5X.L5XeTree(os.path.join(folder_path, XML_READ_FILE), remove_blank_text=True)
    WRITE_PATH = os.path.join(folder_path, XML_WRITE_FILE)
    write_path = os.path.join(folder_path, XML_WRITE_FILE)
    TREE.parse_tree()
    ROOT = TREE.tree.getroot()

    def open_tree(self):
        self.folder_path = os.path.dirname(os.path.abspath(__file__))
        tree = L5X.L5XeTree(os.path.join(self.folder_path, self.XML_READ_FILE), remove_blank_text=True)
        self.write_path = os.path.join(self.folder_path, self.XML_WRITE_FILE)
        tree.parse_tree()
        return tree

    def save_tree(self):
        self.save_file()


    def preparation(self):
        # tree_wrap = self.open_tree()
        # root = tree_wrap.tree.getroot()
        tree_wrap = self.TREE
        root = self.ROOT
        return tree_wrap, root

    def test_read_1(self):
        """Read String data"""
        tree_wrap, root = self.preparation()
        tag = root.tag("ASCII_Scratchpad2")
        self.assertEqual("45", tag.value)
        tree_wrap.save_file(self.write_path)

    def test_read_2(self):
        """Read Bool data"""
        tree_wrap, root = self.preparation()
        tag = root.tag("AFTI_CommandTXDSent")
        self.assertEqual(1, tag.value)
        tree_wrap.save_file(self.write_path)

    def test_read_3(self):
        """Read Real data"""
        tree_wrap, root = self.preparation()
        tag = root.tag("AFTI_ForceValue")
        self.assertEqual(8.9845, tag.value)
        tree_wrap.save_file(self.write_path)

    def test_read_4(self):
        """Read DINT data"""
        tree_wrap, root = self.preparation()
        tag = root.tag("AFTI_ONS")
        self.assertEqual(4096, tag.value)
        tree_wrap.save_file(self.write_path)

    def test_read_5(self):
        """Read array DINT[5] data"""
        tree_wrap, root = self.preparation()
        tag = root.tag("CodeReader_LOT_ScanLotSteps")
        value = tag.value
        for pair in zip([15, 5, 4, 3, -100], value):
            self.assertEqual(pair[0], pair[1])
        tree_wrap.save_file(self.write_path)

    def test_read_6(self):
        """Read array STRING[193] names and data with encoding and make tree representation """
        tree_wrap, root = self.preparation()
        tag = root.tag("Fault_ImmedStopTextPL")
        names = tag.get_names()
        values = tag.get_value(encoder="Windows-1250")
        value = csv.tree_representation(names, values).rstrip("\n").split("\n")
        with open(os.path.join(self.folder_path, "test_read_6.txt"), 'r', encoding='ANSI') as f_r:
            expected_text = f_r.readlines()
        self.assertEqual(len(expected_text), len(value))
        for pair in zip(expected_text, value):
            self.assertEqual(pair[0].rstrip("\n"), pair[1])
        tree_wrap.save_file(self.write_path)

    def test_read_7(self):
        """Read structure names and data with encoding and make tree representation """
        tree_wrap, root = self.preparation()
        tag = root.tag("CodeReader_Shaft")
        names = tag.get_names()
        values = tag.get_value(encoder="Windows-1250")
        value = csv.tree_representation(names, values, separation=';').rstrip("\n").split("\n")
        with open(os.path.join(self.folder_path, "test_read_7.txt"), 'r', encoding='ANSI') as f_r:
            expected_text = f_r.readlines()
        self.assertEqual(len(expected_text), len(value))
        for pair in zip(expected_text, value):
            self.assertEqual(pair[0].rstrip("\n"), pair[1])
        tree_wrap.save_file(self.write_path)

    def test_read_8(self):
        """Read array of structures names and data with encoding and make tree representation """
        tree_wrap, root = self.preparation()
        tag = root.tag("Model_SetupStored")
        names = tag.get_names()
        values = tag.get_value(encoder="Windows-1250")
        value = csv.tree_representation(names, values).rstrip("\n").split("\n")
        with open(os.path.join(self.folder_path, "test_read_8.txt"), 'r', encoding='ANSI') as f_r:
            expected_text = f_r.readlines()
        self.assertEqual(len(expected_text), len(value))
        for pair in zip(expected_text, value):
            self.assertEqual(pair[0].rstrip("\n"), pair[1])
        tree_wrap.save_file(self.write_path)

    def test_read_9(self):
        """Read array DINT[2,3] data"""
        tree_wrap, root = self.preparation()
        tag = root.tag("array_2d")
        expected = [[1, 2, 3], [4, 5, 6]]
        self.assert_recursion(expected, tag.get_value())
        tree_wrap.save_file(self.write_path)

    def test_read_10(self):
        """Read array DINT[2,3,4] data"""
        tree_wrap, root = self.preparation()
        tag = root.tag("array_3d")
        expected = [
            [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]],
            [[13, 14, 15, 16], [17, 18, 19, 20], [21, 22, 23, 24]]
        ]
        self.assert_recursion(expected, tag.get_value())
        tree_wrap.save_file(self.write_path)

    def test_read_11(self):
        """Read multidimmensional array of UDT """
        tree_wrap, root = self.preparation()
        tag = root.tag("a_simple_nested_arr3d")
        expected = [
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
        self.assert_recursion(expected, tag.get_value())
        tree_wrap.save_file(self.write_path)

    def test_write_1(self):
        """Write DINT AFTI_ONS"""
        tree_wrap, root = self.preparation()
        tag = root.tag("AFTI_ONS")
        tag.set_value(1234)
        self.assertEqual(1234, tag.get_value())
        tree_wrap.save_file(self.write_path)

    def test_write_2(self):
        """Write STRING ASCII_Empty"""
        tree_wrap, root = self.preparation()
        tag = root.tag("ASCII_Empty")
        tag.set_value('1234')
        self.assertEqual('1234', tag.get_value())
        tree_wrap.save_file(self.write_path)

    def test_write_3(self):
        """Write custom STRING AFTI_CommandToSend"""
        tree_wrap, root = self.preparation()
        tag = root.tag("AFTI_CommandToSend")
        tag.set_value('1234')
        self.assertEqual('1234', tag.get_value())
        tree_wrap.save_file(self.write_path)

    def test_write_4(self):
        """Write REAL AFTI_ForceValue"""
        tree_wrap, root = self.preparation()
        tag = root.tag("AFTI_ForceValue")
        tag.set_value(1234.12)
        self.assertEqual(1234.12, tag.get_value())
        tree_wrap.save_file(self.write_path)

    def test_write_5(self):
        """Write 2 DINTs in DINT array Fault_TempArrayAOI"""
        tree_wrap, root = self.preparation()
        tag = root.tag("Fault_TempArrayAOI")
        list_value = tag.get_value()
        list_value[2:4] = [34, 89]
        tag.set_value(list_value)
        for pair in zip(list_value, tag.get_value()):
            self.assertEqual(pair[0], pair[1])
        tree_wrap.save_file(self.write_path)

    def test_write_6(self):
        """Write structure a_deeper_str1"""
        encoding = "Windows-1250"
        # tree_wrap, root = self.preparation()
        tree_wrap, root = self.TREE, self.ROOT
        tag = root.tag("a_deeper_str1")
        list_value = [34, 21, '1233', 'Ałępobsf\n']
        tag.set_value(list_value, encoding)
        for pair in zip(list_value, tag.get_value(encoding)):
            self.assertEqual(pair[0], pair[1])
        tree_wrap.save_file(self.WRITE_PATH)

    def test_write_7(self):
        """Write structure a_complex_str1"""
        encoding = "Windows-1250"
        # tree_wrap, root = self.preparation()
        tree_wrap, root = self.TREE, self.ROOT
        tag = root.tag("a_complex_str1")
        list_value = [32, [0, 48, 'abc', 'ałę'], [[1, 4, 'aaa', ''],
                                                  [2, 0, '', ''],
                                                  [3, 321, '', 'ałę'],
                                                  [4, 41, 'asd', ''],
                                                  [5, 1, '', ''],
                                                  [0, 0, '', 'OOOOóóóóOOOO'],
                                                  [0, 0, '', '\n\n'],
                                                  [0, 0, '', ''],
                                                  [0, 0, '', ''],
                                                  [0, 21, '123', 'ąąą']],
                      [0, 3, '', 'ąłę'], [0, 0, [0, 0, '', '\r\n'], [0, 0, 'aaaa\t', ''], 'eee']]
        tag.set_value(list_value, encoding)
        self.assert_recursion(list_value, tag.get_value(encoding))
        tree_wrap.save_file(self.WRITE_PATH)

    def test_write_8(self):
        """Write structure a_complexarr_str1"""
        encoding = "Windows-1250"
        # tree_wrap, root = self.preparation()
        tree_wrap, root = self.TREE, self.ROOT
        tag = root.tag("a_complexarr_str1")
        list_value = [[1, list([2, 3, 'qwe', 'rty']), [[5, 6, 'asd', 'das'],
                                                       [123, 321, 'asd', 'ąłę'],
                                                       [0, 0, '', ''],
                                                       [0, 0, '', ''],
                                                       [0, 0, '', ''],
                                                       [0, 0, '', ''],
                                                       [222, 333, 'ąąą', 'ęęę'],
                                                       [0, 0, '', ''],
                                                       [0, 0, '', ''],
                                                       [0, 0, '', '']],
                       list([3, 5, 'aaa', 'sss']), list([0, 0, [0, 0, 'ddd', 'eee'], [0, 0, 'eee', ''], 'fff'])],
                      [0, list([0, 0, '', '']), [[0, 0, '', ''],
                                                 [0, 0, '', ''],
                                                 [3, 2, 'aaa', 'bbb'],
                                                 [0, 0, '', ''],
                                                 [0, 0, '', ''],
                                                 [0, 0, '', ''],
                                                 [0, 0, '', ''],
                                                 [0, 0, '', ''],
                                                 [0, 0, '', ''],
                                                 [0, 0, '', '']],
                       list([0, 0, '', '\n\n']), list([0, 0, [0, 0, 'ęę', ''], [0, 0, '', ''], 'a'])]]
        tag.set_value(list_value, encoding)
        self.assert_recursion(list_value, tag.get_value(encoding))
        tree_wrap.save_file(self.WRITE_PATH)

    def test_write_9(self):
        """Write array DINT[2,3] data"""
        # tree_wrap, root = self.preparation()
        tree_wrap, root = self.TREE, self.ROOT
        tag = root.tag("array_2d")
        new_values = [[11, 22, 33], [44, 55, 66]]
        tag.set_value(new_values)
        self.assert_recursion(new_values, tag.get_value())
        tree_wrap.save_file(self.WRITE_PATH)

    def test_write_10(self):
        """Write array DINT[2,3,4] data"""
        # tree_wrap, root = self.preparation()
        tree_wrap, root = self.TREE, self.ROOT
        tag = root.tag("array_3d")
        new_values = [
            [[11, 22, 33, 44], [55, 66, 77, 88], [99, 110, 111, 112]],
            [[113, 114, 115, 116], [117, 118, 119, 120], [121, 122, 123, 124]]
        ]
        tag.set_value(new_values)
        self.assert_recursion(new_values, tag.get_value())
        tree_wrap.save_file(self.WRITE_PATH)

    def test_write_11(self):
        """Write multidimmensional array of UDT """
        encoder = "Windows-1250"
        # tree_wrap, root = self.preparation()
        tree_wrap, root = self.TREE, self.ROOT
        tag = root.tag("a_simple_nested_arr3d")
        new_values = [
            [
                [[[1, 2], [[3, 4, 'asd', 'zxc'], [5, 6, 'fgh', 'vbn']]],
                 [[3, 4], [[2, 1, 'ąłę', 'óóó'], [0, 0, '', '']]]],
                [[[0, 0], [[0, 0, '', ''], [0, 0, '', '']]],
                 [[7, 8], [[9, 10, 'qwe', 'ęęł\n'], [11, 12, 'uio', 'p[]']]]]
            ],
            [
                [[[0, 0], [[0, 0, '', ''], [0, 0, '', '']]],
                 [[0, 0], [[0, 0, '', ''], [0, 0, '', '']]]],
                [[[654, 4560], [[0, 222, 'aa', ''], [0, 0, '', '']]],
                 [[13, 14], [[15, 16, '', '\t'],
                             [17, 18, '', 'hhjk']]]]
            ]
        ]
        tag.set_value(new_values, encoder)
        self.assert_recursion(new_values, tag.get_value(encoder))
        tree_wrap.save_file(self.WRITE_PATH)

    def assert_recursion(self, first_element, second_element):
        if isinstance(first_element, list):
            for pair in zip(first_element, second_element):
                self.assert_recursion(pair[0], pair[1])
        else:
            self.assertEqual(first_element, second_element)


if __name__ == '__main__':
    unittest.main()
