#!/bin/bash

# Script to generate test orders for the Serverless Order Processing System demo

# Configuration
API_ENDPOINT=$1
NUM_ORDERS=${2:-20}
DELAY=${3:-1}

if [ -z "$API_ENDPOINT" ]; then
  echo "Usage: $0 <api-endpoint> [number-of-orders] [delay-seconds]"
  echo "Example: $0 https://abc123.execute-api.us-east-1.amazonaws.com/dev 20 1"
  exit 1
fi

echo "Sending $NUM_ORDERS orders to $API_ENDPOINT with ${DELAY}s delay between requests"

# Product IDs for testing
PRODUCTS=("PROD-123" "PROD-456" "PROD-789" "PROD-101" "PROD-202")

# Customer names for testing
CUSTOMERS=("John Doe" "Jane Smith" "Bob Johnson" "Alice Williams" "Charlie Brown")

# Function to generate a random order
generate_order() {
  local customer="${CUSTOMERS[$((RANDOM % ${#CUSTOMERS[@]}))]}"
  local product="${PRODUCTS[$((RANDOM % ${#PRODUCTS[@]}))]}"
  local quantity=$((RANDOM % 10 + 1))
  
  # Occasionally generate invalid orders (20% chance)
  if [ $((RANDOM % 5)) -eq 0 ]; then
    # Invalid order (missing field or negative quantity)
    if [ $((RANDOM % 2)) -eq 0 ]; then
      # Missing field
      echo "{\"customerName\": \"$customer\", \"quantity\": $quantity}"
    else
      # Negative quantity
      echo "{\"customerName\": \"$customer\", \"productId\": \"$product\", \"quantity\": -1}"
    fi
  else
    # Valid order
    echo "{\"customerName\": \"$customer\", \"productId\": \"$product\", \"quantity\": $quantity}"
  fi
}

# Send orders
for ((i=1; i<=$NUM_ORDERS; i++)); do
  ORDER=$(generate_order)
  echo "Sending order $i: $ORDER"
  
  RESPONSE=$(curl -s -X POST \
    "$API_ENDPOINT/order" \
    -H "Content-Type: application/json" \
    -d "$ORDER")
  
  echo "Response: $RESPONSE"
  
  # Extract order ID if available
  ORDER_ID=$(echo $RESPONSE | grep -o '"orderId":"[^"]*"' | cut -d'"' -f4)
  
  if [ ! -z "$ORDER_ID" ]; then
    echo "Order ID: $ORDER_ID"
    
    # Check order status (50% chance)
    if [ $((RANDOM % 2)) -eq 0 ]; then
      echo "Checking status for order $ORDER_ID"
      STATUS_RESPONSE=$(curl -s -X GET "$API_ENDPOINT/order/$ORDER_ID")
      echo "Status response: $STATUS_RESPONSE"
    fi
  fi
  
  # Wait before sending next order
  sleep $DELAY
done

echo "Test complete. Sent $NUM_ORDERS orders."