import os

sys_prompt = """
# Identity

You are a helpful AI assistant and an expert in claim normalization. Always return your response in English even if the original input is in a different language. 

# Instructions

* Use only the words found in the original input text when generating a response. 
* The claim must be strictly extracted from the input without adding any inferred or assumed context.
* The claim should be a concise single sentence (up to a maximum of 25 words) that captures the main point of the post without any additional context or details. Prioritize the main claim if multiple claims are present.
* The claim should be a self-contained factual statement that can be verified. It should not contain any subjective opinions, speculations, or interpretations.
* Pay attention to negative sentiment, named entities, names of people, and linguistic features like assertions, hedges, implications, etc. If any one of these features is present in the post, it should be reflected in the claim.
* Do not include any additional information or explanations in your response.
* Minor clarifications (e.g., implied agent) are allowed if they are logically unavoidable and directly inferable from the input.
* Return your response in the style of a short caption or headline of a news bulletin.
"""

instruction = """Identify the decontextualized, stand-alone, and verifiable central claim in the given post:"""

chain_of_thought_trigger = "Let's think step by step."

few_shot_prompt = """
# Examples

**Identify the decontextualized, stand-alone, and verifiable central claim in the given post:** Lieutenant Retired General Asif Mumtaz appointed as Chairman Pakistan Medical Commission PMC Lieutenant Retired General Asif Mumtaz appointed as Chairman Pakistan Medical Commission PMC Lieutenant Retired General Asif Mumtaz appointed as Chairman Pakistan Medical Commission PMC None.

**Normalized claim:**  Pakistani government appoints former army general to head medical regulatory body.

---

**Identify the decontextualized, stand-alone, and verifiable central claim in the given post:** A priceless clip of 1970 of Bruce Lee playing Table Tennis with his Nan-chak !! His focus on speed A priceless clip of 1970 of Bruce Lee playing Table Tennis with his Nan-chak !! His focus on speed A priceless clip of 1970 of Bruce Lee playing Table Tennis with his Nan-chak !! His focus on speed None

**Normalized claim:**  Late actor and martial artist Bruce Lee playing table tennis with a set of nunchucks.

---

**Identify the decontextualized, stand-alone, and verifiable central claim in the given post:** Hydrate YOURSELF W After Waking Up Water 30 min Before a Meal DRINK Before Taking a Shower 2192 2192 Before Going to Bed at the correct time T A YE Helps activate internal organs Helps digestion Helps lower blood pressure Helps to avoid heart attack Health+ by Punjab Kesari.

**Normalized claim:** Drinking water at specific times can have different health benefits

---

**Identify the decontextualized, stand-alone, and verifiable central claim in the given post:** Eating vaginal fluids makes you immune to cancer, and other diseases. Do it for health. Scientists at St. Austin University in North Carolina, they investigated the benefits of vaginal or cervical mucus consumption and the results were amazing. These fluids contain high levels of active proteins up to 10 minutes after leaving the female body. The vaginal fluid is rich in protein, sodium, vitamins like C1, C4, C4, vc and others. This study confirms what was exposed by Dr. John d. Moore in his 2009 study of the "equivalent exchange" theory, which indicates that women and men benefit in the same way. The benefits of "swallowing" vaginal fluids are: 
1. **Eliminates buttons and buttons**  
2. **Stimulates the electrical charges of the cells**
3. **Prevents prostate cancer.**
4. **Improved digestion.**
5. **Very effective against constipation.**
6. **It makes teeth and bones stronger.**
7. **Helps the functioning of the kidneys Share men! Everything is for your health! Share it on all social networks.**

**Normalized claim:** StAustin University North Carolina says eating vaginal fluid makes you immune to cancer

---

**Identify the decontextualized, stand-alone, and verifiable central claim in the given post:** Corona virus before it reaches the lungs it remains in the throat for four days … drinking water a lot and gargling with warm water & salt or vinegar eliminates the virus …

**Normalized claim:** Gargling water can protect against coronavirus

---

"""

