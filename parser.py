# Autor: Jan Šulák
# Datum: 25.2.2024

import sys
import os
import re
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

VAR_REGEX = re.compile(r"^(LF|TF|GF)@[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*$")
SYMB_REGEX = re.compile(r"^(LF|TF|GF)@[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*$|^(int|string|bool)@.*$|^(nil)@nil$")
LABEL_REGEX = re.compile(r"^[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*$")
TYPE_REGEX = re.compile(r"^(int|string|bool)$")
INT_REGEX = re.compile(r"^(int)@[-+]?((0o[0-7]+)|(0x[0-9a-fA-F]+)|[0-9]+)$")
BOOL_REGEX = re.compile(r"^(bool)@(true|false)$")
STRING_REGEX = re.compile(r"^(string)@([^\s#\\]|\\[0-9]{3})*$")
NIL_REGEX = re.compile(r"^(nil)@nil$")

Args = str
Var = Args("var")
Symb = Args("symb")
Label = Args("label")
Type = Args("type")

# Slovník instrukcí a jejich argumentů.
instructions: dict[str, list[Args]] = {
    "MOVE": [Var, Symb],
    "CREATEFRAME": [],
    "PUSHFRAME": [],
    "POPFRAME": [],
    "DEFVAR": [Var],
    "CALL": [Label],
    "RETURN": [],
    "PUSHS": [Symb],
    "POPS": [Var],
    "ADD": [Var, Symb, Symb],
    "SUB": [Var, Symb, Symb],
    "MUL": [Var, Symb, Symb],
    "IDIV": [Var, Symb, Symb],
    "LT": [Var, Symb, Symb],
    "GT": [Var, Symb, Symb],
    "EQ": [Var, Symb, Symb],
    "AND": [Var, Symb, Symb],
    "OR": [Var, Symb, Symb],
    "NOT": [Var, Symb],
    "INT2CHAR": [Var, Symb],
    "STRI2INT": [Var, Symb, Symb],
    "READ": [Var, Type],
    "WRITE": [Symb],
    "CONCAT": [Var, Symb, Symb],
    "STRLEN": [Var, Symb],
    "GETCHAR": [Var, Symb, Symb],
    "SETCHAR": [Var, Symb, Symb],
    "TYPE": [Var, Symb],
    "LABEL": [Label],
    "JUMP": [Label],
    "JUMPIFEQ": [Label, Symb, Symb],
    "JUMPIFNEQ": [Label, Symb, Symb],
    "EXIT": [Symb],
    "DPRINT": [Symb],
    "BREAK": [],
}


# Funkce vypíše nápovědu, pokud je spuštěna s parametrem --help.
def print_help():
    help_text = """
Usage: 
    parse.py [--help]
    
Options:
    --help  -  Prints this help message.
            
Description:
    This script reads the LANGUAGE from the stdin
    and generates the XML representation of the code
    to the stdout.
    """
    print(help_text)
    return


# Generuje XML reprezentaci instrukcí na základě vstupních dat.
def generate_xml(result):
    root = ET.Element("program")
    root.set("language", "LANGUAGE")
    order = 0
    cnt = 0
    for line in result:
        opcode = line[0].upper()
        args = line[1:]
        cnt = 0
        order += 1

        instruction = ET.SubElement(root, "instruction")
        instruction.set("order", str(order))
        instruction.set("opcode", opcode)

        for arg in args:
            cnt += 1
            arg_type = instructions[opcode][cnt - 1]
            arg_element = ET.SubElement(instruction, f"arg{cnt}")
            if "int@" in arg:
                if re.match(INT_REGEX, arg):
                    arg_element.set("type", "int")
                    arg_element.text = arg.split("@")[1]
                else:
                    print("Error: Invalid integer.", file=sys.stderr)
                    sys.exit(23)
            elif "bool@" in arg:
                if re.match(BOOL_REGEX, arg):
                    arg_element.set("type", "bool")
                    arg_element.text = arg.split("@")[1]
                else:
                    print("Error: Invalid boolean.", file=sys.stderr)
                    sys.exit(23)
            elif "string@" in arg:
                if re.match(STRING_REGEX, arg):
                    arg_element.set("type", "string")
                    after_first_at = arg.split("@")[1:]
                    to_string = "@".join(after_first_at)
                    arg_element.text = to_string
                else:
                    print("Error: Invalid string.", file=sys.stderr)
                    sys.exit(23)
            elif "nil@" in arg:
                if re.match(NIL_REGEX, arg):
                    arg_element.set("type", "nil")
                    arg_element.text = "nil"
                else:
                    print("Error: Invalid nil.", file=sys.stderr)
                    sys.exit(23)
            elif re.match(TYPE_REGEX, arg) and arg_type == "type":
                arg_element.set("type", "type")
                arg_element.text = arg
            elif re.match(VAR_REGEX, arg) and (arg_type == "var" or arg_type == "symb"):
                arg_element.set("type", "var")
                arg_element.text = arg
            elif re.match(LABEL_REGEX, arg) and arg_type == "label":
                arg_element.set("type", "label")
                arg_element.text = arg
            else:
                print("Error: Invalid argument.", file=sys.stderr)
                sys.exit(23)

    xml_str = ET.tostring(root, encoding="UTF-8", method="xml", xml_declaration=True).decode("utf-8")
    xml_str = (minidom.parseString(xml_str).toprettyxml(indent=f"{4 * ' '}", encoding="UTF-8").decode("utf-8"))
    return xml_str


