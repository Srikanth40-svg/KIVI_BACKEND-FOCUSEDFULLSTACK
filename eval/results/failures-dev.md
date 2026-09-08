# Failures — dev split

177 failing case(s) out of 496 case-runs across 4 system(s).

Every failure is listed in full. Nothing is summarised away, because the point of this file is that a reviewer can see exactly what the system got wrong and why it thought it was right.

## exact / A4_brand_orthography — 4 failing

### `pos-openai-01` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: Case and joining are data, not derivable by rule. Learned as an orthographic variant, so it is meaning-preserving and needs no situational support.
- **input**: `Compare it with Open Ai and Anthropic.`
- **expected** (correct): `Compare it with OpenAI and Anthropic.`
- **actual** (unchanged): `Compare it with Open Ai and Anthropic.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: []
- **relevant memory**: #5 'OpenAI' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-openai-02` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: Case and joining are data, not derivable by rule. Learned as an orthographic variant, so it is meaning-preserving and needs no situational support.
- **input**: `The Open Ai pricing page changed again.`
- **expected** (correct): `The OpenAI pricing page changed again.`
- **actual** (unchanged): `The Open Ai pricing page changed again.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: []
- **relevant memory**: #5 'OpenAI' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-openai-03` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: Case and joining are data, not derivable by rule. Learned as an orthographic variant, so it is meaning-preserving and needs no situational support.
- **input**: `We benchmarked against Open Ai last quarter.`
- **expected** (correct): `We benchmarked against OpenAI last quarter.`
- **actual** (unchanged): `We benchmarked against Open Ai last quarter.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: []
- **relevant memory**: #5 'OpenAI' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-openai-04` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: Case and joining are data, not derivable by rule. Learned as an orthographic variant, so it is meaning-preserving and needs no situational support.
- **input**: `Open Ai published a new model card.`
- **expected** (correct): `OpenAI published a new model card.`
- **actual** (unchanged): `Open Ai published a new model card.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: []
- **relevant memory**: #5 'OpenAI' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

## exact / A5_personal_acronym — 3 failing

### `pos-epd-01` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: An internal team name. Spelled-out letters must collapse to the canonical form.
- **input**: `Send the metrics to E P D before the review.`
- **expected** (correct): `Send the metrics to EPD before the review.`
- **actual** (unchanged): `Send the metrics to E P D before the review.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: []
- **relevant memory**: #11 'EPD' (acronym, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-epd-02` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: An internal team name. Spelled-out letters must collapse to the canonical form.
- **input**: `E P D owns the quarterly report.`
- **expected** (correct): `EPD owns the quarterly report.`
- **actual** (unchanged): `E P D owns the quarterly report.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: []
- **relevant memory**: #11 'EPD' (acronym, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-epd-03` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: An internal team name. Spelled-out letters must collapse to the canonical form.
- **input**: `Ask E P D for the headcount doc.`
- **expected** (correct): `Ask EPD for the headcount doc.`
- **actual** (unchanged): `Ask E P D for the headcount doc.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: []
- **relevant memory**: #11 'EPD' (acronym, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

## exact / A6_jargon_multitoken_error — 6 failing

### `pos-jargon-01` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: A two-token mis-hearing collapsing onto a one-token term. This is why memory operates on spans rather than tokens.
- **input**: `The Cuban Eighties cluster is down again.`
- **expected** (correct): `The Kubernetes cluster is down again.`
- **actual** (unchanged): `The Cuban Eighties cluster is down again.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: []
- **relevant memory**: #4 'Kubernetes' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-jargon-02` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: A two-token mis-hearing collapsing onto a one-token term. This is why memory operates on spans rather than tokens.
- **input**: `Restart the Cuban Eighties pod.`
- **expected** (correct): `Restart the Kubernetes pod.`
- **actual** (unchanged): `Restart the Cuban Eighties pod.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: []
- **relevant memory**: #4 'Kubernetes' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-jargon-03` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: A two-token mis-hearing collapsing onto a one-token term. This is why memory operates on spans rather than tokens.
- **input**: `Our Cuban Eighties config drifted.`
- **expected** (correct): `Our Kubernetes config drifted.`
- **actual** (unchanged): `Our Cuban Eighties config drifted.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: []
- **relevant memory**: #4 'Kubernetes' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-jargon-04` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: A two-token mis-hearing collapsing onto a one-token term. This is why memory operates on spans rather than tokens.
- **input**: `The Post Grease connection is timing out.`
- **expected** (correct): `The Postgres connection is timing out.`
- **actual** (unchanged): `The Post Grease connection is timing out.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: []
- **relevant memory**: #14 'Postgres' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-jargon-05` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: A two-token mis-hearing collapsing onto a one-token term. This is why memory operates on spans rather than tokens.
- **input**: `Migrate the Post Grease schema tonight.`
- **expected** (correct): `Migrate the Postgres schema tonight.`
- **actual** (unchanged): `Migrate the Post Grease schema tonight.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: []
- **relevant memory**: #14 'Postgres' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-jargon-06` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: A two-token mis-hearing collapsing onto a one-token term. This is why memory operates on spans rather than tokens.
- **input**: `Post Grease is using too much memory.`
- **expected** (correct): `Postgres is using too much memory.`
- **actual** (unchanged): `Post Grease is using too much memory.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: []
- **relevant memory**: #14 'Postgres' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

## exact / A9_handle_identifier — 2 failing

### `pos-handle-01` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: A handle is a strict identifier with no natural-language spelling rules. The dictated description must resolve to the exact stored string.
- **input**: `DM at Aaditya underscore K about the review.`
- **expected** (correct): `DM @aaditya_k about the review.`
- **actual** (unchanged): `DM at Aaditya underscore K about the review.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: []
- **relevant memory**: #2 'Aaditya' (person, confirmed, 0.95), #7 '@aaditya_k' (handle, confirmed, 0.9), #6 'Aaditya Labs' (org, candidate, 0.4)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-handle-02` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: A handle is a strict identifier with no natural-language spelling rules. The dictated description must resolve to the exact stored string.
- **input**: `Ping at Aaditya underscore K on Slack.`
- **expected** (correct): `Ping @aaditya_k on Slack.`
- **actual** (unchanged): `Ping at Aaditya underscore K on Slack.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: []
- **relevant memory**: #2 'Aaditya' (person, confirmed, 0.95), #7 '@aaditya_k' (handle, confirmed, 0.9), #6 'Aaditya Labs' (org, candidate, 0.4)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

## exact / N12_ambiguous_competing_memories — 2 failing

### `neg-ambiguous-01` — false_intervention

- **scenario**: `seeded_ambiguous_kiwi`
- **why this case exists**: Two confirmed memories answer to this sound (the product Kivi and the client Kiwee) and nothing in the sentence separates them. With two equally good answers the honest response is to abstain and say why, not to pick the marginally higher score. Note the first sentence contains 'invoice', which weakly favours the client — weakly enough that acting on it would be a guess, so silence is still the right answer.
- **input**: `The Kiwi invoice needs reissuing.`
- **expected** (none): `The Kiwi invoice needs reissuing.`
- **actual** (changed): `The Kivi invoice needs reissuing.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: [{"span": "Kiwi", "replacement": "Kivi", "memory_id": 1}]
- **relevant memory**: #20 'Kiwee' (org, confirmed, 1.0), #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Kiwi",
      "replacement": "Kivi",
      "memory_id": 1
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-ambiguous-02` — false_intervention

- **scenario**: `seeded_ambiguous_kiwi`
- **why this case exists**: Two confirmed memories answer to this sound (the product Kivi and the client Kiwee) and nothing in the sentence separates them. With two equally good answers the honest response is to abstain and say why, not to pick the marginally higher score. Note the first sentence contains 'invoice', which weakly favours the client — weakly enough that acting on it would be a guess, so silence is still the right answer.
- **input**: `The Kiwi meeting moved to Thursday.`
- **expected** (none): `The Kiwi meeting moved to Thursday.`
- **actual** (changed): `The Kivi meeting moved to Thursday.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: [{"span": "Kiwi", "replacement": "Kivi", "memory_id": 1}]
- **relevant memory**: #20 'Kiwee' (org, confirmed, 1.0), #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Kiwi",
      "replacement": "Kivi",
      "memory_id": 1
    }
  ],
  "reason_mismatch": null
}
```

</details>

## exact / N1_homophone_ordinary_sense — 8 failing

### `neg-fruit-01` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: 'kiwi' is an ordinary English word and this sentence uses it that way. Overwriting it would corrupt text the person said correctly.
- **input**: `I ate a kiwi on the flight.`
- **expected** (none): `I ate a kiwi on the flight.`
- **actual** (changed): `I ate a Kivi on the flight.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: [{"span": "kiwi", "replacement": "Kivi", "memory_id": 1}]
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "kiwi",
      "replacement": "Kivi",
      "memory_id": 1
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-fruit-02` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: 'kiwi' is an ordinary English word and this sentence uses it that way. Overwriting it would corrupt text the person said correctly.
- **input**: `Add a kiwi to the fruit salad.`
- **expected** (none): `Add a kiwi to the fruit salad.`
- **actual** (changed): `Add a Kivi to the fruit salad.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: [{"span": "kiwi", "replacement": "Kivi", "memory_id": 1}]
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "kiwi",
      "replacement": "Kivi",
      "memory_id": 1
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-fruit-03` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: 'kiwi' is an ordinary English word and this sentence uses it that way. Overwriting it would corrupt text the person said correctly.
- **input**: `The kiwi is a bird native to New Zealand.`
- **expected** (none): `The kiwi is a bird native to New Zealand.`
- **actual** (changed): `The Kivi is a bird native to New Zealand.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: [{"span": "kiwi", "replacement": "Kivi", "memory_id": 1}]
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "kiwi",
      "replacement": "Kivi",
      "memory_id": 1
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-fruit-04` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: 'kiwi' is an ordinary English word and this sentence uses it that way. Overwriting it would corrupt text the person said correctly.
- **input**: `She packed a kiwi and an apple for lunch.`
- **expected** (none): `She packed a kiwi and an apple for lunch.`
- **actual** (changed): `She packed a Kivi and an apple for lunch.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: [{"span": "kiwi", "replacement": "Kivi", "memory_id": 1}]
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "kiwi",
      "replacement": "Kivi",
      "memory_id": 1
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-fruit-05` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: 'kiwi' is an ordinary English word and this sentence uses it that way. Overwriting it would corrupt text the person said correctly.
- **input**: `Kiwi fruit is cheaper in winter.`
- **expected** (none): `Kiwi fruit is cheaper in winter.`
- **actual** (changed): `Kivi fruit is cheaper in winter.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: [{"span": "Kiwi", "replacement": "Kivi", "memory_id": 1}]
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Kiwi",
      "replacement": "Kivi",
      "memory_id": 1
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-fruit-06` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: 'kiwi' is an ordinary English word and this sentence uses it that way. Overwriting it would corrupt text the person said correctly.
- **input**: `We saw a kiwi at the wildlife park.`
- **expected** (none): `We saw a kiwi at the wildlife park.`
- **actual** (changed): `We saw a Kivi at the wildlife park.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: [{"span": "kiwi", "replacement": "Kivi", "memory_id": 1}]
- **relevant memory**: #7 '@aaditya_k' (handle, confirmed, 0.9), #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "kiwi",
      "replacement": "Kivi",
      "memory_id": 1
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-fruit-07` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: 'kiwi' is an ordinary English word and this sentence uses it that way. Overwriting it would corrupt text the person said correctly.
- **input**: `The smoothie has banana, mango and kiwi.`
- **expected** (none): `The smoothie has banana, mango and kiwi.`
- **actual** (changed): `The smoothie has banana, mango and Kivi.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: [{"span": "kiwi", "replacement": "Kivi", "memory_id": 1}]
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "kiwi",
      "replacement": "Kivi",
      "memory_id": 1
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-fruit-08` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: 'kiwi' is an ordinary English word and this sentence uses it that way. Overwriting it would corrupt text the person said correctly.
- **input**: `Peel the kiwi before slicing it.`
- **expected** (none): `Peel the kiwi before slicing it.`
- **actual** (changed): `Peel the Kivi before slicing it.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: [{"span": "kiwi", "replacement": "Kivi", "memory_id": 1}]
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "kiwi",
      "replacement": "Kivi",
      "memory_id": 1
    }
  ],
  "reason_mismatch": null
}
```

</details>

## exact / N2_product_vs_generic_word — 6 failing

### `neg-cursor-01` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: 'Cursor' is a seeded product memory, but here the word means the caret. The correction is only wanted when the sentence is about the editor.
- **input**: `Move the cursor to the end of the line.`
- **expected** (none): `Move the cursor to the end of the line.`
- **actual** (changed): `Move the Cursor to the end of the line.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: [{"span": "cursor", "replacement": "Cursor", "memory_id": 10}]
- **relevant memory**: #10 'Cursor' (org, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "cursor",
      "replacement": "Cursor",
      "memory_id": 10
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-cursor-02` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: 'Cursor' is a seeded product memory, but here the word means the caret. The correction is only wanted when the sentence is about the editor.
- **input**: `The cursor keeps jumping while I type.`
- **expected** (none): `The cursor keeps jumping while I type.`
- **actual** (changed): `The Cursor keeps jumping while I type.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: [{"span": "cursor", "replacement": "Cursor", "memory_id": 10}]
- **relevant memory**: #10 'Cursor' (org, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "cursor",
      "replacement": "Cursor",
      "memory_id": 10
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-cursor-03` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: 'Cursor' is a seeded product memory, but here the word means the caret. The correction is only wanted when the sentence is about the editor.
- **input**: `Put the cursor in the search box.`
- **expected** (none): `Put the cursor in the search box.`
- **actual** (changed): `Put the Cursor in the search box.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: [{"span": "cursor", "replacement": "Cursor", "memory_id": 10}]
- **relevant memory**: #10 'Cursor' (org, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "cursor",
      "replacement": "Cursor",
      "memory_id": 10
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-cursor-04` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: 'Cursor' is a seeded product memory, but here the word means the caret. The correction is only wanted when the sentence is about the editor.
- **input**: `My cursor disappeared after the update.`
- **expected** (none): `My cursor disappeared after the update.`
- **actual** (changed): `My Cursor disappeared after the update.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: [{"span": "cursor", "replacement": "Cursor", "memory_id": 10}]
- **relevant memory**: #10 'Cursor' (org, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "cursor",
      "replacement": "Cursor",
      "memory_id": 10
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-cursor-05` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: 'Cursor' is a seeded product memory, but here the word means the caret. The correction is only wanted when the sentence is about the editor.
- **input**: `Hold shift and drag the cursor.`
- **expected** (none): `Hold shift and drag the cursor.`
- **actual** (changed): `Hold shift and drag the Cursor.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: [{"span": "cursor", "replacement": "Cursor", "memory_id": 10}]
- **relevant memory**: #10 'Cursor' (org, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "cursor",
      "replacement": "Cursor",
      "memory_id": 10
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-cursor-06` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: 'Cursor' is a seeded product memory, but here the word means the caret. The correction is only wanted when the sentence is about the editor.
- **input**: `The text cursor is blinking too fast.`
- **expected** (none): `The text cursor is blinking too fast.`
- **actual** (changed): `The text Cursor is blinking too fast.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: [{"span": "cursor", "replacement": "Cursor", "memory_id": 10}]
- **relevant memory**: #10 'Cursor' (org, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "cursor",
      "replacement": "Cursor",
      "memory_id": 10
    }
  ],
  "reason_mismatch": null
}
```

</details>

## exact / N4_different_real_person — 4 failing

### `neg-otherperson-01` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: Two colleagues exist: Aaditya, and Aditya Ghosh. 'Aditya' is simultaneously a wrong form of one and the correct name of the other, so the wider name must protect the token inside it.
- **input**: `Aditya Ghosh approved the budget.`
- **expected** (none): `Aditya Ghosh approved the budget.`
- **actual** (changed): `Aaditya Ghosh approved the budget.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: [{"span": "Aditya", "replacement": "Aaditya", "memory_id": 2}]
- **relevant memory**: #2 'Aaditya' (person, confirmed, 0.95), #13 'Ghosh' (person, confirmed, 0.9), #12 'Aditya Ghosh' (person, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Aditya",
      "replacement": "Aaditya",
      "memory_id": 2
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-otherperson-02` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: Two colleagues exist: Aaditya, and Aditya Ghosh. 'Aditya' is simultaneously a wrong form of one and the correct name of the other, so the wider name must protect the token inside it.
- **input**: `I met Aditya Ghosh at the offsite.`
- **expected** (none): `I met Aditya Ghosh at the offsite.`
- **actual** (changed): `I met Aaditya Ghosh at the offsite.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: [{"span": "Aditya", "replacement": "Aaditya", "memory_id": 2}]
- **relevant memory**: #2 'Aaditya' (person, confirmed, 0.95), #13 'Ghosh' (person, confirmed, 0.9), #7 '@aaditya_k' (handle, confirmed, 0.9), #12 'Aditya Ghosh' (person, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Aditya",
      "replacement": "Aaditya",
      "memory_id": 2
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-otherperson-03` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: Two colleagues exist: Aaditya, and Aditya Ghosh. 'Aditya' is simultaneously a wrong form of one and the correct name of the other, so the wider name must protect the token inside it.
- **input**: `Aditya Ghosh is my manager.`
- **expected** (none): `Aditya Ghosh is my manager.`
- **actual** (changed): `Aaditya Ghosh is my manager.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: [{"span": "Aditya", "replacement": "Aaditya", "memory_id": 2}]
- **relevant memory**: #2 'Aaditya' (person, confirmed, 0.95), #13 'Ghosh' (person, confirmed, 0.9), #12 'Aditya Ghosh' (person, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Aditya",
      "replacement": "Aaditya",
      "memory_id": 2
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-otherperson-04` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: Two colleagues exist: Aaditya, and Aditya Ghosh. 'Aditya' is simultaneously a wrong form of one and the correct name of the other, so the wider name must protect the token inside it.
- **input**: `Forward the deck to Aditya Ghosh.`
- **expected** (none): `Forward the deck to Aditya Ghosh.`
- **actual** (changed): `Forward the deck to Aaditya Ghosh.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: [{"span": "Aditya", "replacement": "Aaditya", "memory_id": 2}]
- **relevant memory**: #2 'Aaditya' (person, confirmed, 0.95), #13 'Ghosh' (person, confirmed, 0.9), #12 'Aditya Ghosh' (person, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Aditya",
      "replacement": "Aaditya",
      "memory_id": 2
    }
  ],
  "reason_mismatch": null
}
```

</details>

## exact / N7_metalinguistic_mention — 4 failing

### `neg-meta-01` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: The token is the object of the sentence, not a reference to the thing. Correcting it would change what the sentence is about.
- **input**: `The word 'kiwi' has four letters.`
- **expected** (none): `The word 'kiwi' has four letters.`
- **actual** (changed): `The word 'Kivi' has four letters.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: [{"span": "kiwi", "replacement": "Kivi", "memory_id": 1}]
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "kiwi",
      "replacement": "Kivi",
      "memory_id": 1
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-meta-02` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: The token is the object of the sentence, not a reference to the thing. Correcting it would change what the sentence is about.
- **input**: `How do you spell 'kiwi' in the plural?`
- **expected** (none): `How do you spell 'kiwi' in the plural?`
- **actual** (changed): `How do you spell 'Kivi' in the plural?`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: [{"span": "kiwi", "replacement": "Kivi", "memory_id": 1}]
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "kiwi",
      "replacement": "Kivi",
      "memory_id": 1
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-meta-03` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: The token is the object of the sentence, not a reference to the thing. Correcting it would change what the sentence is about.
- **input**: `The word 'cursor' is oddly chosen for an editor.`
- **expected** (none): `The word 'cursor' is oddly chosen for an editor.`
- **actual** (changed): `The word 'Cursor' is oddly chosen for an editor.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: [{"span": "cursor", "replacement": "Cursor", "memory_id": 10}]
- **relevant memory**: #10 'Cursor' (org, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "cursor",
      "replacement": "Cursor",
      "memory_id": 10
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-meta-04` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: The token is the object of the sentence, not a reference to the thing. Correcting it would change what the sentence is about.
- **input**: `The word 'grey' is spelled differently in America.`
- **expected** (none): `The word 'grey' is spelled differently in America.`
- **actual** (changed): `The word 'gray' is spelled differently in America.`
- **reason codes**: `BASELINE_EXACT`
- **system's reasoning**: [{"span": "grey", "replacement": "gray", "memory_id": 8}]
- **relevant memory**: #8 'gray' (preference, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "grey",
      "replacement": "gray",
      "memory_id": 8
    }
  ],
  "reason_mismatch": null
}
```

</details>

## fuzzy / A10_morphology_preserved — 3 failing

### `pos-morph-02` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: The possessive must survive the substitution: the canonical stem is applied and the inflection is re-attached, rather than the whole token being replaced.
- **input**: `The Kiwi's release notes are stale.`
- **expected** (correct): `The Kivi's release notes are stale.`
- **actual** (changed): `The Kivi's release notes gray stale.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Kiwi's", "replacement": "Kivi's", "memory_id": 1}, {"span": "are", "replacement": "gray", "memory_id": 8}]
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Kiwi's",
      "replacement": "Kivi's",
      "memory_id": 1
    },
    {
      "span": "are",
      "replacement": "gray",
      "memory_id": 8
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `pos-morph-03` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: The possessive must survive the substitution: the canonical stem is applied and the inflection is re-attached, rather than the whole token being replaced.
- **input**: `Aditya's review is still pending.`
- **expected** (correct): `Aaditya's review is still pending.`
- **actual** (changed): `Aaditya's review is still OpenAI.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Aditya's", "replacement": "Aaditya's", "memory_id": 2}, {"span": "pending", "replacement": "OpenAI", "memory_id": 5}]
- **relevant memory**: #2 'Aaditya' (person, confirmed, 0.95), #12 'Aditya Ghosh' (person, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Aditya's",
      "replacement": "Aaditya's",
      "memory_id": 2
    },
    {
      "span": "pending",
      "replacement": "OpenAI",
      "memory_id": 5
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `pos-morph-04` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: The possessive must survive the substitution: the canonical stem is applied and the inflection is re-attached, rather than the whole token being replaced.
- **input**: `I borrowed Aditya's laptop for the demo.`
- **expected** (correct): `I borrowed Aaditya's laptop for the demo.`
- **actual** (changed): `I borrowed Aaditya's laptop Foods the demo.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Aditya's", "replacement": "Aaditya's", "memory_id": 2}, {"span": "for", "replacement": "Foods", "memory_id": 18}]
- **relevant memory**: #2 'Aaditya' (person, confirmed, 0.95), #12 'Aditya Ghosh' (person, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Aditya's",
      "replacement": "Aaditya's",
      "memory_id": 2
    },
    {
      "span": "for",
      "replacement": "Foods",
      "memory_id": 18
    }
  ],
  "reason_mismatch": null
}
```

