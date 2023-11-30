# Amazon Transcribe announces a new speech foundation model-powered ASR system that expands support to over 100 languages
# https://aws.amazon.com/blogs/machine-learning/amazon-transcribe-announces-a-new-speech-foundation-model-powered-asr-system-that-expands-support-to-over-100-languages/

# Transcribing with the CLI
# https://docs.aws.amazon.com/transcribe/latest/dg/getting-started-cli.html

# Transcribing with Python
# https://docs.aws.amazon.com/transcribe/latest/dg/getting-started-sdk.html

# Supported formats
# https://docs.aws.amazon.com/transcribe/latest/dg/how-input.html

# aws s3 cp transcribe_ab3.mp4 s3://sagemaker-ap-southeast-1-278313627171/

import argparse
import boto3
import json
import requests
import time
import os


REGION = 'ap-southeast-1'
S3_BUCKET = 'sagemaker-ap-southeast-1-278313627171'
s3_client = boto3.client('s3', region_name = REGION)
transcribe_client = boto3.client('transcribe', region_name = REGION)


def transcribe_file(job_name, file_uri):
    transcribe_client.start_transcription_job(
        TranscriptionJobName = job_name,
        Media = {
            'MediaFileUri': file_uri
        },
        MediaFormat = 'mp4',
        LanguageCode = 'en-US'
    )

    max_tries = 60
    while max_tries > 0:
        max_tries -= 1
        job = transcribe_client.get_transcription_job(TranscriptionJobName = job_name)
        job_status = job['TranscriptionJob']['TranscriptionJobStatus']
        if job_status in ['COMPLETED', 'FAILED']:
            print(f"Job {job_name} is {job_status}.")
            if job_status == 'COMPLETED':
                uri = job['TranscriptionJob']['Transcript']['TranscriptFileUri']
                print(f'Downloading the transcript from: "{uri}"...')
                response = requests.get(uri, allow_redirects=True)
                with open(f"{job_name}.json", 'wb') as f:
                    f.write(response.content)

                r = json.loads(response.content)
                transcript = r['results']['transcripts'][0]['transcript']
                with open(f"{job_name}.txt", 'w') as f:
                    f.write(transcript)

                return transcript
            break
        else:
            print(f"Waiting for {job_name}. Current status is {job_status}.")
        time.sleep(10)


def upload_transcribe_download(file):
    with open(file, 'rb') as f:
        s3_client.upload_fileobj(f, S3_BUCKET, file)

    file_uri = f's3://{S3_BUCKET}/{file}'
    basename, _ = os.path.splitext(file)
    transcript = transcribe_file(basename, file_uri)
    print(f"Transcript saved to {basename}.json")



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', type=str, default='')
    args = parser.parse_args()

    if args.file:
        transcript = upload_transcribe_download(args.file)

    # Usage:
    # python transcribe_audio.py --file transcribe_ab3.mp4
