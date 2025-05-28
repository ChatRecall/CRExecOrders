# ChatRecall Executive Order Downloader

A desktop application for downloading and managing U.S. Executive Orders. This tool allows users to fetch, download, and organize executive orders from the Federal Register.

## Features

- Fetch executive orders from the Federal Register API by year or year range
- Download executive orders as PDF files
- View downloaded and not-yet-downloaded executive orders
- Search and filter executive orders by keyword
- Organize executive orders in a local directory
- View PDF files with your system's default PDF viewer

## Installation

### Prerequisites

- Python 3.8+
- PySide6
- WrapSideSix library
- WrapConfig library
- WrapCapExecOrders library

## Installation

```bash
# Clone the repository
git clone https://github.com/ChatRecall/CRExecOrders.git
cd CRExecOrders

# Install dependencies
pip install -e .
```

## Usage

### Initial Setup

1. When first running the application, you'll be prompted to set up a directory for storing executive orders.
2. Go to Settings (gear icon in toolbar) to configure the storage location.

### Downloading Executive Orders

1. In the "Not Downloaded" tab, select a year range and click "Fetch List" to retrieve available executive orders.
2. Select the orders you want to download:
   - Select individual orders by clicking on them
   - Use "All" to select all orders
   - Use "Clear Selection" to deselect all
3. Click "Selected" to download the selected orders or right-click on an order and select "Download Selection".

### Viewing Downloaded Orders

1. Switch to the "Downloaded" tab to see all downloaded executive orders.
2. Double-click on any order to open the PDF in your default PDF viewer.
3. Use the keyword search to filter the list of downloaded orders.

## Project Structure

- `cr_exec_ord.py` - Main application file
- `dialog_settings.py` - Settings dialog
- `dialog_about.py` - About dialog
- `version.py` - Version information

### Dependencies

This project relies on several WrapTools packages:
- [WrapCapExecOrders](https://github.com/WrapTools/WrapCapExecOrders) (required)
- [WrapConfig](https://github.com/WrapTools/WrapConfig) (required)
- [WrapSideSix](https://github.com/WrapTools/WrapSideSix) (required)