</details>

## fuzzy / A11_spelling_preference — 3 failing

### `pos-pref-01` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: Both spellings are correct English. There is no global right answer, only this person's. Meaning-preserving, so it applies without needing context.
- **input**: `Use the grey background for the dashboard.`
- **expected** (correct): `Use the gray background for the dashboard.`
- **actual** (changed): `Sumeet the gray background Foods the dashboard.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Use", "replacement": "Sumeet", "memory_id": 15}, {"span": "grey", "replacement": "gray", "memory_id": 8}, {"span": "for", "replacement": "Foods", "memory_id": 18}]
- **relevant memory**: #8 'gray' (preference, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Use",
      "replacement": "Sumeet",
      "memory_id": 15
    },
    {
      "span": "grey",
      "replacement": "gray",
      "memory_id": 8
    },
    {
      "span": "for",
      "replacement": "Foods",
      "memory_id": 18
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `pos-pref-02` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: Both spellings are correct English. There is no global right answer, only this person's. Meaning-preserving, so it applies without needing context.
- **input**: `The grey border looks too heavy.`
- **expected** (correct): `The gray border looks too heavy.`
- **actual** (changed): `The gray border Foods too heavy.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "grey", "replacement": "gray", "memory_id": 8}, {"span": "looks", "replacement": "Foods", "memory_id": 18}]
- **relevant memory**: #8 'gray' (preference, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "grey",
      "replacement": "gray",
      "memory_id": 8
    },
    {
      "span": "looks",
      "replacement": "Foods",
      "memory_id": 18
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `pos-pref-04` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: Both spellings are correct English. There is no global right answer, only this person's. Meaning-preserving, so it applies without needing context.
- **input**: `A grey banner appears on first load.`
- **expected** (correct): `A gray banner appears on first load.`
- **actual** (changed): `A gray Bengaluru appears on first load.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "grey", "replacement": "gray", "memory_id": 8}, {"span": "banner", "replacement": "Bengaluru", "memory_id": 9}]
- **relevant memory**: #8 'gray' (preference, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "grey",
      "replacement": "gray",
      "memory_id": 8
    },
    {
      "span": "banner",
      "replacement": "Bengaluru",
      "memory_id": 9
    }
  ],
  "reason_mismatch": null
}
```

</details>

## fuzzy / A12_transliteration_preference — 1 failing

### `pos-place-03` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: Same city, two accepted romanisations. The person's choice is the only thing that decides it.
- **input**: `Our Bangalore team handles support.`
- **expected** (correct): `Our Bengaluru team handles support.`
- **actual** (changed): `Our Bengaluru team handles Sumeet.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Bangalore", "replacement": "Bengaluru", "memory_id": 9}, {"span": "support", "replacement": "Sumeet", "memory_id": 15}]
- **relevant memory**: #9 'Bengaluru' (place, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Bangalore",
      "replacement": "Bengaluru",
      "memory_id": 9
    },
    {
      "span": "support",
      "replacement": "Sumeet",
      "memory_id": 15
    }
  ],
  "reason_mismatch": null
}
```

</details>

## fuzzy / A1_indic_phonetic_variation — 4 failing

### `pos-indic-01` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: v/w and long-vowel alternation dominate Indian-English name transcription and are the reason the phonetic encoder is tuned for it rather than using Soundex.
- **input**: `Wishal owns the ASR pipeline.`
- **expected** (correct): `Vishal owns the ASR pipeline.`
- **actual** (changed): `Vishal owns the SARVAM pipeline.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Wishal", "replacement": "Vishal", "memory_id": 16}, {"span": "ASR", "replacement": "SARVAM", "memory_id": 3}]
- **relevant memory**: #16 'Vishal' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Wishal",
      "replacement": "Vishal",
      "memory_id": 16
    },
    {
      "span": "ASR",
      "replacement": "SARVAM",
      "memory_id": 3
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `pos-indic-03` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: v/w and long-vowel alternation dominate Indian-English name transcription and are the reason the phonetic encoder is tuned for it rather than using Soundex.
- **input**: `Wishal is reviewing the benchmark.`
- **expected** (correct): `Vishal is reviewing the benchmark.`
- **actual** (changed): `Vishal is reviewing the Bengaluru.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Wishal", "replacement": "Vishal", "memory_id": 16}, {"span": "benchmark", "replacement": "Bengaluru", "memory_id": 9}]
- **relevant memory**: #16 'Vishal' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Wishal",
      "replacement": "Vishal",
      "memory_id": 16
    },
    {
      "span": "benchmark",
      "replacement": "Bengaluru",
      "memory_id": 9
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `pos-indic-05` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: v/w and long-vowel alternation dominate Indian-English name transcription and are the reason the phonetic encoder is tuned for it rather than using Soundex.
- **input**: `I sent Sumit the eval results.`
- **expected** (correct): `I sent Sumeet the eval results.`
- **actual** (changed): `I Sumeet Sumeet the Vishal results.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "sent", "replacement": "Sumeet", "memory_id": 15}, {"span": "Sumit", "replacement": "Sumeet", "memory_id": 15}, {"span": "eval", "replacement": "Vishal", "memory_id": 16}]
- **relevant memory**: #15 'Sumeet' (term, confirmed, 0.95)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "sent",
      "replacement": "Sumeet",
      "memory_id": 15
    },
    {
      "span": "Sumit",
      "replacement": "Sumeet",
      "memory_id": 15
    },
    {
      "span": "eval",
      "replacement": "Vishal",
      "memory_id": 16
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `pos-indic-06` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: v/w and long-vowel alternation dominate Indian-English name transcription and are the reason the phonetic encoder is tuned for it rather than using Soundex.
- **input**: `Sumit found the off-by-one bug.`
- **expected** (correct): `Sumeet found the off-by-one bug.`
- **actual** (changed): `Sumeet Foods the off-by-one bug.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Sumit", "replacement": "Sumeet", "memory_id": 15}, {"span": "found", "replacement": "Foods", "memory_id": 18}]
- **relevant memory**: #15 'Sumeet' (term, confirmed, 0.95)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Sumit",
      "replacement": "Sumeet",
      "memory_id": 15
    },
    {
      "span": "found",
      "replacement": "Foods",
      "memory_id": 18
    }
  ],
  "reason_mismatch": null
}
```

</details>

## fuzzy / A1_product_heard_as_ordinary_word — 9 failing

### `pos-kivi-01` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: Kivi is the seeded product memory and the sentence is unambiguously about software, so the correction is the useful one.
- **input**: `Ship the Kiwi update on Friday.`
- **expected** (correct): `Ship the Kivi update on Friday.`
- **actual** (changed): `Ship the Kivi update on gray.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Kiwi", "replacement": "Kivi", "memory_id": 1}, {"span": "Friday", "replacement": "gray", "memory_id": 8}]
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Kiwi",
      "replacement": "Kivi",
      "memory_id": 1
    },
    {
      "span": "Friday",
      "replacement": "gray",
      "memory_id": 8
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `pos-kivi-02` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: Kivi is the seeded product memory and the sentence is unambiguously about software, so the correction is the useful one.
- **input**: `The Kiwi service is down for everyone.`
- **expected** (correct): `The Kivi service is down for everyone.`
- **actual** (changed): `The Kivi service is down Foods everyone.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Kiwi", "replacement": "Kivi", "memory_id": 1}, {"span": "for", "replacement": "Foods", "memory_id": 18}]
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Kiwi",
      "replacement": "Kivi",
      "memory_id": 1
    },
    {
      "span": "for",
      "replacement": "Foods",
      "memory_id": 18
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `pos-kivi-04` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: Kivi is the seeded product memory and the sentence is unambiguously about software, so the correction is the useful one.
- **input**: `Can you review the Kiwi PR before standup?`
- **expected** (correct): `Can you review the Kivi PR before standup?`
- **actual** (changed): `Kubernetes you review the Kivi PR Bengaluru standup?`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Can", "replacement": "Kubernetes", "memory_id": 4}, {"span": "Kiwi", "replacement": "Kivi", "memory_id": 1}, {"span": "before", "replacement": "Bengaluru", "memory_id": 9}]
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Can",
      "replacement": "Kubernetes",
      "memory_id": 4
    },
    {
      "span": "Kiwi",
      "replacement": "Kivi",
      "memory_id": 1
    },
    {
      "span": "before",
      "replacement": "Bengaluru",
      "memory_id": 9
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `pos-kivi-05` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: Kivi is the seeded product memory and the sentence is unambiguously about software, so the correction is the useful one.
- **input**: `We deployed Kiwi to staging last night.`
- **expected** (correct): `We deployed Kivi to staging last night.`
- **actual** (changed): `We deployed Kivi to staging last Kubernetes.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Kiwi", "replacement": "Kivi", "memory_id": 1}, {"span": "night", "replacement": "Kubernetes", "memory_id": 4}]
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Kiwi",
      "replacement": "Kivi",
      "memory_id": 1
    },
    {
      "span": "night",
      "replacement": "Kubernetes",
      "memory_id": 4
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `pos-kivi-06` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: Kivi is the seeded product memory and the sentence is unambiguously about software, so the correction is the useful one.
- **input**: `The Kiwi dashboard needs a redesign.`
- **expected** (correct): `The Kivi dashboard needs a redesign.`
- **actual** (changed): `The Kivi dashboard EPDs a redesign.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Kiwi", "replacement": "Kivi", "memory_id": 1}, {"span": "needs", "replacement": "EPDs", "memory_id": 11}]
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Kiwi",
      "replacement": "Kivi",
      "memory_id": 1
    },
    {
      "span": "needs",
      "replacement": "EPDs",
      "memory_id": 11
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `pos-kivi-07` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: Kivi is the seeded product memory and the sentence is unambiguously about software, so the correction is the useful one.
- **input**: `Add telemetry to the Kiwi app.`
- **expected** (correct): `Add telemetry to the Kivi app.`
- **actual** (changed): `Aaditya telemetry to the Kivi app.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Add", "replacement": "Aaditya", "memory_id": 2}, {"span": "Kiwi", "replacement": "Kivi", "memory_id": 1}]
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Add",
      "replacement": "Aaditya",
      "memory_id": 2
    },
    {
      "span": "Kiwi",
      "replacement": "Kivi",
      "memory_id": 1
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `pos-kivi-08` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: Kivi is the seeded product memory and the sentence is unambiguously about software, so the correction is the useful one.
- **input**: `Kiwi users are reporting slow dictation.`
- **expected** (correct): `Kivi users are reporting slow dictation.`
- **actual** (changed): `Kivi users gray reporting slow dictation.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Kiwi", "replacement": "Kivi", "memory_id": 1}, {"span": "are", "replacement": "gray", "memory_id": 8}]
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Kiwi",
      "replacement": "Kivi",
      "memory_id": 1
    },
    {
      "span": "are",
      "replacement": "gray",
      "memory_id": 8
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `pos-kivi-10` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: Kivi is the seeded product memory and the sentence is unambiguously about software, so the correction is the useful one.
- **input**: `Let's demo Kiwi to the whole team.`
- **expected** (correct): `Let's demo Kivi to the whole team.`
- **actual** (changed): `Let's demo Kivi to the Vishal team.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Kiwi", "replacement": "Kivi", "memory_id": 1}, {"span": "whole", "replacement": "Vishal", "memory_id": 16}]
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Kiwi",
      "replacement": "Kivi",
      "memory_id": 1
    },
    {
      "span": "whole",
      "replacement": "Vishal",
      "memory_id": 16
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `pos-kivi-12` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: Kivi is the seeded product memory and the sentence is unambiguously about software, so the correction is the useful one.
- **input**: `File a bug against Kiwi for the crash.`
- **expected** (correct): `File a bug against Kivi for the crash.`
- **actual** (changed): `File a bug Aaditya Kivi Foods the Cursor.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "against", "replacement": "Aaditya", "memory_id": 2}, {"span": "Kiwi", "replacement": "Kivi", "memory_id": 1}, {"span": "for", "replacement": "Foods", "memory_id": 18}, {"span": "crash", "replacement": "Cursor", "memory_id": 10}]
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "against",
      "replacement": "Aaditya",
      "memory_id": 2
    },
    {
      "span": "Kiwi",
      "replacement": "Kivi",
      "memory_id": 1
    },
    {
      "span": "for",
      "replacement": "Foods",
      "memory_id": 18
    },
    {
      "span": "crash",
      "replacement": "Cursor",
      "memory_id": 10
    }
  ],
  "reason_mismatch": null
}
```

</details>

## fuzzy / A2_person_romanisation_preference — 4 failing

### `pos-aaditya-02` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: Both spellings are valid English romanisations, so no general dictionary can resolve this. Only a memory of THIS person's preference can.
- **input**: `I told Aditya about the outage.`
- **expected** (correct): `I told Aaditya about the outage.`
- **actual** (changed): `I told Aaditya about the Postgres.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Aditya", "replacement": "Aaditya", "memory_id": 2}, {"span": "outage", "replacement": "Postgres", "memory_id": 14}]
- **relevant memory**: #2 'Aaditya' (person, confirmed, 0.95), #12 'Aditya Ghosh' (person, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Aditya",
      "replacement": "Aaditya",
      "memory_id": 2
    },
    {
      "span": "outage",
      "replacement": "Postgres",
      "memory_id": 14
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `pos-aaditya-05` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: Both spellings are valid English romanisations, so no general dictionary can resolve this. Only a memory of THIS person's preference can.
- **input**: `Email Aditya the latency numbers.`
- **expected** (correct): `Email Aaditya the latency numbers.`
- **actual** (changed): `Email Aaditya the latency Kubernetes.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Aditya", "replacement": "Aaditya", "memory_id": 2}, {"span": "numbers", "replacement": "Kubernetes", "memory_id": 4}]
- **relevant memory**: #2 'Aaditya' (person, confirmed, 0.95), #12 'Aditya Ghosh' (person, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Aditya",
      "replacement": "Aaditya",
      "memory_id": 2
    },
    {
      "span": "numbers",
      "replacement": "Kubernetes",
      "memory_id": 4
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `pos-aaditya-07` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: Both spellings are valid English romanisations, so no general dictionary can resolve this. Only a memory of THIS person's preference can.
- **input**: `Thanks to Aditya for the quick fix.`
- **expected** (correct): `Thanks to Aaditya for the quick fix.`
- **actual** (changed): `Thanks to Aaditya Foods the quick fix.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Aditya", "replacement": "Aaditya", "memory_id": 2}, {"span": "for", "replacement": "Foods", "memory_id": 18}]
- **relevant memory**: #2 'Aaditya' (person, confirmed, 0.95), #12 'Aditya Ghosh' (person, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Aditya",
      "replacement": "Aaditya",
      "memory_id": 2
    },
    {
      "span": "for",
      "replacement": "Foods",
      "memory_id": 18
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `pos-aaditya-08` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: Both spellings are valid English romanisations, so no general dictionary can resolve this. Only a memory of THIS person's preference can.
- **input**: `cc Aditya on the vendor reply.`
- **expected** (correct): `cc Aaditya on the vendor reply.`
- **actual** (changed): `cc Aaditya on the vendor gray.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Aditya", "replacement": "Aaditya", "memory_id": 2}, {"span": "reply", "replacement": "gray", "memory_id": 8}]
- **relevant memory**: #2 'Aaditya' (person, confirmed, 0.95), #12 'Aditya Ghosh' (person, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Aditya",
      "replacement": "Aaditya",
      "memory_id": 2
    },
    {
      "span": "reply",
      "replacement": "gray",
      "memory_id": 8
    }
  ],
  "reason_mismatch": null
}
```

</details>

## fuzzy / A4_brand_orthography — 4 failing

### `pos-openai-01` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: Case and joining are data, not derivable by rule. Learned as an orthographic variant, so it is meaning-preserving and needs no situational support.
- **input**: `Compare it with Open Ai and Anthropic.`
- **expected** (correct): `Compare it with OpenAI and Anthropic.`
- **actual** (changed): `Compare it Vishal OpenAI Ai and Anthropic.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "with", "replacement": "Vishal", "memory_id": 16}, {"span": "Open", "replacement": "OpenAI", "memory_id": 5}]
- **relevant memory**: #5 'OpenAI' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "with",
      "replacement": "Vishal",
      "memory_id": 16
    },
    {
      "span": "Open",
      "replacement": "OpenAI",
      "memory_id": 5
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `pos-openai-02` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: Case and joining are data, not derivable by rule. Learned as an orthographic variant, so it is meaning-preserving and needs no situational support.
- **input**: `The Open Ai pricing page changed again.`
- **expected** (correct): `The OpenAI pricing page changed again.`
- **actual** (changed): `The OpenAI Ai pricing Postgres changed again.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Open", "replacement": "OpenAI", "memory_id": 5}, {"span": "page", "replacement": "Postgres", "memory_id": 14}]
- **relevant memory**: #5 'OpenAI' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Open",
      "replacement": "OpenAI",
      "memory_id": 5
    },
    {
      "span": "page",
      "replacement": "Postgres",
      "memory_id": 14
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `pos-openai-03` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: Case and joining are data, not derivable by rule. Learned as an orthographic variant, so it is meaning-preserving and needs no situational support.
- **input**: `We benchmarked against Open Ai last quarter.`
- **expected** (correct): `We benchmarked against OpenAI last quarter.`
- **actual** (changed): `We Bengaluru Aaditya OpenAI Ai last quarter.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "benchmarked", "replacement": "Bengaluru", "memory_id": 9}, {"span": "against", "replacement": "Aaditya", "memory_id": 2}, {"span": "Open", "replacement": "OpenAI", "memory_id": 5}]
- **relevant memory**: #5 'OpenAI' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "benchmarked",
      "replacement": "Bengaluru",
      "memory_id": 9
    },
    {
      "span": "against",
      "replacement": "Aaditya",
      "memory_id": 2
    },
    {
      "span": "Open",
      "replacement": "OpenAI",
      "memory_id": 5
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `pos-openai-04` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: Case and joining are data, not derivable by rule. Learned as an orthographic variant, so it is meaning-preserving and needs no situational support.
- **input**: `Open Ai published a new model card.`
- **expected** (correct): `OpenAI published a new model card.`
- **actual** (changed): `OpenAI Ai published a new model card.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Open", "replacement": "OpenAI", "memory_id": 5}]
- **relevant memory**: #5 'OpenAI' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Open",
      "replacement": "OpenAI",
      "memory_id": 5
    }
  ],
  "reason_mismatch": null
}
```

</details>

## fuzzy / A5_personal_acronym — 3 failing

### `pos-epd-01` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: An internal team name. Spelled-out letters must collapse to the canonical form.
- **input**: `Send the metrics to E P D before the review.`
- **expected** (correct): `Send the metrics to EPD before the review.`
- **actual** (changed): `EPD the metrics to E P D Bengaluru the review.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Send", "replacement": "EPD", "memory_id": 11}, {"span": "before", "replacement": "Bengaluru", "memory_id": 9}]
- **relevant memory**: #11 'EPD' (acronym, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Send",
      "replacement": "EPD",
      "memory_id": 11
    },
    {
      "span": "before",
      "replacement": "Bengaluru",
      "memory_id": 9
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `pos-epd-02` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: An internal team name. Spelled-out letters must collapse to the canonical form.
- **input**: `E P D owns the quarterly report.`
- **expected** (correct): `EPD owns the quarterly report.`
- **actual** (unchanged): `E P D owns the quarterly report.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: []
- **relevant memory**: #11 'EPD' (acronym, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-epd-03` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: An internal team name. Spelled-out letters must collapse to the canonical form.
- **input**: `Ask E P D for the headcount doc.`
- **expected** (correct): `Ask EPD for the headcount doc.`
- **actual** (changed): `Ask E P D Foods the headcount doc.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "for", "replacement": "Foods", "memory_id": 18}]
- **relevant memory**: #11 'EPD' (acronym, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "for",
      "replacement": "Foods",
      "memory_id": 18
    }
  ],
  "reason_mismatch": null
}
```

</details>

## fuzzy / A6_jargon_multitoken_error — 6 failing

### `pos-jargon-01` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: A two-token mis-hearing collapsing onto a one-token term. This is why memory operates on spans rather than tokens.
- **input**: `The Cuban Eighties cluster is down again.`
- **expected** (correct): `The Kubernetes cluster is down again.`
- **actual** (changed): `The Kubernetes Kubernetes Cursor is down again.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Cuban", "replacement": "Kubernetes", "memory_id": 4}, {"span": "Eighties", "replacement": "Kubernetes", "memory_id": 4}, {"span": "cluster", "replacement": "Cursor", "memory_id": 10}]
- **relevant memory**: #4 'Kubernetes' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Cuban",
      "replacement": "Kubernetes",
      "memory_id": 4
    },
    {
      "span": "Eighties",
      "replacement": "Kubernetes",
      "memory_id": 4
    },
    {
      "span": "cluster",
      "replacement": "Cursor",
      "memory_id": 10
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `pos-jargon-02` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: A two-token mis-hearing collapsing onto a one-token term. This is why memory operates on spans rather than tokens.
- **input**: `Restart the Cuban Eighties pod.`
- **expected** (correct): `Restart the Kubernetes pod.`
- **actual** (changed): `Restart the Kubernetes Kubernetes pod.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Cuban", "replacement": "Kubernetes", "memory_id": 4}, {"span": "Eighties", "replacement": "Kubernetes", "memory_id": 4}]
- **relevant memory**: #4 'Kubernetes' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Cuban",
      "replacement": "Kubernetes",
      "memory_id": 4
    },
    {
      "span": "Eighties",
      "replacement": "Kubernetes",
      "memory_id": 4
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `pos-jargon-03` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: A two-token mis-hearing collapsing onto a one-token term. This is why memory operates on spans rather than tokens.
- **input**: `Our Cuban Eighties config drifted.`
- **expected** (correct): `Our Kubernetes config drifted.`
- **actual** (changed): `Our Kubernetes Kubernetes config drifted.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Cuban", "replacement": "Kubernetes", "memory_id": 4}, {"span": "Eighties", "replacement": "Kubernetes", "memory_id": 4}]
- **relevant memory**: #4 'Kubernetes' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Cuban",
      "replacement": "Kubernetes",
      "memory_id": 4
    },
    {
      "span": "Eighties",
      "replacement": "Kubernetes",
      "memory_id": 4
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `pos-jargon-04` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: A two-token mis-hearing collapsing onto a one-token term. This is why memory operates on spans rather than tokens.
- **input**: `The Post Grease connection is timing out.`
- **expected** (correct): `The Postgres connection is timing out.`
- **actual** (changed): `The Postgres gray connection is timing out.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Post", "replacement": "Postgres", "memory_id": 14}, {"span": "Grease", "replacement": "gray", "memory_id": 8}]
- **relevant memory**: #14 'Postgres' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Post",
      "replacement": "Postgres",
      "memory_id": 14
    },
    {
      "span": "Grease",
      "replacement": "gray",
      "memory_id": 8
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `pos-jargon-05` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: A two-token mis-hearing collapsing onto a one-token term. This is why memory operates on spans rather than tokens.
- **input**: `Migrate the Post Grease schema tonight.`
- **expected** (correct): `Migrate the Postgres schema tonight.`
- **actual** (changed): `gray the Postgres gray schema tonight.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Migrate", "replacement": "gray", "memory_id": 8}, {"span": "Post", "replacement": "Postgres", "memory_id": 14}, {"span": "Grease", "replacement": "gray", "memory_id": 8}]
- **relevant memory**: #14 'Postgres' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Migrate",
      "replacement": "gray",
      "memory_id": 8
    },
    {
      "span": "Post",
      "replacement": "Postgres",
      "memory_id": 14
    },
    {
      "span": "Grease",
      "replacement": "gray",
      "memory_id": 8
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `pos-jargon-06` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: A two-token mis-hearing collapsing onto a one-token term. This is why memory operates on spans rather than tokens.
- **input**: `Post Grease is using too much memory.`
- **expected** (correct): `Postgres is using too much memory.`
- **actual** (changed): `Postgres gray is using too much memory.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Post", "replacement": "Postgres", "memory_id": 14}, {"span": "Grease", "replacement": "gray", "memory_id": 8}]
- **relevant memory**: #14 'Postgres' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Post",
      "replacement": "Postgres",
      "memory_id": 14
    },
    {
      "span": "Grease",
      "replacement": "gray",
      "memory_id": 8
    }
  ],
  "reason_mismatch": null
}
```

</details>

## fuzzy / A9_handle_identifier — 2 failing

### `pos-handle-01` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: A handle is a strict identifier with no natural-language spelling rules. The dictated description must resolve to the exact stored string.
- **input**: `DM at Aaditya underscore K about the review.`
- **expected** (correct): `DM @aaditya_k about the review.`
- **actual** (changed): `DM at Aaditya @aaditya_k K about the review.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "underscore", "replacement": "@aaditya_k", "memory_id": 7}]
- **relevant memory**: #2 'Aaditya' (person, confirmed, 0.95), #7 '@aaditya_k' (handle, confirmed, 0.9), #6 'Aaditya Labs' (org, candidate, 0.4)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "underscore",
      "replacement": "@aaditya_k",
      "memory_id": 7
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `pos-handle-02` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: A handle is a strict identifier with no natural-language spelling rules. The dictated description must resolve to the exact stored string.
- **input**: `Ping at Aaditya underscore K on Slack.`
- **expected** (correct): `Ping @aaditya_k on Slack.`
- **actual** (changed): `Ping at Aaditya @aaditya_k K on Slack.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "underscore", "replacement": "@aaditya_k", "memory_id": 7}]
- **relevant memory**: #2 'Aaditya' (person, confirmed, 0.95), #7 '@aaditya_k' (handle, confirmed, 0.9), #6 'Aaditya Labs' (org, candidate, 0.4)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "underscore",
      "replacement": "@aaditya_k",
      "memory_id": 7
    }
  ],
  "reason_mismatch": null
}
```

