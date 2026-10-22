# Embodied AI data foundations for programmers

**Goal:** inspect an episode before trusting it as training or evaluation data.
This free introductory guide focuses on data engineering. You need basic Python;
you do not need a robot, GPU, cloud account or Runix subscription.

This is original Runix learning material, not a claim of a completed robotics
curriculum. It does not teach hardware control or policy training. The exercise
uses **synthetic records created solely for teaching**, not robot measurements.

## 1. Read an episode as a sequence, not a bag of rows

A robot dataset records a sequence of observations and actions within an episode.
Start by asking what each field means: an image from which camera, a position in
which reference frame, an action in which units, and a timestamp from which clock?
A shared field name does not establish a shared meaning across robots.

[RLDS](https://github.com/google-research/rlds) documents episode/step structure,
including `is_first`, `is_last` and `is_terminal`. Those flags are not synonyms:
a final recorded step can arise from truncation rather than task termination.
RLDS also notes that some fields on the last step may not be valid. Follow a
source dataset's contract instead of treating every final observation as a
valid action-labelled training example. The linked RLDS repository is archived;
use it as a format reference, not a promise of an actively maintained dependency.

**Exercise:** write a field dictionary for one episode: field, dtype, shape,
units, frame, timestamp origin and missing-value behavior. Name anything that
the source has not documented instead of filling it with an assumption.

## 2. Establish observation/action alignment

An observation may be sampled before an action, while a resulting observation
is sampled afterward. Cameras, state sensors and control commands may have
different rates and clocks. Record the intended matching rule and allowed lag
before aligning them. A simple timestamp-order check can find defects but cannot
prove that two sensors are synchronized.

The following **synthetic** example catches a backwards timestamp and shows why
splitting a sequence into individual rows can mix the same recording session
into training and evaluation. Run it with Python 3.10+; it uses only the standard
library and never controls hardware.

```python
# Synthetic teaching data; CC BY 4.0, Runix Lab contributors.
from collections import defaultdict

records = [
    {"session": "s1", "episode": "e1", "step": 0, "t_ms": 0},
    {"session": "s1", "episode": "e1", "step": 1, "t_ms": 100},
    {"session": "s1", "episode": "e2", "step": 0, "t_ms": 0},
    {"session": "s1", "episode": "e2", "step": 1, "t_ms": -10},
    {"session": "s2", "episode": "e3", "step": 0, "t_ms": 0},
    {"session": "s2", "episode": "e3", "step": 1, "t_ms": 100},
]

episodes = defaultdict(list)
for row in records:
    episodes[(row["session"], row["episode"])].append(row)

bad = []
for key, rows in episodes.items():
    rows = sorted(rows, key=lambda row: row["step"])
    if any(b["t_ms"] <= a["t_ms"] for a, b in zip(rows, rows[1:])):
        bad.append(key)
print("Non-monotonic episodes:", bad)

train, evaluation = records[::2], records[1::2]
overlap = {r["session"] for r in train} & {r["session"] for r in evaluation}
print("Row-split session overlap:", sorted(overlap))

# A predefined held-out session, not a claim of statistically representative data.
train = [r for r in records if r["session"] == "s1"]
evaluation = [r for r in records if r["session"] == "s2"]
assert {r["session"] for r in train}.isdisjoint(
    {r["session"] for r in evaluation}
)
print("Grouped split session overlap: []")
```

Expected output:

```text
Non-monotonic episodes: [('s1', 'e2')]
Row-split session overlap: ['s1', 's2']
Grouped split session overlap: []
```

**Check your reasoning:** sorting by timestamp instead of step would hide this
fault. Reject or investigate the episode before resampling. A grouped split
removes this particular session overlap; it does not detect duplicate videos,
shared scenes or every other form of evaluation leakage.

## 3. Define the evaluation boundary

Write down the generalization question first: new episodes, recording sessions,
scenes, objects, tasks or embodiments? Grouping by episode is insufficient when
near-identical episodes from one session appear on both sides of the split.
A session split is still insufficient for evaluating unseen objects or robots.

For each proposed dataset, produce a short review:

| Check | Evidence to record |
| --- | --- |
| Provenance | Dataset version, collection/source, stable IDs and transformations |
| Rights | Terms for data, videos, annotations and derivative redistribution |
| Semantics | Observation/action definitions, units, coordinate frame and embodiment |
| Alignment | Clock sources, sampling rates, matching rule and missing frames |
| Coverage | Episodes/sessions/tasks and documented failures or exclusions |
| Evaluation | Grouping rule, held-out entities and checks for duplicates across splits |

Do not silently replace missing fields with zeros or assume every episode
succeeded. Report exclusions alongside the remaining data, and retain the source
IDs so another person can examine the same records.

## Continue with primary sources

- [Open X-Embodiment](https://robotics-transformer-x.github.io/): read the project
  and paper, then inspect the component dataset documentation. It is external
  research, not a Runix dataset or partnership.
- [RLDS format documentation](https://github.com/google-research/rlds): compare
  its step/episode contract with your field dictionary; the repository is archived.
- [RLDS dataset conversion example](https://github.com/kpertsch/rlds_dataset_builder):
  inspect how a dummy dataset is converted before adapting real records. Running
  that external project requires its own dependencies; the inline exercise above
  is intentionally independent of them.

Read original dataset licenses before downloading, adapting or redistributing
third-party data. Linking a resource does not grant rights to its contents.

## Reuse and corrections

Copyright 2026 Runix Lab contributors. This guide, including its inline synthetic
exercise, is licensed under [CC BY 4.0](LICENSE). Attribute Runix Lab, link the
license and indicate changes when adapting it. No third-party course text or
robot dataset is bundled here.

To report an error, open an issue in this repository with the affected section,
a primary source and, for code, the smallest reproduction. You can also contribute
an original exercise after stating its scope and data provenance.
