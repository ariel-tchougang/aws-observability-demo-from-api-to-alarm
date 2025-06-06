# Serverless Observability Demo Guide

This guide provides step-by-step instructions for presenting the Serverless Order Processing System observability demo.

## Demo Preparation

1. Deploy the application using SAM CLI:
   ```bash
   sam build
   sam deploy --guided
   ```

2. Note the API Gateway endpoint URL from the outputs.

3. Open multiple browser tabs for:
   - CloudWatch Dashboard
   - X-Ray Traces
   - CloudWatch Logs
   - CloudWatch Alarms

## Demo Script

### Introduction (2 minutes)

"Today we're going to explore how to implement comprehensive observability in a serverless architecture. We'll see how to use AWS services to gain insights into application performance, detect issues, and troubleshoot problems."

Show the architecture diagram and explain the components:
- API Gateway for REST endpoints
- Three Lambda functions for different stages of order processing
- DynamoDB for data storage
- SNS for notifications
- CloudWatch and X-Ray for observability

### Part 1: Generating Sample Traffic (3 minutes)

"Let's start by generating some sample traffic to our application."

1. Run the test script to generate orders:
   ```bash
   ./test-orders.sh <api-endpoint> 20 1
   ```

2. Explain that this script:
   - Sends both valid and invalid orders
   - Checks status for some orders
   - Creates a realistic traffic pattern

### Part 2: Exploring CloudWatch Metrics (5 minutes)

"Now let's look at the metrics our application is generating."

1. Navigate to the CloudWatch Dashboard
2. Show and explain:
   - Lambda invocation counts across functions
   - Error rates
   - API Gateway request volume and latency
   - DynamoDB capacity consumption
   - Custom metrics for business processes

"These metrics give us a high-level view of our application's health and performance. We can see invocation counts, error rates, and latency at a glance."

### Part 3: Analyzing Logs (5 minutes)

"Let's dive deeper by looking at the application logs."

1. Navigate to CloudWatch Logs
2. Show log groups for each Lambda function
3. Demonstrate:
   - Structured JSON logs
   - Log correlation with X-Ray trace IDs
   - Error messages and stack traces
   - Log Insights queries for analysis

"Logs provide detailed information about what's happening inside our application. With structured logging, we can easily search and analyze log data."

### Part 4: Metric Filters and Alarms (3 minutes)

"We can extract metrics from logs and set up alarms to alert us when issues occur."

1. Show the metric filter that extracts error rates from logs
2. Navigate to CloudWatch Alarms
3. Demonstrate:
   - Error rate alarm
   - Latency alarm
   - Alarm history and states

"Alarms allow us to proactively detect issues before they impact users. We can set thresholds for error rates, latency, and other metrics."

### Part 5: Distributed Tracing with X-Ray (5 minutes)

"Now let's see how we can trace requests as they flow through our system."

1. Navigate to X-Ray Traces
2. Show the service map
3. Select a trace and demonstrate:
   - End-to-end request flow
   - Timing for each component
   - Error identification
   - Correlation with logs

"X-Ray gives us visibility into the entire request path, helping us identify bottlenecks and errors across service boundaries."

### Part 6: Troubleshooting Demo (5 minutes)

"Let's see how we can use these tools to troubleshoot an issue."

1. Generate some error traffic:
   ```bash
   # Send several invalid orders
   curl -X POST \
     "$API_ENDPOINT/order" \
     -H "Content-Type: application/json" \
     -d '{"customerName": "Test Customer", "quantity": 2}'
   ```

2. Show the error alarm triggering
3. Use X-Ray to identify the source of errors
4. Examine logs for detailed error information
5. Demonstrate how to correlate information across tools

"By combining metrics, logs, and traces, we can quickly identify and diagnose issues in our application."

### Conclusion and Well-Architected Connection (2 minutes)

"This demo illustrates key aspects of the AWS Well-Architected Framework, particularly the Operational Excellence pillar. By implementing comprehensive observability, we can:

1. Monitor application health and performance
2. Detect issues quickly
3. Troubleshoot problems efficiently
4. Make data-driven decisions about improvements

These practices help us build resilient, high-performing applications that meet business requirements."

## What's next?

After this demo, you may seek further knowledge about:
- Implementation details
- Best practices for observability
- Cost considerations
- Scaling observability for larger applications