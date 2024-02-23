import json
import boto3
import fitz
from decimal import Decimal
from boto3.dynamodb.types import TypeDeserializer
from datetime import datetime
import botocore
import os

# Initialize the AWS service clients
dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')


def query_dynamodb_item_with_sk_prefix(table_name, partition_key_value, sort_key_prefix):
    table = dynamodb.Table(table_name)
    response = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('PK').eq(partition_key_value) &
                               boto3.dynamodb.conditions.Key('SK').begins_with(sort_key_prefix)
    )
    items = response.get('Items')
    if items:
        return items[0]
    return None


def extract_text_from_pdf(pdf_data):
    text = ""
    pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
    for page in pdf_document:
        text += page.get_text()
    return text


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            if obj % 1 == 0:
                return int(obj)
            else:
                return float(obj)

        return super(DecimalEncoder, self).default(obj)


def lambda_handler(event, context):
    print(event)
    # Define the table name and keys
    table_name = os.environ['DYNAMO_TABLE_NAME']
    partition_key_value = event.get('USER_PK')
    sort_key_prefix = event.get('USER_DETAIL_SK')

    # Query DynamoDB for items where SK begins with "ID#"
    item = query_dynamodb_item_with_sk_prefix(table_name, partition_key_value, sort_key_prefix)

    if item:

        resumeId = item.get('SK').split('#')[-1]
        cvId = item.get('CV')

        # Prepare the response body
        body_content = json.dumps(item, cls=DecimalEncoder)

        s3_bucket_name = os.environ['S3_BUCKET_NAME']

        key = "users/" + resumeId + "/resumes/" + cvId

        try:
            # Attempt to fetch the PDF file from S3
            response = s3_client.get_object(Bucket=s3_bucket_name, Key=key)
            pdf_data = response['Body'].read()

        except botocore.exceptions.ClientError as error:
            # Check the specific error code
            error_code = error.response['Error']['Code']
            if error_code == 'AccessDenied':
                print("Access denied to the S3 object.")
                return {
                    'statusCode': 403,
                    'body': json.dumps({'message': 'Access denied to the specified S3 object'})
                }
            elif error_code == 'NoSuchKey':
                print("The specified key does not exist.")
                return {
                    'statusCode': 404,
                    'body': json.dumps({'message': 'The specified key does not exist'})
                }
            else:
                # Handle other possible exceptions
                print(f"Unexpected error: {error_code}")
                return {
                    'statusCode': 500,
                    'body': json.dumps({'message': 'Internal server error'})
                }

        # Extract text from the PDF
        processed_text = extract_text_from_pdf(pdf_data)

        prompt = (
            'Human:\n'
            f'Find below details from:\n\n{json.dumps(processed_text, indent=2)}\n\n'
            'Name:\nEmail:\nExperience in year:\nAchievements:\nTechnical skills:'
            '\nSoft skills:\nCore skills:\nEducation:\nIndustry experience:\nResponsibilities:'
            '\nAchievements against responsibility:\nCertifications:\nStrength:\n'
            'Experience type (leadership, Mid management, Senior management, Team lead, Individual contributor):'
            '\nTeam handling experience:\nIndustry type(B2B, D2C, C2C, B2C):\n\nAssistant:\" turn'
        )

        # The payload to be provided to Bedrock
        body = json.dumps(
            {
                "prompt": prompt,
                "max_tokens_to_sample": 1000,
                "temperature": 0.5,
                "top_k": 250,
                "top_p": 1,
                "stop_sequences": ["\n\nAssistant:\" turn"],
                "anthropic_version": "bedrock-2023-05-31"
            }
        )

        # The actual call to retrieve an answer from the model
        response = bedrock_runtime.invoke_model(
            body=body,
            modelId='anthropic.claude-v2:1',
            accept='*/*',
            contentType='application/json'
        )

        response_body = json.loads(response['body'].read())

        completion_text = response_body.get('completion', '').strip()

        # Including the next line character to start directly from the next line
        first_colon_pos = completion_text.find(':')
        if first_colon_pos != -1:
            # add 1 to start slicing after the colon and use strip to remove any leading/trailing whitespace or newline characters
            completion_text = completion_text[first_colon_pos + 1:].strip()

        # Update the DynamoDB item with the processed text
        update_response = update_cv_extract_in_dynamodb(table_name, partition_key_value, item['SK'], completion_text)

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'CV extract updated successfully'})
        }

    else:
        return {
            'statusCode': 404,
            'body': 'Item not found'
        }


def update_cv_extract_in_dynamodb(table_name, partition_key, sort_key, cv_extract):
    table = dynamodb.Table(table_name)

    # Get current date and time
    current_datetime = datetime.now().isoformat()

    response = table.update_item(
        Key={
            'PK': partition_key,
            'SK': sort_key
        },
        UpdateExpression="SET cvExtract = :cvExtract, cvExtractDate = :cvExtractDate",

        ExpressionAttributeValues={
            ':cvExtract': cv_extract,
            ':cvExtractDate': current_datetime
        },
        ReturnValues="UPDATED_NEW"
    )
    return response