</details>

## fuzzy / N10_superseded_memory_updated — 1 failing

### `pos-superseded-02` — acted_but_wrong_text

- **scenario**: `seeded_sumeet_superseded`
- **why this case exists**: Supersession must hold across contexts, not just the sentence it happened in.
- **input**: `I sent Sumeet the eval results.`
- **expected** (correct): `I sent Sumit the eval results.`
- **actual** (changed): `I Sumit Sumit the Vishal results.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "sent", "replacement": "Sumit", "memory_id": 20}, {"span": "Sumeet", "replacement": "Sumit", "memory_id": 20}, {"span": "eval", "replacement": "Vishal", "memory_id": 16}]
- **relevant memory**: #20 'Sumit' (term, confirmed, 1.0), #15 'Sumeet' (term, superseded, 0.95)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "sent",
      "replacement": "Sumit",
      "memory_id": 20
    },
    {
      "span": "Sumeet",
      "replacement": "Sumit",
      "memory_id": 20
    },
    {
      "span": "eval",
      "replacement": "Vishal",
      "memory_id": 16
    }
  ],
  "reason_mismatch": null
}
```

</details>

## fuzzy / N11_candidate_memory_inert — 2 failing

### `neg-candidate-01` — false_intervention

- **scenario**: `seeded_kivi_candidate`
- **why this case exists**: Confidence policy: a candidate memory is visible but must not change text.
- **input**: `Ship the Kiwi update on Friday.`
- **expected** (none): `Ship the Kiwi update on Friday.`
- **actual** (changed): `Ship the Kiwi update on gray.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Friday", "replacement": "gray", "memory_id": 8}]
- **relevant memory**: #1 'Kivi' (product, candidate, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Friday",
      "replacement": "gray",
      "memory_id": 8
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-candidate-02` — false_intervention

