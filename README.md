# Serverless Order Processing System - Observability Demo

This demo showcases a comprehensive approach to observability in a serverless architecture using AWS services.

![Serverless Observability Architecture](resources/snaplambda-observability.png)

## Architecture Overview

The demo implements a simple serverless order processing system with these components:

| Component                | Role                                                  |
| ------------------------ | ----------------------------------------------------- |
| API Gateway              | Exposes REST endpoints for order submission and status checking  |
| Lambda: `OrderValidator` | Validates incoming orders                             |
| Lambda: `OrderProcessor` | Processes valid orders and saves to DynamoDB          |
| Lambda: `OrderStatus`    | Retrieves order status                                |
| DynamoDB                 | Stores order and status information                   |
| SNS Topic                | Publishes failure alerts                              |
| CloudWatch               | Stores logs, metrics, dashboards                      |
| AWS X-Ray                | Traces API-to-Lambda-to-DynamoDB interactions         |
| CloudTrail               | Logs API activity and changes                         |

👉 Check [architecture details](./architecture-components.md)

![Architecture diagram](resources/serverless-observability-architecture.png)

---

## Observability Features Demonstrated

1. **Metrics**:
   - Built-in Lambda, API Gateway, and DynamoDB metrics
   - Custom business metrics (order validation rate, processing time)

2. **Logs**:
   - Structured logging across all Lambda functions
   - Log correlation with X-Ray trace IDs

3. **Metric Filters**:
   - Extracting error rates from logs
   - Creating custom metrics from log patterns

4. **Alarms**:
   - Error rate thresholds
   - Latency thresholds
   - Composite alarms

5. **Traces with X-Ray**:
   - End-to-end request tracing
   - Service maps
   - Latency analysis

## Deployment Instructions

### Prerequisites

- AWS CLI installed and configured
- AWS SAM CLI installed
- Python 3.11+

### Deploy the Application

1. Clone this repository
2. Navigate to the project directory
3. Deploy using SAM CLI:

```bash
sam build
sam deploy --guided --region <YOUR_AWS_REGION> --profile <YOUR_AWS_PROFILE>
```

Follow the prompts to complete the deployment.

## Testing the Application

👉 Check [step-by-step demo guide](./demo-guide.md)

### Submit an Order

```bash
curl -X POST \
  https://{api-id}.execute-api.{region}.amazonaws.com/{stage}/order \
  -H 'Content-Type: application/json' \
  -d '{
    "customerName": "John Doe",
    "productId": "PROD-123",
    "quantity": 2
  }'
```

### Check Order Status

```bash
curl -X GET \
  https://{api-id}.execute-api.{region}.amazonaws.com/{stage}/order/{orderId}
```

## Observability Demo Walkthrough

### 1. CloudWatch Metrics

Navigate to CloudWatch > Metrics to observe:

- **Built-in metrics**: Lambda invocations, errors, duration
- **Custom metrics**: Order validation rate, processing time
- **API Gateway metrics**: Request count, latency, errors

### 2. CloudWatch Logs

Navigate to CloudWatch > Log groups to observe:

- Structured logs from Lambda functions
- Error patterns
- Correlation with X-Ray trace IDs

### 3. CloudWatch Metric Filters

Navigate to CloudWatch > Log groups > Metric filters to observe:

- Error rate extraction from logs
- Custom metrics created from log patterns

### 4. CloudWatch Alarms

Navigate to CloudWatch > Alarms to observe:

- Error rate alarms
- Latency alarms
- Alarm states and history

### 5. X-Ray Traces

Navigate to X-Ray > Traces to observe:

- End-to-end request flow
- Service map visualization
- Latency breakdown by service
- Error identification

## Troubleshooting Scenarios

### Scenario 1: High Error Rate

1. Submit multiple invalid orders
2. Observe error metrics increasing
3. See alarms triggering
4. Use X-Ray to identify the source of errors
5. Correlate with logs for detailed error information

### Scenario 2: Performance Degradation

1. Submit many orders in quick succession
2. Observe latency metrics
3. Use X-Ray to identify bottlenecks
4. Check CloudWatch Logs for any warnings or errors

## Well-Architected Framework Connection

This demo illustrates key aspects of the AWS Well-Architected Framework:

- **Operational Excellence**: Comprehensive monitoring and observability
- **Reliability**: Error detection and notification
- **Performance Efficiency**: Latency tracking and bottleneck identification
- **Security**: Proper IAM permissions and secure API endpoints
- **Cost Optimization**: Serverless architecture with pay-per-use pricing

## Ideas of improvements

- Store non validated orders into another DynamoDB table
- Write validated orders into an SQS queue and have Order Processing Lambda function read from it

## Clean Up

To avoid incurring charges, delete the resources when you're done:

```bash
sam delete --region <YOUR_AWS_REGION> --profile <YOUR_AWS_PROFILE>
```