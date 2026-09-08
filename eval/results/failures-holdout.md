# Failures — holdout split

51 failing case(s) out of 139 case-runs across 4 system(s).

Every failure is listed in full. Nothing is summarised away, because the point of this file is that a reviewer can see exactly what the system got wrong and why it thought it was right.

## exact / A4_brand_orthography — 2 failing

### `hold-pos-08` — missed_intervention

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: unseen split-brand case. None of this vocabulary appears in the seed or dev split.
- **input**: `The Tensor Flow model needs retraining.`
- **expected** (correct): `The TensorFlow model needs retraining.`
- **actual** (unchanged): `The Tensor Flow model needs retraining.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: []
- **relevant memory**: #5 'TensorFlow' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `hold-pos-09` — missed_intervention

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: unseen sentence, mixed known and unknown terms. None of this vocabulary appears in the seed or dev split.
- **input**: `Tensor Flow and PyTorch disagree here.`
- **expected** (correct): `TensorFlow and PyTorch disagree here.`
- **actual** (unchanged): `Tensor Flow and PyTorch disagree here.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: []
- **relevant memory**: #5 'TensorFlow' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

## exact / A5_personal_acronym — 1 failing

### `hold-pos-15` — missed_intervention

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: unseen acronym. None of this vocabulary appears in the seed or dev split.
- **input**: `Send the deck to O K R review.`
- **expected** (correct): `Send the deck to OKR review.`
- **actual** (unchanged): `Send the deck to O K R review.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: []
- **relevant memory**: #9 'OKR' (acronym, confirmed, 0.9), #8 '@nilima_r' (handle, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

## exact / A7_multiword_entity — 2 failing

### `hold-pos-16` — missed_intervention

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: unseen multi-word company, casing only. None of this vocabulary appears in the seed or dev split.
- **input**: `Amber rail signed the contract.`
- **expected** (correct): `Amber Rail signed the contract.`
- **actual** (unchanged): `Amber rail signed the contract.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: []
- **relevant memory**: #10 'Amber Rail' (org, confirmed, 0.76)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `hold-pos-17` — missed_intervention

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: unseen context for an unseen multi-word entity. None of this vocabulary appears in the seed or dev split.
- **input**: `Chase amber rail about the invoice.`
- **expected** (correct): `Chase Amber Rail about the invoice.`
- **actual** (unchanged): `Chase amber rail about the invoice.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: []
- **relevant memory**: #10 'Amber Rail' (org, confirmed, 0.76)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

## exact / A9_handle_identifier — 1 failing

### `hold-pos-14` — missed_intervention

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: unseen handle. None of this vocabulary appears in the seed or dev split.
- **input**: `DM at Nilima underscore R the final numbers.`
- **expected** (correct): `DM @nilima_r the final numbers.`
- **actual** (unchanged): `DM at Nilima underscore R the final numbers.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: []
- **relevant memory**: #9 'OKR' (acronym, confirmed, 0.9), #8 '@nilima_r' (handle, confirmed, 0.9), #3 'Nilima' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

## exact / N7_metalinguistic_mention — 1 failing

### `hold-neg-13` — false_intervention

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: metalinguistic use of a preference memory.
- **input**: `The word 'colour' is spelled differently in Britain.`
- **expected** (none): `The word 'colour' is spelled differently in Britain.`
- **actual** (changed): `The word 'color' is spelled differently in Britain.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: [{"span": "colour", "replacement": "color", "memory_id": 6}]
- **relevant memory**: #6 'color' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "colour",
      "replacement": "color",
      "memory_id": 6
    }
  ],
  "reason_mismatch": null
}
```

</details>

## fuzzy / A11_spelling_preference — 3 failing

