import spacy
import benepar
from nltk import Tree

benepar.download('benepar_en3')

nlp = spacy.load("en_core_web_lg")
nlp.add_pipe('benepar', config={'model': 'benepar_en3'}, last=True)


def sent_segmentation(doc):
    target_labels = ['S', 'SBAR', 'SQ', 'SBARQ', 'VP', 'VB', 'VBP', 'VBD', 'VBZ', 'MD']

    def contains_target_label(tree):
        """Recursively check if any node in the tree has a label in target_labels."""
        if tree.label() in target_labels:
            return True
        for child in tree:
            if isinstance(child, Tree) and contains_target_label(child):
                return True
        return False

    for sent in doc.sents:
        parse_tree = sent._.parse_string  # Get the constituency parsing
        tree = Tree.fromstring(parse_tree)

        # Return True if the root or any descendant has a target label
        if contains_target_label(tree):
            return True

    return False


def structure_idf(doc):
    # Ensure we are working with the parsed sentence tree from Benepar
    if doc.is_parsed and len(list(doc.sents)) > 0:
        # Use the first sentence's parse tree from doc (assuming only one sentence per doc)
        parse_tree_str = list(doc.sents)[0]._.parse_string  # Benepar stores constituency parse in this attribute

        parse_tree = Tree.fromstring(parse_tree_str)  # Convert the parse string to a tree structure

        # Main Clause Identification (starting with 'S' as the root)
        if parse_tree.label() == 'S':
            children = list(parse_tree)  # Get the immediate children of the root

            # Flags to track structure elements for various clauses
            found_NP = False
            found_VP = False

            # Iterate through top-level children of the parse tree
            for child in children:
                # Case 1: Embedded Subordinate Clause
                if child.label() == 'SBAR':
                    return "Embedded subordinate clause"

                # Check for NP and VP sequence for SV Simple or Imperative
                if child.label() == 'NP':
                    found_NP = True
                elif child.label() == 'VP':
                    if found_NP:
                        # Check if VP contains 'MD' or an embedded 'S' with specific patterns
                        for grandchild in child:
                            # Case 2: Non-finite Modal
                            if grandchild.label() == 'MD':
                                return "Non-finite Modal"

                            # Case 3: Non-finite to-inf structure
                            elif grandchild.label() == 'S':
                                found_S = True
                                for grandchild2 in grandchild:
                                    if grandchild2.label() == 'VP':
                                        found_TO = False
                                        found_nested_VP = False

                                        # Check for 'TO' and nested VP structure within VP
                                        for grandchild3 in grandchild2:
                                            if grandchild3.label() == 'TO':
                                                found_TO = True
                                            elif grandchild3.label() == 'VP' and found_TO:
                                                found_nested_VP = True
                                                break

                                        if found_TO and found_nested_VP:
                                            return "Non-finite to-inf"

                        # Default case for SV structure if no other patterns are matched
                        return "SV simple"

                    # Case 4: Imperative (when there’s no NP before VP)
                    elif not found_NP:
                        return "Imperative"

            # Case 5: Preposed-Adv (ADVP/PP before NP and VP)
            found_adv = False
            found_NP = False
            found_VP = False

            # Second loop to check for Preposed-Adv structure
            for child in children:
                if child.label() in ('ADVP', 'PP'):
                    found_adv = True
                elif child.label() == 'NP' and found_adv:
                    found_NP = True
                elif child.label() == 'VP' and found_adv:
                    found_VP = True

            if found_adv and found_NP and found_VP:
                return "Preposed Adv"

        # Relative Clauses Identification
        children = list(parse_tree)

        found_NP = False
        found_vp = False

        for child in children:
            if child.label() == 'NP':
                found_NP = True

                found_nested_NP = False
                found_SBAR = False

                for grandchild in child:
                    if grandchild.label() == 'NP':
                        found_nested_NP = True
                    elif grandchild.label() == 'SBAR':
                        if found_nested_NP:
                            found_SBAR = True

                            found_WHNP = False
                            found_S = False

                            for grandchild2 in grandchild:
                                if grandchild2.label() == 'WHNP':
                                    found_WHNP = True
                                elif grandchild2.label() == 'S':
                                    if found_WHNP:
                                        found_S = True

                                        found_NP = False
                                        found_VP = False

                                        for grandchild3 in grandchild2:
                                            if grandchild3.label() == 'NP':
                                                found_NP = True
                                            elif grandchild3.label() == 'VP':
                                                if found_NP:
                                                    found_VP = True

                                        if found_NP and found_VP:
                                            found_PRP = any(grandchild4.label() == 'PRP' for grandchild4 in grandchild3)
                                            if found_PRP:
                                                return "OR-inv"
                                            else:
                                                return "OR+inv"
                                        elif found_VP and not found_NP:
                                            return "SR"


            # Declarative and Interrogative Clauses
            elif child.label() == 'VP' and found_NP:
                found_vp = True

                # Check VP children for 'that/if' conditions
                for grandchild in child:
                    if grandchild.label() == 'SBAR':
                        found_s = False
                        found_that = False
                        found_if = False

                        for grandchild2 in grandchild:
                            if grandchild2.label() == 'IN' and grandchild2[0].lower() == 'that':
                                found_that = True
                            elif grandchild2.label() == 'IN' and grandchild2[0].lower() == 'if':
                                found_if = True
                            elif grandchild2.label() == 'S':
                                found_s = True

                        # Determine Declarative-that or Interrogative-if
                        if found_that and found_s:
                            return "Declarative-that"
                        elif found_if and found_s:
                            return "Interrogative-if"

        # If the root is 'SBAR', identify as Subordinate Clause
        if parse_tree.label() == 'SBAR':
            return "Subordinate Clause"

        # Yes/No Question Identification (root 'SQ')
        if parse_tree.label() == 'SQ':
            children = list(parse_tree)
            found_aux = False
            found_np = False

            for child in children:
                # Check for auxiliary verb first
                if child.label() in ('VBP', 'VBD', 'VBZ', 'MD'):
                    found_aux = True

                # Check for NP after auxiliary
                elif child.label() == 'NP':
                    if found_aux:
                        found_np = True

                    if found_aux and found_np:
                        return "yes/no-questions"

        # Wh-Question Identification (root 'SBARQ')
        elif parse_tree.label() == 'SBARQ':
            children = list(parse_tree)
            found_whadvp = False
            found_whnp = False
            found_sq = False
            found_why = False

            for i, child in enumerate(children):
                # Check for WHADVP (e.g., 'why')
                if child.label() == 'WHADVP':
                    whadvp_children = list(child)
                    for whadvp_child in whadvp_children:
                        if whadvp_child.label() == 'WRB':
                            if whadvp_child[0].lower() == 'why':
                                found_why = True
                            found_whadvp = True

                # Check for WHNP (e.g., 'what', 'who')
                elif child.label() == 'WHNP':
                    found_whnp = True

                # SQ or S should come after WHADVP or WHNP
                elif child.label() in ('S', 'SQ'):
                    if (found_whadvp or found_whnp) and i > 0:
                        found_sq = True
                        if found_why:
                            return "why-questions"
                        elif found_whadvp or found_whnp:
                            return "wh-questions"

        # If no other structure is identified
        return "Other Structure"


