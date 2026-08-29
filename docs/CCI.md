# Cosmetic Conflict Index (CCI)

## 1. What is CCI?

Cosmetic Conflict Index (CCI) is a numerical score used to represent
the overall conflict risk among cosmetic ingredients.

The CCI considers:

- Severity of conflicts
- Number of conflicts
- Conflict density
- Cumulative risk

The score ranges from 0 to 100.

---

## 2. Why CCI is Needed?

A cosmetic product may contain several ingredients.

Looking at individual conflicts alone does not provide an overall
risk assessment.

CCI combines multiple conflict factors into one score.

This allows the system to classify the overall risk as:

- Safe
- Low
- Medium
- High

---

## 3. Severity Weights

Each conflict severity is converted into a numerical value.

| Severity | Weight |
|----------|--------|
| Low | 1 |
| Medium | 2 |
| High | 3 |

---

## 4. Cumulative Risk

Cumulative Risk is the sum of the severity weights of all detected
ingredient conflicts.

Formula:

Cumulative Risk = Sum of severity weights

Example:

High + Medium + Low

= 3 + 2 + 1

= 6

---

## 5. Conflict Density

Conflict Density measures how many possible ingredient combinations
result in conflicts.

Formula:

Conflict Density =
Number of detected conflicts /
Number of possible ingredient pairs

Number of possible pairs:

n × (n - 1) / 2

where n is the number of ingredients.

Example:

4 ingredients:

4 × 3 / 2 = 6 possible pairs

If 3 conflicts are detected:

Conflict Density = 3 / 6

= 0.5

---

## 6. CCI Formula

The implemented CCI formula is:

CCI =

(Cumulative Risk / Maximum Possible Risk) × 70

+

Conflict Density × 30

Maximum Possible Risk:

Number of possible pairs × 3

The CCI is limited to a maximum of 100.

---

## 7. Risk Thresholds

| CCI Score | Risk Level |
|-----------|------------|
| 0 | Safe |
| 0.01 – 25 | Low |
| 25.01 – 50 | Medium |
| Above 50 | High |

---

## 8. Recommendations

### Safe

No major conflicts detected.

### Low

Use with caution.

### Medium

Consider avoiding simultaneous use.

### High

Avoid combining these products.

---

## 9. Example

Ingredients:

- Retinol
- Vitamin C
- Salicylic Acid
- Niacinamide

Detected conflicts:

- Retinol + Vitamin C → Medium
- Retinol + Salicylic Acid → High
- Retinol + Niacinamide → Low

Cumulative Risk:

2 + 3 + 1 = 6

Number of possible pairs:

4 × 3 / 2 = 6

Conflict Density:

3 / 6 = 0.5

The CCI calculation combines these values to produce an overall
risk score.

The resulting CCI is then converted into a risk category.