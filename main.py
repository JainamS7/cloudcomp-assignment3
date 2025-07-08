import os
import logging
import socket
from datetime import datetime
from flask import jsonify, request
import functions_framework
from google.cloud import storage

# Define the file bounds dictionary.
FILE_BOUNDS = {
    "data_16.1.txt": ["1.000", "4052740000"],
    "data_16.2.txt": ["4052750000", "34846100000"],
    "data_16.3.txt": ["34846200000", "81574500000"],
    "data_16.4.txt": ["81574600000", "383028000000"],
    "data_16.5.txt": ["383029000000", "850312000000"],
    "data_16.6.txt": ["850313000000", "4175950000000"],
    "data_16.7.txt": ["4175960000000", "8848790000000"],
    "data_16.8.txt": ["8848800000000", "45216200000000"],
    "data_16.9.txt": ["45216300000000", "439360000000000"],
    "data_16.10.txt": ["439361000000000", "906643000000000"],
    "data_16.11.txt": ["906646000000000", "4739250000000000"],
    "data_16.12.txt": ["4739260000000000", "9412080000000000"],
    "data_16.13.txt": ["9412090000000000", "50849000000000000"],
    "data_16.14.txt": ["50849100000000000", "97577300000000000"],
    "data_16.15.txt": ["97577400000000000", "543055000000000000"],
    "data_16.16.txt": ["543056000000000000", "10000000000000000000000000"]
}

# Change this if your bucket name is different.
BUCKET_NAME = 'cloudcompassignment3'

def download_file(file_name):
    """Download the file from Cloud Storage if not present locally."""
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(file_name)
    local_path = os.path.join(os.getcwd(), file_name)
    blob.download_to_filename(local_path)
    logging.info("Downloaded %s to %s", file_name, local_path)
    return local_path

def find_file(x_value):
    """
    Given an x_value, check FILE_BOUNDS to determine which file should contain it.
    If the file is not already present locally, download it.
    Returns the local file path or None if no file matches.
    """
    x_float = float(x_value)
    for file_name, bounds in FILE_BOUNDS.items():
        lower, upper = float(bounds[0]), float(bounds[1])
        if lower <= x_float < upper:
            local_path = os.path.join(os.getcwd(), file_name)
            if not os.path.exists(local_path):
                local_path = download_file(file_name)
            return local_path
    return None

def read_data_file(file_path):
    """
    Reads the data file and stores the values in an array.
    Each element is a tuple (x, pi(x)).
    """
    data_array = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or line.startswith('//'):
                    continue
                parts = line.split()
                if len(parts) < 2:
                    continue
                try:
                    x_val = float(parts[0].replace(',', ''))
                    pi_val = int(parts[1].replace(',', ''))
                    data_array.append((x_val, pi_val))
                except ValueError:
                    continue
    except FileNotFoundError:
        logging.error("File %s not found.", file_path)
    return data_array

def find_pi_value(x_target, data_array):
    """
    Searches the data array for the given x_target.
    If an exact match is found (within 1e-6), returns (True, pi_value, None, None).
    Otherwise, returns the last record with x < x_target and the first record with x > x_target.
    """
    lower_record = None
    upper_record = None
    for x_val, pi_val in data_array:
        if abs(x_val - x_target) < 1e-6:
            return True, pi_val, None, None
        if x_val < x_target:
            lower_record = (x_val, pi_val)
        elif x_val > x_target:
            upper_record = (x_val, pi_val)
            break
    return False, None, lower_record, upper_record

@functions_framework.http
def hello_http(request):
    """
    HTTP Cloud Function.
    Expects a POST request with form parameter 'x'.
    Uses find_file to determine (and download if needed) which file contains x,
    reads the file into an array, and returns the result from find_pi_value.
    Also includes the file name in the response.
    """
    start_time = datetime.now()
    hostname = socket.gethostname()

    x_input = request.form.get('x', '').replace(',', '')
    try:
        x_value = float(x_input)
    except ValueError:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        return jsonify({
            'error': "Please enter a valid number.",
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration,
            'hostname': hostname
        }), 400

    file_path = find_file(x_value)
    if file_path is None:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        return jsonify({
            'error': "No file found for the provided x value.",
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration,
            'hostname': hostname
        }), 400

    data_array = read_data_file(file_path)
    found, pi_value, lower_record, upper_record = find_pi_value(x_value, data_array)
    file_used = os.path.basename(file_path)
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    if found:
        return jsonify({
            'x': x_value,
            'result': pi_value,
            'file': file_used,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration,
            'hostname': hostname
        })
    else:
        lower_primes = lower_record[1] if lower_record is not None else "unknown"
        upper_primes = upper_record[1] if upper_record is not None else "unknown"
        return jsonify({
            'x': x_value,
            'file': file_used,
            'message': f"There are at least {lower_primes} primes less than {x_value} and at most {upper_primes} primes less than {x_value}",
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration,
            'hostname': hostname
        }), 200