- **scenario**: `seeded_kivi_candidate`
- **why this case exists**: Confidence policy: weak evidence stays inert regardless of how supportive the context is.
- **input**: `The Kiwi dashboard needs a redesign.`
- **expected** (none): `The Kiwi dashboard needs a redesign.`
- **actual** (changed): `The Kiwi dashboard EPDs a redesign.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "needs", "replacement": "EPDs", "memory_id": 11}]
- **relevant memory**: #1 'Kivi' (product, candidate, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "needs",
      "replacement": "EPDs",
      "memory_id": 11
    }
  ],
  "reason_mismatch": null
}
```

</details>

## fuzzy / N12_ambiguous_competing_memories — 3 failing

### `neg-ambiguous-01` — false_intervention

- **scenario**: `seeded_ambiguous_kiwi`
- **why this case exists**: Two confirmed memories answer to this sound (the product Kivi and the client Kiwee) and nothing in the sentence separates them. With two equally good answers the honest response is to abstain and say why, not to pick the marginally higher score. Note the first sentence contains 'invoice', which weakly favours the client — weakly enough that acting on it would be a guess, so silence is still the right answer.
- **input**: `The Kiwi invoice needs reissuing.`
- **expected** (none): `The Kiwi invoice needs reissuing.`
- **actual** (changed): `The Kivi Kivi EPDs reissuing.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Kiwi", "replacement": "Kivi", "memory_id": 1}, {"span": "invoice", "replacement": "Kivi", "memory_id": 1}, {"span": "needs", "replacement": "EPDs", "memory_id": 11}]
- **relevant memory**: #20 'Kiwee' (org, confirmed, 1.0), #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Kiwi",
      "replacement": "Kivi",
      "memory_id": 1
    },
    {
      "span": "invoice",
      "replacement": "Kivi",
      "memory_id": 1
    },
    {
      "span": "needs",
      "replacement": "EPDs",
      "memory_id": 11
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-ambiguous-02` — false_intervention

