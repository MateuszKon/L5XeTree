import lxml.etree as ET
import os

try:
    from .modules import *
except ImportError:
    from modules import *


class L5XData(ET.ElementBase):

    @property
    def ctext(self):
        text_string: str = self.text
        return text_string

    @ctext.setter
    def ctext(self, value):
        self.text = ET.CDATA(value)

    @property
    def root(self):
        root_element: L5XRoot = self.find("..").root
        return root_element

    def child(self):
        return self.find("./*")

    def get_tag_name(self):
        return self.getparent().get_tag_name()


class L5XRoot(L5XData):

    @property
    def root(self):
        return self

    @property
    def programs(self):
        programs: list[L5XProgram] = self.findall("./Controller/Programs/Program")
        return programs

    def program(self, name):
        for program in self.programs:
            if program.attrib["Name"] == name:
                return program
        return None

    def replace_code(self, old, new, count=0):
        for program in self.programs:
            program.replace_code(old, new, count)

    @property
    def programs_name(self):
        names = list()
        for program in self.programs:
            names.append(program.attrib["Name"])
        return names

    def get_tag_all(self, scope='Controller'):
        if scope == "Controller":
            return self.findall("Controller/Tags/Tag")
        else:
            return self.findall("Controller/Programs/Program[@Name='{}']/Tags/Tag".format(scope))

    def get_tag_all_names(self, scope):
        return [element.attrib["Name"] for element in self.get_tag_all(scope)]

    def tag(self, tag_name, scope='Controller'):
        tag: L5XTag
        if scope == 'Controller':
            tag = self.find("Controller/Tags/Tag[@Name='{}']".format(tag_name))
        else:
            tag = self.program(scope).tag(tag_name)
        return tag

    def new_tag(self, name, data_type, dimensions=None, description=None, comments=None, radix=None, tag_type="Base",
                constant="false", external_access="None",
                scope="Controller", value=None, encoder=None):
        tag_obj = L5XTag(self, name, data_type, dimensions=dimensions, description=description, comments=comments,
                         radix=radix, tag_type=tag_type, constant=constant, external_access=external_access)
        if scope == "Controller":
            self.find("Controller/Tags").append(tag_obj)
        else:
            self.program(scope).find("Tags").append(tag_obj)
        if value is not None:
            tag_obj.set_value(value, encoder=encoder)
        return tag_obj

    def get_data_types_all(self):
        data_types: list[L5XDataType] = self.findall("Controller/DataTypes/DataType")
        return data_types

    def get_data_types_all_names(self):
        return [element.attrib["Name"] for element in self.get_data_types_all()]

    def get_data_types_string(self):
        data_types: list[L5XDataType] = self.findall("Controller/DataTypes/DataType[@Family='StringFamily']")
        return data_types

    def get_data_types_string_names(self):
        return [element.attrib["Name"] for element in self.get_data_types_string()]

    def get_data_types_nonstring(self):
        data_types: list[L5XDataType] = self.findall("Controller/DataTypes/DataType[@Family='NoFamily]")
        return data_types

    def get_data_types_nonstring_names(self):
        return [element.attrib["Name"] for element in self.get_data_types_nonstring()]

    def data_type(self, data_type_name):
        if data_type_name.upper() in L5XTag.SYSTEM_DATA_TYPES_DICT:
            return L5XTag.SYSTEM_DATA_TYPES_DICT[data_type_name]()
        elif data_type_name.upper() in L5XTag.SIMPLE_DATA_TYPE:
            return L5XDataTypeSimple()
        else:
            data_type: L5XDataType = self.find("Controller/DataTypes/DataType[@Name='{}']".format(data_type_name))
            return data_type


class L5XDataType(L5XData):

    @property
    def is_string_family(self):
        return self.attrib["Family"] == "StringFamily"

    @property
    def type(self):
        return "NORMAL"

    @property
    def max_string_length(self):
        if self.is_string_family:
            return int(self.find("Members/Member[@Name='DATA']").attrib["Dimension"])
        else:
            raise TypeError("Data Type '" + self.attrib["Name"] +
                            "' is not string family - L5XDataType.max_string_length function error")

    def get_data_type_members(self):
        return self.findall("Members/Member")


class L5XDataTypeSimple(L5XDataType):

    @property
    def is_string_family(self):
        return False

    @property
    def type(self):
        return "SIMPLE"

    def get_data_type_members(self):
        return None

class L5XDataTypeString(L5XDataType):

    @property
    def is_string_family(self):
        return True

    @property
    def type(self):
        return "STRING"

    @property
    def max_string_length(self):
        return 82

    def get_data_type_members(self):
        return list([L5XMember("LEN", "DINT", "0"),
                     L5XMember("DATA", "SINT", "82", radix="ASCII")])


class L5XDataTypeTimer(L5XDataType):

    @property
    def is_string_family(self):
        return False

    @property
    def type(self):
        return "SYSTEM"

    def get_data_type_members(self):
        return list([L5XMember("PRE", "DINT", "0"),
                     L5XMember("ACC", "DINT", "0"),
                     L5XMember("EN", "BOOL", "0"),
                     L5XMember("TT", "BOOL", "0"),
                     L5XMember("DN", "BOOL", "0")])


class L5XDataTypeCounter(L5XDataType):

    @property
    def is_string_family(self):
        return False

    @property
    def type(self):
        return "SYSTEM"

    def get_data_type_members(self):
        return list([L5XMember("PRE", "DINT", "0"),
                     L5XMember("ACC", "DINT", "0"),
                     L5XMember("CD", "BOOL", "0"),
                     L5XMember("DN", "BOOL", "0"),
                     L5XMember("OV", "BOOL", "0"),
                     L5XMember("UN", "BOOL", "0")])


