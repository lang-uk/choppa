import unittest
from typing import List

from xmlschema.validators.exceptions import XMLSchemaValidationError  # type: ignore

from choppa.srx_parser import SrxDocument
from choppa.structures import LanguageRule, Rule
from choppa.iterators import AccurateSrxTextIterator


class SrxParserTest(unittest.TestCase):
    SRX_2_XSD: str = "data/xsd/srx20.xsd"

    def test_languagetool_rules(self) -> None:
        document: SrxDocument = SrxDocument(ruleset="data/srx/segment_new.srx", validate_ruleset=self.SRX_2_XSD)
        self.assertTrue(document.cascade)

        self.split_helper(["Це просте речення."], document)
        self.split_helper(["Вони приїхали в Париж. ", "Але там їм геть не сподобалося."], document)
        self.split_helper(["Панк-рок — напрям у рок-музиці, що виник у середині 1970-х рр. у США і Великобританії."], document)
        self.split_helper(["Разом із втечами, вже у XV ст. почастішали збройні виступи селян."], document)
        self.split_helper(["На початок 1994 р. державний борг України становив 4,8 млрд. дол. США"], document)
        self.split_helper(["4,8 млрд. дол. США. ", "Але наступного року..."], document)
        self.split_helper(["Київ, вул. Сагайдачного, буд. 43, кв. 4."], document)
        self.split_helper(["на вул.\n  Сагайдачного."], document)

    def test_languagetool_initial_rules(self) -> None:
        document: SrxDocument = SrxDocument(ruleset="data/srx/segment_new.srx", validate_ruleset=self.SRX_2_XSD)
        self.assertTrue(document.cascade)

        self.split_helper(["Є.Бакуліна"], document)
        self.split_helper(["Є.В.Бакуліна"], document)
        # self.split_helper(["Засідав І. П. Єрмолюк"], document)
        self.split_helper(["І. П. Єрмолюк скликав нараду."], document)
        # self.split_helper(["Наша зустріч з А. Марчуком і Г. В. Тріскою відбулася в грудні минулого року."], document)
        # self.split_helper(["Наша зустріч з А.Марчуком і М.В.Хвилею відбулася в грудні минулого року."], document)
        self.split_helper(["Комендант преподобний С.\u00A0Мокітімі"], document)
        # self.split_helper(["Комендант преподобний С.\u00A0С.\u00A0Мокітімі 1."], document)
        # self.split_helper(["Комендант преподобний С.\u00A0С. Мокітімі 2."], document)
        self.split_helper(["Склад: акад. Вернадський, проф. Харченко, доц. Семеняк."], document)
        self.split_helper(["Ів. Франко."], document)
        # self.split_helper(["Алисов Н. В. , Хореев Б. С."], document)
        self.split_helper(["і Г.-К. Андерсена"], document)
        self.split_helper([" — К. : Наук. думка, 1990."], document)
        self.split_helper(["Маркс К. «Показова держава»"], document)
        
        # #   latin I
        # self.split_helper(["М. Л. Гончарука, I. О. Денисюка"], document)
        self.split_helper(["I. I. Дорошенко"], document)

    def test_languagetool_other_rules(self) -> None:
        document: SrxDocument = SrxDocument(ruleset="data/srx/segment_new.srx", validate_ruleset=self.SRX_2_XSD)
        self.assertTrue(document.cascade)

        self.split_helper(["елементів множини A. Отже, нехай"], document)
        
        self.split_helper(["Опергрупа приїхала в с. Лісове."], document)
        self.split_helper(["300 р. до н. е."], document)
        self.split_helper(["З 300 р. до н.е., і по цей день."], document)
        self.split_helper(["Пролісок (рос. пролесок) — маленька квітка."], document)
        self.split_helper(["Квітка Цісик (англ. Kvitka Cisyk також Kacey Cisyk від ініціалів К.С.); 4 квітня 1953р., Квінз, Нью-Йорк — 29 березня 1998 р., Мангеттен, Нью-Йорк) — американська співачка українського походження."], document)
        self.split_helper(["До Інституту ім. Глієра під'їжджає чорне авто."], document)
        self.split_helper(["До Інституту ім. акад. Вернадського."], document)
        self.split_helper(["До вулиці гетьмана Скоропадського під'їжджає чорне авто."], document)
        self.split_helper(["До табору «Артек»."], document)
        self.split_helper(["Спільні пральні й т. д. й т. п. ", "Перемогли!"], document)
        self.split_helper(["в Хоролі з п. Кушніренком договорилися"], document)
        self.split_helper(["і п. 10 від 23.1.33 р."], document)
        self.split_helper(["і т. п. ", "10 від 23.1.33 р."], document)
        self.split_helper(["і т.п. ", "10 від 23.1.33 р."], document)
        self.split_helper(["див. стор. 24."], document)
        self.split_helper(["Від англ.\n  File."], document)
        self.split_helper(["Від фр.  \nparachute."], document)
        self.split_helper(["фільму\nС. Ейзенштейна"], document)

        self.split_helper(["Від р. Дніпро."], document)
        self.split_helper(["В 1941 р. Конрад Цузе побудував."], document)
        self.split_helper(["Наприкінці 1254 р. Данило почав"], document)
        self.split_helper(["У травні 1949 р. Грушківський район"], document)
        self.split_helper(["У травні 1949 р. \nГрушківський район"], document)
        self.split_helper(["Упродовж 2011–2014 р. Швейцарія надасть"], document)
        self.split_helper(["15 вересня 1995 р. Україною було підписано"], document)
        self.split_helper(["Але закінчилося аж у січні 2013 р. ", "Як бачимо"], document)

        self.split_helper(["інкримінують ч. 1 ст. 11"], document)

        self.split_helper(["В цих світлих просторих апартаментах...  м’які крісла, килими, дорогі статуетки"], document)
        self.split_helper(["А та — навперейми... «давайте мені!»"], document)
        self.split_helper(["слугував ...    «витяг з протоколу зустрічі"], document)
        self.split_helper(["на... Луганському"], document)
        self.split_helper(["(вони самі це визнали. - Ред.)"], document)

        self.split_helper(["Всього 33 тис. 356 особи"], document)
        self.split_helper(["Всього 33 тис. (за словами прораба)"], document)
        self.split_helper(["з яких приблизно   1,2 тис. – чоловіки."], document)
        self.split_helper(["У с. Вижва"], document)
        self.split_helper(["Книжка (с. 200)"], document)
        self.split_helper(["позначені: «с. Вижва»"], document)
        self.split_helper(["в м.Києві"], document)
        self.split_helper(["Микола Васюк (с. Корнієнки, Полтавська обл.)"], document)
        self.split_helper(["U.S. Marine"], document)
        self.split_helper(["B.B. King"], document)
        self.split_helper(["Церква Св. Духа і церква св. Духа"], document)
        self.split_helper(["Валерій (міліціонер-пародист.  –  Авт.) стане пародистом."], document)
        self.split_helper(["Сьогодні (у четвер.  - Ред.), вранці."], document)
        self.split_helper([" ([27]див. Тиждень № 9, 2008)"], document)

        self.split_helper(["і «Р. Б. К.»"], document)
        self.split_helper(["У. Т: "], document)
        self.split_helper(["Іван Ч. (1914 р. н.)"], document)
        self.split_helper(["альбом “Сніжність” (2006 р.) – разом із Юрієм"], document)
        self.split_helper(["СК “Слон” (2008 р.) ", "У минулому харків’янка"], document)

        self.split_helper(["рис. 14, Мал. 5; Арт. 88-99"], document)

    def test_tokenize_with_special_chars(self) -> None:
        document: SrxDocument = SrxDocument(ruleset="data/srx/segment_new.srx", validate_ruleset=self.SRX_2_XSD)

        self.split_helper(["– С.\u202f5-7."], document)
        # still no split for initials
        self.split_helper(["товариш С.\u202fОхримович."], document)
        self.split_helper(["З особливим обуренням сприймав С.\u202f Шелухин легітимізацію"], document)
        self.split_helper(["відбув у тюрмах.\u202f", "Нещодавно письменник"], document)
        self.split_helper(["закрито бібліотеку української літератури.\u202f ", "Раніше відділ боротьби з екстремізмом..."], document)

    def split_helper(self, sentences: List[str], document: SrxDocument) -> None:
        text_iterator: AccurateSrxTextIterator = AccurateSrxTextIterator(document, "uk_two", "".join(sentences))
        segments: List[str] = list(text_iterator)
        self.assertEqual(sentences, segments)
