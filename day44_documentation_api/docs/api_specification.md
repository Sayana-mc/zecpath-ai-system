\# HR Interview AI – API Specification



\## 1. Base Information



Base URL:



/api/v1



Content-Type:



application/json



The API uses JSON request and response formats.



\---



\# 2. API Endpoints



\## 2.1 Health Check



\### Endpoint



GET /api/v1/health



\### Purpose



Checks whether the HR AI service is available.



\### Response



```json

{

&#x20;   "status": "healthy",

&#x20;   "service": "hr-interview-ai",

&#x20;   "version": "1.0.0"

}

