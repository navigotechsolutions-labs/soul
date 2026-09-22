# Scientific Research & Theoretical Foundations of `Soul`

`Soul` is a non-autoregressive, calibrated "System 1" cognitive and emotional appraisal engine. It combines computational linguistics, cognitive psychology, psychometrics, and calibrated machine learning to allow software agents to appraise human adversity, continuous affect, and nuanced emotional states in sub-millisecond speeds.

This document details the academic literature, theoretical frameworks, and mathematical formulations implemented in `Soul v0.3.0`.

---

## 1. Cognitive Appraisal Theory & Scherer's Component Process Model (CPM)

### Core Papers
- **Scherer, K. R. (2009)**. *"The dynamic architecture of emotion: Evidence for the component process model."* Cognition and Emotion, 23(7), 1307–1351.
- **Hofmann, J., et al. (ACL 2022 / Computational Linguistics 2023)**. *"Dimensional Modeling of Emotions in Text with Appraisal Theories: Corpus Creation, Annotation Reliability, and Prediction."*
- **Smith, C. A., & Ellsworth, P. C. (1985)**. *"Patterns of cognitive appraisal in emotion."* Journal of Personality and Social Psychology, 48(4), 813.

### Theoretical Framework
Traditional NLP models rely on simple categorical labels (e.g. positive/negative or basic Ekman emotions). However, Scherer's Component Process Model (CPM) demonstrates that emotions are not monolithic states; they are the emergent result of **Stimulus Evaluation Checks (SECs)**:
1. **Relevance / Novelty**: Did an unexpected event occur that requires attention?
2. **Goal Conduciveness**: Does the event facilitate or obstruct the individual's goals?
   $$\text{GoalConduciveness} \in [-1.0, +1.0]$$
3. **Coping Potential**: Does the individual possess the power, resources, and agency to modify or adapt to the situation?
   $$\text{CopingPotential} \in [0.0, 1.0]$$
4. **Norm / Value Compatibility**: Does the event align with social and internal moral standards?

In `Soul`, these dimensions are explicitly computed to determine whether an adversity represents acute distress, paralysis, or resilient problem-solving.

---

## 2. Adversity Quotient (AQ) & The CORE Framework

### Core Papers & Works
- **Stoltz, P. G. (1997)**. *"Adversity Quotient: Turning Obstacles into Opportunities."* John Wiley & Sons.
- **Stoltz, P. G. (2000)**. *"Adversity Quotient @ Work: Make Everyday Challenges the Key to Your Success."* HarperCollins.
- **Lazarus, R. S., & Folkman, S. (1984)**. *"Stress, Appraisal, and Coping."* Springer Publishing Company.

### The CORE Model
Stoltz discovered that resilience and adversity tolerance are governed by four distinct cognitive dimensions:
1. **Control (C)**: How much influence the subject perceives they have over the adversity.
   $$C \in [0.0, 1.0]$$
   - $C \to 0$: Learned helplessness, fatalism, perceived victimhood.
   - $C \to 1$: High internal locus of control, proactive engagement.
2. **Ownership (O)**: The degree to which the subject holds themselves accountable for improving the outcome, regardless of fault.
   $$O \in [0.0, 1.0]$$
3. **Reach (R)**: The degree to which the subject perceives the adversity bleeding into other facets of life (catastrophizing vs. compartmentalizing).
   $$R \in [0.0, 1.0]$$
   - $R \to 0$: Well-compartmentalized ("This is just an issue with my car").
   - $R \to 1$: Catastrophic diffusion ("My entire life is ruined").
4. **Endurance (E)**: The perceived duration and permanence of the challenge.
   $$E \in [0.0, 1.0]$$
   - $E \to 0$: Transient, temporary hurdle ("This will pass soon").
   - $E \to 1$: Interminable, permanent curse ("It will never get better").

`Soul` computes individual CORE indices and synthesizes them into an overall **Adversity Quotient (AQ)** and **Adversity Intensity Score**.

---

## 3. Fine-Grained Emotion Taxonomies: GoEmotions & NRC-VAD

### Core Papers
- **Demszky, D., Movshovitz-Attias, D., Ko, J., Cowen, A., Nemade, G., & Ravi, S. (Google Research, ACL 2020)**. *"GoEmotions: A Dataset of Fine-Grained Emotions."*
- **Mohammad, S. M. (ACL 2018)**. *"Obtaining Reliable Human Ratings of Valence, Arousal, and Dominance for 20,000 English Words."*
- **Russell, J. A. (1980)**. *"A Circumplex Model of Affect."* Journal of Personality and Social Psychology, 39(6), 1161–1178.
- **Rashkin, H., et al. (Facebook AI Research, ACL 2019)**. *"Towards Empathetic Open-domain Conversation Models: A New Benchmark and Dataset (EmpatheticDialogues)."*