class L5XMember(L5XData):

    def __init__(self, name, data_type, dimension, radix=None, hidden="false", external_access="Read/Write"):
        radix = L5XTag.set_radix(data_type, radix, None)
        if radix is None:
            radix = "NullType"
        attrib = {"Name": name, "DataType": data_type, "Dimension": dimension, "Radix": radix, "Hidden": hidden,
                  "ExternalAccess": external_access}
        super().__init__(attrib=attrib)
        self.tag = "Member"

    @property
    def name(self):
        return self.attrib["Name"]

    @property
    def data_type(self):
        return self.attrib["DataType"]

    @property
    def dimension(self):
        return self.attrib["Dimension"]

    @property
    def is_hidden(self):
        return self.attrib["Hidden"].lower() in ["true", "t", "1"]

    def get_member_data(self):
        return self.name, self.data_type, self.dimension


class L5XTag(L5XData):

    SIMPLE_DATA_TYPE = {"BOOL", "LINT", "DINT", "INT", "SINT", "REAL"}
    RADIX_DICT = {"SINT": "Decimal", "INT": "Decimal", "DINT": "Decimal", "LINT": "Decimal", "REAL": "Float"}
    DEFAULT_VALUE_DICT = {"SINT": 0, "INT": 0, "DINT": 0, "LINT": 0, "REAL": 0.0, "BOOL": 0}
    SYSTEM_DATA_TYPES_DICT = {"STRING": L5XDataTypeString, "TIMER": L5XDataTypeTimer, "COUNTER": L5XDataTypeCounter}

    def _init(self):
        super()._init()
        self.tag_structure = None

    # TODO: Probably somewhere Radix is wrong, while importing to Studio: 'Error: Line 45047: Invalid display style.'
    def __init__(self, root, name, data_type, dimensions=None, description=None, comments=None, radix=None,
                 tag_type="Base", constant="false", external_access="None"):
        attrib = {"Name": name, "TagType": tag_type, "DataType": data_type}
        if dimensions is not None:
            if not isinstance(dimensions, list):
                dimensions = list(dimensions)
            str_dimensions = " ".join(str(x) for x in dimensions)
            attrib["Dimensions"] = str_dimensions
        radix = self.set_radix(data_type, radix, root)
        if radix is not None:
            attrib["Radix"] = radix
        attrib["Constant"] = constant
        attrib["ExternalAccess"] = external_access
        super().__init__(attrib=attrib)
        self.tag = "Tag"
        data_type_obj = root.data_type(data_type)
        if data_type_obj.is_string_family:
            data = L5XTagData.DataString()
        else:
            data = L5XTagData("Decorated")
            data.append(L5XAbstractData.create_head_element(root, data_type, dimensions))
        if description is not None:
            self.append(L5XDescription(description))
        if comments is not None:
            comments_obj = L5XComments()
            for comment_operand, comment_string in comments:
                comments_obj.append(L5XComment(comment_operand, comment_string))
            self.append(comments_obj)
        self.append(data)

    @staticmethod
    def set_radix(data_type, radix, root):
        if radix is None:
            if data_type in L5XTag.RADIX_DICT:
                radix = L5XTag.RADIX_DICT[data_type]
            elif root is not None:
                data_type_obj = root.data_type(data_type)
                if data_type_obj is not None:
                    if data_type_obj.is_string_family:
                        radix = "ASCII"
        return radix

    @staticmethod
    def default_value(data_type):
        return L5XTag.DEFAULT_VALUE_DICT[data_type]

    def rename_tag(self, new_name):
        # zmiana zazwy taga
        old_name = self.name
        self.name = new_name
        # sprawdzenie czy local tag czy control tag
        if self.scope == 'Controller':
            # replace we wszystkich rutynach ca??ego kontrolera
            self.root.replace_code(old_name, self.name)
        else:
            # replace tylko w rutynach programu kt??rego dotyczy tag
            self.root.program(self.scope).replace_code(old_name, self.name)

    def _get_description_obj(self):
        description: L5XDescription = self.find('Description')
        return description

    def _get_comments_obj(self):
        comments: L5XComments = self.find('Comments')
        return comments

    def _get_comment_obj(self, operand):
        comment: L5XComment = self.find("./Comments/Comment[@Operand='{}']".format(operand))
        return comment

    def _get_data_obj(self, data_format=None):
        data: L5XTagData
        if data_format is None:
            data = self.find('Data')
        else:
            data = self.find('Data[@Format="{}"]'.format(data_format))
        return data

    def get_tag_name(self):
        return self.name

    @property
    def name(self):
        name: str = self.attrib['Name']
        return name

    @name.setter
    def name(self, value):
        self.attrib['Name'] = value

    @property
    def data_type(self):
        data_type: str = self.attrib['DataType']
        return data_type

    @property
    def dimensions(self):
        if 'Dimensions' in self.attrib:
            return self.attrib['Dimensions'].split(" ")
        else:
            return None

    @property
    def description(self):
        if self._get_description_obj() is not None:
            return self._get_description_obj().ctext
        else:
            return ""

    @description.setter
    def description(self, value):
        if self._get_description_obj() is None:
            self.insert(0, L5XDescription(value))
        else:
            self._get_description_obj().desc = value

    def get_element_comment(self, operand):
        if self._get_comment_obj(operand) is not None:
            return self._get_comment_obj(operand).comment
        else:
            return ""

    def set_element_comment(self, operand, value):
        if self._get_comments_obj() is None:
            insert_index = self.getchildren().index(self._get_data_obj())
            self.insert(insert_index, L5XComments())
        if self._get_comment_obj(operand) is None:
            self._get_comments_obj().append(L5XComment(operand, ""))
        self._get_comment_obj(operand).comment = value

    @property
    def scope(self):
        scope_tag = self.find("./../..")
        if scope_tag.tag == 'Controller':
            return 'Controller'
        elif scope_tag.tag == 'Program':
            program: str = scope_tag.attrib['Name']
            return program
        else:
            raise TypeError("Nie da si?? zdefiniowa?? scope taga " + self.tag +
                            " - grandparent w pliku L5X nie jest Controllerem ani Programem")

    @property
    def value(self):
        return self.get_value()

    @value.setter
    def value(self, value):
        self.tag_structure = None
        self.set_value(value)

    def get_value(self, encoder=None, headers=False):
        # returns value from L5XStructure object
        data_object = self._get_data_obj("Decorated")
        if data_object is not None and data_object.child() is not None:
            data_child = self._get_data_obj("Decorated").child()
            if data_child.tag in ["Structure", "DataValue", "Array"]:
                return data_child.get_value(encoder, headers)
            else:
                raise TypeError("Unexpected xml tag: '" + data_child.tag + "' expected: " +
                                '"Structure", "DataValue", "Array"')
        else:
            data = self._get_data_obj("String")
            if data is not None:
                return data.get_value(encoder, headers)
            else:
                raise TypeError("Tag '" + self.attrib["Name"] + "' has unexpected data; expected: " +
                                '"Decorated", "String"')

    def set_value(self, value, encoder=None):
        # sets value of L5XStructure object
        data_object = self._get_data_obj("Decorated")
        if data_object is not None and data_object.child() is not None:
            data_child = self._get_data_obj("Decorated").child()
            if data_child.tag in ["Structure", "DataValue", "Array"]:
                data_child.set_value(value, encoder)
            else:
                raise TypeError("Unexpected xml tag: '" + data_child.tag + "' expected: " +
                                '"Structure", "DataValue", "Array"')
        else:
            data = self._get_data_obj("String")
            if data is not None:
                data_type = self.attrib["DataType"]
                data.set_value_datatype(value, data_type, encoder)
            else:
                raise TypeError("Tag '" + self.attrib["Name"] + "' has unexpected data; expected: " +
                                '"Decorated", "String"')
        self.tag_structure = None

    def get_value_element(self, path_string, encoder=None):
        if self._get_data_obj("Decorated").child().tag in ["Structure", "Array"]:
            return self._get_data_obj("Decorated").child().get_value_element(path_string.split("."), encoder)
        else:
            raise TypeError("Unexpected xml tag: '" + self.find("./Data[@Format='Decorated']/*").tag + "' expected: " +
                            '"Structure", "Array"')

    def set_value_element(self, value, path_string, encoder=None):
        if self._get_data_obj("Decorated").child().tag in ["Structure", "Array"]:
            pattern = r"\w\[[0-9]+\]"
            while True:
                match = re.search(pattern, path_string)
                if match:
                    path_string = path_string[:match.start()+1] + "." + path_string[match.start()+1:]
                else:
                    break
            return self._get_data_obj("Decorated").child().set_value_element(value, path_string.split("."), encoder)
        else:
            raise TypeError("Unexpected xml tag: '" + self.find("./Data[@Format='Decorated']/*").tag + "' expected: " +
                            '"Structure", "Array"')

    def get_names(self, concatenate_path=True, headers=False):
        data_child: L5XAbstractData = self._get_data_obj("Decorated").child()
        if data_child is not None:
            if data_child.attrib["DataType"] in self.SIMPLE_DATA_TYPE:
                name: str = self.attrib["Name"]
                return name
            elif data_child.tag in ["Structure", "Array"]:
                name: list[str] = data_child.get_names(self.attrib["Name"], concatenate_path, headers)
                return name
            else:
                raise TypeError("Unexpected xml tag: '" + data_child.tag + "' expected: " +
                                '"Structure", "Array" or simple data type ("BOOL", "LINT", "DINT", "INT", "SINT", ' +
                                '"REAL")')
        else:
            data = self._get_data_obj("String")
            if data is not None:
                name: str = self.attrib["Name"]
                return name
            else:
                raise TypeError("Tag '" + self.attrib["Name"] + "' has unexpected data; expected: " +
                                '"Decorated", "String"')

    def get_tag_structure(self, encoder=None):
        if self.tag_structure is None:
            self.encoder = encoder
            self.tag_structure = self.build_tag_structure(encoder)
        elif self.encoder != encoder:
            self.encoder = encoder
            self.tag_structure = self.build_tag_structure(encoder)
        return self.tag_structure

    def build_tag_structure(self, encoder=None, concatenate_path=False):
        name = self.name
        data_type = self.data_type
        if self.dimensions is not None:
            data_type += "[" + ",".join(self.dimensions) + "]"
        data_object = self._get_data_obj("Decorated")
        if data_object is not None and data_object.child() is not None:
            data_child = self._get_data_obj("Decorated").child()
            if data_child.tag in ["Structure", "DataValue", "Array"]:
                value, children = data_child.additional_tag_structure(encoder)
            else:
                raise TypeError("Unexpected xml tag: '" + data_child.tag + "' expected: " +
                                '"Structure", "DataValue", "Array"')
        else:
            data = self._get_data_obj("String")
            if data is not None:
                value, children = data.additional_tag_structure(encoder)
            else:
                raise TypeError("Tag '" + self.attrib["Name"] + "' has unexpected data; expected: " +
                                '"Decorated", "String"')
        return name, data_type, value, children


