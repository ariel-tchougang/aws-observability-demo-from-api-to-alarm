# Architecture Components

## Main Components

### Client
- Sends requests to API Gateway
- Submits orders and checks order status

### API Gateway
- Exposes REST endpoints
- Routes requests to appropriate Lambda functions
- Endpoints:
  - POST /order - Submit new order
  - GET /order/{orderId} - Check order status

### Lambda Functions

#### Order Validator
- Validates incoming order requests
- Checks for required fields and valid data
- Forwards valid orders to Order Processor
- Sends notifications for invalid orders

#### Order Processor
- Processes valid orders
- Stores order data in DynamoDB
- Sends notifications for processing results

#### Order Status
- Retrieves order information from DynamoDB
- Returns order status to client

### DynamoDB
- Stores order information
- Schema includes:
  - orderId (primary key)
  - customerName
  - productId
  - quantity
  - status
  - processedAt

### SNS Topic
- Sends notifications about order processing
- Used for both success and failure notifications

## Observability Components

### CloudWatch Logs
- Captures application logs from all Lambda functions
- Stores API Gateway access logs

### CloudWatch Metrics
- Built-in metrics for all AWS services
- Custom business metrics:
  - Order validation rate
  - Processing time
  - Success/failure rates

### CloudWatch Alarms
- Monitors error rates
- Alerts on latency thresholds
- Composite alarms for complex conditions

### X-Ray
- Provides distributed tracing
- Creates service maps
- Helps identify bottlenecks and errors

### CloudWatch Dashboard
- Visualizes all metrics in one place
- Shows system health at a glance
- Includes custom and built-in metrics