import json
import os
import random
import time
import boto3 # type: ignore
import logging
from aws_xray_sdk.core import patch_all # type: ignore
from datetime import datetime

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize X-Ray tracing
patch_all()

# Initialize clients
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')
cloudwatch = boto3.client('cloudwatch')

# Environment variables
ORDERS_TABLE = os.environ.get('ORDERS_TABLE')
NOTIFICATION_TOPIC = os.environ.get('NOTIFICATION_TOPIC')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'dev')

def publish_metrics(status, processing_time):
    """Publish custom metrics to CloudWatch"""
    try:
        cloudwatch.put_metric_data(
            Namespace='SnapLambda',
            MetricData=[
                {
                    'MetricName': 'OrderProcessing',
                    'Dimensions': [
                        {'Name': 'Environment', 'Value': ENVIRONMENT},
                        {'Name': 'Status', 'Value': status}
                    ],
                    'Value': 1,
                    'Unit': 'Count'
                },
                {
                    'MetricName': 'ProcessingTime',
                    'Dimensions': [
                        {'Name': 'Environment', 'Value': ENVIRONMENT}
                    ],
                    'Value': processing_time,
                    'Unit': 'Milliseconds'
                }
            ]
        )
    except Exception as e:
        logger.error(f"Failed to publish metrics: {str(e)}")

def process_order(order):
    """Process the order and store in DynamoDB"""
    # Simulate processing time
    processing_delay = random.uniform(0.1, 0.5)
    time.sleep(processing_delay)
    
    # Simulate occasional processing failures (15%)
    if random.random() < 0.15:
        logger.error(f"Processing failed: Simulated random processing error for order {order['orderId']}")
        return False, "Processing error"
    
    try:
        # Add additional order information
        order['status'] = 'PROCESSED'
        order['processedAt'] = datetime.utcnow().isoformat()
        
        # Store in DynamoDB
        table = dynamodb.Table(ORDERS_TABLE)
        table.put_item(Item=order)
        
        logger.info(f"Order {order['orderId']} processed successfully and stored in DynamoDB")
        return True, None
    except Exception as e:
        logger.error(f"Failed to store order in DynamoDB: {str(e)}", exc_info=True)
        return False, str(e)

def lambda_handler(event, context):
    """Lambda handler for order processing"""
    start_time = time.time()
    
    logger.info(f"Received order for processing: {event}")
    
    try:
        # Process the order
        success, error_message = process_order(event)
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Publish custom metrics
        status = 'Success' if success else 'Failed'
        publish_metrics(status, processing_time)
        
        if success:
            # Send success notification
            if NOTIFICATION_TOPIC:
                sns.publish(
                    TopicArn=NOTIFICATION_TOPIC,
                    Subject=f"Order Processed Successfully - {ENVIRONMENT}",
                    Message=f"Order processed successfully:\n{json.dumps(event, indent=2)}"
                )
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Order processed successfully',
                    'orderId': event['orderId']
                })
            }
        else:
            logger.error(f"Order processing failed: {error_message}")
            
            # Send failure notification
            if NOTIFICATION_TOPIC:
                sns.publish(
                    TopicArn=NOTIFICATION_TOPIC,
                    Subject=f"Order Processing Failed - {ENVIRONMENT}",
                    Message=f"Order processing failed: {error_message}\n{json.dumps(event, indent=2)}"
                )
            
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'message': 'Order processing failed',
                    'error': error_message,
                    'orderId': event['orderId']
                })
            }
            
    except Exception as e:
        logger.error(f"Error in order processor: {str(e)}", exc_info=True)
        
        # Publish error metric
        cloudwatch.put_metric_data(
            Namespace='SnapLambda',
            MetricData=[{
                'MetricName': 'ProcessingErrors',
                'Dimensions': [{'Name': 'Environment', 'Value': ENVIRONMENT}],
                'Value': 1,
                'Unit': 'Count'
            }]
        )
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Internal server error during order processing'
            })
        }