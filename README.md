## Parser jazyka LANGUAGE <br>
Jan Šulák <br>

### Popis programu

Program je napsán v jazyce Python a využívá tyto knihovny:
* `sys` pro práci se standardním vstupem a výstupem <br>
* `re` pro regulární výrazy <br>
* `xml.etree.ElementTree` a `xml.dom.minidom` pro generování výsledné XML reprezentace

Cílem programu je vytvořit XML reprezentaci kódu v jazyce LANGUAGE. Skript analyzuje jednotlivé instrukce s jejich argumenty a na základě získaných informací generuje XML strukturu. Na začátku jsou definovány regulární výrazy pro ověření platnosti jednotlivých instrukcí a argumentů. Instrukce jsou uložený ve slovníku, kde klíč je název instrukce (operační kód) a hodnota obsahuje typy argumentů. Program pracuje pouze s jedním parametrem `--help`, který zobrazí nápovědu. Vstupní data jsou přijmána ze standardního vstupu, výstup je odváděn na standardní výstup a chybové hlášky jsou odváděny na standardní chybový výstup.

### Funkce

* `print_help()`: Tato funkce vypíše nápovědu, pokud je spuštěna s parametrem `--help`. <br>
* `generate_xml(result)`: Generuje XML reprezentaci instrukcí na základě vstupních dat. <br>
* `erase_comments(input)`: Odstraňuje komentáře ze vstupních dat. <br>
* `remove_empty_lines(input)`: Odstraňuje prázdné řádky ze vstupních dat. <br>
* `check_arg(arg_type, arg)`: Ověřuje platnost argumentů instrukcí. <br>
* `analyze_instructions(lines)`: Analyzuje instrukce a kontroluje platnost jejich argumentů. <br>
* `parse_input(input)`: Rozdělí vstupní data na instrukce a argumenty. <br>
* `main()`: Hlavní funkce programu, která řídí celý proces voláním jednotlivých funkcí. <br>

Tento program umožňuje efektivně zpracovat jazyk LANGUAGE a jeho výstup ve formátu XML lze využít dalšími nástroji například při následné interpretaci.