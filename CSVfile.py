class CSVfile:

    def tree_representation(names, values, separation='\t', new_line='\n', leading='', child_shifted=True):
        s = separation
        string = ""
        child_leading = leading
        # print(names)
        for name, value in zip(names, values):
            if isinstance(name, list):
                if len(name) == len(value):
                    if child_shifted:
                        child_leading = leading + s
                    string += CSVfile.tree_representation(name, value, separation=s, new_line=new_line, leading=child_leading,
                                                  child_shifted=child_shifted)
                else:
                    raise ValueError("List of names if different size that list of values")
            else:
                string += leading + name + s + str(value) + new_line
        return string
