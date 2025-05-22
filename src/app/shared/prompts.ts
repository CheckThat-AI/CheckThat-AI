import { PromptStyleOption } from './types';

interface PromptTemplate {
  title: string;
  description: string;
  template: string;
}

export const sys_prompt = `# Identity

You are a helpful AI assistant and an expert in claim detection, extraction, and normalization.  

# Instructions

* You are given a noisy social media post that contains only text but it might have 
  been posted alongside a photo or video on the platform it was extracted from.
  
* Your task is to detect, extract, and respond with a normalized claim.

* A claim is a statement or assertion that can be objectively verified as true or false 
  based on empirical evidence  or reality.

* Follow to below steps to analyze the input text and arrive at the final response.

    * Step 1: Sentence Splitting and Context Creation
        * Start by splitting the post into individual sentences. 
        * Now create or retrieve a context for each of those sentences by looking at
          the two preceding and two following sentences.

    * Step 2: Selection
        * Now determine if each sentence contains any verifiable information based on 
          the context created for the sentence in the previous step.
        * For each sentence, do the following:
            * If the sentence does not contain any verfiable information, discard that 
              sentence.
            * If the sentence contains both verifiable and unverifiable information, 
              rewrite the sentence retaining only verifiable information.
            * If the sentence doe not conatin any unverifiable information, return the 
              original sentence.

    * Step 3: Disambiguation
        * The task here is to identify two types of ambiguity. 
        * The first is referential ambiguity, which occurs when it is unclear what a 
          word or phrase refers to. For example, in the sentence “They will update the 
          policy next year,” the terms “They,” “the policy,” and “next year” are 
          ambiguous. 
        * The second is structural ambiguity, which occurs when grammatical structure 
          allows for multiple interpretations. For instance, the sentence “AI has 
          advanced renewable energy and sustainable agriculture at Company A and 
          Company B” can be interpreted as: (1) AI has advanced renewable energy and 
          sustainable agriculture at both Company A and Company B, or (2) AI has 
          advanced renewable energy at Company A, and it has advanced sustainable 
          agriculture at Company B.
        * Now determine whether each instance of ambiguity can be resolved using the 
          question and the context. 
        * The standard for resolution is whether a group of readers would likely agree 
          on the correct interpretation. For example, recall the sentence “AI has 
          advanced renewable energy and sustainable agriculture at Company A and 
          Company B.” If the context specified that Company A builds solar panels and 
          Company B reduces farms’ water usage, readers would likely conclude that AI 
          has advanced renewable energy at Company A and sustainable agriculture at 
          Company B. Conversely, if the context only described both companies as 
          “environmental pioneers,” readers would have insufficient information to 
          determine the correct interpretation.
        * If any ambiguity is unresolvable, discard the sentence even if it has 
          unambiguous, verifiable components.
        * If all ambiguity is resolved, return a clarified version of the sentence. 
        * If there is no ambiguity, retain the original sentence for the next step.
        
    * Step 4: Decomposition
        * Your task is to identify all specific and verifiable propositions in the 
          sentence and ensure that each proposition is decontextualized. A proposition 
          is "decontextualized" if (1) it is fully self -contained , meaning it can be 
          understood in isolation (i.e., without the question , the context , and the 
          other propositions), AND (2) its meaning in isolation matches its meaning 
          when interpreted alongside the question , the context , and the other 
          propositions. The propositions should also be the simplest possible discrete 
          units of information.

* If no verifiable claims are found, return an extractive summary of the central idea 
  of the post in a single sentence.

* Use only the words found in the original input text when generating a response. 

* The claim must be strictly extracted from the input without adding any inferred or 
  assumed context.

* The claim should be a concise single sentence (up to a maximum of 25 words) that 
  captures the main point of the post without any additional context or details. 
  Prioritize the main claim if multiple claims are present.

* The claim should be a self-contained factual statement that can be verified. It 
  should not contain any subjective opinions, speculations, or interpretations.

* Pay attention to negative sentiment, named entities, names of people, and linguistic 
  features like assertions, hedges, implications, etc. If any one of these features are 
  present in the post, it should be reflected in the claim.

* Do not include any additional information or explanations in your response.
* Minor clarifications (e.g., implied agent) are allowed if they are logically 
  unavoidable and directly inferable from the input.

* If the input text contains any Named Entities, they must be included in your 
  responses.

* Return your response in the style of a short caption or headline of a news bulletin.

* If the given input text is mostly likely to be referencing or directly talking about 
  or posted alongside a photo or video, return the response that starts with either 
  (1) Photo shows <your_response> or (2) Video shows <your_response>.
  
* Always return your response in English even if the original input is in a different 
  language.
`;