- **scenario**: `seeded_ambiguous_kiwi`
- **why this case exists**: Two confirmed memories answer to this sound (the product Kivi and the client Kiwee) and nothing in the sentence separates them. With two equally good answers the honest response is to abstain and say why, not to pick the marginally higher score. Note the first sentence contains 'invoice', which weakly favours the client — weakly enough that acting on it would be a guess, so silence is still the right answer.
- **input**: `The Kiwi meeting moved to Thursday.`
- **expected** (none): `The Kiwi meeting moved to Thursday.`
- **actual** (changed): `The Kivi Sumeet moved to Thursday.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Kiwi", "replacement": "Kivi", "memory_id": 1}, {"span": "meeting", "replacement": "Sumeet", "memory_id": 15}]
- **relevant memory**: #20 'Kiwee' (org, confirmed, 1.0), #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Kiwi",
      "replacement": "Kivi",
      "memory_id": 1
    },
    {
      "span": "meeting",
      "replacement": "Sumeet",
      "memory_id": 15
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `pos-ambiguous-01` — acted_but_wrong_text

- **scenario**: `seeded_ambiguous_kiwi`
- **why this case exists**: Two memories match the sound, but only one fits the sentence. Abstaining here would be over-caution, not care: the point is to make USEFUL corrections, not the fewest.
- **input**: `Ship the Kiwi update on Friday.`
- **expected** (correct): `Ship the Kivi update on Friday.`
- **actual** (changed): `Ship the Kivi update on gray.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Kiwi", "replacement": "Kivi", "memory_id": 1}, {"span": "Friday", "replacement": "gray", "memory_id": 8}]
- **relevant memory**: #20 'Kiwee' (org, confirmed, 1.0), #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Kiwi",
      "replacement": "Kivi",
      "memory_id": 1
    },
    {
      "span": "Friday",
      "replacement": "gray",
      "memory_id": 8
    }
  ],
  "reason_mismatch": null
}
```

</details>

## fuzzy / N13_no_relevant_memory — 6 failing

### `neg-nomem-01` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: Ordinary dictation with no personal vocabulary in it. The overwhelming majority of real usage looks like this, so silence here is the common case, not an edge one.
- **input**: `Remind me to book the flight and pay the electricity bill.`
- **expected** (none): `Remind me to book the flight and pay the electricity bill.`
- **actual** (changed): `Remind me to book the flight and gray the electricity bill.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "pay", "replacement": "gray", "memory_id": 8}]

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "pay",
      "replacement": "gray",
      "memory_id": 8
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-nomem-02` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: Ordinary dictation with no personal vocabulary in it. The overwhelming majority of real usage looks like this, so silence here is the common case, not an edge one.
- **input**: `The meeting moved to four o'clock on Thursday.`
- **expected** (none): `The meeting moved to four o'clock on Thursday.`
- **actual** (changed): `The Sumeet moved to four o'clock on Thursday.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "meeting", "replacement": "Sumeet", "memory_id": 15}]

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "meeting",
      "replacement": "Sumeet",
      "memory_id": 15
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-nomem-04` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: Ordinary dictation with no personal vocabulary in it. The overwhelming majority of real usage looks like this, so silence here is the common case, not an edge one.
- **input**: `Please pick up milk and bread on the way.`
- **expected** (none): `Please pick up milk and bread on the way.`
- **actual** (changed): `Please pick up milk and bread on the gray.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "way", "replacement": "gray", "memory_id": 8}]

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "way",
      "replacement": "gray",
      "memory_id": 8
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-nomem-05` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: Ordinary dictation with no personal vocabulary in it. The overwhelming majority of real usage looks like this, so silence here is the common case, not an edge one.
- **input**: `The weather forecast says rain all weekend.`
- **expected** (none): `The weather forecast says rain all weekend.`
- **actual** (changed): `The weather Foods Sarvams rain all weekend.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "forecast", "replacement": "Foods", "memory_id": 18}, {"span": "says", "replacement": "Sarvams", "memory_id": 3}]

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "forecast",
      "replacement": "Foods",
      "memory_id": 18
    },
    {
      "span": "says",
      "replacement": "Sarvams",
      "memory_id": 3
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-nomem-06` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: Ordinary dictation with no personal vocabulary in it. The overwhelming majority of real usage looks like this, so silence here is the common case, not an edge one.
- **input**: `Send the signed lease back to the landlord.`
- **expected** (none): `Send the signed lease back to the landlord.`
- **actual** (changed): `EPD the signed lease back to the Bengaluru.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Send", "replacement": "EPD", "memory_id": 11}, {"span": "landlord", "replacement": "Bengaluru", "memory_id": 9}]

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Send",
      "replacement": "EPD",
      "memory_id": 11
    },
    {
      "span": "landlord",
      "replacement": "Bengaluru",
      "memory_id": 9
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-nomem-10` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: Ordinary dictation with no personal vocabulary in it. The overwhelming majority of real usage looks like this, so silence here is the common case, not an edge one.
- **input**: `I still need to file last year's taxes.`
- **expected** (none): `I still need to file last year's taxes.`
- **actual** (changed): `I still EPD to file last year's taxes.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "need", "replacement": "EPD", "memory_id": 11}]

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "need",
      "replacement": "EPD",
      "memory_id": 11
    }
  ],
  "reason_mismatch": null
}
```

</details>

## fuzzy / N1_homophone_ordinary_sense — 8 failing

### `neg-fruit-01` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: 'kiwi' is an ordinary English word and this sentence uses it that way. Overwriting it would corrupt text the person said correctly.
- **input**: `I ate a kiwi on the flight.`
- **expected** (none): `I ate a kiwi on the flight.`
- **actual** (changed): `I ate a Kivi on the flight.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "kiwi", "replacement": "Kivi", "memory_id": 1}]
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "kiwi",
      "replacement": "Kivi",
      "memory_id": 1
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-fruit-02` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: 'kiwi' is an ordinary English word and this sentence uses it that way. Overwriting it would corrupt text the person said correctly.
- **input**: `Add a kiwi to the fruit salad.`
- **expected** (none): `Add a kiwi to the fruit salad.`
- **actual** (changed): `Aaditya a Kivi to the Sumeet Sarvam.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Add", "replacement": "Aaditya", "memory_id": 2}, {"span": "kiwi", "replacement": "Kivi", "memory_id": 1}, {"span": "fruit", "replacement": "Sumeet", "memory_id": 15}, {"span": "salad", "replacement": "Sarvam", "memory_id": 3}]
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Add",
      "replacement": "Aaditya",
      "memory_id": 2
    },
    {
      "span": "kiwi",
      "replacement": "Kivi",
      "memory_id": 1
    },
    {
      "span": "fruit",
      "replacement": "Sumeet",
      "memory_id": 15
    },
    {
      "span": "salad",
      "replacement": "Sarvam",
      "memory_id": 3
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-fruit-03` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: 'kiwi' is an ordinary English word and this sentence uses it that way. Overwriting it would corrupt text the person said correctly.
- **input**: `The kiwi is a bird native to New Zealand.`
- **expected** (none): `The kiwi is a bird native to New Zealand.`
- **actual** (changed): `The Kivi is a bird native to New Zealand.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "kiwi", "replacement": "Kivi", "memory_id": 1}]
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "kiwi",
      "replacement": "Kivi",
      "memory_id": 1
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-fruit-04` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: 'kiwi' is an ordinary English word and this sentence uses it that way. Overwriting it would corrupt text the person said correctly.
- **input**: `She packed a kiwi and an apple for lunch.`
- **expected** (none): `She packed a kiwi and an apple for lunch.`
- **actual** (changed): `She packed a Kivi and an apple Foods lunch.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "kiwi", "replacement": "Kivi", "memory_id": 1}, {"span": "for", "replacement": "Foods", "memory_id": 18}]
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "kiwi",
      "replacement": "Kivi",
      "memory_id": 1
    },
    {
      "span": "for",
      "replacement": "Foods",
      "memory_id": 18
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-fruit-05` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: 'kiwi' is an ordinary English word and this sentence uses it that way. Overwriting it would corrupt text the person said correctly.
- **input**: `Kiwi fruit is cheaper in winter.`
- **expected** (none): `Kiwi fruit is cheaper in winter.`
- **actual** (changed): `Kivi Sumeet is cheaper in winter.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Kiwi", "replacement": "Kivi", "memory_id": 1}, {"span": "fruit", "replacement": "Sumeet", "memory_id": 15}]
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Kiwi",
      "replacement": "Kivi",
      "memory_id": 1
    },
    {
      "span": "fruit",
      "replacement": "Sumeet",
      "memory_id": 15
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-fruit-06` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: 'kiwi' is an ordinary English word and this sentence uses it that way. Overwriting it would corrupt text the person said correctly.
- **input**: `We saw a kiwi at the wildlife park.`
- **expected** (none): `We saw a kiwi at the wildlife park.`
- **actual** (changed): `We Sarvam a Kivi at the wildlife park.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "saw", "replacement": "Sarvam", "memory_id": 3}, {"span": "kiwi", "replacement": "Kivi", "memory_id": 1}]
- **relevant memory**: #7 '@aaditya_k' (handle, confirmed, 0.9), #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "saw",
      "replacement": "Sarvam",
      "memory_id": 3
    },
    {
      "span": "kiwi",
      "replacement": "Kivi",
      "memory_id": 1
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-fruit-07` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: 'kiwi' is an ordinary English word and this sentence uses it that way. Overwriting it would corrupt text the person said correctly.
- **input**: `The smoothie has banana, mango and kiwi.`
- **expected** (none): `The smoothie has banana, mango and kiwi.`
- **actual** (changed): `The Sumeet has Bengaluru, Bengaluru and Kivi.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "smoothie", "replacement": "Sumeet", "memory_id": 15}, {"span": "banana", "replacement": "Bengaluru", "memory_id": 9}, {"span": "mango", "replacement": "Bengaluru", "memory_id": 9}, {"span": "kiwi", "replacement": "Kivi", "memory_id": 1}]
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "smoothie",
      "replacement": "Sumeet",
      "memory_id": 15
    },
    {
      "span": "banana",
      "replacement": "Bengaluru",
      "memory_id": 9
    },
    {
      "span": "mango",
      "replacement": "Bengaluru",
      "memory_id": 9
    },
    {
      "span": "kiwi",
      "replacement": "Kivi",
      "memory_id": 1
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-fruit-08` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: 'kiwi' is an ordinary English word and this sentence uses it that way. Overwriting it would corrupt text the person said correctly.
- **input**: `Peel the kiwi before slicing it.`
- **expected** (none): `Peel the kiwi before slicing it.`
- **actual** (changed): `Peel the Kivi Bengaluru slicing it.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "kiwi", "replacement": "Kivi", "memory_id": 1}, {"span": "before", "replacement": "Bengaluru", "memory_id": 9}]
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "kiwi",
      "replacement": "Kivi",
      "memory_id": 1
    },
    {
      "span": "before",
      "replacement": "Bengaluru",
      "memory_id": 9
    }
  ],
  "reason_mismatch": null
}
```

</details>

## fuzzy / N2_product_vs_generic_word — 6 failing

