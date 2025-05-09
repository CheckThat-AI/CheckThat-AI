# Claim Extraction and Normalization

This project is a part of <a href="https://checkthat.gitlab.io/clef2025/task2/" rel="noopener nofollow ugc">CLEF-CheckThat! Lab's Task2 (2025)</a>. Given a noisy, unstructured social media post, the task is to simplify it into a concise form.
This is a text generation task in which systems have to generate the normlized claims for the given social media posts.

## Project Structure

```
clef-2025-checkthat-lab-task2
├── src
│   ├── claim_norm.py               # Main entry point
│   └── utils                       # Package containing helper functions for claim normalization logic
│       ├── __init__.py             # Package initialization
│       ├── evaluate.py             # Logic for evaluating the generated claims
│       ├── self_refine.py          # Logic for the self-refine stage
│       ├── get_model_response.py   # Logic to query the model using the API
│       ├── gpt.py                  # helper function to get the response from gpt-4.1-nano model using OpenAI API
│       ├── llama.py                # helper function to get the response from llama-3.3-70B model using together.ai API
│       ├── gemini.py               # helper function to get the response from gemini-2.0-flash model using gemini API
│       └── grok.py                 # helper function to get the response from xAI's grok3 model using OpenAI API
├── data
│   └── dev.csv                     # Development dataset for testing
├── requirements.txt                # Project dependencies
└── README.md                       # Project documentation
```

## Setup Instructions

1. **Clone the repository:**
   ```bash 
   git clone <repository-url>
   cd src
   ```

2. **Create a virtual environment:**
   ```bash 
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt  
   ```
   Use `uv pip install -r requirements.txt` for faster installation if you already have uv installed. 
   
   If not, run `pip install uv` first.

4. **Set up environment variables:**
Set the API keys for the model of your choice. This code works with the APIs of OpenAI, Gemini, Grok, and Together.ai

      ***Linux/macOS***
      ```bash 
      export API_KEY="xxxxxxxx"
      ```
      ***Windows*** 
      ```bash
      $env:API_KEY="xxxxxxxxx"
      ```
## Usage

To run the code with default values for the baseline condition(without the self-refine step), execute the following command:

```bash
python claim_norm.py 
```
This command runs the code with together.ai's API using the free version of Llama-3.3-70B

To choose model, prompt style, and number of self-refine iterations, run the below command
```bash
python claim_norm.py -m OpenAI -p Zero-Shot -it 1
```
This will run the code using OpenAI API to extract normalized claims using GPT-4.1-nano with one iteration of the self-refine step.

Once the program starts running, you will see the output that looks something like below:

```
Extracting claims and evaluating with METEOR: 0%|                                         | 0/1 [00:00<?, ?it/s]

Initial Claim: Trophy hunting is horrific.

-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ Self-refine Iteration 1 of 1 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

=========================== Feedback ==================================

Feedback: {
   'verifiability': ['2', 'The response lacks specific, quantifiable evidence or credible sources to support the claim that trophy hunting is horrific.'], 
   'false_likelihood': ['6', 'The response contains an emotive statement without providing context or facts, making it potentially misleading or false.'], 
   'public_interest': ['8', 'The topic of trophy hunting is of significant public interest and relevance, particularly among animal welfare and conservation groups.'], 
   'potential_harm': ['4', 'The response may cause emotional distress or offense to some individuals, but it does not promote hate speech or violence.'], 
   'check_worthiness': ['9', 'The response requires fact-checking to verify the claims and ensure that the information is accurate and reliable.']
}

======================= End of Feedback ===============================

Refined Claim: Trophy hunting has raised concerns among animal welfare and conservation groups due to its potential impact on wildlife populations and animal welfare.

-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ End of Self-refine Iteration 1 of 1 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-

Extracting claims and evaluating with METEOR: 100%|██████████████████████████████████████████| 1/1 [00:39<00:00, 39.96s/it]

Average METEOR Score: {'Llama_Zero-Shot': np.float64(0.02293577981651376)}
```
***Go to src/utils/self_refine.py to comment the print statements to make the code run faster when evaluating a large dataset***

## Help
Run the below command to list the accepted model names and prompt styles.
```bash
python cliam_norm.py -h
```
## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.