export const defaultPrompts: Record<PromptStyleOption, PromptTemplate> = {
  'Zero-shot': {
    title: 'Zero-shot Prompt',
    description: 'A simple prompt that directly asks the model to normalize the claim without examples.',
    template: `Identify the decontextualized, stand-alone, and verifiable central claim in the given post: {input}`
  },
  'Few-shot': {
    title: 'Few-shot Prompt',
    description: 'A prompt that includes several examples to guide the model.',
    template: `# Here are some examples of how to identify a decontextualized, stand-alone, and verifiable central claim in a post:
<user_query id="example-1">
**Identify the decontextualized, stand-alone, and verifiable central claim in the given post:** Lieutenant Retired General Asif Mumtaz appointed as Chairman Pakistan Medical Commission PMC Lieutenant Retired General Asif Mumtaz appointed as Chairman Pakistan Medical Commission PMC Lieutenant Retired General Asif Mumtaz appointed as Chairman Pakistan Medical Commission PMC None.
</user_query>

<assistant_response id="example-1">
**Normalized claim:**  Pakistani government appoints former army general to head medical regulatory body.
</assistant_response>
---------------------------------------------

<user_query id="example-2">
**Identify the decontextualized, stand-alone, and verifiable central claim in the given post:** A priceless clip of 1970 of Bruce Lee playing Table Tennis with his Nan-chak !! His focus on speed A priceless clip of 1970 of Bruce Lee playing Table Tennis with his Nan-chak !! His focus on speed A priceless clip of 1970 of Bruce Lee playing Table Tennis with his Nan-chak !! His focus on speed None
</user_query>

<assistant_response id="example-2">
**Normalized claim:**  Late actor and martial artist Bruce Lee playing table tennis with a set of nunchucks.
</assistant_response>
---------------------------------------------

<user_query id="example-3">
**Identify the decontextualized, stand-alone, and verifiable central claim in the given post:** Hydrate YOURSELF W After Waking Up Water 30 min Before a Meal DRINK Before Taking a Shower 2192 2192 Before Going to Bed at the correct time T A YE Helps activate internal organs Helps digestion Helps lower blood pressure Helps to avoid heart attack Health+ by Punjab Kesari.
</user_query>

<assistant_response id="example-3">
**Normalized claim:** Drinking water at specific times can have different health benefits
</assistant_response>
---------------------------------------------

<user_query id="example-4">
**Identify the decontextualized, stand-alone, and verifiable central claim in the given post:** Eating vaginal fluids makes you immune to cancer, and other diseases. Do it for health. Scientists at St. Austin University in North Carolina, they investigated the benefits of vaginal or cervical mucus consumption and the results were amazing. These fluids contain high levels of active proteins up to 10 minutes after leaving the female body. The vaginal fluid is rich in protein, sodium, vitamins like C1, C4, C4, vc and others. This study confirms what was exposed by Dr. John d. Moore in his 2009 study of the "equivalent exchange" theory, which indicates that women and men benefit in the same way. The benefits of "swallowing" vaginal fluids are: 
  1. **Eliminates buttons and buttons**  
  2. **Stimulates the electrical charges of the cells**
  3. **Prevents prostate cancer.**
  4. **Improved digestion.**
  5. **Very effective against constipation.**
  6. **It makes teeth and bones stronger.**
  7. **Helps the functioning of the kidneys Share men! Everything is for your health! Share it on all social networks.**
</user_query>

<assistant_response id="example-4">
**Normalized claim:** St Austin University North Carolina says eating vaginal fluid makes you immune to cancer
</assistant_response>
---------------------------------------------

<user_query id="example-5">
**Identify the decontextualized, stand-alone, and verifiable central claim in the given post:** Corona virus before it reaches the lungs it remains in the throat for four days … drinking water a lot and gargling with warm water & salt or vinegar eliminates the virus …
</user_query>

<assistant_response id="example-5">
**Normalized claim:** Gargling water can protect against coronavirus
</assistant_response>
---------------------------------------------

<|User|>: Identify the decontextualized, stand-alone, and verifiable central claim in the given post: {input} <|End_user|>`
  },
  'Zero-shot-CoT': {
    title: 'Zero-shot Chain-of-Thought',
    description: 'A prompt that encourages the model to think through the normalization process step by step.',
    template: `Identify the decontextualized, stand-alone, and verifiable central claim in the given post: {input}. Let's think step by step.`
  },
  'Few-shot-CoT': {
    title: 'Few-shot Chain-of-Thought',
    description: 'A prompt that combines examples with step-by-step thinking.',
    template: `# Here are some examples of how to identify a decontextualized, stand-alone, and verifiable central claim in a post:
<user_query id="example-1">
**Identify the decontextualized, stand-alone, and verifiable central claim in the given post:** Lieutenant Retired General Asif Mumtaz appointed as Chairman Pakistan Medical Commission PMC Lieutenant Retired General Asif Mumtaz appointed as Chairman Pakistan Medical Commission PMC Lieutenant Retired General Asif Mumtaz appointed as Chairman Pakistan Medical Commission PMC None.
Let's think step by step.
</user_query>

<assistant_response id="example-1">
**Normalized claim:**  Pakistani government appoints former army general to head medical regulatory body.
</assistant_response>
---------------------------------------------

<user_query id="example-2">
**Identify the decontextualized, stand-alone, and verifiable central claim in the given post:** A priceless clip of 1970 of Bruce Lee playing Table Tennis with his Nan-chak !! His focus on speed A priceless clip of 1970 of Bruce Lee playing Table Tennis with his Nan-chak !! His focus on speed A priceless clip of 1970 of Bruce Lee playing Table Tennis with his Nan-chak !! His focus on speed None
Let's think step by step.
</user_query>

<assistant_response id="example-2">
**Normalized claim:**  Late actor and martial artist Bruce Lee playing table tennis with a set of nunchucks.
</assistant_response>
---------------------------------------------

<user_query id="example-3">
**Identify the decontextualized, stand-alone, and verifiable central claim in the given post:** Hydrate YOURSELF W After Waking Up Water 30 min Before a Meal DRINK Before Taking a Shower 2192 2192 Before Going to Bed at the correct time T A YE Helps activate internal organs Helps digestion Helps lower blood pressure Helps to avoid heart attack Health+ by Punjab Kesari.
Let's think step by step.
</user_query>

<assistant_response id="example-3">
**Normalized claim:** Drinking water at specific times can have different health benefits
</assistant_response>
---------------------------------------------

<user_query id="example-4">
**Identify the decontextualized, stand-alone, and verifiable central claim in the given post:** Eating vaginal fluids makes you immune to cancer, and other diseases. Do it for health. Scientists at St. Austin University in North Carolina, they investigated the benefits of vaginal or cervical mucus consumption and the results were amazing. These fluids contain high levels of active proteins up to 10 minutes after leaving the female body. The vaginal fluid is rich in protein, sodium, vitamins like C1, C4, C4, vc and others. This study confirms what was exposed by Dr. John d. Moore in his 2009 study of the "equivalent exchange" theory, which indicates that women and men benefit in the same way. The benefits of "swallowing" vaginal fluids are: 
  1. **Eliminates buttons and buttons**  
  2. **Stimulates the electrical charges of the cells**
  3. **Prevents prostate cancer.**
  4. **Improved digestion.**
  5. **Very effective against constipation.**
  6. **It makes teeth and bones stronger.**
  7. **Helps the functioning of the kidneys Share men! Everything is for your health! Share it on all social networks.**
Let's think step by step.
</user_query>

<assistant_response id="example-4">
**Normalized claim:** St Austin University North Carolina says eating vaginal fluid makes you immune to cancer
</assistant_response>
---------------------------------------------

<user_query id="example-5">
**Identify the decontextualized, stand-alone, and verifiable central claim in the given post:** Corona virus before it reaches the lungs it remains in the throat for four days … drinking water a lot and gargling with warm water & salt or vinegar eliminates the virus …
Let's think step by step.
</user_query>

<assistant_response id="example-5">
**Normalized claim:** Gargling water can protect against coronavirus
</assistant_response>
---------------------------------------------

<|User|>: Identify the decontextualized, stand-alone, and verifiable central claim in the given post: {input} <|End_user|>
Let's think step by step.`
  }
}; 