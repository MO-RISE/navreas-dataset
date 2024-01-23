situation_description = """
There a 3 ships in this marine traffic situation:
Ship 1 has s course of 90 degrees and a speed of 20 knots.
Ship 2 has a course of 90 degrees and a speed of 10 knots.
Ship 3 has a course of 315 degrees and a speed of 10 knots.
Ship 1 is at a relative bearing of 180 degrees with respect to ship 2 and a distance of 1 nautical mile.
Ship 3 is at a relative bearing of 45 degrees with respect to ship 2 and a distance of 1 nautical mile. 
There is a traffic separation scheme north of ship 1 and 2 and at northwest of ship 3.
There is a restriced area south of ship 2 and west of ship 3.
Ship 1 and 2 monitor an straight eastboudn route. 
Ship 3 monitors a route that turns west between the traffic seperation scheme area and the restricted area.

"""

possible_solutions = [
 "Ship 1 reduces her speed matching the speed of ship 2. Ship 2 alters her course to starboard but keeping clear of the restricted area. Ship 3 keeps course and speed.",
 "Ship 1 changes her course to position herself between ship 2 and the restricted area. Ship 3 reduces her speed. Ship 2 keeps course and speed.",
 "Ship 1 changes her course to port to overtake ship 2 on her port side and pass ahead of ship 3. Ship 2 changes her course to port to pass ahead of ship 3. Ship 3 keeps her course and speed.",
 "Ship 1 changes her course to starboard to pass ship 2 on her starboard side and go astern of ship 3. Ship 2 changes her course to starboard to pass astern of ship 3. Ship 3 keeps her course and speed.",
 "Ship 1 changes her course to port to overtake ship 2. Ship 2 changes her course to starboard to pass astern of ship 3. Ship 3 keeps her course and speed.",
 "Ship 2 changes her course to port to pass ahead of ship 3. Ship 1 changes her course to starboard to pass astern of ship 3.",
 "Ship 2 reduces her speed. Ship 1 reduces her speed to match the speed of ship 2. Ship 3 keeps her course and speed.",
 "Ship 3 changes her course to starboard to pass ahead of ship 1 and 2. Ship 1 alters her course to port to overtake ship 2 on her port side. Ship 2 keeps her course and speed.",
 "Ship 3 changes her course to starboard to pass ahead of ship 1 and 2. Ship 1 alters her course to starboard to overtake ship 2 on her starboard side. Ship 2 alters her course to port.",
 "Ship 3 changes her course to port to pass astern of ship 1 and 2. Ship 2 keeps her course and speed. Ship 1 reduces her speed to match the speed of ship 2."
]

possible_solution_multiple_choice = """
(A) solution 1: Ship 1 reduces her speed matching the speed of ship 2. Ship 2 alters her course to starboard but keeping clear of the restricted area. Ship 3 keeps course and speed.
(B) solution 2: Ship 1 changes her course to position herself between ship 2 and the restricted area. Ship 3 reduces her speed. Ship 2 keeps course and speed. 
(C) solution 3: Ship 1 changes her course to port to overtake ship 2 on her port side and pass ahead of ship 3. Ship 2 changes her course to port to pass ahead of ship 3. Ship 3 keeps her course and speed.
(D) solution 4: Ship 1 changes her course to starboard to pass ship 2 on her starboard side and go astern of ship 3. Ship 2 changes her course to starboard to pass astern of ship 3. Ship 3 keeps her course and speed.
(E) solution 5: Ship 1 changes her course to port to overtake ship 2. Ship 2 changes her course to starboard to pass astern of ship 3. Ship 3 keeps her course and speed.
(F) solution 6: Ship 2 changes her course to port to pass ahead of ship 3. Ship 1 changes her course to starboard to pass astern of ship 3.
(G) solution 7: Ship 2 reduces her speed. Ship 1 reduces her speed to match the speed of ship 2. Ship 3 keeps her course and speed.
(H) solution 8: Ship 3 changes her course to starboard to pass ahead of ship 1 and 2. Ship 1 alters her course to port to overtake ship 2 on her port side. Ship 2 keeps her course and speed.
(I) solution 9: Ship 3 changes her course to starboard to pass ahead of ship 1 and 2. Ship 1 alters her course to starboard to overtake ship 2 on her starboard side. Ship 2 alters her course to port.
(J) solution 10: Ship 3 changes her course to port to pass astern of ship 1 and 2. Ship 2 keeps her course and speed. Ship 1 reduces her speed to match the speed of ship 2.
"""

colreg_violation_question = """Consider the following solution to the marine traffic situation: "{}". Does any of the ships violate the International Collision Regulations (COLREGS)? Please select the
appropriate option: \n {}"""


