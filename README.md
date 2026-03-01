# 🚀 Unibase API

> **A high-performance, unified distributed file system built across multiple cloud providers.**
> *Built for HackIllinois 2026*

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Async-47A248.svg)](https://www.mongodb.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

## 🌍 The Impact

Modern cloud storage is fragmented. Users are forced to juggle multiple free-tier accounts across Google Drive, Box, and Dropbox, constantly worrying about individual file size limits and account quotas. 

**Unibase solves this by creating a single, massive virtual hard drive. All accessible through an API.**

By striping data across multiple cloud providers in parallel, Unibase essentially turns standard cloud storage accounts into a high-speed RAID cluster. It circumvents single-provider file limits, maximizes network bandwidth through concurrent uploads, and provides a unified interface for all your data. 

This project was inspired by the Youtube Video: ["I tried using Discord as a Database for my Website"
](https://www.youtube.com/watch?v=QjiuozL8vrM)


## ✨ Key Features

- **Asynchronous Pipelining:** Files aren't just uploaded; they are streamed. Unibase dynamically <ins>fragments</ins> files and <ins>parallel-uploads</ins> chunks *while* the file is still being read, ensuring minimal memory footprint and faster upload times.
- **Dynamic File Fragmentation:** Instead of loading massive uploads into server RAM, Unibase reads files in small bursts and mathematically slices them into <ins>fixed-size binary chunks</ins> on the fly (256 MB). This prevents memory exhaustion on both what the server can handle plus the restrictive cloud provider limits. 
- **Enterprise-Grade Validation:** Strict data typing through Pydantic is paired with real time SHA-256 hasing. Unibase calculates a cryptographic checksum for every single chunk during the initial fragmentation, strictly verifying those exact hashes when pulling the pieces back down to guarantee zero data corruption during reconstruction.
- **Load Balancing:** A round-robin algorithm automatically distributes data chunks evenly across Google Drive, Box, and Dropbox.

---

## 📖 API Reference & Usage

### 0. Database Storage
To streamline demos, all cloud authentication are managed on the backend. The API is currently hosted on a remote server, allowing developers  to test the endpoints directly using the provided cURL commands without the need to clone the repository or configure environment variables.


### 1. Upload a File (`POST /upload`)
Uploads a file to the Unibase engine. The API streams the file, fragments it into chunks, generates SHA-256 checksums, and distributes the chunks across connected cloud providers.

**Request (cURL):**
```bash
curl -s -X POST "https://sleekiest-unctuously-janise.ngrok-free.dev/upload" -F "file=@cat.jpg" | python3 -m json.tool
```

### 2. Reconstruct & Fetch File (`GET /files/{file_name}`)
Queries the MongoDB instance for the metadata on chunk locations, pulls the pieces back from the respective cloud providers, and reconstitutes the file on the backend server. Useful for verifying data integrity and checking retrieval speeds.

**Request (cURL):**
```bash
curl -X GET "https://sleekiest-unctuously-janise.ngrok-free.dev/cat.jpg" |  python3 -m json.tool
```

### 3. Delete File (`DELETE /files/{file_name}`)
Triggers a comprehensive teardown of the distributed file. It deletes the physical chunks from Box, Google Drive, and Dropbox, completely removes the logical file record from MongoDB, and recalculates your new storage capacity.

**Request (cURL):**
```bash
curl -X DELETE "http://127.0.0.1:8000/files/cat.jpg" |  python3 -m json.tool
```

## 🧠 Architecture: How It Works

### 1. Fragmentation & Hashing (`fragmenter.py`)
When a file is uploaded to the FastAPI endpoint, Unibase reads it into memory in small, manageable bursts. As it reads, it mathematically slices the data into fixed-size `.bin` chunks (e.g., 4MB). During this process, a rolling SHA-256 hash is generated for both the individual chunks and the master file.

### 2. Parallel Cloud Uploads (`chunk_uploader.py`)
Once a chunk hits its size limit, it is instantly sealed. A background `asyncio` task is triggered to upload that specific chunk to its assigned cloud provider (Box, Google Drive, etc.) via `httpx`. The main thread immediately goes back to chopping the next chunk, creating a highly efficient pipeline.

### 3. Metadata Indexing (`store_metadata.py`)
As cloud providers confirm the receipt of a chunk, Unibase receives a unique `provider_id`. This ID, along with the chunk's index, size, and hash, is validated through a Pydantic model and pushed to MongoDB via `$set` operations, storing the file mapping as a highly-searchable JSON document.

### 4. Seamless Reconstruction
When a user requests a file, Unibase queries MongoDB to retrieve the sorted list of cloud IDs. It then issues parallel download requests to the respective cloud providers, verifies the SHA-256 hashes of the returning data, stitches the chunks back together in perfect mathematical order, and streams the unified file back to the user.

---