class L5XAbstractData(L5XData):

    @staticmethod
    def create_head_element(root, data_type, dimensions):
        if dimensions is not None:
            return L5XTagArray.Array(root, data_type, dimensions)
        elif data_type in L5XTag.SIMPLE_DATA_TYPE:
            return L5XTagDataValue.DataValue(root, data_type)
        elif root.data_type(data_type) is not None:
            return L5XTagStructure.Structure(root, data_type)
        else:
            raise ValueError("There is not data type '{}' in project".format(data_type))

    @staticmethod
    def create_sub_element(root, name, data_type, dimensions):
        if int(dimensions) != 0:
            return L5XTagArray.ArrayMember(root, name, data_type, dimensions)
        elif data_type in L5XTag.SIMPLE_DATA_TYPE:
            return L5XTagDataValue.DataValueMember(root, name, data_type)
        elif root.data_type(data_type) is not None:
            return L5XTagStructure.StructureMember(root, name, data_type)
        else:
            raise ValueError("There is not data type '{}' in project".format(data_type))

    def get_value(self, encoder=None, headers=False):
        pass

    def get_value_datatype(self, data_type, encoder=None, headers=False):
        pass

    def set_value(self, value, encoder=None):
        pass

    def set_value_datatype(self, value, data_type, encoder=None):
        pass

    def get_value_element(self, path, encoder=None):
        pass

    def set_value_element(self, value, path, encoder=None):
        pass

    def get_names(self, leading_name, concatenate_path=True, headers=False):
        pass

    def get_names_datatype(self, data_type, leading_name, concatenate_path=True, headers=False):
        pass

    def additional_tag_structure(self, encoder=None):
        pass

    def build_child_structure(self, parent_name, parent_data_type, encoder=None, concatenate_path=True):
        pass

    def _get_string_value(self, encoder=None):
        if encoder is not None:
            return self._get_encoded_string(encoder)
        else:
            return self.ctext.strip("'")

    def _set_string_value(self, string, max_string_length, encoder=None):
        cut_string, is_cut = RSLogixEncoding.cut_too_long_string(string, encoder, max_string_length)
        if is_cut:
            print('String is too long for this tag datatype: "' + string + '". String is cut.')
        string = cut_string
        if encoder is not None:
            string = RSLogixEncoding.encode_string(string, encoder)
            # string_bytes = string.encode(encoder)
            # if len(string_bytes) > max_string_length:
            #     print('String is too long for this tag datatype: "' + string + '". String is cut.')
            #     string_bytes = string_bytes[:max_string_length]
            # string_hex = bytes.hex(string_bytes)
            # new_string = "'$" + "$".join(string_hex[index:index + 2] for index in range(0, len(string_hex), 2)) + "'"
            # self.ctext = new_string
        # else:
        #     self.ctext = "'" + string + "'"
        self.ctext = "'" + string + "'"

    def _get_encoded_string(self, encoder):
        string = self.ctext.strip("'")
        return RSLogixEncoding.decode_string(string, encoder)

    def _get_string_len(self, encoder=None):
        data_type = None
        data_format = None
        if "DataType" in self.attrib:
            data_type = self.attrib["DataType"]
        elif "Format" in self.attrib:
            data_format = self.attrib["Format"]
        if data_type == "STRING" or data_type in self.root.get_data_types_string_names() or data_format == "String":
            string = self.get_value(encoder)
            if encoder is not None:
                return len(string.encode(encoder))
            else:
                return len(string)
        else:
            raise TypeError("Unexpected data type of DataValue: " + data_type)


