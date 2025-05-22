import { PromptStyleOption } from './types';

interface PromptTemplate {
  title: string;
  description: string;
  template: string;
}

export const defaultPrompts: Record<PromptStyleOption, PromptTemplate> = {
  'Zero-shot': {
    title: 'Zero-shot Prompt',
    description: 'A simple prompt that directly asks the model to normalize the claim without examples.',
    template: `[PLACEHOLDER] Normalize the following claim into a clear, concise statement.`
  },
  'Few-shot': {
    title: 'Few-shot Prompt',
    description: 'A prompt that includes several examples to guide the model.',
    template: `[PLACEHOLDER] Here are some examples of claim normalization:

Original: "Scientists say climate change is real and happening now"
Normalized: "Climate change is occurring in the present"

Original: "The new study shows that vaccines are 95% effective"
Normalized: "Vaccines have 95% effectiveness according to a recent study"

Now normalize the following claim.`
  },
  'Zero-shot-CoT': {
    title: 'Zero-shot Chain of Thought',
    description: 'A prompt that encourages the model to think through the normalization process step by step.',
    template: `[PLACEHOLDER] Let's normalize this claim step by step:

1. First, identify the main subject and action
2. Then, remove any unnecessary words or qualifiers
3. Finally, restructure the sentence to be clear and concise

Let's think through this:
1. Main subject and action:
2. Words to remove:
3. Final normalized claim:`
  },
  'Few-shot-CoT': {
    title: 'Few-shot Chain of Thought',
    description: 'A prompt that combines examples with step-by-step thinking.',
    template: `[PLACEHOLDER] Let's look at some examples of claim normalization with step-by-step thinking:

Example 1:
Claim: "Experts warn that social media is causing mental health issues"
Steps:
1. Main subject: social media
2. Action: causing mental health issues
3. Remove qualifiers: "Experts warn that"
4. Normalized: "Social media causes mental health issues"

Example 2:
Claim: "New research suggests that exercise can reduce stress"
Steps:
1. Main subject: exercise
2. Action: can reduce stress
3. Remove qualifiers: "New research suggests that"
4. Normalized: "Exercise reduces stress"

Now normalize the following claim using the same step-by-step approach.`
  }
}; 