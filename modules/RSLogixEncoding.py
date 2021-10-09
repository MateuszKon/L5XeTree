import re
import warnings


class RSLogixEncoding:

    SPECIAL_CHARACTERS_DICT = {"$$": "$", "$\\": "\\", "$L": "\n", "$N": "\r\n", "$P": "\f", "$R": "\r", "$T": "\t"}

    @staticmethod
    def decode_string(string, encoder):
        # pattern searching for characters: $00 - $FF
        pattern = r"([\$][0-9A-Fa-f]{2})+"
        pattern_special = r"[\$][\$\\LNPRT]"
        index = 0
        while True:
            match = re.search(pattern_special, string[index:])
            if match:
                try:
                    string = string[:index + match.start()] + RSLogixEncoding.SPECIAL_CHARACTERS_DICT[match.group()]\
                             + string[index + match.end():]
                except ValueError:
                    print('Error during decoding string with encoder "' + encoder + '"; invalid string: "' + string +
                          '"')
            else:
                break
            index += match.start() + 1
        # search for in whole string
        index = 0
        while True:
            match = re.search(pattern, string[index:])
            if match:
                # hex_text - get found characters without $ signs
                hex_text = match.group().replace("$", "")
                try:
                    # hex_array - change characters into bytes array
                    hex_array = bytes.fromhex(hex_text)
                    # characters - change bytes into characters with encoder
                    characters = hex_array.decode(encoder)
                    # string replace $00 with ecnoded character
                    string = string[:index + match.start()] + characters + string[index + match.end():]
                except ValueError:
                    print('Error during decoding string with encoder "' + encoder + '"; invalid string: "' + string +
                          '"')
                index += match.start() + 1
            else:
                break
        return string

    @staticmethod
    def encode_string(string: str, encoder):
        # change string into array of encoded characters
        copy_string = list()
        for i, char in enumerate(string):
            try:
                copy_string.append(char.encode(encoder))
            except UnicodeEncodeError:
                warnings.warn("Not all characters can be encoded with selected encoder")
                copy_string.append(char.encode(encoder, "replace"))
        string = copy_string
        #
        # string = [char.encode(encoder) for char in string]
        for i, char in enumerate(string):
            # if character is build from 2 or more bytes or it isn't from ASCII table (above number 127)
            if len(char) > 1 or not 31 < char[0] < 127 or char[0] in [0x24, 0x5C]:
                # change special characters into string like '$FF' or '$FF$FF'
                char = char.hex()
                string[i] = '$' + '$'.join(char[i:i+2] for i in range(0, len(char), 2))
            else:
                # simple decode normal character
                string[i] = char.decode(encoder)
        # concatenate array into single string
        return "".join(string)

    @staticmethod
    def cut_too_long_string(string: str, encoder, max_length):
        if encoder is None:
            encoder = "ASCII"
        string_enc = string.encode(encoder)
        if len(string_enc) > max_length:
            is_cut = 1
            string = string_enc[0:max_length].decode(encoder)
        else:
            is_cut = 0
        return string, is_cut