class L5XComplexData(L5XAbstractData):

    @property
    def name(self):
        name: str = self.attrib['Name']
        return name

    @property
    def data_type(self):
        data_type: str = self.attrib['DataType']
        return data_type

    @property
    def dimensions(self):
        if 'Dimensions' in self.attrib:
            return self.attrib['Dimensions'].split(" ")
        else:
            return None


class L5XTagData(L5XAbstractData):

    def __init__(self, data_format, **extra):
        attrib = {"Format": data_format, **extra}
        super().__init__(attrib=attrib)
        self.tag = "Data"

    @classmethod
    def DataString(cls):
        self = L5XTagData("String", Length="0")
        self.ctext = ""
        return self

    def child(self):
        if self.attrib["Format"] == "String":
            return None
        else:
            data: L5XAbstractData = self.find("./*")
            return data

    def get_value(self, encoder=None, headers=False):
        if self.attrib["Format"] == "String":
            return self._get_string_value(encoder)
        else:
            raise TypeError('Unexpected usage of get_value function for class L5XTagData - tag "' +
                            self.find("./..").attrib["Name"] + '"; expected Data format: "String", is: "' +
                            self.attrib["Format"] + '"')

    def set_value_datatype(self, string, data_type, encoder=None):
        if self.attrib["Format"] == "String":
            if data_type == "STRING":
                max_string_length = 82
            elif data_type in self.root.get_data_types_string_names():
                max_string_length = self.root.data_type(data_type).max_string_length
            else:
                raise TypeError('Unexpected data type, trying save string to data type: "' + data_type + '"')
            self._set_string_value(string, max_string_length, encoder)
            self.attrib["Length"] = str(self._get_string_len(encoder))
        else:
            raise TypeError('Unexpected useage of get_value function for class L5XTagData - tag "' +
                            self.find("./..").attrib["Name"] + '"; expected Data format: "String", is: "' +
                            self.attrib["Format"] + '"')

    def additional_tag_structure(self, encoder=None):
        if self.attrib["Format"] == "String":
            return self._get_string_value(encoder), None
        else:
            raise TypeError('Unexpected useage of get_value function for class L5XTagData - tag "' +
                            self.find("./..").attrib["Name"] + '"; expected Data format: "String", is: "' +
                            self.attrib["Format"] + '"')