# Revision for the structure identifier
def struct_idf(text):
    doc = nlp(text)
    output = []  # List to store multiple outputs
    for sent in doc.sents:
        parse_string = sent._.parse_string
        tree = Tree.fromstring(parse_string)

        # WH-QUESTIONS
        def wh_question(node):
            """ Recursive function to check for WH-question structure in the tree. """
            if not isinstance(node, Tree):
                return False

            # Condition 1: Find WHNP/WHADVP and SQ at the same depth level
            found_wh = False

            for child in node:
                if isinstance(child, Tree):
                    if child.label() in ('WHNP', 'WHADVP'):
                        found_wh = True
                    elif child.label() == 'SQ' and found_wh:
                        return True  # Found WH followed by SQ at the same level

            # Condition 2: Find WHNP/WHADVP preceding S and ? below S
            found_s = False
            for child in node:
                if isinstance(child, Tree):
                    if child.label() in ('WHNP', 'WHADVP'):
                        found_wh = True
                    elif child.label() == 'S' and found_wh:
                        found_s = True
                    elif found_s and '?' in child.leaves():  # Check lower depth level
                        return True  # Found WH preceding S with ? below S

            # Recursively check all children
            for child in node:
                if wh_question(child):
                    return True

            return False

        # OBJECT RELATIVE WITHOUT INTERVENER
        def or_no_intv(node):
            if not isinstance(node, Tree):
                return False

            # Check if the current node is labeled 'NP'
            if node.label() == 'NP':
                # Check if this 'NP' has another 'NP' as a direct child
                has_np_in_np = any(grandchild.label() == 'NP' for grandchild in node if isinstance(grandchild, Tree))
                if has_np_in_np:
                    # Check for an 'SBAR' child directly and if 'who' or 'that' appears in the leaves
                    has_who_that = any(word in node.leaves() for word in ('who', 'that'))
                    for sbar_child in node:
                        if isinstance(sbar_child, Tree) and sbar_child.label() == 'SBAR' and has_who_that:
                            # Look for the 'S' node directly within 'SBAR'
                            for s_child in sbar_child:
                                if isinstance(s_child, Tree) and s_child.label() == 'S':
                                    # Check if 'S' has both 'NP' and 'VP' children
                                    has_np_and_vp = any(
                                        child.label() == 'NP' for child in s_child if isinstance(child, Tree)) and \
                                                    any(child.label() == 'VP' for child in s_child if
                                                        isinstance(child, Tree))

                                    if has_np_and_vp:
                                        # Find the 'NP' under 'S' and check for 'PRP' as its child
                                        for np_child in s_child:
                                            if isinstance(np_child, Tree) and np_child.label() == 'NP':
                                                has_prp = any(grandchild.label() == 'PRP' for grandchild in np_child if
                                                              isinstance(grandchild, Tree))
                                                if has_prp:
                                                    return True  # All conditions are met

            # Recursively check all children
            for child in node:
                if or_no_intv(child):
                    return True

            return False

        # OBJECT RELATIVE WITH INTERVENER
        def or_intv(node):
            if not isinstance(node, Tree):
                return False

            # Check if the current node is labeled 'NP'
            if node.label() == 'NP':
                # Check if this 'NP' has another 'NP' as a direct child
                has_np_in_np = any(grandchild.label() == 'NP' for grandchild in node if isinstance(grandchild, Tree))
                if has_np_in_np:
                    # Check for an 'SBAR' child directly and if 'who' or 'that' appears in the leaves
                    has_who_that = any(word in node.leaves() for word in ('who', 'that'))
                    for sbar_child in node:
                        if isinstance(sbar_child, Tree) and sbar_child.label() == 'SBAR' and has_who_that:
                            # Look for the 'S' node directly within 'SBAR'
                            for s_child in sbar_child:
                                if isinstance(s_child, Tree) and s_child.label() == 'S':
                                    # Check if 'S' has both 'NP' and 'VP' children
                                    has_np_and_vp = any(
                                        child.label() == 'NP' for child in s_child if isinstance(child, Tree)) and \
                                                    any(child.label() == 'VP' for child in s_child if
                                                        isinstance(child, Tree))

                                    if has_np_and_vp:
                                        # Find the 'NP' under 'S' and check for 'PRP' as its child
                                        for np_child in s_child:
                                            if isinstance(np_child, Tree) and np_child.label() == 'NP':
                                                has_prp = any(grandchild.label() != 'PRP' for grandchild in np_child if
                                                              isinstance(grandchild, Tree))
                                                if has_prp:
                                                    return True  # All conditions are met

            # Recursively check all children
            for child in node:
                if or_intv(child):
                    return True

            return False

        # SUBJECT RELATIVE
        def sr(node):
            if not isinstance(node, Tree):
                return False

            # Check if the current node is labeled 'NP'
            if node.label() == 'NP':
                # Check if this 'NP' has another 'NP' as a direct child
                has_np_in_np = any(grandchild.label() == 'NP' for grandchild in node if isinstance(grandchild, Tree))
                if has_np_in_np:
                    # Check for an 'SBAR' child directly and if 'who' or 'that' appears in the leaves
                    has_who_that = any(word in node.leaves() for word in ('who', 'that'))
                    for sbar_child in node:
                        if isinstance(sbar_child, Tree) and sbar_child.label() == 'SBAR' and has_who_that:
                            # Look for the 'S' node directly within 'SBAR'
                            for s_child in sbar_child:
                                if isinstance(s_child, Tree) and s_child.label() == 'S':
                                    # Check if 'S' has 'VP' child
                                    has_vp = any(child.label() == 'VP' for child in s_child if isinstance(child, Tree))
                                    if has_vp:
                                        return True  # All conditions are met

            # Recursively check all children
            for child in node:
                if sr(child):
                    return True

            return False

        # DECLARATIVE 'THAT' INTERROGATIVE 'IF'
        def decl_that_int_if(node):
            if not isinstance(node, Tree):
                return False

            for child in node:
                if isinstance(child, Tree) and child.label() == 'VP':
                    # Check if this VP has an 'SBAR' child
                    has_sbar = any(grandchild.label() == 'SBAR' for grandchild in child if isinstance(grandchild, Tree))
                    # Check if "that" or "if" is in the leaves of the VP node
                    has_that_if = any(word in child.leaves() for word in ('that', 'if'))

                    if has_sbar and has_that_if:
                        return True

            # Recursively check all children
            for child in node:
                if decl_that_int_if(child):
                    return True

            return False

        # SUBORDINATE CLAUSE
        def subordinate_clause(node):
            if not isinstance(node, Tree):
                return False

            found_wh_in = False
            for child in node:
                if isinstance(child, Tree):
                    if child.label() in ('WHNP', 'WHADVP', 'IN'):
                        found_wh_in = True
                    elif child.label() == 'S' and found_wh_in:
                        return True

                        # Recursively check all children
            for child in node:
                if subordinate_clause(child):
                    return True

            return False

        # YES/NO QUESTIONS
        def yes_no_q(node):
            if not isinstance(node, Tree):
                return False

            # Check if the current node is labeled 'S'
            if node.label() == 'S':
                # Check if '?' is among the leaves of this 'S' node
                if '?' in node.leaves():
                    return True  # Found 'S' as the root with '?' as a leaf

            # Check for 'SQ' at any level
            for child in node:
                if isinstance(child, Tree):
                    if child.label() == 'SQ':
                        return True

            # Recursively check all children
            for child in node:
                if yes_no_q(child):
                    return True

            return False

        # PREPOSED ADVERB
        def prep_adv(node):
            if not isinstance(node, Tree):
                return False

            found_adv_pp = False
            found_np = False

            for child in node:
                if isinstance(child, Tree):
                    if child.label() in ('ADVP', 'PP'):
                        found_adv_pp = True
                    elif child.label() == 'NP' and found_adv_pp:
                        found_np = True
                    elif child.label() == 'VP' and found_adv_pp and found_np:
                        return True  # Found all things at the same level

            # Recursively check all children
            for child in node:
                if prep_adv(child):
                    return True

            return False

        # PREPOSED ADVERB AND SINV
        def prep_adv_sinv(node):
            if not isinstance(node, Tree):
                return False

            found_adv_pp = False
            found_vp = False

            for child in node:
                if isinstance(child, Tree):
                    if child.label() in ('ADVP', 'PP'):
                        found_adv_pp = True
                    elif child.label() == 'VP' and found_adv_pp:
                        found_vp = True
                    elif child.label() == 'NP' and found_adv_pp and found_vp:
                        return True  # Found all things at the same level

            # Recursively check all children
            for child in node:
                if prep_adv_sinv(child):
                    return True

            return False

        # SUBJECT-VERB INVERSE
        def sinv(node):
            if not isinstance(node, Tree):
                return False

            found_vp = False

            for child in node:
                if isinstance(child, Tree):
                    if child.label() == 'VP':
                        found_vp = True
                    elif child.label() == 'NP' and found_vp:
                        return True  # Found all things at the same level

            # Recursively check all children
            for child in node:
                if sinv(child):
                    return True

            return False

        # IMPERATIVE
        def imperative(node):
            if not isinstance(node, Tree):
                return False

            # Check if there's any 'NP' at this level
            has_np = any(child.label() == 'NP' for child in node if isinstance(child, Tree))

            # If there is an 'NP', it's not an imperative structure
            if has_np:
                return False

            # If no 'NP' is found, check for 'VP'
            if any(child.label() == 'VP' for child in node if isinstance(child, Tree)):
                return True

            # Recursively check all children
            for child in node:
                if imperative(child):
                    return True

            return False

        # SV WITH NON-FINITE TO-INFINITIVE
        def sv_to_inf(node):
            if not isinstance(node, Tree):
                return False

            found_np = False

            for child in node:
                if isinstance(child, Tree):
                    if child.label() == 'NP':
                        found_np = True
                    elif child.label() == 'VP' and found_np:
                        # Initialize has_to to False
                        has_to = False
                        # Look for an S within the VP with "to" as an infinitive
                        for grandchild in child:
                            if isinstance(grandchild, Tree) and grandchild.label() == 'S':
                                has_to = any(
                                    "to" == word and idx == 0 for idx, word in enumerate(grandchild.leaves())
                                )

                        # Now check has_to safely
                        if has_to:
                            return True

            # Recursively check all children
            for child in node:
                if sv_to_inf(child):
                    return True

            return False

        # SV WITH NON-FINITE MODAL
        def sv_modal(node):
            """ Recursive function to check for an NP followed by a VP with a modal verb (MD) """
            if not isinstance(node, Tree):
                return False

            found_np = False

            for child in node:
                if isinstance(child, Tree):
                    if child.label() == 'NP':
                        found_np = True
                    elif child.label() == 'VP' and found_np:
                        found_md = False
                        for grandchild in child:
                            if isinstance(grandchild, Tree) and grandchild.label() == 'MD':
                                found_md = True
                            elif isinstance(grandchild, Tree) and grandchild.label() == 'VP' and found_md:
                                return True

            # Recursively check all children
            for child in node:
                if sv_modal(child):
                    return True

            return False

        # SV SIMPLE
        def sv(node):
            if not isinstance(node, Tree):
                return False

            found_np = False

            for child in node:
                if isinstance(child, Tree):
                    if child.label() == 'NP':
                        found_np = True
                    elif child.label() == 'VP' and found_np:
                        return True

            # Recursively check all children
            for child in node:
                if sv(child):
                    return True

            return False

        # Check each structure independently and append to `output` if matched.
        if wh_question(tree):
            output.append("WH Question")
        if or_intv(tree):
            output.append("Object Relative With Intv")
        if or_no_intv(tree):
            output.append("Object Relative Without Intv")
        if sr(tree):
            output.append("Subject Relative")
        if decl_that_int_if(tree):
            output.append("Decl-that/Int_if")
        if subordinate_clause(tree):
            output.append("Subordinate clause")
        if yes_no_q(tree):
            output.append("Yes/No Question")
        if prep_adv(tree):
            output.append("Preposed adverb")
        if prep_adv_sinv(tree):
            output.append("Preposed adverb and SINV")
        if sinv(tree):
            output.append("Subject-Verb Inversion")
        if imperative(tree):
            output.append("Imperative")
        if sv_to_inf(tree):
            output.append("SV with non-finite TO-Infinitive")
        if sv_modal(tree):
            output.append("SV with non-finite modal")
        if sv(tree):
            output.append("Subject-Verb Simple")

        # If no matches, classify as "Other Structure"
        if not output:
            output.append("Other Structure")

    return output


# Function to get constituency parse tree (Used to check structure identification)
def parse_const(text):
    doc = nlp(text)
    return ' '.join([sent._.parse_string for sent in doc.sents])