# Odstraňuje komentáře ze vstupních dat.
def erase_comments(input):
    result = []
    for line in input:
        if "#" in line:
            line = line.split("#")[0]
        result.append(line)
    result = remove_empty_lines(result)
    return result


# Odstraňuje prázdné řádky ze vstupních dat.
def remove_empty_lines(input):
    result = []
    for line in input:
        if line.strip():
            result.append(line)
    return result


# Ověřuje platnost argumentů instrukcí.
def check_arg(arg_type, arg):
    if arg_type == "var" and not re.match(VAR_REGEX, arg):
        print("Error: Invalid variable name.", file=sys.stderr)
        sys.exit(23)
    elif arg_type == "symb" and not re.match(SYMB_REGEX, arg):
        print("Error: Invalid symbol.", file=sys.stderr)
        sys.exit(23)
    elif arg_type == "label" and not re.match(LABEL_REGEX, arg):
        print("Error: Invalid label name.", file=sys.stderr)
        sys.exit(23)
    elif arg_type == "type" and not re.match(TYPE_REGEX, arg):
        print("Error: Invalid type.", file=sys.stderr)
        sys.exit(23)
    return


# Analyzuje instrukce a kontroluje platnost jejich argumentů.
def analyze_instructions(lines):
    for line in lines:
        opcode = line[0].upper()
        if opcode in instructions:
            args = line[1:]
            if len(instructions[opcode]) != len(args):
                print(opcode, "Error: Invalid number of arguments.", file=sys.stderr)
                sys.exit(23)
            for i in range(len(instructions[opcode])):
                check_arg(instructions[opcode][i], args[i])
        else:
            print(f"Error: Instruction {opcode} is not in the list.", file=sys.stderr)
            sys.exit(22)
    return


# Rozdělí vstupní data na instrukce a argumenty.
def parse_input(input):
    result = erase_comments(input)

    header = False
    list_of_lines = []
    list_of_instructions = []

    for line in result:
        if not header:
            if ".LANGUAGE" in line.strip().upper():
                header = True
            else:
                print("Error: Header is missing.", file=sys.stderr)
                sys.exit(21)
        elif ".LANGUAGE" in line.strip().upper() and header:
            print("Error: Too many headers.", file=sys.stderr)
            sys.exit(23)
        list_of_instructions = line.split()
        list_of_lines.append(list_of_instructions)
    if not header:
        print("Error: Header is missing.", file=sys.stderr)
        sys.exit(21)
    if list_of_lines[0][0].upper() != ".LANGUAGE":
        print("Error: Header is missing.", file=sys.stderr)
        sys.exit(21)
    list_of_lines.pop(0)
    analyze_instructions(list_of_lines)

    return list_of_lines

class InputPermissionError(PermissionError):
    pass
class OutputPermissionError(PermissionError):
    pass

def main():
    try:
        # Kontrola, zda existuje vstupní soubor
        if not sys.stdin.isatty():
            input_file = sys.stdin
        else:
            raise FileNotFoundError("File does not exist.")

        # Kontrola, přístupu k vstupnímu a výstupnímu souboru
        if hasattr(input_file, 'name') and input_file.name != '<stdin>':
            if not os.access(input_file.name, os.R_OK):
                raise InputPermissionError(f"File {input_file.name} is not readable.")

        output_file = sys.stdout
        if hasattr(output_file, 'name') and output_file.name != '<stdout>':
            if not os.access(output_file.name, os.W_OK):
                raise OutputPermissionError(f"Write into {output_file.name} is not allowed.")

        result = input_file.read().splitlines()
        # Zpracování vstupních dat
        result = parse_input(result)
        output_file.write(generate_xml(result))

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(11)
        
    except InputPermissionError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(11)
        
    except OutputPermissionError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(12)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(99)

if __name__ == "__main__":
    # Kontrola parametrů
    if "--help" in sys.argv:
        if len(sys.argv) > 2:
            print("Error: --help cannot be combined with other parameters.", file=sys.stderr)
            sys.exit(10)
        else:
            print_help()
            sys.exit(0)
    elif len(sys.argv) > 1:
        print("Error: --help is the only parameter that can be provided.", file=sys.stderr)
        sys.exit(10)
    else:
        main()