class L5XTagStructure(L5XComplexData):

    def __init__(self, root, tag_name, attrib, data_type):
        super().__init__(attrib=attrib)
        self.tag = tag_name
        self.recursive_init_structure(root, data_type)

    @classmethod
    def Structure(cls, root, data_type):
        attrib = {"DataType": data_type}
        tag_name = "Structure"
        return cls(root, tag_name, attrib, data_type)

    @classmethod
    def StructureMember(cls, root, name, data_type):
        attrib = {"Name": name, "DataType": data_type}
        tag_name = "StructureMember"
        return cls(root, tag_name, attrib, data_type)

    def recursive_init_structure(self, root, data_type):
        data_type_obj = root.data_type(data_type)
        if data_type_obj.is_string_family:
            self.append(L5XTagDataValue.DataValueMember(root, "LEN", "DINT"))
            self.append(L5XTagDataValue.DataValueMember(root, "DATA", data_type))
        else:
            for member in data_type_obj.get_data_type_members():
                member_name, member_data_type, member_dimension = member.get_member_data()
                new_element = L5XAbstractData.create_sub_element(root, member_name, member_data_type, member_dimension)
                self.append(new_element)

    def _get_data_value_member_obj(self, name=None):
        data_value_member: L5XTagDataValue
        if name is not None:
            data_value_member = self.find("./DataValueMember[@Name='{}']".format(name))
        else:
            data_value_member = self.find("./DataValueMember")
        return data_value_member

    def get_value(self, encoder=None, headers=False):
        data_type = self.attrib["DataType"]
        if data_type == "STRING" or data_type in self.root.get_data_types_string_names():
            count = int(self._get_data_value_member_obj("LEN").get_value(encoder, headers))
            if count:
                string: str = self._get_data_value_member_obj("DATA").get_value(encoder, headers)
                return string
            else:
                return ""
        else:
            values_list = []
            element: L5XAbstractData
            for element in self.findall("./*"):
                values_list.append(element.get_value(encoder, headers))
            return values_list

    def set_value(self, value, encoder=None):
        data_type: str = self.attrib["DataType"]
        if data_type == "STRING" or data_type in self.root.get_data_types_string_names():
            self._get_data_value_member_obj("DATA").set_value(value, encoder)
            count = self._get_data_value_member_obj("DATA")._get_string_len(encoder)
            self._get_data_value_member_obj("LEN").set_value(count)
        else:
            # raise TypeError("Unexpected data type of TagStructure: " + data_type)
            all_elements = self.findall("./")
            if len(all_elements) == len(value):
                for child, single_value in zip(all_elements, value):
                    child.set_value(single_value, encoder)
            else:
                raise ValueError('Values have different dimensions than expected in tag (tag: "{}")'.format(
                    self.get_tag_name()))

    def get_value_element(self, path, encoder=None):
        if len(path) > 1:
            return self.find("./*[@Name='{x}']".format(x=path[0])).get_value_element(path[1:], encoder)
        else:
            return self.find("./*[@Name='{x}']".format(x=path[0])).get_value(encoder)

    def set_value_element(self, value, path, encoder=None):
        if len(path) > 1:
            self.find("./*[@Name='{x}']".format(x=path[0])).set_value_element(value, path[1:], encoder)
        else:
            self.find("./*[@Name='{x}']".format(x=path[0])).set_value(value, encoder)

    def get_names(self, leading_name, concatenate_path=True, headers=False):
        leading_name_memory = leading_name
        if not concatenate_path:
            leading_name = ""
        data_type: str = self.attrib["DataType"]
        if data_type == "STRING" or data_type in self.root.get_data_types_string_names():
            if concatenate_path:
                return leading_name + "." + self.attrib["Name"]
            else:
                return leading_name + self.attrib["Name"]
        else:
            if self.tag == "StructureMember":
                if concatenate_path:
                    leading_name += "."
                leading_name += self.attrib["Name"]
            array_names = []
            element: L5XAbstractData
            for element in self.findall("./*"):
                array_names.append(element.get_names(leading_name, concatenate_path, headers))
            if headers:
                if self.tag == "Structure":
                    structure_name = leading_name_memory
                else:
                    if concatenate_path:
                        structure_name = leading_name
                    else:
                        structure_name = self.attrib["Name"]
                array_names = [structure_name, array_names]
            return array_names

    def additional_tag_structure(self, encoder=None):
        data_type = self.data_type
        if data_type == "STRING" or data_type in self.root.get_data_types_string_names():
            count = int(self._get_data_value_member_obj("LEN").get_value(encoder))
            if count:
                string: str = self._get_data_value_member_obj("DATA").get_value(encoder)
                return string, None
            else:
                return "", None
        else:
            # normal structure
            return None, self.findall("./*")

    def build_child_structure(self, parent_name, parent_data_type, encoder=None, concatenate_path=True):
        name = self.name
        if concatenate_path:
            name = ".".join([parent_name, name])
        data_type = self.data_type
        value = None
        children = None
        if data_type == "STRING" or data_type in self.root.get_data_types_string_names():
            count = int(self._get_data_value_member_obj("LEN").get_value(encoder))
            if count:
                value = self._get_data_value_member_obj("DATA").get_value(encoder)
            else:
                value = ""
        else:
            # normal structure
            children = self.findall("./*")
        return name, data_type, value, children


