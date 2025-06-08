import json
import os
import random
import uuid
import boto3 # type: ignore
import logging
from aws_xray_sdk.core import patch_all # type: ignore
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize X-Ray tracing
patch_all()

sns = boto3.client('sns')
cloudwatch = boto3.client('cloudwatch')

NOTIFICATION_TOPIC = os.environ.get('NOTIFICATION_TOPIC')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'dev')

def publish_metrics(is_valid, processing_time_millis):
    """Publish custom metrics to CloudWatch"""
    try:
        cloudwatch.put_metric_data(
            Namespace='SnapLambda',
            MetricData=[
                {
                    'MetricName': 'OrderValidation',
                    'Dimensions': [
                        {'Name': 'Environment', 'Value': ENVIRONMENT},
                        {'Name': 'Status', 'Value': 'Valid' if is_valid else 'Invalid'}
                    ],
                    'Value': 1,
                    'Unit': 'Count'
                },
                {
                    'MetricName': 'ValidationProcessingTime',
                    'Dimensions': [
                        {'Name': 'Environment', 'Value': ENVIRONMENT}
                    ],
                    'Value': processing_time_millis,
                    'Unit': 'Milliseconds'
                }
            ]
        )
    except Exception as e:
        logger.error(f"Failed to publish metrics: {str(e)}")

def validate_order(order):
    """Validate the order data"""
    required_fields = ['customerName', 'productId', 'quantity']
    
    for field in required_fields:
        if field not in order:
            logger.error(f"Validation failed: Missing required field '{field}' - order_id {order.get('orderId')}")
            return False
    
    if not isinstance(order['quantity'], int) or order['quantity'] <= 0:
        logger.error(f"Validation failed: Invalid quantity {order.get('quantity')} - order_id {order.get('orderId')}")
        return False
    
    # Simulate occasional validation failures (10%)
    # TODO 1: remove or comment out this random test to fix troubleshooting case
    if random.random() < 0.1:
        logger.error(f"Validation failed: Simulated random validation error - order_id {order.get('orderId')}")
        return False
        
    return True

def lambda_handler(event, context):
    """Lambda handler for order validation"""
    start_time = time.time()
    
    logger.info(f"Received order validation request: {event}")
    
    try:
        if 'body' in event:
            body = json.loads(event['body'])
        else:
            body = event
            
        order_id = str(uuid.uuid4())
        body['orderId'] = order_id
        
        is_valid = validate_order(body)
        
        processing_time_millis = (time.time() - start_time) * 1000
        
        publish_metrics(is_valid, processing_time_millis)
        
        if is_valid:
            logger.info(f"Order {order_id} validated successfully")
            
            lambda_client = boto3.client('lambda')
            lambda_client.invoke(
                FunctionName=f"SnapLambda-OrderProcessor-{ENVIRONMENT}",
                InvocationType='Event',
                Payload=json.dumps(body)
            )
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'message': 'Order validated and submitted for processing',
                    'orderId': order_id
                })
            }
        else:
            logger.warning(f"Order validation failed for request: {body}")
            
            if NOTIFICATION_TOPIC:
                sns.publish(
                    TopicArn=NOTIFICATION_TOPIC,
                    Subject=f"Order Validation Failed - {ENVIRONMENT}",
                    Message=f"Order validation failed:\n{json.dumps(body, indent=2)}"
                )
            
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'message': 'Order validation failed',
                    'errors': ['Invalid order data']
                })
            }
            
    except Exception as e:
        logger.error(f"Error processing order: {str(e)}", exc_info=True)
        
        cloudwatch.put_metric_data(
            Namespace='SnapLambda',
            MetricData=[{
                'MetricName': 'ValidationErrors',
                'Dimensions': [{'Name': 'Environment', 'Value': ENVIRONMENT}],
                'Value': 1,
                'Unit': 'Count'
            }]
        )
        
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'message': 'Internal server error during order validation'
            })
        }