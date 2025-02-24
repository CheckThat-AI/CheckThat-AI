# Task 2: Claim Normalization

Given a noisy, unstructured social media post, the task is to simplify it into a concise form.
This is a text generation task in which systems have to generate the normlized claims for the goven social media posts.

# Steps to run the code
Prior to everything, you need o make sure you have all the dependencies installed. Run the following command first to install the dependencies and libraries.

```
pip install -r requirements.txt
```

## 1. Data Pre-processing
Start by processing the dataset to match the instruction finetuning format for the together.ai platform

```
python3 process_data.py
```

   Run the above command on CLI and this will generate a JSONL file with reformatted data.

## 2. Upload the file to together.ai's fine-tuning queue.
    
   First, set your account's API key to an environment variable named TOGETHER_API_KEY:
    
 ```
export TOGETHER_API_KEY=xxxxx
 ```
    
  Install together library 
    
  ```
  pip install together --upgrade
  ```
    
   Run the below command to upload the file
    
  ```
  python3 upload.py
  ```
    
   You should see a response that looks something like the below:
    
  ```
    {
    id='file-629e58b4-ff73-438c-b2cc-f69542b27980', 
    object=<ObjectType.File: 'file'>, 
    created_at=1732573871, 
    type=None, 
    purpose=<FilePurpose.FineTune: 'fine-tune'>, 
    filename='small_coqa.jsonl', 
    bytes=0, 
    line_count=0, 
    processed=False, 
    FileType='jsonl'
    }
  ```  
## 3. Create a fine-tuning job on together.ai
Run the below command to create a fine-tuning job on together.ai

### Python
```
python3 together_finetune.py -m model_name -f file-id
```
### CLI
```
together fine-tuning create \
  --training-file "file-629e58b4-ff73-438c-b2cc-f69542b27980" \
  --model "meta-llama/Meta-Llama-3.1-8B-Instruct-Reference" \
  --lora
```
The response object will have all the details of your job, including its ID and a `status` key that starts out as "pending":
```
{
  id='ft-66592697-0a37-44d1-b6ea-9908d1c81fbd', 
  training_file='file-63b9f097-e582-4d2e-941e-4b541aa7e328', 
  validation_file='', 
  model='meta-llama/Meta-Llama-3.1-8B-Instruct-Reference', 
  output_name='zainhas/Meta-Llama-3.1-8B-Instruct-Reference-30b975fd', 
... 
  status=<FinetuneJobStatus.STATUS_PENDING: 'pending'>
}
```
## 4. Monitoring the fine-tuning status
Go to your Dashboard on togther.ai and look under jobs to monitor the fine-tuning progress. Alternatively, you can also use the below command to get the status of the job.
```
together fine-tuning retrieve "ft-66592697-0a37-44d1-b6ea-9908d1c81fbd"
```
Your fine-tuning job will go through several phases, including `Pending` , `Queued` , `Running` , `Uploading` , and `Completed` .
## 5. Download Checkpoints
Once the fine-tuning jo is completed, download the Adapter checkpoints to run locally with your base model.

## 6. Downloading model from hugging face
Download the base version of your chosen model from hugging face
Authenticate yourself first by logging into your Hugging Face account
```
huggingface-cli login
```
Run the below command to download the model
```
huggingface-cli download meta-llama/Meta-Llama-3.1-8B-Instruct --include "original/*" --local-dir meta-llama/Meta-Llama-3.1-8B-Instruct
```
## 7. Run local Inference 
To evaluate the performance on the validation set, run inference locally using the below command
```
python3 evaluate.py
```
Make sure you update the paths to the model and adapters in your evaluate.py file