class L5XTagArray(L5XComplexData):

    def __init__(self, root, tag_name, attrib, data_type, dimensions):
        super().__init__(attrib=attrib)
        self.tag = tag_name
        self.recurse_init_elements(root, "", data_type, dimensions)

    @classmethod
    def Array(cls, root, data_type, dimensions, radix=None):
        attrib = {"DataType": data_type, "Dimensions": cls.set_dimensions_attrib(dimensions)}
        radix = L5XTag.set_radix(data_type, radix, root)
        if radix is not None:
            attrib["Radix"] = radix
        tag_name = "Array"
        return cls(root, tag_name, attrib, data_type, dimensions)

    @classmethod
    def ArrayMember(cls, root, name, data_type, dimensions, radix=None):
        attrib = {"Name": name, "DataType": data_type, "Dimensions": cls.set_dimensions_attrib(dimensions)}
        radix = L5XTag.set_radix(data_type, radix, root)
        if radix is not None:
            attrib["Radix"] = radix
        tag_name = "ArrayMember"
        return cls(root, tag_name, attrib, data_type, dimensions)

    @staticmethod
    def set_dimensions_attrib(dimensions):
        if isinstance(dimensions, list):
            string = ",".join(str(x) for x in dimensions)
        else:
            string = str(dimensions)
        return string

    def recurse_init_elements(self, root, index_name_start, data_type, dimensions):
        if len(dimensions) > 1:
            for i in range(0, int(dimensions[0])):
                if index_name_start == "":
                    index_name = str(i)
                else:
                    index_name = index_name_start + "," + str(i)
                self.recurse_init_elements(root, index_name, data_type, dimensions[1:])
        else:
            for i in range(0, int(dimensions[0])):
                if index_name_start == "":
                    index_name = "[" + str(i) + "]"
                else:
                    index_name = "[" + index_name_start + "," + str(i) + "]"
                self.append(L5XTagArrayElement(root, data_type, index_name))

    def get_value(self, encoder=None, headers=False):
        values_list = []
        data_type = self.attrib["DataType"]
        dimensions = [int(dim) for dim in self.attrib["Dimensions"].split(",")]
        element: L5XTagArrayElement
        for element in self.findall("./Element"):
            values_list.append(element.get_value_datatype(data_type, encoder, headers))
        # values_list = np.array(values_list)
        if len(dimensions) == 1:
            return values_list
        else:
            expected_length = 1
            for x in dimensions:
                expected_length *= x
            if len(values_list) == expected_length:
                new_list = list()
                i = 0
                if len(dimensions) == 2:
                    while i < len(values_list):
                        new_list.append(values_list[i:i + dimensions[1]])
                        i += dimensions[1]
                elif len(dimensions) == 3:
                    while i < len(values_list):
                        part_list = list()
                        for j in range(0, dimensions[1]):
                            part_list.append(values_list[i:i+dimensions[2]])
                            i += dimensions[2]
                        new_list.append(part_list)
                else:
                    raise ValueError('Unexpected number of dimmensions ({}) of array (tag: "{}")'.
                                     format(len(dimensions), self.get_tag_name()))
                return new_list
            else:
                raise ValueError('Expected length of array is different than number of values available (tag: "{}")'.
                                 format(self.get_tag_name()))

    def set_value(self, values, encoder=None):
        data_type = self.attrib["DataType"]
        element: L5XTagArrayElement
        dimensions = [int(dim) for dim in self.attrib["Dimensions"].split(",")]
        # for every extra dimmension above 1 do iteration of flattening nestted list
        for i in range(0, len(dimensions)-1):
            new_values = list()
            for part_values in values:
                new_values += part_values
            values = new_values
        all_elements = self.findall("./Element")
        if len(all_elements) == len(values):
            for element, value in zip(all_elements, values):
                element.set_value_datatype(value, data_type, encoder)
        else:
            raise ValueError('Values have different dimensions than expected in tag (tag: "{}")'.format(
                self.get_tag_name()))

    def get_value_element(self, path, encoder=None):
        data_type = self.attrib["DataType"]
        if len(path) > 1:
            return self.find("./*[@Index='{x}']".format(x=path[0])).get_value_element(path[1:], encoder)
        else:
            return self.find("./*[@Index='{x}']".format(x=path[0])).get_value_datatype(data_type, encoder)

    def set_value_element(self, value, path, encoder=None):
        data_type = self.attrib["DataType"]
        if len(path) > 1:
            self.find("./*[@Index='{x}']".format(x=path[0])).set_value_element(value, path[1:], encoder)
        else:
            self.find("./*[@Index='{x}']".format(x=path[0])).set_value_datatype(value, data_type, encoder)

    def get_names(self, leading_name, concatenate_path=True, headers=False):
        data_type = self.attrib["DataType"]
        leading_name_memory = leading_name
        if not concatenate_path:
            leading_name = ""
        if self.tag == "ArrayMember":
            if concatenate_path:
                leading_name += "."
            leading_name += self.attrib["Name"]
        array_names = []
        element: L5XTagArrayElement
        for element in self.findall("./*"):
            array_names.append(element.get_names_datatype(data_type, leading_name, concatenate_path, headers))
        if headers:
            if self.tag == "Array":
                structure_name = leading_name_memory
            else:
                if concatenate_path:
                    structure_name = leading_name
                else:
                    structure_name = self.attrib["Name"]
            array_names = [structure_name, array_names]
        return array_names

    def additional_tag_structure(self, encoder=None):
        return None, self.findall("./Element")

    def build_child_structure(self, parent_name, parent_data_type, encoder=None, concatenate_path=True):
        name = self.name
        if concatenate_path:
            name = ".".join([parent_name, name])
        data_type = self.data_type + "[" + ",".join(self.dimensions) + "]"
        value = None
        children = self.findall("./Element")
        return name, data_type, value, children


