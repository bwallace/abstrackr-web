# -*- coding: utf-8 -*-

import re
import logging

logging.basicConfig(level=logging.INFO)


class MarkUpper:
    """This class takes in a list of terms and can do term highlighting for any 
    string using this list.

    Parameters: 
        labeled_terms: list of [Term]

    """

    ### for term highlighting
    NEG_C = "#9900FF"
    STRONG_NEG_C = "#FF0000"
    POS_C = "#4CC417"
    STRONG_POS_C = "#3366FF"
    COLOR_D = {1: POS_C, 2: STRONG_POS_C, -1: NEG_C, -2: STRONG_NEG_C}

    def __init__(self, labeled_terms):
        """note that we need to escape regex characters before adding terms to 
        the dict
        """
        self.term_d = dict([(re.escape(t.term.lower()), self.COLOR_D[t.label]) \
            for t in labeled_terms])

    def markup(self, text_to_mark_up):
        """Call re.sub function to replace occurances of the term in the input 
        text with the corresponding color tags."""
        
        if len(self.term_d.keys()) == 0:
            """trying to match an empty regex causes problems, so return if dict 
            is empty
            """
            return text_to_mark_up

        pattern = self._pattern()
        return pattern.sub(self._add_color_tag, text_to_mark_up)

    def _pattern(self):
        """Compiles a re pattern that matches any of the terms in term_d."""
        return re.compile("|".join(self.term_d.keys()), re.IGNORECASE)

    def _add_color_tag(self, match_object):
        """This is the replacement function that is passed into re.sub that 
        takes a matched term and puts the right color tag around it. 
        """
        return "<font color='%s'><b>%s</b></font>" % \
            (self.term_d[re.escape(match_object.group(0)).lower()],
             match_object.group(0))

if __name__ == "__main__":
    test_abstract = "Chemical and spectroscopic analyses ((13)C\r\n cross-polarization-magic angle spinning NMR\r\n"
    benchmark_abstract = "<font color='#9900FF'><b>Chemical</b></font> <font color='#9900FF'><b>and</b></font> <font color='#FF0000'><b>spectroscopic</b></font> analyses ((13)C\r\n cross-polarization-magic angle spinning NMR\r\n"

    class Term: pass

    t1 = Term()
    t1.term = "Chemical"
    t1.label = 1

    t2 = Term()
    t2.term = "and"
    t2.label = -1

    t3 = Term()
    t3.term = "spectroscopic"
    t3.label = -2

    t4 = Term()
    t4.term = "spec"
    t4.label = 2

    t5 = Term()
    t5.term = "color"
    t5.label = 1

    t6 = Term()
    t6.term = "font"
    t6.label = -2

    t7 = Term()
    t7.term = "chemical"
    t7.label = -1

    test_terms = [t1, t2, t3, t3, t4, t5, t6, t7]

    m_upper = MarkUpper(test_terms)

    marked_abs = m_upper.markup(test_abstract)

    logging.info(marked_abs)
    logging.info(benchmark_abstract)
    logging.info("match? " + str(marked_abs == benchmark_abstract))