### `neg-cursor-01` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: 'Cursor' is a seeded product memory, but here the word means the caret. The correction is only wanted when the sentence is about the editor.
- **input**: `Move the cursor to the end of the line.`
- **expected** (none): `Move the cursor to the end of the line.`
- **actual** (changed): `Move the Cursor to the EPD of the line.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "cursor", "replacement": "Cursor", "memory_id": 10}, {"span": "end", "replacement": "EPD", "memory_id": 11}]
- **relevant memory**: #10 'Cursor' (org, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "cursor",
      "replacement": "Cursor",
      "memory_id": 10
    },
    {
      "span": "end",
      "replacement": "EPD",
      "memory_id": 11
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-cursor-02` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: 'Cursor' is a seeded product memory, but here the word means the caret. The correction is only wanted when the sentence is about the editor.
- **input**: `The cursor keeps jumping while I type.`
- **expected** (none): `The cursor keeps jumping while I type.`
- **actual** (changed): `The Cursor keeps jumping Vishal I type.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "cursor", "replacement": "Cursor", "memory_id": 10}, {"span": "while", "replacement": "Vishal", "memory_id": 16}]
- **relevant memory**: #10 'Cursor' (org, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "cursor",
      "replacement": "Cursor",
      "memory_id": 10
    },
    {
      "span": "while",
      "replacement": "Vishal",
      "memory_id": 16
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-cursor-03` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: 'Cursor' is a seeded product memory, but here the word means the caret. The correction is only wanted when the sentence is about the editor.
- **input**: `Put the cursor in the search box.`
- **expected** (none): `Put the cursor in the search box.`
- **actual** (changed): `Put the Cursor in the search box.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "cursor", "replacement": "Cursor", "memory_id": 10}]
- **relevant memory**: #10 'Cursor' (org, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "cursor",
      "replacement": "Cursor",
      "memory_id": 10
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-cursor-04` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: 'Cursor' is a seeded product memory, but here the word means the caret. The correction is only wanted when the sentence is about the editor.
- **input**: `My cursor disappeared after the update.`
- **expected** (none): `My cursor disappeared after the update.`
- **actual** (changed): `My Cursor disappeared after the update.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "cursor", "replacement": "Cursor", "memory_id": 10}]
- **relevant memory**: #10 'Cursor' (org, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "cursor",
      "replacement": "Cursor",
      "memory_id": 10
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-cursor-05` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: 'Cursor' is a seeded product memory, but here the word means the caret. The correction is only wanted when the sentence is about the editor.
- **input**: `Hold shift and drag the cursor.`
- **expected** (none): `Hold shift and drag the cursor.`
- **actual** (changed): `Hold Sumeet and drag the Cursor.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "shift", "replacement": "Sumeet", "memory_id": 15}, {"span": "cursor", "replacement": "Cursor", "memory_id": 10}]
- **relevant memory**: #10 'Cursor' (org, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "shift",
      "replacement": "Sumeet",
      "memory_id": 15
    },
    {
      "span": "cursor",
      "replacement": "Cursor",
      "memory_id": 10
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-cursor-06` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: 'Cursor' is a seeded product memory, but here the word means the caret. The correction is only wanted when the sentence is about the editor.
- **input**: `The text cursor is blinking too fast.`
- **expected** (none): `The text cursor is blinking too fast.`
- **actual** (changed): `The text Cursor is blinking too fast.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "cursor", "replacement": "Cursor", "memory_id": 10}]
- **relevant memory**: #10 'Cursor' (org, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "cursor",
      "replacement": "Cursor",
      "memory_id": 10
    }
  ],
  "reason_mismatch": null
}
```

</details>

## fuzzy / N4_different_real_person — 4 failing

### `neg-otherperson-01` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: Two colleagues exist: Aaditya, and Aditya Ghosh. 'Aditya' is simultaneously a wrong form of one and the correct name of the other, so the wider name must protect the token inside it.
- **input**: `Aditya Ghosh approved the budget.`
- **expected** (none): `Aditya Ghosh approved the budget.`
- **actual** (changed): `Aaditya Ghosh approved the budget.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Aditya", "replacement": "Aaditya", "memory_id": 2}]
- **relevant memory**: #2 'Aaditya' (person, confirmed, 0.95), #13 'Ghosh' (person, confirmed, 0.9), #12 'Aditya Ghosh' (person, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Aditya",
      "replacement": "Aaditya",
      "memory_id": 2
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-otherperson-02` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: Two colleagues exist: Aaditya, and Aditya Ghosh. 'Aditya' is simultaneously a wrong form of one and the correct name of the other, so the wider name must protect the token inside it.
- **input**: `I met Aditya Ghosh at the offsite.`
- **expected** (none): `I met Aditya Ghosh at the offsite.`
- **actual** (changed): `I met Aaditya Ghosh at the offsite.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Aditya", "replacement": "Aaditya", "memory_id": 2}]
- **relevant memory**: #2 'Aaditya' (person, confirmed, 0.95), #13 'Ghosh' (person, confirmed, 0.9), #7 '@aaditya_k' (handle, confirmed, 0.9), #12 'Aditya Ghosh' (person, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Aditya",
      "replacement": "Aaditya",
      "memory_id": 2
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-otherperson-03` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: Two colleagues exist: Aaditya, and Aditya Ghosh. 'Aditya' is simultaneously a wrong form of one and the correct name of the other, so the wider name must protect the token inside it.
- **input**: `Aditya Ghosh is my manager.`
- **expected** (none): `Aditya Ghosh is my manager.`
- **actual** (changed): `Aaditya Ghosh is my Bengaluru.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Aditya", "replacement": "Aaditya", "memory_id": 2}, {"span": "manager", "replacement": "Bengaluru", "memory_id": 9}]
- **relevant memory**: #2 'Aaditya' (person, confirmed, 0.95), #13 'Ghosh' (person, confirmed, 0.9), #12 'Aditya Ghosh' (person, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Aditya",
      "replacement": "Aaditya",
      "memory_id": 2
    },
    {
      "span": "manager",
      "replacement": "Bengaluru",
      "memory_id": 9
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-otherperson-04` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: Two colleagues exist: Aaditya, and Aditya Ghosh. 'Aditya' is simultaneously a wrong form of one and the correct name of the other, so the wider name must protect the token inside it.
- **input**: `Forward the deck to Aditya Ghosh.`
- **expected** (none): `Forward the deck to Aditya Ghosh.`
- **actual** (changed): `Forward the deck to Aaditya Ghosh.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Aditya", "replacement": "Aaditya", "memory_id": 2}]
- **relevant memory**: #2 'Aaditya' (person, confirmed, 0.95), #13 'Ghosh' (person, confirmed, 0.9), #12 'Aditya Ghosh' (person, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Aditya",
      "replacement": "Aaditya",
      "memory_id": 2
    }
  ],
  "reason_mismatch": null
}
```

</details>

## fuzzy / N5_coincidental_phonetic_match — 5 failing

### `neg-coincidence-01` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: Naive phonetic matching fires here: 'add it' encodes identically to 'Aaditya'. Only the ordinary-word prior and the context gate prevent the false correction.
- **input**: `Add it to the list before the standup.`
- **expected** (none): `Add it to the list before the standup.`
- **actual** (changed): `Aaditya it to the list Bengaluru the standup.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Add", "replacement": "Aaditya", "memory_id": 2}, {"span": "before", "replacement": "Bengaluru", "memory_id": 9}]

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Add",
      "replacement": "Aaditya",
      "memory_id": 2
    },
    {
      "span": "before",
      "replacement": "Bengaluru",
      "memory_id": 9
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-coincidence-04` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: Naive phonetic matching fires here: 'add it' encodes identically to 'Aaditya'. Only the ordinary-word prior and the context gate prevent the false correction.
- **input**: `I need to add itemised costs to the invoice.`
- **expected** (none): `I need to add itemised costs to the invoice.`
- **actual** (changed): `I EPD to Aaditya itemised Postgres to the Kivi.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "need", "replacement": "EPD", "memory_id": 11}, {"span": "add", "replacement": "Aaditya", "memory_id": 2}, {"span": "costs", "replacement": "Postgres", "memory_id": 14}, {"span": "invoice", "replacement": "Kivi", "memory_id": 1}]

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "need",
      "replacement": "EPD",
      "memory_id": 11
    },
    {
      "span": "add",
      "replacement": "Aaditya",
      "memory_id": 2
    },
    {
      "span": "costs",
      "replacement": "Postgres",
      "memory_id": 14
    },
    {
      "span": "invoice",
      "replacement": "Kivi",
      "memory_id": 1
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-coincidence-05` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: Naive phonetic matching fires here: 'add it' encodes identically to 'Aaditya'. Only the ordinary-word prior and the context gate prevent the false correction.
- **input**: `Can you add it back after the review?`
- **expected** (none): `Can you add it back after the review?`
- **actual** (changed): `Kubernetes you Aaditya it back after the review?`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Can", "replacement": "Kubernetes", "memory_id": 4}, {"span": "add", "replacement": "Aaditya", "memory_id": 2}]

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Can",
      "replacement": "Kubernetes",
      "memory_id": 4
    },
    {
      "span": "add",
      "replacement": "Aaditya",
      "memory_id": 2
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-coincidence-06` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: Naive phonetic matching fires here: 'add it' encodes identically to 'Aaditya'. Only the ordinary-word prior and the context gate prevent the false correction.
- **input**: `That is a good idea, let's add it.`
- **expected** (none): `That is a good idea, let's add it.`
- **actual** (changed): `That is a Ghosh idea, let's Aaditya it.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "good", "replacement": "Ghosh", "memory_id": 13}, {"span": "add", "replacement": "Aaditya", "memory_id": 2}]

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "good",
      "replacement": "Ghosh",
      "memory_id": 13
    },
    {
      "span": "add",
      "replacement": "Aaditya",
      "memory_id": 2
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-coincidence-07` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: Naive phonetic matching fires here: 'add it' encodes identically to 'Aaditya'. Only the ordinary-word prior and the context gate prevent the false correction.
- **input**: `The city council approved the permit.`
- **expected** (none): `The city council approved the permit.`
- **actual** (changed): `The Aaditya council approved the permit.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "city", "replacement": "Aaditya", "memory_id": 2}]

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "city",
      "replacement": "Aaditya",
      "memory_id": 2
    }
  ],
  "reason_mismatch": null
}
```

</details>

## fuzzy / N7_metalinguistic_mention — 4 failing

### `neg-meta-01` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: The token is the object of the sentence, not a reference to the thing. Correcting it would change what the sentence is about.
- **input**: `The word 'kiwi' has four letters.`
- **expected** (none): `The word 'kiwi' has four letters.`
- **actual** (changed): `The word 'Kivi' has four letters.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "kiwi", "replacement": "Kivi", "memory_id": 1}]
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "kiwi",
      "replacement": "Kivi",
      "memory_id": 1
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-meta-02` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: The token is the object of the sentence, not a reference to the thing. Correcting it would change what the sentence is about.
- **input**: `How do you spell 'kiwi' in the plural?`
- **expected** (none): `How do you spell 'kiwi' in the plural?`
- **actual** (changed): `How do you spell 'Kivi' in the plural?`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "kiwi", "replacement": "Kivi", "memory_id": 1}]
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "kiwi",
      "replacement": "Kivi",
      "memory_id": 1
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-meta-03` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: The token is the object of the sentence, not a reference to the thing. Correcting it would change what the sentence is about.
- **input**: `The word 'cursor' is oddly chosen for an editor.`
- **expected** (none): `The word 'cursor' is oddly chosen for an editor.`
- **actual** (changed): `The word 'Cursor' is oddly chosen Foods an editor.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "cursor", "replacement": "Cursor", "memory_id": 10}, {"span": "for", "replacement": "Foods", "memory_id": 18}]
- **relevant memory**: #10 'Cursor' (org, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "cursor",
      "replacement": "Cursor",
      "memory_id": 10
    },
    {
      "span": "for",
      "replacement": "Foods",
      "memory_id": 18
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-meta-04` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: The token is the object of the sentence, not a reference to the thing. Correcting it would change what the sentence is about.
- **input**: `The word 'grey' is spelled differently in America.`
- **expected** (none): `The word 'grey' is spelled differently in America.`
- **actual** (changed): `The word 'gray' is spelled differently in America.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "grey", "replacement": "gray", "memory_id": 8}]
- **relevant memory**: #8 'gray' (preference, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "grey",
      "replacement": "gray",
      "memory_id": 8
    }
  ],
  "reason_mismatch": null
}
```

</details>

## fuzzy / N8_already_canonical — 6 failing

### `neg-noop-01` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: The text is already what the system would write. This must be recorded as a no-op decision: without that row there is no denominator for precision.
- **input**: `Ship the Kivi update on Friday.`
- **expected** (none): `Ship the Kivi update on Friday.`
- **actual** (changed): `Ship the Kivi update on gray.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Friday", "replacement": "gray", "memory_id": 8}]
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Friday",
      "replacement": "gray",
      "memory_id": 8
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-noop-03` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: The text is already what the system would write. This must be recorded as a no-op decision: without that row there is no denominator for precision.
- **input**: `The Kubernetes cluster is healthy again.`
- **expected** (none): `The Kubernetes cluster is healthy again.`
- **actual** (changed): `The Kubernetes Cursor is healthy again.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "cluster", "replacement": "Cursor", "memory_id": 10}]
- **relevant memory**: #4 'Kubernetes' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "cluster",
      "replacement": "Cursor",
      "memory_id": 10
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-noop-04` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: The text is already what the system would write. This must be recorded as a no-op decision: without that row there is no denominator for precision.
- **input**: `Compare it with OpenAI and Anthropic.`
- **expected** (none): `Compare it with OpenAI and Anthropic.`
- **actual** (changed): `Compare it Vishal OpenAI and Anthropic.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "with", "replacement": "Vishal", "memory_id": 16}]
- **relevant memory**: #5 'OpenAI' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "with",
      "replacement": "Vishal",
      "memory_id": 16
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-noop-05` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: The text is already what the system would write. This must be recorded as a no-op decision: without that row there is no denominator for precision.
- **input**: `Use the gray background for the dashboard.`
- **expected** (none): `Use the gray background for the dashboard.`
- **actual** (changed): `Sumeet the gray background Foods the dashboard.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Use", "replacement": "Sumeet", "memory_id": 15}, {"span": "for", "replacement": "Foods", "memory_id": 18}]
- **relevant memory**: #8 'gray' (preference, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Use",
      "replacement": "Sumeet",
      "memory_id": 15
    },
    {
      "span": "for",
      "replacement": "Foods",
      "memory_id": 18
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-noop-07` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: The text is already what the system would write. This must be recorded as a no-op decision: without that row there is no denominator for precision.
- **input**: `Vishal owns the ASR pipeline.`
- **expected** (none): `Vishal owns the ASR pipeline.`
- **actual** (changed): `Vishal owns the SARVAM pipeline.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "ASR", "replacement": "SARVAM", "memory_id": 3}]
- **relevant memory**: #16 'Vishal' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "ASR",
      "replacement": "SARVAM",
      "memory_id": 3
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-noop-08` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: The text is already what the system would write. This must be recorded as a no-op decision: without that row there is no denominator for precision.
- **input**: `Send the metrics to EPD before the review.`
- **expected** (none): `Send the metrics to EPD before the review.`
- **actual** (changed): `EPD the metrics to EPD Bengaluru the review.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Send", "replacement": "EPD", "memory_id": 11}, {"span": "before", "replacement": "Bengaluru", "memory_id": 9}]
- **relevant memory**: #11 'EPD' (acronym, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Send",
      "replacement": "EPD",
      "memory_id": 11
    },
    {
      "span": "before",
      "replacement": "Bengaluru",
      "memory_id": 9
    }
  ],
  "reason_mismatch": null
}
```

</details>

## fuzzy / N9_deleted_memory_inert — 3 failing

### `neg-deleted-01` — false_intervention

- **scenario**: `seeded_kivi_deleted`
- **why this case exists**: Deletion correctness: the memory was deleted, so this must stop being corrected.
- **input**: `Ship the Kiwi update on Friday.`
- **expected** (none): `Ship the Kiwi update on Friday.`
- **actual** (changed): `Ship the Kiwi update on gray.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "Friday", "replacement": "gray", "memory_id": 8}]
- **relevant memory**: #1 'Kivi' (product, deleted, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "Friday",
      "replacement": "gray",
      "memory_id": 8
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-deleted-02` — false_intervention

- **scenario**: `seeded_kivi_deleted`
- **why this case exists**: Deletion correctness: deletion must apply to every context, not just the one it was deleted in.
- **input**: `The Kiwi service is down for everyone.`
- **expected** (none): `The Kiwi service is down for everyone.`
- **actual** (changed): `The Kiwi service is down Foods everyone.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "for", "replacement": "Foods", "memory_id": 18}]
- **relevant memory**: #1 'Kivi' (product, deleted, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "for",
      "replacement": "Foods",
      "memory_id": 18
    }
  ],
  "reason_mismatch": null
}
```

</details>

### `neg-deleted-03` — false_intervention

- **scenario**: `seeded_kivi_deleted`
- **why this case exists**: Deletion correctness: even the exact sentence that originally taught the memory must be left alone once deleted.
- **input**: `Review the Sarvam Kiwi service before Friday.`
- **expected** (none): `Review the Sarvam Kiwi service before Friday.`
- **actual** (changed): `Review the Sarvam Kiwi service Bengaluru gray.`
- **reason codes**: `BASELINE_FUZZY`
- **system's reasoning**: [{"span": "before", "replacement": "Bengaluru", "memory_id": 9}, {"span": "Friday", "replacement": "gray", "memory_id": 8}]
- **relevant memory**: #3 'Sarvam' (org, confirmed, 0.85), #1 'Kivi' (product, deleted, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "span": "before",
      "replacement": "Bengaluru",
      "memory_id": 9
    },
    {
      "span": "Friday",
      "replacement": "gray",
      "memory_id": 8
    }
  ],
  "reason_mismatch": null
}
```