class L5XTagDataValue(L5XAbstractData):

    def __init__(self, root, tag_name, attrib, string=None):
        super().__init__(attrib=attrib)
        self.tag = tag_name
        if string is not None:
            self.ctext = string

    @classmethod
    def DataValue(cls, root, data_type, radix=None):
        attrib = dict()
        attrib["DataType"] = data_type
        radix = L5XTag.set_radix(data_type, radix, root)
        if radix is not None:
            attrib["Radix"] = radix
        attrib["Value"] = str(L5XTag.default_value(data_type))
        tag_name = "DataValue"
        return cls(root, tag_name, attrib)

    @classmethod
    def DataValueMember(cls, root, name, data_type, radix=None):
        attrib = dict()
        attrib["Name"] = name
        attrib["DataType"] = data_type
        radix = L5XTag.set_radix(data_type, radix, root)
        if radix is not None:
            attrib["Radix"] = radix
        data_type_obj = root.data_type(data_type)
        # If it's not string, i will be None
        string_value = None
        # Check if object is string
        if data_type_obj.is_string_family:
            string_value = ""
        # if not set simple default value
        elif data_type_obj.type == "SIMPLE":
            attrib["Value"] = str(L5XTag.default_value(data_type))
        tag_name = "DataValueMember"
        return cls(root, tag_name, attrib, string_value)

    def get_value(self, encoder=None, headers=False):
        data_type = self.attrib["DataType"]
        if data_type in L5XTag.SIMPLE_DATA_TYPE:
            value = self.attrib["Value"]
            if "." in value:
                return float(value)
            else:
                return int(value)
        elif data_type == "STRING" or data_type in self.root.get_data_types_string_names():
            return self._get_string_value(encoder)
        else:
            raise TypeError('Unexpected data type of DataValue: "' + data_type + '"')

    def set_value(self, value, encoder=None):
        data_type = self.attrib["DataType"]
        if data_type in L5XTag.SIMPLE_DATA_TYPE:
            self.attrib["Value"] = str(value)
        elif data_type == "STRING" or data_type in self.root.get_data_types_string_names():
            if data_type == "STRING":
                max_string_length = 82
            else:
                max_string_length = self.root.data_type(data_type).max_string_length
            self._set_string_value(value, max_string_length, encoder)
        else:
            raise TypeError("Unexpected data type of DataValue: " + data_type)

    def get_names(self, leading_name, concatenate_path=True, headers=False):
        if concatenate_path:
            leading_name += "."
        else:
            leading_name = ""
        return leading_name + self.attrib["Name"]

    def additional_tag_structure(self, encoder=None):
        data_type = self.attrib["DataType"]
        if data_type in L5XTag.SIMPLE_DATA_TYPE:
            value = self.attrib["Value"]
            if "." in value:
                return float(value), None
            else:
                return int(value), None
        elif data_type == "STRING" or data_type in self.root.get_data_types_string_names():
            return self._get_string_value(encoder), None
        else:
            raise TypeError('Unexpected data type of DataValue: "' + data_type + '"')

    def build_child_structure(self, parent_name, parent_data_type, encoder=None, concatenate_path=True):
        name = self.attrib["Name"]
        if concatenate_path:
            name = ".".join([parent_name, name])
        data_type = self.attrib["DataType"]
        if data_type in L5XTag.SIMPLE_DATA_TYPE:
            value_str = self.attrib["Value"]
            if "." in value_str:
                value = float(value_str)
            else:
                value = int(value_str)
        elif data_type == "STRING" or data_type in self.root.get_data_types_string_names():
            value = self._get_string_value(encoder)
        else:
            raise TypeError('Unexpected data type of DataValue: "' + data_type + '"')
        return name, data_type, value, None


class L5XTagArrayElement(L5XAbstractData):

    def __init__(self, root, data_type, index):
        attrib = {"Index": index}
        if data_type in L5XTag.SIMPLE_DATA_TYPE:
            attrib["Value"] = str(L5XTag.default_value(data_type))
            super().__init__(attrib=attrib)
        elif data_type in root.get_data_types_all_names():
            super().__init__(attrib=attrib)
            self.append(L5XTagStructure.Structure(root, data_type))
        else:
            raise ValueError("Data type '{}' is not defined in L5X project".format(data_type))
        self.tag = "Element"

    @property
    def get_index(self):
        return self.attrib["Index"]

    def get_value_datatype(self, data_type, encoder=None, headers=False):
        if data_type in L5XTag.SIMPLE_DATA_TYPE:
            if "." in self.attrib["Value"]:
                return float(self.attrib["Value"])
            else:
                return int(self.attrib["Value"])
        # elif data_type == "STRING" or data_type in self.root.get_data_types_string_names():
        else:
            return self.find("./Structure").get_value(encoder, headers)
        # else:
        #     raise TypeError("Unexpected data type of TagArrayElement: " + data_type)

    def set_value_datatype(self, value, data_type, encoder=None):
        if data_type in L5XTag.SIMPLE_DATA_TYPE:
            self.attrib["Value"] = str(value)
        elif data_type == "STRING" or data_type in self.root.get_data_types_string_names():
            self.find("./Structure").set_value(value, encoder)
        else:
            # raise TypeError("Unexpected data type of TagArrayElement: " + data_type)
            child = self.find("./")
            child.set_value(value, encoder)


    def get_value_element(self, path, encoder=None):
        return self.child().get_value_element(path, encoder)

    def set_value_element(self, value, path, encoder=None):
        self.child().set_value_element(value, path, encoder)

    def get_names_datatype(self, data_type, leading_name, concatenate_path=True, headers=False):
        element_name = leading_name + self.attrib["Index"]
        if self.child() is not None and data_type != "STRING" and \
                not (data_type in self.root.get_data_types_string_names()):
            element: L5XAbstractData
            if len(self.findall("./*")) > 1:
                array_names = []
                for element in self.findall("./*"):
                    array_names.append(element.get_names(element_name, concatenate_path, headers))
                return array_names
            else:
                element = self.find("./*")
                return element.get_names(element_name, concatenate_path, headers)
        else:
            return element_name

    def build_child_structure(self, parent_name, parent_data_type, encoder=None, concatenate_path=True):
        name = parent_name + self.get_index
        data_type = parent_data_type.split("[")[0]
        value = None
        children = None
        if data_type in L5XTag.SIMPLE_DATA_TYPE:
            if "." in self.attrib["Value"]:
                value = float(self.attrib["Value"])
            else:
                value =  int(self.attrib["Value"])
        elif data_type == "STRING" or data_type in self.root.get_data_types_string_names():
            value = self.find("./Structure").get_value(encoder)
        else:
            children = self.findall("./Structure/*")
        return name, data_type, value, children


class L5XProgram(L5XData):

    @property
    def routines(self):
        routines: list[L5XRoutine] = self.findall("Routines/Routine")
        return routines

    def replace_code(self, old, new, count=0):
        for routine in self.routines:
            routine.replace_code(old, new, count)

    def tag(self, tag_name):
        tag: L5XTag = self.find("Tags/Tag[@Name='{}']".format(tag_name))
        return tag


class L5XRoutine(L5XData):

    @property
    def rungs(self):
        rungs: list[L5XRung] = self.findall("RLLContent/Rung")
        return rungs

    def replace_code(self, old, new, count=0):
        for rung in self.rungs:
            rung.replace_code(old, new, count)


