# MdDoc
[![GitHub stars](https://img.shields.io/github/stars/ByteMedia-AG/mddoc-public.svg?style=social)](https://github.com/ByteMedia-AG/mddoc-public/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/ByteMedia-AG/mddoc-public.svg?style=social)](https://github.com/ByteMedia-AG/mddoc-public/network)
[![GitHub issues](https://img.shields.io/github/issues/ByteMedia-AG/mddoc-public.svg)](https://github.com/ByteMedia-AG/mddoc-public/issues)
[![GitHub license](https://img.shields.io/github/license/ByteMedia-AG/mddoc-public.svg)](https://github.com/ByteMedia-AG/mddoc-public/blob/main/LICENSE)
[![GitHub last commit](https://img.shields.io/github/last-commit/ByteMedia-AG/mddoc-public.svg)](https://github.com/ByteMedia-AG/mddoc-public/commits/main)

## About MdDoc 

_MdDoc_ is a web-based application for creating, editing, and organizing documents in Markdown or plain text. Each document can include a title, description, tags, and an optional file attachment. The system tracks a full revision history: every change is saved, and archived documents additionally support versioning.

Users can restore earlier revisions or versions at any time. Deletion is non-destructive – documents are simply marked as deleted and remain available for searching and review. An integrated cleanup tool allows selective removal of deleted documents, outdated revisions, and archived content.

_MdDoc_ was created out of a personal need to better organize notes, guides, and written material accumulated over time. It helps prevent accidental data loss by preserving older document states and offers a lightweight, flexible way to manage all kinds of text-based information. While designed for general use, it is especially well suited for users who value structure, traceability, and simplicity in document management.

## Installation Instructions
Follow these steps to set up the project in a local development environment.
### Requirements
- Python 3.13 or higher
- Git (to clone the repository)
- A virtual environment tool (e.g. `venv`, `virtualenv`)
### Setup
#### 1. Clone the repository
```bash
git clone https://github.com/your-username/your-project.git
cd your-project
```
#### 2. Create and activate a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```
#### 3. Install dependencies
```bash
pip install -r requirements.txt
```
#### 4. Apply database migrations
```bash
./manage.py migrate
```
#### 5. Create an admin user
```
./manage.py createsuperuser
```
#### 6. Start the development server
```
./manage.py runserver
```
### Access
Once the server is running, open your browser and navigate to:
```
http://127.0.0.1:8000/
```
You can access the Django admin at:
```
http://127.0.0.1:8000/admin/
```
<!-- trigger license recognition -->