questions = [
        {
            'text':f"Which of the following possible solutions is the safest? \n {possible_solution_multiple_choice}",
            'correct_answer': '(A)',
            'correct_reasoning': 'Safest with no violations of the COLREGS.'
        },
        {
            'text': colreg_violation_question.format(possible_solutions[1-1], "(A) ship 2 violates rule 17 \n (B) ship 1 violates rule 13 \n (C) no violations"),
            'correct_answer': '(C)',
            'correct_reasoning': 'No violations of the COLREGS. Ship 3 follows rule 17, ship 2 follows rule 15, ship 1 eases the situation by not overtaking ship 2'
        },
        {
            'text': colreg_violation_question.format(possible_solutions[2-1], "(A) ship 3 violates rule 17 and ship 2 violates rule 15 \n (B) ship 1 violates rule 13 \n (C) no violations"),
            'correct_answer': '(A)',
            'correct_reasoning': 'Ship 3 is the stand-on vessel and should keep course and speed. Ship 2 should give way to Ship 3. Ship 1 does not violate a rule but is not easing the situation.'
        },
        {
            'text': colreg_violation_question.format(possible_solutions[3-1], "(A) ship 2 violates rule 15 \n (B) ship 3 violates rule 17 \n (C) no violations "),
            'correct_answer': '(A)',
            'correct_reasoning': 'Ship 2 is keeping out of the way of ship 1, but it does not avoid crossing ahead of it.' 
        },
        {
            'text': colreg_violation_question.format(possible_solutions[4-1], "(A) ship 1 violates rule 17 \n (B) ship 2 violates rule 17 \n (C) no violations"),
            'correct_answer': '(C)',
            'correct_reasoning': 'No violations of the COLREGS, but ship 1 is not easing the situation by overtaking ship 2.'
        },
        {
            'text': colreg_violation_question.format(possible_solutions[5-1], "(A) ship 2 violates rule 17 \n (B) ship 2 violates rule 13 \n (C) no violations"),
            'correct_answer': '(C)',
            'correct_reasoning': 'ship 2 follows rule 15, give-way has priority over being the stand-on vessel on the crossing situation with ship 3'
        },
        {
            'text': colreg_violation_question.format(possible_solutions[6-1], "(A) ship 2 violates rule 15 \n (B) ship 1 violates rule 13 \n (C) no violations"),
            'correct_answer': '(A)',
            'correct_reasoning': 'Ship 2 is keeping out of the way of ship 1, but it does not avoid crossing ahead of it.'
        },
        {
            'text': colreg_violation_question.format(possible_solutions[7-1], "(A) ship 1 violates rule 15 \n (B) ship 3 violates rule 17 \n (C) no violations"),
            'correct_answer': '(C)',
            'correct_reasoning': 'No violations of the COLREGS. Ship 3 follows rule 17, ship 2 follows rule 15, ship 1 eases the situation by not overtaking ship 2'
        },
        {
            'text': colreg_violation_question.format(possible_solutions[8-1], "(A) ship 3 violates rule 17 and ship 2 violates rule 15 \n (B) ship 1 violates rule 17 \n (C) no violations"),
            'correct_answer': '(A)',
            'correct_reasoning': 'ship 3 is the stand-on vessel in the crossing situation with ship 2 and therefore it should keep course and speed, ship 2 should give way.'
        },
        {
            'text': colreg_violation_question.format(possible_solutions[9-1], "(A) ship 1 violates rule 15 \n (B) ship 3 violates rule 17 \n (C) no violations"),
            'correct_answer': '(B)',
            'correct_reasoning': 'ship 3 is the stand-on vessel in the crossing situation with ship 2 and therefore it should keep course and speed',
        },
        {
            'text': colreg_violation_question.format(possible_solutions[10-1], "(A) ship 3 violates rule 17 and ship 2 violates rule 15 \n (B) ship 3 violates rule 17 and ship 1 violates rule 13 \n (C) no violations"),
            'correct_answer': '(A)',
            'correct_reasoning': 'ship 3 is the stand-on vessel in the crossing situation with ship 2 and therefore it should keep course and speed, ship 2 should give way.',
        },
        {
            'text':"""What is the effect of ship 1 overtaking ship 2 on the traffic situation? Please select the appropriate option:
            (A) ship 1 eases the situation by overtaking ship 2
            (B) ship 1 worsens the situation by overtaking ship 2
            (C) ship 1 has no effect on the situation by overtaking ship 2
            """,
            'correct_answer': '(B)',
            'correct_reasoning': 'ship 1 limits the freedom of ship 2 to resolve its crossing situation with ship 3'
        },
        {
            'text':"""What is the preferred action by ship 2 to resolve its situation with ship 3? Please select the appropriate option:
            (A) ship 2 alters her course to starbord to cross astern of ship 3 but keeps clear of the restricted area
            (B) ship 2 alters her course to portside to cross ahead of ship 3 but keeps clear of the entering the wrong lane in the traffic separation scheme
            (C) ship 2 reduces her speed to let ship 3 pass
            (D) ship 2 waits for ship 3 to take an action
            """,
            'correct_answer': '(A)',
            'correct_reasoning': 'ship 2 must give way to ship 3 and avoid crossing ahead of it according to rule 15'
        },    
    ]


def print_questions_for_review():
    print(situation_description)
    i = 1
    for question in questions:
        print(f'Question {i}')
        print(question['text'])
        print('\n')
        print('Correct answer \n')
        print(question['correct_answer'])
        print('\n')
        print('Correct reasoning \n')
        print(question['correct_reasoning'])
        print('\n')
        i += 1