class L5XRung(L5XData):

    def _get_code_obj(self):
        code: L5XText = self.find('Text')
        return code

    def _get_comment_obj(self):
        comment: L5XComment = self.find('Comment')
        return comment

    @property
    def code(self):
        return self._get_code_obj().ctext

    @code.setter
    def code(self, value):
        self._get_code_obj().ctext = value

    def replace_code(self, old, new, count=0):
        self._get_code_obj().replace_code(old, new, count)

    @property
    def comment(self):
        return self._get_comment_obj().ctext

    @comment.setter
    def comment(self, value):
        self._get_comment_obj().ctext = value

    def decor_comment(self, string=None, decorator='=', lines=1, repeat=92, decor_empty=False):
        if not string:
            string = self.comment
        self._get_comment_obj().replace_decor(decorator, lines, repeat, decor_empty, string)


class L5XText(L5XData):

    def replace_code(self, old, new, count=0):
        self.ctext = re.sub(old, new, self.ctext, count)


class L5XDescription(L5XData):

    def _init(self):
        super()._init()
        self.tag = "Description"

    def __init__(self, desc_string):
        super().__init__()
        self.tag = "Description"
        self.ctext = desc_string

    @property
    def desc(self):
        return self.ctext

    @desc.setter
    def desc(self, value):
        self.ctext = value


class L5XComments(L5XData):

    def _init(self):
        super()._init()
        self.tag = "Comments"

    def __init__(self):
        super().__init__()
        self.tag = "Comments"


class L5XComment(L5XData):

    def _init(self, attrib=None):
        super()._init()
        self.tag = "Comment"
        if attrib is not None:
            self.attrib = attrib

    def __init__(self, operand, comment_string):
        super().__init__(attrib={"Operand": operand})
        self.tag = "Comment"
        self.ctext = comment_string

    @property
    def comment(self):
        return self.ctext

    @comment.setter
    def comment(self, value):
        self.ctext = value

    @staticmethod
    def decor(string, decorator='=', lines=1, repeat=92):
        # decor comment with decorator before and after comment
        return (decorator*repeat + '\n')*lines + string + ('\n' + decorator*repeat)*lines

    @staticmethod
    def strip_decor(string):  # add stripping decorators as: #===============================#
        pattern = r"\A\s*((([\w\W])\3{4,})\n)*(?P<string>.+)([\n]\2)*\s*\Z"
        try:
            return re.search(pattern, string).group("string")
        except AttributeError:
            return ""

    def replace_decor(self, decorator='=', lines=1, repeat=92, decor_empty=False, string=""):
        if string or decor_empty:
            self.ctext = self.decor(self.strip_decor(string), decorator, lines, repeat)
        return self


class L5XeTree:
    L5X_NAMESPACE_DICT = {"Description": L5XDescription, "Comment": L5XComment, "DataType": L5XDataType, "Tag": L5XTag,
                          "Rung": L5XRung, "Routine": L5XRoutine, "Program": L5XProgram, "Text": L5XText,
                          "RSLogix5000Content": L5XRoot, "Comments": L5XComments, "Structure": L5XTagStructure,
                          "DataValue": L5XTagDataValue, "DataValueMember": L5XTagDataValue, "Array": L5XTagArray,
                          "StructureMember": L5XTagStructure, "Element": L5XTagArrayElement, "ArrayMember": L5XTagArray,
                          "Data": L5XTagData, "Member": L5XMember}
    UTF8_DECODER_DICT = {"$C4$84": "??", "$C4$86": "??", "$C4$98": "??", "$C5$81": "??", "$C5$83": "??", "$C3$93": "??",
                         "$C5$9A": "??", "$C5$B9": "??", "$C5$BB": "??", "$C4$85": "??", "$C4$87": "??", "$C4$99": "??",
                         "$C5$82": "??", "$C5$84": "??", "$C3$B3": "??", "$C5$9B": "??", "$C5$BA": "??", "$C5$BC": "??"}
    DECODERS_DICT = {'utf8': UTF8_DECODER_DICT}
    TMP_XML_FILE = 'tmp.xml'

    def __init__(self, xml_open, remove_blank_text=False):
        self.xml_open = xml_open
        self.fallback = ET.ElementDefaultClassLookup(element=L5XData)
        self.lookup = ET.ElementNamespaceClassLookup(self.fallback)
        self.parser = ET.XMLParser(strip_cdata=False, remove_blank_text=remove_blank_text)
        self.parser.set_element_class_lookup(self.lookup)
        self.namespace = self.lookup.get_namespace("")
        for key in self.L5X_NAMESPACE_DICT:
            self.namespace[key] = self.L5X_NAMESPACE_DICT[key]

    def __enter__(self):
        return self.parse_tree()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return 0

    def parse_tree(self):
        self.tree = ET.parse(self.xml_open, self.parser)
        return self

    def save_file(self, xml_write):
        self.tree.write(self.TMP_XML_FILE, encoding='utf-8', xml_declaration=True)
        # Przepisanie pliku ??eby znak ko??ca linii by?? \r\n zamiast \n
        with open(xml_write, 'w', encoding='utf-8') as f_w:
            with open(self.TMP_XML_FILE, 'r', encoding='utf-8') as f_r:
                f_w.write(f_r.read())
        os.remove(self.TMP_XML_FILE)
        return 0

    def decode_string(self, string, decoder='UTF8'):
        """
        Funkcja przestarza??a - nie powinno si?? jej u??ywa??
        Zmienia znaki z kodowanie CP1250 (w ten spos??b zapisywane s?? polskie znaki w L5X) na UTF
        :param string: string do zamnienienia
        :param decoder: rodzaj kodowania do zdekodowania - obs??ugiwane UTF8
        :return: zamieniony string
        """
        if not self.DECODERS_DICT[decoder.lower()]:
            raise ValueError("Nie ma takiego dekodera: {}".format(decoder))
        for word, initial in self.DECODERS_DICT[decoder.lower()].items():
            string = string.replace(word, initial)
        return string
