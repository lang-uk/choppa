# choppa
Partial python port of java SRX segmenter, [originally written](https://github.com/loomchild/segment) by Jarek Lipski aka `loomchild`. 

In a nutshell it allows you to tokenize texts into the sentences (but generally it's rule-based, so you can chop anything textual).

Shipped with `segment.srx` set of segmentation rules for different languages, crafted by the great team of [languagetool](https://github.com/languagetool-org/languagetool).

# Current status and plans
That port currently covers:
* All structures (`structures.py`) necessary for parser to operate (`Rule`, `LanguageRule`, `LanguageMap`)
* Abstract and **Accurate legacy** iterator (`iterators.py`) which basically segments text into the chunks according to the SRX rules
* SAX based parser (`srx_parser.py`) to read SRX rules from xml files (both SRX1.0 and SRX2.0)
* SrxDocument (again `srx_parser.py`) class which allows you to manage rules and cache regexes
* A partial implementation of [Java Matcher class](https://docs.oracle.com/javase/7/docs/api/java/util/regex/Matcher.html#method_summary), which is absent in python.
* Tests for everything above (and beyond)
* [Additional tests](https://github.com/languagetool-org/languagetool/blob/66a66e5484aaaa5794fd530da18179b0bf441250/languagetool-language-modules/uk/src/test/java/org/languagetool/tokenizers/uk/UkrainianSRXSentenceTokenizerTest.java) from LanguageTool for Ukrainian language
* [Type hints](https://docs.python.org/3/library/typing.html)

I also _pythonized_ the code to the some extend (by removing some of setters/getters, _snake_casing_ methods and variables and adapting data structures).


# Important notes
First and foremost, I would like to thank Jarek for his work and the quality of his code. My project is not original, it just brings the power of srx segmenter to python world. And it relies completely on the work
done by Jarek.

Please pay attention to the fact that only [Accurate iterator](https://github.com/loomchild/segment#accurate-algorithm) is currently implemented (and I don't have immediate plans to implement the rest). Accurate Iterator should work well on a relatively small documents (i.e **do not use** it on multi GB plaintext corpora!). Other iterators from original library allows to parse large documents efficiently while sacrificing some accuracy (limiting look-behind patterns, etc). If you really need it — I'm always open for the pull requests. Similary, I've only implemented SAX reader for rules and using `xmlschema` package for schema validation. Last but not least, various readers aren't ported from the original library too, in my opinion, python already has a lot of built-in tools for that behaviour.

Also, I don't have any plan of porting UI at all. You can simply reuse some of UI's available.


# Copyrights and kudos
* Python port: Dmytro Chaplynskyi
* Original Java implementation: Jarek Lipski
* Segmentation rules: Daniel Naber, Jaume Ortolà et al (153 contributors!)
* Special thanks to Andriy Rysin, driving force behind Ukrainian language in LanguageTool