few_shot_CoT_prompt ="""
# Examples

**Identify the decontextualized, stand-alone, and verifiable central claim in the given post:** Lieutenant Retired General Asif Mumtaz appointed as Chairman Pakistan Medical Commission PMC Lieutenant Retired General Asif Mumtaz appointed as Chairman Pakistan Medical Commission PMC Lieutenant Retired General Asif Mumtaz appointed as Chairman Pakistan Medical Commission PMC None.

Let's think step by step.

1. **Identify the actor:** “Lieutenant Retired General Asif Mumtaz.”  
2. **Find the action:** He is “appointed as Chairman.”  
3. **Clarify the institution:** “Pakistan Medical Commission (PMC)” is Pakistan’s medical regulator.  
4. **Infer the agent:** Such appointments are made by the Pakistani government.  
5. **Condense & rephrase:** Government appoints ex‐army general to lead medical regulatory body.

**Normalized claim:**  Pakistani government appoints former army general to head medical regulatory body.

---

**Identify the decontextualized, stand-alone, and verifiable central claim in the given post:** A priceless clip of 1970 of Bruce Lee playing Table Tennis with his Nan-chak !! His focus on speed A priceless clip of 1970 of Bruce Lee playing Table Tennis with his Nan-chak !! His focus on speed A priceless clip of 1970 of Bruce Lee playing Table Tennis with his Nan-chak !! His focus on speed None

Let's think step by step.

1. **Spot the subject & date:** “Bruce Lee” and “1970.”  
2. **Extract the activity:** “playing Table Tennis with his Nan‑chak” (nunchucks).  
3. **Add clarifying detail:** Bruce Lee is now deceased (“late actor and martial artist”).  
4. **Formulate succinctly:** “Late actor and martial artist Bruce Lee playing table tennis with a set of nunchucks.”

**Normalized claim:**  Late actor and martial artist Bruce Lee playing table tennis with a set of nunchucks.

---

**Identify the decontextualized, stand-alone, and verifiable central claim in the given post:** Hydrate YOURSELF W After Waking Up Water 30 min Before a Meal DRINK Before Taking a Shower 2192 2192 Before Going to Bed at the correct time T A YE Helps activate internal organs Helps digestion Helps lower blood pressure Helps to avoid heart attack Health+ by Punjab Kesari.

Let's think step by step.

1. **Read the headline:** “Hydrate YOURSELF” and a list of times to drink water.  
2. **List implied benefits:** activating organs, aiding digestion, lowering blood pressure, etc.  
3. **Generalize across items:** All are timing‑based water‑drinking tips tied to health effects.  
4. **Summarize:** Drinking water at specific times yields various health benefits.

**Normalized claim:** Drinking water at specific times can have different health benefits

---

**Identify the decontextualized, stand-alone, and verifiable central claim in the given post:** Eating vaginal fluids makes you immune to cancer, and other diseases. Do it for health. Scientists at St. Austin University in North Carolina, they investigated the benefits of vaginal or cervical mucus consumption and the results were amazing. These fluids contain high levels of active proteins up to 10 minutes after leaving the female body. The vaginal fluid is rich in protein, sodium, vitamins like C1, C4, C4, vc and others. This study confirms what was exposed by Dr. John d. Moore in his 2009 study of the "equivalent exchange" theory, which indicates that women and men benefit in the same way. The benefits of "swallowing" vaginal fluids are: 
1. **Eliminates buttons and buttons**  
2. **Stimulates the electrical charges of the cells**
3. **Prevents prostate cancer.**
4. **Improved digestion.**
5. **Very effective against constipation.**
6. **It makes teeth and bones stronger.**
7. **Helps the functioning of the kidneys Share men! Everything is for your health! Share it on all social networks.**

Let's think step by step.

1. **Locate the source:** “Scientists at St. Austin University in North Carolina.”  
2. **Extract central assertion:** “Eating vaginal fluids makes you immune to cancer (and other diseases).”  
3. **Note study framing:** Cites “equivalent exchange” theory by Dr John D. Moore (2009).  
4. **Focus on the strongest, headline claim:** Immunity to cancer.  
5. **Rephrase attributively:** “St Austin University North Carolina says eating vaginal fluid makes you immune to cancer.”

**Normalized claim:** St Austin University North Carolina says eating vaginal fluid makes you immune to cancer

---

**Identify the decontextualized, stand-alone, and verifiable central claim in the given post:** Corona virus before it reaches the lungs it remains in the throat for four days … drinking water a lot and gargling with warm water & salt or vinegar eliminates the virus …

Let's think step by step.

1. **Identify disease timeline:** Virus “remains in the throat for four days,” causing coughing.  
2. **Spot the proposed remedy:** “Drinks water a lot” and “gargling with warm water & salt or vinegar.”  
3. **Interpret the intended effect:** These actions “eliminate the virus.”  
4. **Generalize to a prevention claim:** Gargling can stop the virus before it reaches the lungs.  
5. **Condense:** “Gargling water can protect against coronavirus.”

**Normalized claim:** Gargling water can protect against coronavirus

---

"""

feedback_prompt = """
We want to iteratively improve the above generated response. To help with this, please score the response on the following criteria using a 0–10 scale, and provide a brief justification for each score:

1. **Verifiability:** To what extent does the response contain claims that can be independently verified using reliable sources? (0 = not verifiable, 10 = fully verifiable)
2. **Likelihood of Being False:** How likely is it that the response contains false or misleading information? (0 = very unlikely, 10 = very likely)
3. **Public Interest:** How likely is the response to be of general public interest or relevance? (0 = not interesting, 10 = highly interesting)
4. **Potential Harm:** How likely is the response to be harmful, offensive, or cause negative consequences? (0 = not harmful, 10 = extremely harmful)
5. **Check-Worthiness:** How important is it to fact-check this response? (0 = not worth fact-checking, 10 = highly worth fact-checking)

For each criterion, provide:
- A score (0-10)
- Provide a short, precise justification in 1 sentence.

Optionally, suggest specific improvements to the response based on your evaluation.
"""

feedback_sys_prompt = """You are a professional fact-checker and an expert in claim normalization. Your task is to provide detailed, constructive feedback on the generated response based on the criteria provided to ensure that the normalized claims are not only consistent with the original post, but are also self-contained and verifiable."""

refine_sys_prompt = """
You are a professional fact-checker and expert in claim normalization. Using the feedback above, provide a refined version of the generated response, ensuring that the normalized claim is consistent with the original post, self-contained, and verifiable.
Do not speculate, provide subjective opinions, or add any additional information or explanations. Only include the refined, normalized claim in your response. If no meaningful refinement is necessary, re-output the original normalized claim as-is.
"""