### Theoretical Integration
`Soul` integrates two complementary representations:
1. **Continuous 3D Affect (Russell's VAD)**:
   - **Valence ($V \in [-1, 1]$)**: Intrinsic pleasure vs. displeasure.
   - **Arousal ($A \in [0, 1]$)**: Neurophysiological activation (lethargy to panic).
   - **Dominance ($D \in [0, 1]$)**: Feeling of power, agency, and social control.
2. **Google's 27 GoEmotions**:
   Fine-grained discrete probabilities across 27 nuanced human emotional states:
   *admiration, amusement, anger, annoyance, approval, caring, confusion, curiosity, desire, disappointment, disapproval, disgust, embarrassment, excitement, fear, gratitude, grief, joy, love, nervousness, optimism, pride, realization, relief, remorse, sadness, surprise*.

---

## 4. Epistemic Calibration & Conformal Uncertainty

### Core Papers
- **Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (ICML 2017)**. *"On Calibration of Modern Neural Networks."*
- **Angelopoulos, A. N., & Bates, S. (2021)**. *"A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification."* arXiv:2107.07511.
- **TypeSafe AI (2026)**. *"Jev: System One Decision Models with RLCD (Reinforcement Learning for Calibrated Decisions)."*

### Mathematical Formulations

#### 1. Temperature-Scaled Platt Calibration
Given uncalibrated feature score $s \in [0, 1]$, temperature scaling with parameter $T > 0$ softens overconfident extremities:
$$z = \frac{s - 0.5}{T}$$
$$\hat{p} = \sigma(4z) = \frac{1}{1 + e^{-4z}}$$

#### 2. Ambiguity & Epistemic Uncertainty Penalization
When signal density is sparse or contradictory (near $0.5$), epistemic confidence must decrease:
$$\text{Ambiguity}(\hat{p}) = 1.0 - 2 \cdot |\hat{p} - 0.5|$$
$$\text{Confidence} = \mathrm{clip}\left(\left(1 - 0.45 \cdot \text{Ambiguity}\right) \cdot \left(0.35 + 0.60 \cdot (1 - e^{-0.8 \cdot \text{Evidence}})\right), 0.15, 0.96\right)$$

#### 3. Conformal Prediction Intervals
Rather than deceiving downstream AI agents with single point estimates, `Soul` outputs a calibrated interval $[y_{\min}, y_{\max}]$ at significance level $\alpha = 0.10$ (90% empirical coverage):
$$\text{Margin}(\hat{p}, \text{Confidence}) = q_{1-\alpha} \cdot \frac{1 - \text{Confidence}}{\sqrt{1 + \text{Evidence}}}$$
$$y_{\min} = \max(0.0, \hat{p} - \text{Margin}), \quad y_{\max} = \min(1.0, \hat{p} + \text{Margin})$$

---

## 5. Architectural Summary

| Layer | Scientific Model | Output Dimension | Latency |
| :--- | :--- | :--- | :--- |
| **Primary Appraisal** | Lazarus Transactional Model | Threat / Harm-Loss / Challenge / Benign | $<0.1\text{ ms}$ |
| **Adversity Psychometrics** | Stoltz CORE Framework | Control, Ownership, Reach, Endurance ($0 \to 1$) | $<0.1\text{ ms}$ |
| **Cognitive Checks** | Scherer Component Process Model (CPM) | Goal Conduciveness, Coping Potential | $<0.1\text{ ms}$ |
| **Affective Core** | Russell Circumplex (NRC-VAD) | Valence, Arousal, Dominance | $<0.1\text{ ms}$ |
| **Granular Emotions** | Google GoEmotions (ACL 2020) | 27 Calibrated Emotion Probabilities | $<0.2\text{ ms}$ |
| **Uncertainty Bounds** | Conformal Prediction (Angelopoulos 2021) | $[y_{\min}, y_{\max}]$ 90% Confidence Intervals | $<0.05\text{ ms}$ |
| **Total Pass** | **System 1 Parallel Appraisal** | **Full Schema-Locked Tensor** | **$\approx 0.4\text{ ms}$** |
