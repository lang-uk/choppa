# choppa
Partial python port of java SRX segmenter, [originally written](https://github.com/loomchild/segment) by [Jarek Lipski](https://github.com/loomchild). 

In a nutshell, it allows you to tokenize texts into sentences (but generally, it's rule-based so that you can chop anything textual).

Shipped with `segment.srx` set of segmentation rules for different languages, crafted by the great team of [languagetool](https://github.com/languagetool-org/languagetool).

# Current status and plans
That port currently covers:
* All structures (`structures.py`) necessary for the parser to operate (`Rule`, `LanguageRule`, `LanguageMap`)
* Abstract, Accurate (legacy), and SrxTextIterator iterator (`iterators.py`), which basically segments text into chunks according to the SRX rules
* Extra classes required for the SrxTextIterator (`TextManager`, `RuleManager`)
* Some utils (`utils.py`), for regex mangling
* SAX based parser (`srx_parser.py`) to read SRX rules from xml files ([**SRX2.0 only**](https://github.com/loomchild/segment#srx-file))
* SrxDocument (again `srx_parser.py`) class which allows you to manage rules and cache regexes
* A partial implementation of [Java Matcher class](https://docs.oracle.com/javase/7/docs/api/java/util/regex/Matcher.html#method_summary), which is absent in python.
* Tests for everything above (and beyond)
* [Additional tests](https://github.com/languagetool-org/languagetool/blob/66a66e5484aaaa5794fd530da18179b0bf441250/languagetool-language-modules/uk/src/test/java/org/languagetool/tokenizers/uk/UkrainianSRXSentenceTokenizerTest.java) from LanguageTool for Ukrainian language
* [Type hints](https://docs.python.org/3/library/typing.html)

I also _pythonized_ the code to some extent (by removing some setters/getters, _snake_casing_ methods, and variables and adapting data structures).


# Important notes
First and foremost, I would like to thank Jarek for his work and code quality. My project is not original, it just brings the power of srx segmenter to the python world. And it relies entirely on the work
done by Jarek.

Please pay attention to the fact that only [Accurate iterator](https://github.com/loomchild/segment#accurate-algorithm) and [Ultimate iterator](https://github.com/loomchild/segment#algorithm) is currently implemented (and I don't have immediate plans to implement the rest). Accurate Iterator should work well on relatively small documents (i.e. **do not use** it on multi GB plaintext corpora!), but [known for some bugs](https://github.com/loomchild/segment/issues/22). Ultimate iterator from the original library is also ported, allowing to parse large documents efficiently while sacrificing accuracy (limiting look-behind patterns, etc). If you need other iterators or are keen to optimize that beast — I'm always open for the pull requests. Similarly, I've only implemented SAX reader for rules and I'm using `xmlschema` package for schema validation. 

Also, I don't have any plan of porting UI at all. You can reuse some of UI's available.


# Copyrights and kudos
* Python port: Dmytro Chaplynskyi
* Original Java implementation: Jarek Lipski
* Segmentation rules: Daniel Naber, Jaume Ortolà et al (153 contributors!)
* Special thanks to Andriy Rysin, the driving force behind the Ukrainian language in LanguageTool