### `hold-pos-10` — acted_but_wrong_text

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: unseen preference pair, opposite direction to the dev split. None of this vocabulary appears in the seed or dev split.
- **input**: `Use the colour palette from the brand guide.`
- **expected** (correct): `Use the color palette from the brand guide.`
- **actual** (changed): `Use the color from the brand guide.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "colour palette", "replacement": "color", "memory_id": 6}]
- **relevant memory**: #6 'color' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "colour palette",
      "replacement": "color",
      "memory_id": 6
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `hold-pos-11` — acted_but_wrong_text

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: unseen context. None of this vocabulary appears in the seed or dev split.
- **input**: `The colour contrast fails the audit.`
- **expected** (correct): `The color contrast fails the audit.`
- **actual** (changed): `The color fails the audit.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "colour contrast", "replacement": "color", "memory_id": 6}]
- **relevant memory**: #6 'color' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "colour contrast",
      "replacement": "color",
      "memory_id": 6
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `hold-pos-18` — acted_but_wrong_text

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: a spelling preference is meaning-preserving, so it applies in ANY context, including one with no work-related cues at all. That is the deliberate difference between a preference memory and a referent-changing correction.
- **input**: `The colour of the sky was unreal.`
- **expected** (correct): `The color of the sky was unreal.`
- **actual** (changed): `The color the sky was unreal.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "colour of", "replacement": "color", "memory_id": 6}]
- **relevant memory**: #6 'color' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "colour of",
      "replacement": "color",
      "memory_id": 6
    }
  ],
  "reason_mismatch": null
}
```

</details>

## fuzzy / A12_transliteration_preference — 2 failing

