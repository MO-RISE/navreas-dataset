# NAVigation REASoning dataset

A diagnostic dataset for navigation reasoning.

The dataset cosnsist of multiple choice questions in JSON:

```json
[
  {
    "question": "An own ship has a target vessel at a relative bearing of 90 degrees. Which of the given terms best describe the location of the the target ship relative to the own ship.",
    "choices": ["astern", "ahead", "at starboard", "at portside"],
    "answer": "at starboard",
    "image": ""
  }
]
```

## Capabiltities tested

**Spatial relationship and estimation of motion**

- At starboard or at portside?
- A ahead or astern?
- Moving or standing still?
- Approaching or receding?
- Starboard turn or portside turn?
- CPA? TCPA?
- Will cross ahead or astern?
- Bow and stern crossing distance?

**Scene understanding**

- Number and type of target vessels
- Determine if there is risk of collision (Yes or No, following Rule 8)
- If yes, determine the type of COLREG situation (head-on, crossing, overtaking).
- Determine which vessel should give way.
- Restricted waters, for who?
- Traffic separation scheme?

**Actions to be taken according to COLREG and good seamanship (Rule 2, 8, 13, 14, and 15)**

- Stand-on or give-way?
- Alteration of course or speed.
- Well-defined (i.e. readily apparent visually or by radar)
- Timely.
- Reduce the risk of collision (plan for everyone’s safety)
- Consider maneuvering capabilities.
- Consider uncertainties.
- Consider the restrictions and limitations of surrounding vessels.