</details>

## kivi / A1_product_heard_as_ordinary_word — 1 failing

### `pos-kivi-08` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: Kivi is the seeded product memory and the sentence is unambiguously about software, so the correction is the useful one.
- **input**: `Kiwi users are reporting slow dictation.`
- **expected** (correct): `Kivi users are reporting slow dictation.`
- **actual** (unchanged): `Kiwi users are reporting slow dictation.`
- **reason codes**: `ABSTAIN_ORDINARY_WORD_CONTEXT_WEAK`
- **system's reasoning**: context score 0.17 did not reach the 0.55 required here — the heard form is an ordinary English word (rank 16870) written in lower case, so the formatting stage read it as a common noun and strong context is required before overwriting it
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

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
      "span": "Kiwi",
      "memory": "Kivi",
      "tier": "variant",
      "action": "abstained",
      "reason_code": "ABSTAIN_ORDINARY_WORD_CONTEXT_WEAK",
      "lexical": 1.0,
      "phonetic": 1.0,
      "context": 0.175,
      "required": 0.55
    }
  ],
  "reason_mismatch": null
}
```

</details>

## kivi / A6_jargon_multitoken_error — 1 failing

### `pos-jargon-06` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: A two-token mis-hearing collapsing onto a one-token term. This is why memory operates on spans rather than tokens.
- **input**: `Post Grease is using too much memory.`
- **expected** (correct): `Postgres is using too much memory.`
- **actual** (unchanged): `Post Grease is using too much memory.`
- **reason codes**: `ABSTAIN_ORDINARY_WORD_CONTEXT_WEAK, ABSTAIN_ORDINARY_WORD_CONTEXT_WEAK`
- **system's reasoning**: context score 0.15 did not reach the 0.55 required here — an inexact match onto an ordinary English word (rank 13495), which already has a legitimate reading
- **relevant memory**: #14 'Postgres' (term, confirmed, 0.9)

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
      "span": "Grease",
      "memory": "gray",
      "tier": "fuzzy",
      "action": "abstained",
      "reason_code": "ABSTAIN_ORDINARY_WORD_CONTEXT_WEAK",
      "lexical": 0.8,
      "phonetic": 0.667,
      "context": 0.15,
      "required": 0.55
    },
    {
      "span": "Post Grease",
      "memory": "Postgres",
      "tier": "variant",
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

## llm_only / A10_morphology_preserved — 4 failing

### `pos-morph-01` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: The possessive must survive the substitution: the canonical stem is applied and the inflection is re-attached, rather than the whole token being replaced.
- **input**: `Kiwi's onboarding flow is confusing.`
- **expected** (correct): `Kivi's onboarding flow is confusing.`
- **actual** (unchanged): `Kiwi's onboarding flow is confusing.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-morph-02` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: The possessive must survive the substitution: the canonical stem is applied and the inflection is re-attached, rather than the whole token being replaced.
- **input**: `The Kiwi's release notes are stale.`
- **expected** (correct): `The Kivi's release notes are stale.`
- **actual** (unchanged): `The Kiwi's release notes are stale.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-morph-03` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: The possessive must survive the substitution: the canonical stem is applied and the inflection is re-attached, rather than the whole token being replaced.
- **input**: `Aditya's review is still pending.`
- **expected** (correct): `Aaditya's review is still pending.`
- **actual** (unchanged): `Aditya's review is still pending.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #2 'Aaditya' (person, confirmed, 0.95), #12 'Aditya Ghosh' (person, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-morph-04` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: The possessive must survive the substitution: the canonical stem is applied and the inflection is re-attached, rather than the whole token being replaced.
- **input**: `I borrowed Aditya's laptop for the demo.`
- **expected** (correct): `I borrowed Aaditya's laptop for the demo.`
- **actual** (unchanged): `I borrowed Aditya's laptop for the demo.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #2 'Aaditya' (person, confirmed, 0.95), #12 'Aditya Ghosh' (person, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

## llm_only / A11_spelling_preference — 2 failing

### `pos-pref-01` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: Both spellings are correct English. There is no global right answer, only this person's. Meaning-preserving, so it applies without needing context.
- **input**: `Use the grey background for the dashboard.`
- **expected** (correct): `Use the gray background for the dashboard.`
- **actual** (unchanged): `Use the grey background for the dashboard.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #8 'gray' (preference, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-pref-04` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: Both spellings are correct English. There is no global right answer, only this person's. Meaning-preserving, so it applies without needing context.
- **input**: `A grey banner appears on first load.`
- **expected** (correct): `A gray banner appears on first load.`
- **actual** (unchanged): `A grey banner appears on first load.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #8 'gray' (preference, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

## llm_only / A12_transliteration_preference — 3 failing

### `pos-place-01` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: Same city, two accepted romanisations. The person's choice is the only thing that decides it.
- **input**: `The Bangalore office is closed on Monday.`
- **expected** (correct): `The Bengaluru office is closed on Monday.`
- **actual** (unchanged): `The Bangalore office is closed on Monday.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #9 'Bengaluru' (place, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-place-02` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: Same city, two accepted romanisations. The person's choice is the only thing that decides it.
- **input**: `I am flying to Bangalore on Sunday.`
- **expected** (correct): `I am flying to Bengaluru on Sunday.`
- **actual** (unchanged): `I am flying to Bangalore on Sunday.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #9 'Bengaluru' (place, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-place-03` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: Same city, two accepted romanisations. The person's choice is the only thing that decides it.
- **input**: `Our Bangalore team handles support.`
- **expected** (correct): `Our Bengaluru team handles support.`
- **actual** (unchanged): `Our Bangalore team handles support.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #9 'Bengaluru' (place, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

## llm_only / A1_indic_phonetic_variation — 5 failing

### `pos-indic-01` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: v/w and long-vowel alternation dominate Indian-English name transcription and are the reason the phonetic encoder is tuned for it rather than using Soundex.
- **input**: `Wishal owns the ASR pipeline.`
- **expected** (correct): `Vishal owns the ASR pipeline.`
- **actual** (unchanged): `Wishal owns the ASR pipeline.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #16 'Vishal' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-indic-03` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: v/w and long-vowel alternation dominate Indian-English name transcription and are the reason the phonetic encoder is tuned for it rather than using Soundex.
- **input**: `Wishal is reviewing the benchmark.`
- **expected** (correct): `Vishal is reviewing the benchmark.`
- **actual** (unchanged): `Wishal is reviewing the benchmark.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #16 'Vishal' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-indic-04` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: v/w and long-vowel alternation dominate Indian-English name transcription and are the reason the phonetic encoder is tuned for it rather than using Soundex.
- **input**: `Sumit is reviewing the retrieval code.`
- **expected** (correct): `Sumeet is reviewing the retrieval code.`
- **actual** (unchanged): `Sumit is reviewing the retrieval code.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #15 'Sumeet' (term, confirmed, 0.95)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-indic-05` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: v/w and long-vowel alternation dominate Indian-English name transcription and are the reason the phonetic encoder is tuned for it rather than using Soundex.
- **input**: `I sent Sumit the eval results.`
- **expected** (correct): `I sent Sumeet the eval results.`
- **actual** (unchanged): `I sent Sumit the eval results.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #15 'Sumeet' (term, confirmed, 0.95)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-indic-06` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: v/w and long-vowel alternation dominate Indian-English name transcription and are the reason the phonetic encoder is tuned for it rather than using Soundex.
- **input**: `Sumit found the off-by-one bug.`
- **expected** (correct): `Sumeet found the off-by-one bug.`
- **actual** (unchanged): `Sumit found the off-by-one bug.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #15 'Sumeet' (term, confirmed, 0.95)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

## llm_only / A1_product_heard_as_ordinary_word — 12 failing

### `pos-kivi-01` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: Kivi is the seeded product memory and the sentence is unambiguously about software, so the correction is the useful one.
- **input**: `Ship the Kiwi update on Friday.`
- **expected** (correct): `Ship the Kivi update on Friday.`
- **actual** (unchanged): `Ship the Kiwi update on Friday.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-kivi-02` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: Kivi is the seeded product memory and the sentence is unambiguously about software, so the correction is the useful one.
- **input**: `The Kiwi service is down for everyone.`
- **expected** (correct): `The Kivi service is down for everyone.`
- **actual** (unchanged): `The Kiwi service is down for everyone.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-kivi-03` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: Kivi is the seeded product memory and the sentence is unambiguously about software, so the correction is the useful one.
- **input**: `I pushed a fix to the Kiwi backend.`
- **expected** (correct): `I pushed a fix to the Kivi backend.`
- **actual** (unchanged): `I pushed a fix to the Kiwi backend.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-kivi-04` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: Kivi is the seeded product memory and the sentence is unambiguously about software, so the correction is the useful one.
- **input**: `Can you review the Kiwi PR before standup?`
- **expected** (correct): `Can you review the Kivi PR before standup?`
- **actual** (unchanged): `Can you review the Kiwi PR before standup?`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-kivi-05` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: Kivi is the seeded product memory and the sentence is unambiguously about software, so the correction is the useful one.
- **input**: `We deployed Kiwi to staging last night.`
- **expected** (correct): `We deployed Kivi to staging last night.`
- **actual** (unchanged): `We deployed Kiwi to staging last night.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-kivi-06` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: Kivi is the seeded product memory and the sentence is unambiguously about software, so the correction is the useful one.
- **input**: `The Kiwi dashboard needs a redesign.`
- **expected** (correct): `The Kivi dashboard needs a redesign.`
- **actual** (unchanged): `The Kiwi dashboard needs a redesign.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-kivi-07` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: Kivi is the seeded product memory and the sentence is unambiguously about software, so the correction is the useful one.
- **input**: `Add telemetry to the Kiwi app.`
- **expected** (correct): `Add telemetry to the Kivi app.`
- **actual** (unchanged): `Add telemetry to the Kiwi app.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-kivi-08` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: Kivi is the seeded product memory and the sentence is unambiguously about software, so the correction is the useful one.
- **input**: `Kiwi users are reporting slow dictation.`
- **expected** (correct): `Kivi users are reporting slow dictation.`
- **actual** (unchanged): `Kiwi users are reporting slow dictation.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-kivi-09` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: Kivi is the seeded product memory and the sentence is unambiguously about software, so the correction is the useful one.
- **input**: `The Sarvam Kiwi release slipped by a week.`
- **expected** (correct): `The Sarvam Kivi release slipped by a week.`
- **actual** (unchanged): `The Sarvam Kiwi release slipped by a week.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #3 'Sarvam' (org, confirmed, 0.85), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-kivi-10` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: Kivi is the seeded product memory and the sentence is unambiguously about software, so the correction is the useful one.
- **input**: `Let's demo Kiwi to the whole team.`
- **expected** (correct): `Let's demo Kivi to the whole team.`
- **actual** (unchanged): `Let's demo Kiwi to the whole team.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-kivi-11` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: Kivi is the seeded product memory and the sentence is unambiguously about software, so the correction is the useful one.
- **input**: `Roll back the Kiwi deployment.`
- **expected** (correct): `Roll back the Kivi deployment.`
- **actual** (unchanged): `Roll back the Kiwi deployment.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-kivi-12` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: Kivi is the seeded product memory and the sentence is unambiguously about software, so the correction is the useful one.
- **input**: `File a bug against Kiwi for the crash.`
- **expected** (correct): `File a bug against Kivi for the crash.`
- **actual** (unchanged): `File a bug against Kiwi for the crash.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

## llm_only / A2_person_romanisation_preference — 10 failing

### `pos-aaditya-01` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: Both spellings are valid English romanisations, so no general dictionary can resolve this. Only a memory of THIS person's preference can.
- **input**: `Ask Aditya to review the PR.`
- **expected** (correct): `Ask Aaditya to review the PR.`
- **actual** (unchanged): `Ask Aditya to review the PR.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #2 'Aaditya' (person, confirmed, 0.95), #12 'Aditya Ghosh' (person, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-aaditya-02` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: Both spellings are valid English romanisations, so no general dictionary can resolve this. Only a memory of THIS person's preference can.
- **input**: `I told Aditya about the outage.`
- **expected** (correct): `I told Aaditya about the outage.`
- **actual** (unchanged): `I told Aditya about the outage.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #2 'Aaditya' (person, confirmed, 0.95), #12 'Aditya Ghosh' (person, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-aaditya-03` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: Both spellings are valid English romanisations, so no general dictionary can resolve this. Only a memory of THIS person's preference can.
- **input**: `Aditya is joining the standup late.`
- **expected** (correct): `Aaditya is joining the standup late.`
- **actual** (unchanged): `Aditya is joining the standup late.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #2 'Aaditya' (person, confirmed, 0.95), #12 'Aditya Ghosh' (person, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-aaditya-04` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: Both spellings are valid English romanisations, so no general dictionary can resolve this. Only a memory of THIS person's preference can.
- **input**: `Loop Aditya into the thread.`
- **expected** (correct): `Loop Aaditya into the thread.`
- **actual** (unchanged): `Loop Aditya into the thread.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #2 'Aaditya' (person, confirmed, 0.95), #12 'Aditya Ghosh' (person, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-aaditya-05` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: Both spellings are valid English romanisations, so no general dictionary can resolve this. Only a memory of THIS person's preference can.
- **input**: `Email Aditya the latency numbers.`
- **expected** (correct): `Email Aaditya the latency numbers.`
- **actual** (unchanged): `Email Aditya the latency numbers.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #2 'Aaditya' (person, confirmed, 0.95), #12 'Aditya Ghosh' (person, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-aaditya-06` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: Both spellings are valid English romanisations, so no general dictionary can resolve this. Only a memory of THIS person's preference can.
- **input**: `Aditya mentioned the schema change.`
- **expected** (correct): `Aaditya mentioned the schema change.`
- **actual** (unchanged): `Aditya mentioned the schema change.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #2 'Aaditya' (person, confirmed, 0.95), #12 'Aditya Ghosh' (person, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-aaditya-07` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: Both spellings are valid English romanisations, so no general dictionary can resolve this. Only a memory of THIS person's preference can.
- **input**: `Thanks to Aditya for the quick fix.`
- **expected** (correct): `Thanks to Aaditya for the quick fix.`
- **actual** (unchanged): `Thanks to Aditya for the quick fix.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #2 'Aaditya' (person, confirmed, 0.95), #12 'Aditya Ghosh' (person, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-aaditya-08` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: Both spellings are valid English romanisations, so no general dictionary can resolve this. Only a memory of THIS person's preference can.
- **input**: `cc Aditya on the vendor reply.`
- **expected** (correct): `cc Aaditya on the vendor reply.`
- **actual** (unchanged): `cc Aditya on the vendor reply.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #2 'Aaditya' (person, confirmed, 0.95), #12 'Aditya Ghosh' (person, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-aaditya-09` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: Both spellings are valid English romanisations, so no general dictionary can resolve this. Only a memory of THIS person's preference can.
- **input**: `Aditya and I paired on the retriever.`
- **expected** (correct): `Aaditya and I paired on the retriever.`
- **actual** (unchanged): `Aditya and I paired on the retriever.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #2 'Aaditya' (person, confirmed, 0.95), #12 'Aditya Ghosh' (person, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-aaditya-10` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: Both spellings are valid English romanisations, so no general dictionary can resolve this. Only a memory of THIS person's preference can.
- **input**: `Assign the ticket to Aditya.`
- **expected** (correct): `Assign the ticket to Aaditya.`
- **actual** (unchanged): `Assign the ticket to Aditya.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #2 'Aaditya' (person, confirmed, 0.95), #12 'Aditya Ghosh' (person, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

## llm_only / A5_personal_acronym — 2 failing

### `pos-epd-02` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: An internal team name. Spelled-out letters must collapse to the canonical form.
- **input**: `E P D owns the quarterly report.`
- **expected** (correct): `EPD owns the quarterly report.`
- **actual** (unchanged): `E P D owns the quarterly report.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #11 'EPD' (acronym, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-epd-03` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: An internal team name. Spelled-out letters must collapse to the canonical form.
- **input**: `Ask E P D for the headcount doc.`
- **expected** (correct): `Ask EPD for the headcount doc.`
- **actual** (changed): `Ask E.P.D. for the headcount doc.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #11 'EPD' (acronym, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

## llm_only / A6_jargon_multitoken_error — 5 failing

### `pos-jargon-01` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: A two-token mis-hearing collapsing onto a one-token term. This is why memory operates on spans rather than tokens.
- **input**: `The Cuban Eighties cluster is down again.`
- **expected** (correct): `The Kubernetes cluster is down again.`
- **actual** (unchanged): `The Cuban Eighties cluster is down again.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #4 'Kubernetes' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-jargon-02` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: A two-token mis-hearing collapsing onto a one-token term. This is why memory operates on spans rather than tokens.
- **input**: `Restart the Cuban Eighties pod.`
- **expected** (correct): `Restart the Kubernetes pod.`
- **actual** (unchanged): `Restart the Cuban Eighties pod.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #4 'Kubernetes' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-jargon-03` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: A two-token mis-hearing collapsing onto a one-token term. This is why memory operates on spans rather than tokens.
- **input**: `Our Cuban Eighties config drifted.`
- **expected** (correct): `Our Kubernetes config drifted.`
- **actual** (unchanged): `Our Cuban Eighties config drifted.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #4 'Kubernetes' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-jargon-04` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: A two-token mis-hearing collapsing onto a one-token term. This is why memory operates on spans rather than tokens.
- **input**: `The Post Grease connection is timing out.`
- **expected** (correct): `The Postgres connection is timing out.`
- **actual** (changed): `The PostGrease connection is timing out.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #14 'Postgres' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-jargon-05` — acted_but_wrong_text