### `hold-pos-12` — acted_but_wrong_text

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: unseen city pair. None of this vocabulary appears in the seed or dev split.
- **input**: `The Bombay team is joining the review.`
- **expected** (correct): `The Mumbai team is joining the review.`
- **actual** (changed): `The Mumbai is joining the review.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Bombay team", "replacement": "Mumbai", "memory_id": 7}]
- **relevant memory**: #7 'Mumbai' (org, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Bombay team",
      "replacement": "Mumbai",
      "memory_id": 7
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `hold-pos-13` — acted_but_wrong_text

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: unseen context. None of this vocabulary appears in the seed or dev split.
- **input**: `I land in Bombay on Tuesday.`
- **expected** (correct): `I land in Mumbai on Tuesday.`
- **actual** (changed): `I land Mumbai on Tuesday.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "in Bombay", "replacement": "Mumbai", "memory_id": 7}]
- **relevant memory**: #7 'Mumbai' (org, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "in Bombay",
      "replacement": "Mumbai",
      "memory_id": 7
    }
  ],
  "reason_mismatch": null
}
```

</details>

## fuzzy / A2_person_romanisation_preference — 5 failing

### `hold-pos-01` — acted_but_wrong_text

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: unseen name, unseen romanisation pair. None of this vocabulary appears in the seed or dev split.
- **input**: `Ask Prateek to check the deployment.`
- **expected** (correct): `Ask Prathik to check the deployment.`
- **actual** (changed): `Aarav to check the deployment.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Ask Prateek", "replacement": "Aarav", "memory_id": 11}]
- **relevant memory**: #1 'Prathik' (person, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Ask Prateek",
      "replacement": "Aarav",
      "memory_id": 11
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `hold-pos-02` — acted_but_wrong_text

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: unseen name in an unseen context. None of this vocabulary appears in the seed or dev split.
- **input**: `Prateek is reviewing the retry logic.`
- **expected** (correct): `Prathik is reviewing the retry logic.`
- **actual** (changed): `Prathiks reviewing the retry logic.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Prateek is", "replacement": "Prathiks", "memory_id": 1}]
- **relevant memory**: #1 'Prathik' (person, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Prateek is",
      "replacement": "Prathiks",
      "memory_id": 1
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `hold-pos-03` — acted_but_wrong_text

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: short sentence, minimal context. None of this vocabulary appears in the seed or dev split.
- **input**: `I owe Prateek a reply.`
- **expected** (correct): `I owe Prathik a reply.`
- **actual** (changed): `I owe Prathik reply.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Prateek a", "replacement": "Prathik", "memory_id": 1}]
- **relevant memory**: #1 'Prathik' (person, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Prateek a",
      "replacement": "Prathik",
      "memory_id": 1
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `hold-pos-04` — acted_but_wrong_text

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: second unseen name pair. None of this vocabulary appears in the seed or dev split.
- **input**: `Neelima is presenting the benchmark.`
- **expected** (correct): `Nilima is presenting the benchmark.`
- **actual** (changed): `Nilimas Prathik the benchmark.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Neelima is", "replacement": "Nilimas", "memory_id": 3}, {"span": "presenting", "replacement": "Prathik", "memory_id": 1}]
- **relevant memory**: #3 'Nilima' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Neelima is",
      "replacement": "Nilimas",
      "memory_id": 3
    },
    {
      "span": "presenting",
      "replacement": "Prathik",
      "memory_id": 1
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `hold-pos-05` — acted_but_wrong_text

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: unseen context for an unseen name. None of this vocabulary appears in the seed or dev split.
- **input**: `Email Neelima the final numbers.`
- **expected** (correct): `Email Nilima the final numbers.`
- **actual** (changed): `Email Nilima @nilima_r.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Neelima the", "replacement": "Nilima", "memory_id": 3}, {"span": "final numbers", "replacement": "@nilima_r", "memory_id": 8}]
- **relevant memory**: #3 'Nilima' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Neelima the",
      "replacement": "Nilima",
      "memory_id": 3
    },
    {
      "span": "final numbers",
      "replacement": "@nilima_r",
      "memory_id": 8
    }
  ],
  "reason_mismatch": null
}
```

</details>

## fuzzy / A4_brand_orthography — 2 failing

### `hold-pos-08` — acted_but_wrong_text

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: unseen split-brand case. None of this vocabulary appears in the seed or dev split.
- **input**: `The Tensor Flow model needs retraining.`
- **expected** (correct): `The TensorFlow model needs retraining.`
- **actual** (changed): `The TensorFlow model Nilimas retraining.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Tensor Flow", "replacement": "TensorFlow", "memory_id": 5}, {"span": "needs", "replacement": "Nilimas", "memory_id": 3}]
- **relevant memory**: #5 'TensorFlow' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Tensor Flow",
      "replacement": "TensorFlow",
      "memory_id": 5
    },
    {
      "span": "needs",
      "replacement": "Nilimas",
      "memory_id": 3
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `hold-pos-09` — acted_but_wrong_text

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: unseen sentence, mixed known and unknown terms. None of this vocabulary appears in the seed or dev split.
- **input**: `Tensor Flow and PyTorch disagree here.`
- **expected** (correct): `TensorFlow and PyTorch disagree here.`
- **actual** (changed): `TensorFlow @nilima_r PyTorch disagree Vercel.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Tensor Flow", "replacement": "TensorFlow", "memory_id": 5}, {"span": "and", "replacement": "@nilima_r", "memory_id": 8}, {"span": "here", "replacement": "Vercel", "memory_id": 4}]
- **relevant memory**: #5 'TensorFlow' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Tensor Flow",
      "replacement": "TensorFlow",
      "memory_id": 5
    },
    {
      "span": "and",
      "replacement": "@nilima_r",
      "memory_id": 8
    },
    {
      "span": "here",
      "replacement": "Vercel",
      "memory_id": 4
    }
  ],
  "reason_mismatch": null
}
```

</details>

## fuzzy / A5_personal_acronym — 1 failing

### `hold-pos-15` — acted_but_wrong_text

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: unseen acronym. None of this vocabulary appears in the seed or dev split.
- **input**: `Send the deck to O K R review.`
- **expected** (correct): `Send the deck to OKR review.`
- **actual** (changed): `Send the deck to O OKR review.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "K R", "replacement": "OKR", "memory_id": 9}]
- **relevant memory**: #9 'OKR' (acronym, confirmed, 0.9), #8 '@nilima_r' (handle, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "K R",
      "replacement": "OKR",
      "memory_id": 9
    }
  ],
  "reason_mismatch": null
}
```

</details>

## fuzzy / A6_jargon_heard_as_ordinary — 2 failing

### `hold-pos-06` — acted_but_wrong_text

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: unseen product, unseen mis-hearing. None of this vocabulary appears in the seed or dev split.
- **input**: `Deploy it on Versell instead.`
- **expected** (correct): `Deploy it on Vercel instead.`
- **actual** (changed): `Deploy it Vercel instead.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "on Versell", "replacement": "Vercel", "memory_id": 4}]
- **relevant memory**: #4 'Vercel' (product, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "on Versell",
      "replacement": "Vercel",
      "memory_id": 4
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `hold-pos-07` — acted_but_wrong_text

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: unseen context. None of this vocabulary appears in the seed or dev split.
- **input**: `Versell is rate limiting the build.`
- **expected** (correct): `Vercel is rate limiting the build.`
- **actual** (changed): `Vercels Prathik limiting the build.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Versell is", "replacement": "Vercels", "memory_id": 4}, {"span": "rate", "replacement": "Prathik", "memory_id": 1}]
- **relevant memory**: #4 'Vercel' (product, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Versell is",
      "replacement": "Vercels",
      "memory_id": 4
    },
    {
      "span": "rate",
      "replacement": "Prathik",
      "memory_id": 1
    }
  ],
  "reason_mismatch": null
}
```

</details>

## fuzzy / A7_multiword_entity — 1 failing

### `hold-pos-16` — acted_but_wrong_text

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: unseen multi-word company, casing only. None of this vocabulary appears in the seed or dev split.
- **input**: `Amber rail signed the contract.`
- **expected** (correct): `Amber Rail signed the contract.`
- **actual** (changed): `Amber Rail signed the color.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Amber rail", "replacement": "Amber Rail", "memory_id": 10}, {"span": "contract", "replacement": "color", "memory_id": 6}]
- **relevant memory**: #10 'Amber Rail' (org, confirmed, 0.76)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Amber rail",
      "replacement": "Amber Rail",
      "memory_id": 10
    },
    {
      "span": "contract",
      "replacement": "color",
      "memory_id": 6
    }
  ],
  "reason_mismatch": null
}
```

</details>

## fuzzy / A9_handle_identifier — 1 failing

### `hold-pos-14` — acted_but_wrong_text

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: unseen handle. None of this vocabulary appears in the seed or dev split.
- **input**: `DM at Nilima underscore R the final numbers.`
- **expected** (correct): `DM @nilima_r the final numbers.`
- **actual** (changed): `DM at @nilima_r R the @nilima_r.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Nilima underscore", "replacement": "@nilima_r", "memory_id": 8}, {"span": "final numbers", "replacement": "@nilima_r", "memory_id": 8}]
- **relevant memory**: #9 'OKR' (acronym, confirmed, 0.9), #8 '@nilima_r' (handle, confirmed, 0.9), #3 'Nilima' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Nilima underscore",
      "replacement": "@nilima_r",
      "memory_id": 8
    },
    {
      "span": "final numbers",
      "replacement": "@nilima_r",
      "memory_id": 8
    }
  ],
  "reason_mismatch": null
}
```

</details>

## fuzzy / N13_no_relevant_memory — 5 failing

### `hold-neg-03` — false_intervention

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: this persona has no Cursor memory, so nothing may happen.
- **input**: `Move the cursor to the top.`
- **expected** (none): `Move the cursor to the top.`
- **actual** (changed): `Zorvex the cursor to the top.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Move", "replacement": "Zorvex", "memory_id": 2}]

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Move",
      "replacement": "Zorvex",
      "memory_id": 2
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `hold-neg-04` — false_intervention

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: this persona has no Kivi memory: the dev split's vocabulary must not leak.
- **input**: `I ate a kiwi on the flight.`
- **expected** (none): `I ate a kiwi on the flight.`
- **actual** (changed): `I Prathik a kiwi on the flight.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "ate", "replacement": "Prathik", "memory_id": 1}]

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "ate",
      "replacement": "Prathik",
      "memory_id": 1
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `hold-neg-05` — false_intervention

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: the dev split's headline sentence must be untouched for a different person.
- **input**: `Ask Aditya to review the Sarvam Kiwi service.`
- **expected** (none): `Ask Aditya to review the Sarvam Kiwi service.`
- **actual** (changed): `Ask Aditya to review the Aarav Kiwi Zorvex.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Sarvam", "replacement": "Aarav", "memory_id": 11}, {"span": "service", "replacement": "Zorvex", "memory_id": 2}]

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Sarvam",
      "replacement": "Aarav",
      "memory_id": 11
    },
    {
      "span": "service",
      "replacement": "Zorvex",
      "memory_id": 2
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `hold-neg-11` — false_intervention

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: ordinary sentence containing a common proper noun.
- **input**: `Please confirm the invoice total by Friday.`
- **expected** (none): `Please confirm the invoice total by Friday.`
- **actual** (changed): `Please color the invoice total by Friday.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "confirm", "replacement": "color", "memory_id": 6}]

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "confirm",
      "replacement": "color",
      "memory_id": 6
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `hold-neg-12` — false_intervention

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: hypothetical naming must not trigger a correction.
- **input**: `We might call the next service Verdance.`
- **expected** (none): `We might call the next service Verdance.`
- **actual** (changed): `We might call the next Zorvex Vercel.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "service", "replacement": "Zorvex", "memory_id": 2}, {"span": "Verdance", "replacement": "Vercel", "memory_id": 4}]

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "service",
      "replacement": "Zorvex",
      "memory_id": 2
    },
    {
      "span": "Verdance",
      "replacement": "Vercel",
      "memory_id": 4
    }
  ],
  "reason_mismatch": null
}
```

</details>

## fuzzy / N3_common_word_collision — 3 failing

### `hold-neg-01` — false_intervention

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: 'amber' alone is an ordinary word and must not pull in the company memory.
- **input**: `The amber warning light came on.`
- **expected** (none): `The amber warning light came on.`
- **actual** (changed): `The Amber Rail light came on.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "amber warning", "replacement": "Amber Rail", "memory_id": 10}]
- **relevant memory**: #10 'Amber Rail' (org, confirmed, 0.76)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "amber warning",
      "replacement": "Amber Rail",
      "memory_id": 10
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `hold-neg-06` — false_intervention

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: 'flow' must not be pulled toward TensorFlow.
- **input**: `The flow of the meeting was poor.`
- **expected** (none): `The flow of the meeting was poor.`
- **actual** (changed): `The flow of the meeting was color.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "poor", "replacement": "color", "memory_id": 6}]
- **relevant memory**: #5 'TensorFlow' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "poor",
      "replacement": "color",
      "memory_id": 6
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `hold-neg-07` — false_intervention

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: 'tensor' alone is a technical word, not the brand.
- **input**: `Tensor products come up in the proof.`
- **expected** (none): `Tensor products come up in the proof.`
- **actual** (changed): `TensorFlows color in the proof.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Tensor products", "replacement": "TensorFlows", "memory_id": 5}, {"span": "come up", "replacement": "color", "memory_id": 6}]
- **relevant memory**: #5 'TensorFlow' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Tensor products",
      "replacement": "TensorFlows",
      "memory_id": 5
    },
    {
      "span": "come up",
      "replacement": "color",
      "memory_id": 6
    }
  ],
  "reason_mismatch": null
}
```

</details>

## fuzzy / N7_metalinguistic_mention — 1 failing

### `hold-neg-13` — false_intervention

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: metalinguistic use of a preference memory.
- **input**: `The word 'colour' is spelled differently in Britain.`
- **expected** (none): `The word 'colour' is spelled differently in Britain.`
- **actual** (changed): `The OKR 'colors spelled differently in Britain.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "colour' is", "replacement": "colors", "memory_id": 6}, {"span": "word", "replacement": "OKR", "memory_id": 9}]
- **relevant memory**: #6 'color' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "colour' is",
      "replacement": "colors",
      "memory_id": 6
    },
    {
      "span": "word",
      "replacement": "OKR",
      "memory_id": 9
    }
  ],
  "reason_mismatch": null
}
```

</details>

## fuzzy / N8_already_canonical — 2 failing

### `hold-neg-08` — false_intervention

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: already correct: must be a recorded no-op.
- **input**: `Aarav is reviewing the schema change.`
- **expected** (none): `Aarav is reviewing the schema change.`
- **actual** (changed): `Aaravs reviewing the schema change.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Aarav is", "replacement": "Aaravs", "memory_id": 11}]
- **relevant memory**: #11 'Aarav' (term, confirmed, 0.72)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Aarav is",
      "replacement": "Aaravs",
      "memory_id": 11
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `hold-neg-09` — false_intervention

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: already correct.
- **input**: `Zorvex latency dropped after the rollout.`
- **expected** (none): `Zorvex latency dropped after the rollout.`
- **actual** (changed): `Zorvex dropped after the color.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Zorvex latency", "replacement": "Zorvex", "memory_id": 2}, {"span": "rollout", "replacement": "color", "memory_id": 6}]
- **relevant memory**: #2 'Zorvex' (term, confirmed, 0.85)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Zorvex latency",
      "replacement": "Zorvex",
      "memory_id": 2
    },
    {
      "span": "rollout",
      "replacement": "color",
      "memory_id": 6
    }
  ],
  "reason_mismatch": null
}
```

