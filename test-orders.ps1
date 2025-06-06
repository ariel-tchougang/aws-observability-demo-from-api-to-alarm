# PowerShell script to generate test orders for the Serverless Order Processing System demo

param(
    [Parameter(Mandatory=$true)]
    [string]$ApiEndpoint,
    
    [Parameter(Mandatory=$false)]
    [int]$NumOrders = 20,
    
    [Parameter(Mandatory=$false)]
    [int]$DelaySeconds = 1
)

Write-Host "Sending $NumOrders orders to $ApiEndpoint with ${DelaySeconds}s delay between requests"

# Product IDs for testing
$Products = @("PROD-123", "PROD-456", "PROD-789", "PROD-101", "PROD-202")

# Customer names for testing
$Customers = @("John Doe", "Jane Smith", "Bob Johnson", "Alice Williams", "Charlie Brown")

# Function to generate a random order
function Generate-Order {
    $customer = $Customers | Get-Random
    $product = $Products | Get-Random
    $quantity = Get-Random -Minimum 1 -Maximum 11
    
    # Occasionally generate invalid orders (20% chance)
    if ((Get-Random -Minimum 0 -Maximum 5) -eq 0) {
        # Invalid order (missing field or negative quantity)
        if ((Get-Random -Minimum 0 -Maximum 2) -eq 0) {
            # Missing field
            return @{
                customerName = $customer
                quantity = $quantity
            } | ConvertTo-Json
        } else {
            # Negative quantity
            return @{
                customerName = $customer
                productId = $product
                quantity = -1
            } | ConvertTo-Json
        }
    } else {
        # Valid order
        return @{
            customerName = $customer
            productId = $product
            quantity = $quantity
        } | ConvertTo-Json
    }
}

# Send orders
for ($i = 1; $i -le $NumOrders; $i++) {
    $order = Generate-Order
    Write-Host "Sending order ${i}: $order"
    
    $response = Invoke-RestMethod -Uri "$ApiEndpoint/order" -Method Post -Body $order -ContentType "application/json" -ErrorAction SilentlyContinue
    
    if ($response) {
        Write-Host "Response: $($response | ConvertTo-Json -Compress)"
        
        # Extract order ID if available
        if ($response.orderId) {
            Write-Host "Order ID: $($response.orderId)"
            
            # Check order status (50% chance)
            if ((Get-Random -Minimum 0 -Maximum 2) -eq 0) {
                Write-Host "Checking status for order $($response.orderId)"
                try {
                    $statusResponse = Invoke-RestMethod -Uri "$ApiEndpoint/order/$($response.orderId)" -Method Get -ErrorAction SilentlyContinue
                    Write-Host "Status response: $($statusResponse | ConvertTo-Json -Compress)"
                } catch {
                    Write-Host "Error checking status: $_"
                }
            }
        }
    } else {
        Write-Host "Error sending order"
    }
    
    # Wait before sending next order
    Start-Sleep -Seconds $DelaySeconds
}

Write-Host "Test complete. Sent $NumOrders orders."