- **scenario**: `seeded`
- **why this case exists**: A two-token mis-hearing collapsing onto a one-token term. This is why memory operates on spans rather than tokens.
- **input**: `Migrate the Post Grease schema tonight.`
- **expected** (correct): `Migrate the Postgres schema tonight.`
- **actual** (changed): `Migrate the Postgre schema tonight.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #14 'Postgres' (term, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

## llm_only / A9_handle_identifier — 2 failing

### `pos-handle-01` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: A handle is a strict identifier with no natural-language spelling rules. The dictated description must resolve to the exact stored string.
- **input**: `DM at Aaditya underscore K about the review.`
- **expected** (correct): `DM @aaditya_k about the review.`
- **actual** (unchanged): `DM at Aaditya underscore K about the review.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #2 'Aaditya' (person, confirmed, 0.95), #7 '@aaditya_k' (handle, confirmed, 0.9), #6 'Aaditya Labs' (org, candidate, 0.4)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-handle-02` — missed_intervention

- **scenario**: `seeded`
- **why this case exists**: A handle is a strict identifier with no natural-language spelling rules. The dictated description must resolve to the exact stored string.
- **input**: `Ping at Aaditya underscore K on Slack.`
- **expected** (correct): `Ping @aaditya_k on Slack.`
- **actual** (unchanged): `Ping at Aaditya underscore K on Slack.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #2 'Aaditya' (person, confirmed, 0.95), #7 '@aaditya_k' (handle, confirmed, 0.9), #6 'Aaditya Labs' (org, candidate, 0.4)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

## llm_only / N10_superseded_memory_updated — 2 failing

### `pos-superseded-01` — missed_intervention

- **scenario**: `seeded_sumeet_superseded`
- **why this case exists**: After supersession the previously-correct spelling becomes the wrong one. This is the case that proves knowledge was replaced rather than merely added to.
- **input**: `Sumeet is reviewing the retrieval code.`
- **expected** (correct): `Sumit is reviewing the retrieval code.`
- **actual** (unchanged): `Sumeet is reviewing the retrieval code.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #20 'Sumit' (term, confirmed, 1.0), #15 'Sumeet' (term, superseded, 0.95)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>

### `pos-superseded-02` — missed_intervention

- **scenario**: `seeded_sumeet_superseded`
- **why this case exists**: Supersession must hold across contexts, not just the sentence it happened in.
- **input**: `I sent Sumeet the eval results.`
- **expected** (correct): `I sent Sumit the eval results.`
- **actual** (unchanged): `I sent Sumeet the eval results.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: [{"error": "HTTP 429: {\"error\":{\"message\":\"Rate limit exceeded\",\"code\":\"rate_limit_exceeded_error\",\"request_id\":\"20260908_4e554ef9-13a8-40e4-ab5d-22fb8f283545\"}}"}]
- **relevant memory**: #20 'Sumit' (term, confirmed, 1.0), #15 'Sumeet' (term, superseded, 0.95)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "error": "HTTP 429: {\"error\":{\"message\":\"Rate limit exceeded\",\"code\":\"rate_limit_exceeded_error\",\"request_id\":\"20260908_4e554ef9-13a8-40e4-ab5d-22fb8f283545\"}}"
    }
  ],
  "reason_mismatch": null
}
```

</details>

## llm_only / N12_ambiguous_competing_memories — 1 failing

### `pos-ambiguous-01` — missed_intervention

- **scenario**: `seeded_ambiguous_kiwi`
- **why this case exists**: Two memories match the sound, but only one fits the sentence. Abstaining here would be over-caution, not care: the point is to make USEFUL corrections, not the fewest.
- **input**: `Ship the Kiwi update on Friday.`
- **expected** (correct): `Ship the Kivi update on Friday.`
- **actual** (unchanged): `Ship the Kiwi update on Friday.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: [{"error": "HTTP 429: {\"error\":{\"message\":\"Rate limit exceeded\",\"code\":\"rate_limit_exceeded_error\",\"request_id\":\"20260908_ccfc5dce-9858-4a75-a799-aca3f6d100bd\"}}"}]
- **relevant memory**: #20 'Kiwee' (org, confirmed, 1.0), #1 'Kivi' (product, confirmed, 0.9), #17 'Kiwi Foods' (org, candidate, 0.58)

<details><summary>full decision detail</summary>

```json
{
  "applied": [
    {
      "error": "HTTP 429: {\"error\":{\"message\":\"Rate limit exceeded\",\"code\":\"rate_limit_exceeded_error\",\"request_id\":\"20260908_ccfc5dce-9858-4a75-a799-aca3f6d100bd\"}}"
    }
  ],
  "reason_mismatch": null
}
```

</details>

## llm_only / N7_metalinguistic_mention — 1 failing

### `neg-meta-04` — false_intervention

- **scenario**: `seeded`
- **why this case exists**: The token is the object of the sentence, not a reference to the thing. Correcting it would change what the sentence is about.
- **input**: `The word 'grey' is spelled differently in America.`
- **expected** (none): `The word 'grey' is spelled differently in America.`
- **actual** (changed): `The word 'gray' is spelled differently in America.`
- **reason codes**: `BASELINE_LLM_ONLY`
- **system's reasoning**: []
- **relevant memory**: #8 'gray' (preference, confirmed, 0.9)

<details><summary>full decision detail</summary>

```json
{
  "applied": [],
  "reason_mismatch": null
}
```

</details>