</details>

## kivi / A7_multiword_entity — 2 failing

### `hold-pos-16` — missed_intervention

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: unseen multi-word company, casing only. None of this vocabulary appears in the seed or dev split.
- **input**: `Amber rail signed the contract.`
- **expected** (correct): `Amber Rail signed the contract.`
- **actual** (unchanged): `Amber rail signed the contract.`
- **reason codes**: `ABSTAIN_ORDINARY_WORD_CONTEXT_WEAK, ABSTAIN_ORDINARY_WORD_CONTEXT_WEAK`
- **system's reasoning**: context score 0.00 did not reach the 0.75 required here — an inexact match onto a very common English word (rank 1204) is the highest-risk substitution there is
- **relevant memory**: #10 'Amber Rail' (org, confirmed, 0.76)

<details><summary>full decision detail</summary>

```json
{
  "counts": {
    "applied": 0,
    "abstained": 2,
    "noop": 0,
    "blocked": 0
  },
  "protected_spans": [],
  "candidates": [
    {
      "span": "contract",
      "memory": "color",
      "tier": "fuzzy",
      "action": "abstained",
      "reason_code": "ABSTAIN_ORDINARY_WORD_CONTEXT_WEAK",
      "lexical": 0.727,
      "phonetic": 0.333,
      "context": 0.0,
      "required": 0.75
    },
    {
      "span": "Amber rail",
      "memory": "Amber Rail",
      "tier": "exact",
      "action": "abstained",
      "reason_code": "ABSTAIN_ORDINARY_WORD_CONTEXT_WEAK",
      "lexical": 1.0,
      "phonetic": 1.0,
      "context": 0.45,
      "required": 0.75
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `hold-pos-17` — missed_intervention

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: unseen context for an unseen multi-word entity. None of this vocabulary appears in the seed or dev split.
- **input**: `Chase amber rail about the invoice.`
- **expected** (correct): `Chase Amber Rail about the invoice.`
- **actual** (unchanged): `Chase amber rail about the invoice.`
- **reason codes**: `ABSTAIN_ORDINARY_WORD_CONTEXT_WEAK`
- **system's reasoning**: context score 0.17 did not reach the 0.75 required here — the heard form is an ordinary English word (rank 4108) written in lower case, so the formatting stage read it as a common noun and strong context is required before overwriting it
- **relevant memory**: #10 'Amber Rail' (org, confirmed, 0.76)

<details><summary>full decision detail</summary>

```json
{
  "counts": {
    "applied": 0,
    "abstained": 1,
    "noop": 0,
    "blocked": 0
  },
  "protected_spans": [],
  "candidates": [
    {
      "span": "amber rail",
      "memory": "Amber Rail",
      "tier": "exact",
      "action": "abstained",
      "reason_code": "ABSTAIN_ORDINARY_WORD_CONTEXT_WEAK",
      "lexical": 1.0,
      "phonetic": 1.0,
      "context": 0.175,
      "required": 0.75
    }
  ],
  "reason_mismatch": null
}
```

</details>

## llm_only / A11_spelling_preference — 2 failing

### `hold-pos-10` — missed_intervention

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: unseen preference pair, opposite direction to the dev split. None of this vocabulary appears in the seed or dev split.
- **input**: `Use the colour palette from the brand guide.`
- **expected** (correct): `Use the color palette from the brand guide.`
- **actual** (unchanged): `Use the colour palette from the brand guide.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #6 'color' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `hold-pos-18` — missed_intervention

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: a spelling preference is meaning-preserving, so it applies in ANY context, including one with no work-related cues at all. That is the deliberate difference between a preference memory and a referent-changing correction.
- **input**: `The colour of the sky was unreal.`
- **expected** (correct): `The color of the sky was unreal.`
- **actual** (unchanged): `The colour of the sky was unreal.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #6 'color' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

## llm_only / A12_transliteration_preference — 2 failing

### `hold-pos-12` — missed_intervention

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: unseen city pair. None of this vocabulary appears in the seed or dev split.
- **input**: `The Bombay team is joining the review.`
- **expected** (correct): `The Mumbai team is joining the review.`
- **actual** (unchanged): `The Bombay team is joining the review.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #7 'Mumbai' (org, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `hold-pos-13` — missed_intervention

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: unseen context. None of this vocabulary appears in the seed or dev split.
- **input**: `I land in Bombay on Tuesday.`
- **expected** (correct): `I land in Mumbai on Tuesday.`
- **actual** (unchanged): `I land in Bombay on Tuesday.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #7 'Mumbai' (org, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

## llm_only / A2_person_romanisation_preference — 5 failing

### `hold-pos-01` — missed_intervention

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: unseen name, unseen romanisation pair. None of this vocabulary appears in the seed or dev split.
- **input**: `Ask Prateek to check the deployment.`
- **expected** (correct): `Ask Prathik to check the deployment.`
- **actual** (unchanged): `Ask Prateek to check the deployment.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #1 'Prathik' (person, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `hold-pos-02` — missed_intervention

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: unseen name in an unseen context. None of this vocabulary appears in the seed or dev split.
- **input**: `Prateek is reviewing the retry logic.`
- **expected** (correct): `Prathik is reviewing the retry logic.`
- **actual** (unchanged): `Prateek is reviewing the retry logic.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #1 'Prathik' (person, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `hold-pos-03` — missed_intervention

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: short sentence, minimal context. None of this vocabulary appears in the seed or dev split.
- **input**: `I owe Prateek a reply.`
- **expected** (correct): `I owe Prathik a reply.`
- **actual** (unchanged): `I owe Prateek a reply.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #1 'Prathik' (person, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `hold-pos-04` — missed_intervention

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: second unseen name pair. None of this vocabulary appears in the seed or dev split.
- **input**: `Neelima is presenting the benchmark.`
- **expected** (correct): `Nilima is presenting the benchmark.`
- **actual** (unchanged): `Neelima is presenting the benchmark.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #3 'Nilima' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `hold-pos-05` — missed_intervention

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: unseen context for an unseen name. None of this vocabulary appears in the seed or dev split.
- **input**: `Email Neelima the final numbers.`
- **expected** (correct): `Email Nilima the final numbers.`
- **actual** (unchanged): `Email Neelima the final numbers.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #3 'Nilima' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

