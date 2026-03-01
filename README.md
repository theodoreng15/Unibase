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

Unibase operates on a strict separation of concerns: physical data lives in the cloud, while logical state lives in MongoDB.

Because files are mathematically sliced into dozens of chunks and scattered across different cloud providers (Box, Google Drive, Dropbox), the system needs a source of truth to put them back together. We use an asynchronous MongoDB cluster to act as this master ledger.

When a file is uploaded, Unibase creates a FileMetadata document in MongoDB using the file's name as the primary _id. As the background tasks finish uploading individual chunks to the cloud, they receive a unique provider_id from the respective cloud API. Unibase uses atomic $set operations to instantly log this ChunkMetadata—which includes the chunk's index, assigned cloud provider, cloud ID, and SHA-256 hash—into the file's master document.

---
