import regex as re  # type: ignore

# Java-only regex constructs that have to be translated before a rule
# pattern can be compiled by the regex package. The \\. alternative
# consumes any other escape pair first, so \h/\v are only rewritten when
# the backslash is not itself escaped.
#
# \h and \v are Java's horizontal/vertical whitespace classes; in Python
# patterns \v is the literal LINE TABULATION escape, so both are mapped to
# the equivalent \p{H}/\p{V} properties added to the regex package in
# 2022.8.17 (https://github.com/mrabarnett/mrab-regex/issues/477).
# \p{H}/\p{V} match Java's classes exactly, while the regex package's own
# \h misses U+180E.
#
# (?U) is Java's UNICODE_CHARACTER_CLASS inline flag (used by LanguageTool
# rules to fix the JDK >= 19 \b regression); Python character classes are
# Unicode-aware by default for str patterns, so the flag is dropped.
JAVA_CONSTRUCT_PATTERN: re.Regex = re.compile(r"\\h|\\v|\\.|\(\?U\)")
JAVA_CONSTRUCT_REPLACEMENTS = {
    r"\h": r"\p{H}",
    r"\v": r"\p{V}",
    "(?U)": "",
}


def translate_java_regex(pattern: str) -> str:
    """
    Translates Java-only regex constructs (\\h, \\v, (?U)) into their
    Python regex-package equivalents. See JAVA_CONSTRUCT_PATTERN above.
    """
    return JAVA_CONSTRUCT_PATTERN.sub(
        lambda match: JAVA_CONSTRUCT_REPLACEMENTS.get(match.group(), match.group()),
        pattern,
    )


STAR_PATTERN: re.Regex = re.compile("(?<=(?<!\\\\)(?:\\\\\\\\){0,100})\\*")
PLUS_PATTERN: re.Regex = re.compile("(?<=(?<!\\\\)(?:\\\\\\\\){0,100})(?<![\\?\\*\\+]|\\{[0-9],?[0-9]?\\}?\\})\\+")
RANGE_PATTERN: re.Regex = re.compile("(?<=(?<!\\\\)(?:\\\\\\\\){0,100})\\{\\s*([0-9]+)\\s*,\\s*\\}")
CAPTURING_GROUP_PATTERN: re.Regex = re.compile("(?<=(?<!\\\\)(?:\\\\\\\\){0,100})\\((?!\\?)")


def remove_block_quotes(pattern: str) -> str:
    """
    Replaces block quotes in regular expressions with normal quotes. For
    example "\\Qabc\\E" will be replace with "\\a\\b\\c".

    @param pattern
    @return pattern with replaced block quotes
    """

    pattern_builder: str = ""
    quote: bool = False
    previous_char: str = ""

    for current_char in pattern:
        if quote:
            if previous_char == "\\" and current_char == "E":
                quote = False
                # Need to remove "\\" at the end as it has been added
                # in previous iteration.
                pattern_builder = pattern_builder[:-2]
            else:
                pattern_builder += "\\" + current_char

        else:
            if previous_char == "\\" and current_char == "Q":
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

def create_lookbehind_pattern(pattern: str, max_lenght: int) -> str:
    if not pattern:
        return pattern

    return "(?<=" + finitize(pattern, max_lenght) + ")"
