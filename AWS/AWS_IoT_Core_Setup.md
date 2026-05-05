# AWS IoT Core & Backend Setup Guide

This document outlines the configuration required for the FocusFlow AWS backend. The architecture consists of AWS IoT Core for message ingestion, Lambda functions for data processing and retrieval, DynamoDB for storage, and API Gateway for the dashboard interface.

## 1. DynamoDB Tables
Create four DynamoDB tables with the following schema:

| Table Name | Partition Key (String) | Sort Key (String) |
| :--- | :--- | :--- |
| `FocusFlow_CV` | `device_id` | `ts` |
| `FocusFlow_Environment` | `device_id` | `ts` |
| `FocusFlow_Session` | `device_id` | `ts` |
| `FocusFlow_Focus` | `device_id` | `ts` |

**Settings:**
- Capacity mode: **On-demand** (recommended for testing).
- Encryption: **Owned by Amazon DynamoDB**.

---

## 2. Lambda Functions

### A. Data Ingestion (Writer)
**Function Name:** `FocusFlow_CVWriter_Lambda`
- **Runtime:** Python 3.12+
- **Code:** [FocusFlow_CVWriter_Lambda.py](file:///Users/michaelkaramichalis/Developer/CMT223/AWS/FocusFlow_CVWriter_Lambda.py)
- **Role Permissions:** `dynamodb:PutItem` on all four tables.
- **Description:** Routes incoming MQTT messages to the appropriate DynamoDB table based on the topic or payload structure.

### B. Dashboard API (Reader)
**Function Name:** `FocusFlow_CVAPI_Lambda`
- **Runtime:** Python 3.12+
- **Code:** [FocusFlow_CVAPI_Lambda.py](file:///Users/michaelkaramichalis/Developer/CMT223/AWS/FocusFlow_CVAPI_Lambda.py)
- **Role Permissions:** `dynamodb:Query` on all four tables.
- **Description:** Provides REST endpoints for the FocusFlow Dashboard to fetch real-time and historical data.

---

## 3. AWS IoT Core Rules
Create a rule to trigger the `FocusFlow_CVWriter_Lambda` for all FocusFlow topics.

- **Rule Name:** `FocusFlow_Data_Routing`
- **SQL Statement:**
  ```sql
  SELECT *, topic() as topic FROM 'sdk/test/python'
  UNION ALL
  SELECT *, topic() as topic FROM 'focusflow/#'
  ```
- **Action:** Invoke Lambda function `FocusFlow_CVWriter_Lambda`.

---

## 4. API Gateway Setup
Expose the `FocusFlow_CVAPI_Lambda` via a REST API.

1. **Create REST API:** `FocusFlow_API`
2. **Create Resources & Methods:**
   - `/cv/latest` (GET)
   - `/cv/history` (GET)
   - `/env/latest` (GET)
   - `/env/history` (GET)
   - `/session/latest` (GET)
   - `/session/history` (GET)
   - `/focus/latest` (GET)
   - `/focus/history` (GET)
   - `/health` (GET)
3. **Integration:** Point all methods to `FocusFlow_CVAPI_Lambda` using **Lambda Proxy Integration**.
4. **CORS:** Enable CORS for all resources (required for the web dashboard).
5. **Deploy:** Create a stage (e.g., `prod`) and note the **Invoke URL**.

---

## 5. IAM Policy Template
Assign this policy to the execution roles of both Lambda functions (adjusting to `Query` or `PutItem` as needed for least privilege):

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:PutItem",
                "dynamodb:Query",
                "dynamodb:GetItem"
            ],
            "Resource": [
                "arn:aws:dynamodb:*:*:table/FocusFlow_CV",
                "arn:aws:dynamodb:*:*:table/FocusFlow_Environment",
                "arn:aws:dynamodb:*:*:table/FocusFlow_Session",
                "arn:aws:dynamodb:*:*:table/FocusFlow_Focus"
            ]
        },
        {
            "Effect": "Allow",
            "Action": "logs:CreateLogGroup",
            "Resource": "arn:aws:logs:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:log-group:/aws/lambda/FocusFlow_*"
        }
    ]
}
```
