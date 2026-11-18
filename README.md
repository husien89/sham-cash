# Sham Cash - Digital Wallet & Notification System

## 📖 Overview
Sham Cash is a secure, web-based digital wallet application built with vanilla JavaScript and Google App Engine compatible structure. It features QR code generation, transaction history, notification systems, and PDF statement exports.

## 🚀 Features
- **QR Code Payments:** Generate and scan QR codes for instant transfers.
- **Transaction History:** Detailed log of all incoming and outgoing payments.
- **Notifications:** Real-time alerts for account activities.
- **PDF Export:** Download official account statements (Dekont).
- **Role-Based Access:** Admin and User roles with secure authentication.
- **Responsive Design:** Works seamlessly on mobile and desktop.

## 🛠️ Tech Stack
- **Frontend:** HTML5, CSS3, Vanilla JavaScript (ES6 Modules)
- **Libraries:** 
  - `qrcode` for QR generation.
  - `jspdf` & `jspdf-autotable` for PDF reports.
- **Backend:** Python (Flask) & Google Cloud Datastore.
- **Storage:** LocalStorage (for demo) / Datastore (for production).

## 📂 Project Structure
```text
sham-cash/
├── index.html          # Main Dashboard
├── login.html          # Authentication Page
├── notifications.html  # Notification Center
├── settings.html       # User Settings
├── app.js              # Main Application Logic (QR, PDF)
├── auth.js             # Authentication & Session Management
├── data.js             # Data Handling (Transactions, Notifications)
├── styles.css          # Global Styles
├── package.json        # Dependencies
├── app.yaml            # App Engine Configuration
└── main.py             # Backend Server (Flask)