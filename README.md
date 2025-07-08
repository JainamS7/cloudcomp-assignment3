# Pi Finder - Cloud Computing Assignment 3

A distributed web application that calculates π(x) - the number of primes less than or equal to a given value x. This project demonstrates cloud computing concepts including serverless functions, distributed architecture, caching strategies, and scalable deployment.

![Pi Finder](https://img.shields.io/badge/Cloud-Computing-blue) ![Python](https://img.shields.io/badge/Python-3.9-green) ![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Platform-orange)

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Setup and Deployment](#setup-and-deployment)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Technical Implementation](#technical-implementation)
- [File Structure](#file-structure)
- [Contributing](#contributing)

## 🔍 Overview

Pi Finder is a cloud-based application that efficiently computes the prime counting function π(x), which returns the number of prime numbers less than or equal to x. The application uses a hybrid approach:

- **Small values (< 10 million)**: Uses Google Cloud Run endpoints with optional memcache for faster responses
- **Large values (≥ 10 million)**: Employs distributed query logic across multiple compute instances

The application leverages precomputed prime data stored in Google Cloud Storage, providing quick lookup for large ranges of numbers.

## 🏗️ Architecture

The application follows a distributed microservices architecture:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Load Balancer │    │   Backend       │
│   (HTML/JS)     │───▶│   (Cloud Run)   │───▶│   (Cloud Func)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │  Cloud Storage  │
                                               │  (Data Files)   │
                                               └─────────────────┘
```

### Components:

1. **Frontend**: Single-page web application with responsive design
2. **Cloud Run Services**: Scalable endpoints for small value processing
3. **Cloud Functions**: Serverless backend for data processing
4. **Cloud Storage**: Bucket containing precomputed prime data files
5. **Kubernetes Deployment**: Container orchestration for distributed processing
6. **Distributed Endpoints**: Multiple IP addresses for handling large value ranges

## ✨ Features

- **Responsive Web Interface**: Clean, modern UI with real-time input validation
- **Dual Processing Modes**: 
  - Memcache-enabled for faster repeated queries
  - Direct calculation for fresh computations
- **Distributed Architecture**: Automatic routing based on input value ranges
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **CORS Support**: Cross-origin resource sharing for web deployment
- **Loading States**: Visual feedback during computation
- **Range Validation**: Input validation with appropriate error messages

## 🚀 Setup and Deployment

### Prerequisites

- Google Cloud Platform account
- Cloud SDK installed and configured
- Python 3.9+
- Flask framework
- Google Cloud Storage bucket

### Backend Deployment

1. **Deploy Cloud Function**:
   ```bash
   # Extract the serverless function
   unzip "Serverless function.zip"
   
   # Deploy to Google Cloud Functions
   gcloud functions deploy pi-finder \
     --runtime python39 \
     --trigger-http \
     --allow-unauthenticated \
     --source .
   ```

2. **Setup Cloud Storage**:
   ```bash
   # Create storage bucket
   gsutil mb gs://cloudcompassignment3
   
   # Upload data files (data_16.1.txt to data_16.16.txt)
   gsutil cp data_16.*.txt gs://cloudcompassignment3/
   ```

3. **Deploy Kubernetes Resources**:
   ```bash
   kubectl apply -f deployment-12.yaml
   ```

### Frontend Deployment

1. **Deploy to Cloud Run**:
   ```bash
   # Build and deploy the frontend
   gcloud run deploy pi-finder-frontend \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

2. **Static Hosting** (Alternative):
   - Deploy `index.html` to any static hosting service
   - Ensure CORS is properly configured for API endpoints

### Environment Configuration

Update the endpoint URLs in `index.html` to match your deployed services:

```javascript
// Cloud Run endpoints
const MEMCACHE_ENDPOINT = "https://memcache-84132083246.us-central1.run.app";
const DIRECT_ENDPOINT = "https://try4-84132083246.us-central1.run.app";

// Distributed endpoints
const DISTRIBUTED_ENDPOINTS = [
  "http://34.48.174.206:8080/find",
  "http://34.86.161.38:8080/find",
  "http://34.150.242.225:8080/find",
  "http://34.86.189.230:8080/find"
];
```

## 💻 Usage

### Web Interface

1. **Access the Application**: Open `index.html` in a web browser or visit the deployed URL
2. **Enter Value**: Input a positive number in the text field
3. **Select Processing Mode**: 
   - For values < 10 million: Choose between "Use Memcache" or "Direct Calculation"
   - For values ≥ 10 million: Distributed query is used automatically
4. **Calculate**: Click "Calculate π(x)" to get the result

### Input Ranges

- **Small values (1 to 9,999,999)**: Processed via Cloud Run endpoints
- **Large values (10,000,000+)**: Processed via distributed compute instances
- **Maximum supported**: Up to 10^25 (limited by available data files)

### Example Queries

- `π(100)` = 25 (there are 25 primes ≤ 100)
- `π(1000)` = 168 (there are 168 primes ≤ 1000)
- `π(1000000)` = 78498 (there are 78,498 primes ≤ 1,000,000)

## 📡 API Endpoints

### Cloud Run Endpoints

#### POST `/`
Calculate π(x) for values < 10 million

**Request:**
```
Content-Type: application/x-www-form-urlencoded
x=1000
```

**Response:**
```json
{
  "x": 1000,
  "result": 168,
  "file": "data_16.1.txt",
  "start_time": "2023-XX-XXTXX:XX:XX",
  "end_time": "2023-XX-XXTXX:XX:XX",
  "duration_seconds": 0.15,
  "hostname": "instance-name"
}
```

### Distributed Endpoints

#### GET `/find?x={value}`
Calculate π(x) for values ≥ 10 million

**Request:**
```
GET http://34.48.174.206:8080/find?x=50000000
```

**Response:**
```
3001134
```

### Value Range Distribution

| Range | Endpoint |
|-------|----------|
| 1 - 383,028,000,000 | 34.48.174.206:8080 |
| 383,029,000,000 - 45,216,200,000,000 | 34.86.161.38:8080 |
| 45,216,300,000,000 - 9,412,080,000,000,000 | 34.150.242.225:8080 |
| 9,412,090,000,000,000 - 10^25 | 34.86.189.230:8080 |

## 🔧 Technical Implementation

### Data Storage Strategy

The application uses 16 data files (`data_16.1.txt` to `data_16.16.txt`) stored in Google Cloud Storage, each containing precomputed prime counts for specific ranges:

```python
FILE_BOUNDS = {
    "data_16.1.txt": ["1.000", "4052740000"],
    "data_16.2.txt": ["4052750000", "34846100000"],
    # ... additional ranges
}
```

### Caching Strategy

- **Memcache Endpoint**: Utilizes Google Cloud Memcache for faster repeated queries
- **Direct Calculation**: Bypasses cache for fresh computations
- **File Caching**: Downloaded data files are cached locally in Cloud Functions

### Error Handling

- Input validation for positive numbers
- Range checking for supported values
- Network error handling with fallback mechanisms
- CORS error handling with new tab fallback

### Performance Optimizations

- **Binary Search**: Efficient lookup in sorted data files
- **Lazy Loading**: Data files downloaded only when needed
- **Connection Pooling**: Reused connections for multiple requests
- **Distributed Load**: Load balanced across multiple endpoints

## 📁 File Structure

```
cloudcomp-assignment3/
├── index.html              # Frontend web application
├── main.py                 # Cloud Function backend code
├── requirements.txt        # Python dependencies
├── deployment-12.yaml      # Kubernetes deployment configuration
├── Serverless function.zip # Packaged Cloud Function
└── README.md              # This file
```

### Key Files

- **`index.html`**: Complete web application with embedded CSS and JavaScript
- **`main.py`**: Cloud Function that handles prime counting logic
- **`requirements.txt`**: Python dependencies (Flask, Google Cloud Storage)
- **`deployment-12.yaml`**: Kubernetes deployment for distributed processing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -m 'Add feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

### Development Guidelines

- Follow Python PEP 8 style guidelines
- Add appropriate error handling
- Include documentation for new features
- Test across different input ranges
- Ensure CORS compatibility

## 📄 License

This project is part of a Cloud Computing assignment and is intended for educational purposes.

## 🙏 Acknowledgments

- Google Cloud Platform for hosting infrastructure
- Flask framework for backend development
- Modern web standards for responsive frontend design

---

**© 2023 Pi Finder - A Cloud Computing Project**