## llm_only / A6_jargon_heard_as_ordinary — 2 failing

### `hold-pos-06` — acted_but_wrong_text

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: unseen product, unseen mis-hearing. None of this vocabulary appears in the seed or dev split.
- **input**: `Deploy it on Versell instead.`
- **expected** (correct): `Deploy it on Vercel instead.`
- **actual** (changed): `Deploy it on Verse instead.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #4 'Vercel' (product, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `hold-pos-07` — missed_intervention

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: unseen context. None of this vocabulary appears in the seed or dev split.
- **input**: `Versell is rate limiting the build.`
- **expected** (correct): `Vercel is rate limiting the build.`
- **actual** (unchanged): `Versell is rate limiting the build.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #4 'Vercel' (product, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

## llm_only / A9_handle_identifier — 1 failing

### `hold-pos-14` — missed_intervention

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: unseen handle. None of this vocabulary appears in the seed or dev split.
- **input**: `DM at Nilima underscore R the final numbers.`
- **expected** (correct): `DM @nilima_r the final numbers.`
- **actual** (unchanged): `DM at Nilima underscore R the final numbers.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #9 'OKR' (acronym, confirmed, 0.9), #8 '@nilima_r' (handle, confirmed, 0.9), #3 'Nilima' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

## llm_only / N7_metalinguistic_mention — 1 failing

### `hold-neg-13` — false_intervention

- **scenario**: `holdout_persona`
- **why this case exists**: Holdout: metalinguistic use of a preference memory.
- **input**: `The word 'colour' is spelled differently in Britain.`
- **expected** (none): `The word 'colour' is spelled differently in Britain.`
- **actual** (changed): `The word 'color' is spelled differently in Britain.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #6 'color' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

## llm_only / N9_deleted_memory_inert — 1 failing

### `hold-del-02` — false_intervention

- **scenario**: `holdout_amber_deleted`
- **why this case exists**: Holdout: after deletion the memory must stop affecting output, on vocabulary the system was never tuned against.
- **input**: `Chase amber rail about the invoice.`
- **expected** (none): `Chase amber rail about the invoice.`
- **actual** (changed): `Chase Amber Rail about the invoice.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #1 'Amber Rail' (org, deleted, 0.76)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>
