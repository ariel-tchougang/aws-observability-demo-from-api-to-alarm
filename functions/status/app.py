import json
import os
import time
import boto3
import logging
import decimal
from aws_xray_sdk.core import patch_all
from botocore.exceptions import ClientError

# Helper class to convert Decimal to float for JSON serialization
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize X-Ray tracing
patch_all()

# Initialize clients
dynamodb = boto3.resource('dynamodb')
cloudwatch = boto3.client('cloudwatch')

# Environment variables
ORDERS_TABLE = os.environ.get('ORDERS_TABLE')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'dev')

def publish_metrics(status_found, processing_time):
    """Publish custom metrics to CloudWatch"""
    try:
        cloudwatch.put_metric_data(
            Namespace='SnapLambda',
            MetricData=[
                {
                    'MetricName': 'OrderStatusLookup',
                    'Dimensions': [
                        {'Name': 'Environment', 'Value': ENVIRONMENT},
                        {'Name': 'Result', 'Value': 'Found' if status_found else 'NotFound'}
                    ],
                    'Value': 1,
                    'Unit': 'Count'
                },
                {
                    'MetricName': 'StatusLookupTime',
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

def get_order_status(order_id):
    """Retrieve order status from DynamoDB"""
    table = dynamodb.Table(ORDERS_TABLE)
    
    try:
        response = table.get_item(Key={'orderId': order_id})
        
        if 'Item' in response:
            logger.info(f"Order {order_id} found in database")
            return True, response['Item']
        else:
            logger.warning(f"Order {order_id} not found in database")
            return False, None
            
    except ClientError as e:
        logger.error(f"DynamoDB error: {str(e)}", exc_info=True)
        raise

def lambda_handler(event, context):
    """Lambda handler for order status retrieval"""
    start_time = time.time()
    
    logger.info(f"Received order status request: {event}")
    
    try:
        # Extract order ID from path parameters
        if 'pathParameters' in event and event['pathParameters'] and 'orderId' in event['pathParameters']:
            order_id = event['pathParameters']['orderId']
        else:
            logger.error("No order ID provided in request")
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'message': 'Order ID is required'
                })
            }
        
        # Get order status
        found, order_data = get_order_status(order_id)
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Publish custom metrics
        publish_metrics(found, processing_time)
        
        if found:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(order_data, cls=DecimalEncoder)
            }
        else:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'message': f"Order {order_id} not found"
                })
            }
            
    except Exception as e:
        logger.error(f"Error retrieving order status: {str(e)}", exc_info=True)
        
        # Publish error metric
        cloudwatch.put_metric_data(
            Namespace='SnapLambda',
            MetricData=[{
                'MetricName': 'StatusErrors',
                'Dimensions': [{'Name': 'Environment', 'Value': ENVIRONMENT}],
                'Value': 1,
                'Unit': 'Count'
            }]
        )
        
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'message': 'Internal server error while retrieving order status'
            })
        }