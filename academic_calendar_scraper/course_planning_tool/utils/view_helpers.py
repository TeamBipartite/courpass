COURSE = 0
ALL_PREREQS_SHOWN = 1
DEPT_PERM = 2
MIN_YEAR = 3

IS_PREREQ = 0
IS_COREQ = 1
GROUP_ID = 2

NUM_REQS_FROM_GROUP = 0
ALL_COURSES_SHOWN = 1
MIN_GRADE = 2
SUB_RULES = 3

ALPHABET_LENGTH = 26

def get_header_legend_data(header_info: list[tuple]) -> list[tuple]:
    not_all_prereqs_icon = "<i class='fa-solid fa-eye-slash'></i>"
    dept_perm_icon = "<i class='fa-solid fa-file-signature'></i>"
    min_years = set([])
    result = {}
    for header_item in header_info:
        if not_all_prereqs_icon not in result and not header_item[ALL_PREREQS_SHOWN]:
            result[not_all_prereqs_icon] = "Not all prerequisites shown. See calendar for details."
        if dept_perm_icon not in result and header_item[DEPT_PERM]:
            result[dept_perm_icon] = "Or department permission."
        if header_item[MIN_YEAR] > 0:
            min_years.add(header_item[MIN_YEAR])

    if len(min_years) > 0:
        list(min_years).sort()
        min_year_as_str = " ".join([str(min_year) for min_year in min_years])
        result[f"<sup>{min_year_as_str}</sup>"] = "Minimum year standing required."
    
    return result.items()

def get_processed_grid_data(grid_info: list[list[tuple[bool, bool, list[int]]]]) -> list[list[tuple[bool, bool, str]]]:
    """
    Constructs a modified version of the given grid_info, where each tuple's list of integers
    is used to construct the group key as a string to display in the UI.
    The modified data structure can be used to fill each row and column of the prereq grid.
    """
    result = []
    for row in grid_info:
        row_result = []
        for col in row:
            tup = (col[IS_PREREQ], col[IS_COREQ], get_group_key(col[GROUP_ID]))
            row_result.append(tup)
        result.append(row_result)
    
    return result
        
def get_group_key(group_id: list[int]) -> str:
    """
    Construct an alphanumeric group key (as a string) from the given 
    group_id where elements at even index positions are digits in [0-9] 
    and elements at odd index positions are characters in [a-z].
    Ex: A group_id of [1, 0, 2, 1] becomes the string '1a2b'
    """
    key = ""
    for idx in range(len(group_id)):
        key += translate_subkey(group_id[idx], idx)
    
    return key

def translate_subkey(group_subid: int, idx: int) -> str:
    """
    Generate a subkey based on the group_subid and the idx.
    If the given idx is even then the returned subkey is group_subid 
    as a string. Otherwise, the returned subkey is a character in
    [a-z] (at the offset of group_subid in the alphabet).
    Ex: If group_subid = 2 and idx = 1 then 'c' is returned.
    """
    if idx % 2 == 0:
        return str(group_subid)
    else:
        return chr(ord('a') + (abs(group_subid)) % ALPHABET_LENGTH)

#TODO: add named tuple to definition
def get_group_legend(group_info: list[tuple[int, str, bool, list]]) -> str:
    """
    Construct the HTML group legend using the given group_info. 
    The returned HTML string consists of nested divs that mimic a nested sublists
    where each list item corresponds to a group rule. 
    """
    # Use a list to store the legend to ensure we have a reference to the string as it's modified
    legend = [""]

    # Create a legend item for each group rule
    for idx in range (1, len(group_info)): # Ignore index 0 as group at index 0 is always required
        add_rule_to_legend(group_info[idx], idx, 0, legend)

    # Return the HTML string only
    return legend[0]

def add_rule_to_legend(rule_info: tuple, key: int, idx: int, html_legend: list[str]) -> None:
    """
    Recursively add a rule to the html_legend.
    Note that each rule will be added with a margin of 20*idx px. 
    Assumptions: the given html_legend is a list of length 1 where the list item
    is a string holding the (potentially partially built) legend.
    """
    html_legend[0] += f'<div style="margin-left:{20*idx}px;">{get_rule_text(rule_info, key, idx)}</div>'

    if len(rule_info[SUB_RULES]) == 0: 
        return
    
    for subrule_idx in range(len(rule_info[SUB_RULES])):
        add_rule_to_legend(rule_info[SUB_RULES][subrule_idx], subrule_idx, idx+1, html_legend)


def get_rule_text(rule_info: tuple, key: int, idx: int) -> str:
    """
    Return a string with the human readable rule description based on the information
    in rule_info. The rule text is prefixed with a subkey built from the given key and idx.
    """
    rule = ""
    rule += f"<sup><b>{translate_subkey(key, idx)}</b></sup> "

    if rule_info[NUM_REQS_FROM_GROUP] > 0:
        if rule_info[NUM_REQS_FROM_GROUP] == 1:
            rule += f"There is {rule_info[NUM_REQS_FROM_GROUP]} course in this group needed to satisfy the requirement. "
        else: 
            rule += f"There are {rule_info[NUM_REQS_FROM_GROUP]} courses in this group needed to satisfy the requirement. "
    
    if rule_info[ALL_COURSES_SHOWN]:
        rule += "All courses are shown on the above table. "
    else:
        rule += "Not all courses are shown on the above table; see the course calendar for details. "
    
    if rule_info[MIN_GRADE] != "":
        rule += f"A minimum grade of {rule_info[MIN_GRADE]} is required in this course."
    
    return rule
