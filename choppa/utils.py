import regex as re   # type: ignore

STAR_PATTERN: re.Regex = re.compile("(?<=(?<!\\\\)(?:\\\\\\\\){0,100})\\*")
PLUS_PATTERN: re.Regex = re.compile("(?<=(?<!\\\\)(?:\\\\\\\\){0,100})(?<![\\?\\*\\+]|\\{[0-9],?[0-9]?\\}?\\})\\+")
RANGE_PATTERN: re.Regex = re.compile("(?<=(?<!\\\\)(?:\\\\\\\\){0,100})\\{\\s*([0-9]+)\\s*,\\s*\\}")
CAPTURING_GROUP_PATTERN: re.Regex = re.compile("(?<=(?<!\\\\)(?:\\\\\\\\){0,100})\\((?!\\?)")


def remove_block_quotes(pattern: str) -> str:
    """
    Replaces block quotes in regular expressions with normal quotes. For
    example "\Qabc\E" will be replace with "\a\b\c".

    @param pattern
    @return pattern with replaced block quotes
    """

    pattern_builder: str = ""
    quote: bool = False;
    previous_char: str = ""

    for current_char in pattern:
        if quote:
            if previous_char == '\\' and current_char == 'E':
                quote = False
                # Need to remove "\\" at the end as it has been added
                # in previous iteration.
                pattern_builder = pattern_builder[:-2]
            else:
                pattern_builder += '\\' + current_char

        else:
            if previous_char == '\\' and current_char == 'Q':
                quote = True
                # Need to remove "\" at the end as it has been added
                # in previous iteration.
                pattern_builder = pattern_builder[:-1]
            else:
                pattern_builder += current_char
        previous_char = current_char

    return pattern_builder

def finitize(pattern: str, infinity: int) -> str:
    """
    Changes unlimited length pattern to limited length pattern. It is done by
    replacing constructs with "*" and "+" symbols with their finite 
    counterparts - "{0,n}" and {1,n}. 
    As a side effect block quotes are replaced with normal quotes
    by using {@link #removeBlockQuotes(String)}.
    
    @param pattern pattern to be finitized
    @param infinity "n" number
    @return limited length pattern
    """

    pattern = remove_block_quotes(pattern)
    
    pattern = STAR_PATTERN.sub("{0," + str(infinity) + "}", pattern)
    pattern = PLUS_PATTERN.sub("{1," + str(infinity) + "}", pattern)
    pattern = RANGE_PATTERN.sub("{\\1," + str(infinity) + "}", pattern)
    
    return pattern
