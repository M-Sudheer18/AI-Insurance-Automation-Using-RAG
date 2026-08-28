# 🏥 AI-Powered Insurance Claim Automation

An AI-powered health insurance claim verification system that uses **Retrieval-Augmented Generation (RAG)** and **Google Gemini** to analyze insurance claims against policy documents and generate automated claim assessment reports.

The system evaluates submitted patient information, medical bills, and consultation/medical reports to determine whether a claim should be **Approved, Rejected, or sent for Manual Review**.

---

## 🚀 Why This Project?

Manual insurance claim processing can be time-consuming and requires reviewing multiple documents against complex policy rules.

This system helps automate the initial claim assessment by:

- 📄 Reading insurance policy documents
- 👤 Verifying patient information
- 🧾 Analyzing medical bills
- 🩺 Reviewing medical/consultation reports
- 🔎 Retrieving relevant policy information using RAG
- 🚫 Checking medical conditions against policy exclusions
- ⚠️ Identifying inconsistencies and suspicious information
- 🤖 Using Gemini for claim reasoning and report generation
- 📊 Producing a structured claim assessment report
- ✅ Approving valid claims
- ❌ Rejecting claims that fail required criteria
- 👨‍💼 Sending uncertain cases for Manual Review

---

## ✨ Key Features

### 🔍 RAG-Based Policy Verification

The application retrieves relevant information from insurance policy documents instead of relying only on the language model's general knowledge.

### 📑 Multi-Document Claim Analysis

A claim can be evaluated using:

- Patient Information
- Medical Bill
- Consultation / Medical Report

The documents are extracted and supplied to the AI for verification.

### 🚫 Exclusion Checking

The system retrieves relevant policy exclusion information and checks whether the diagnosed condition appears in the exclusion list.

### 🛡️ Fraud & Inconsistency Assessment

The AI reviews submitted information for potential indicators such as:

- Conflicting patient details
- Inconsistent dates
- Mismatched medical facilities
- Billing inconsistencies
- Duplicate information
- Suspicious amounts

Suspicious indicators do not automatically prove fraud; they can result in **Manual Review**.

### 🤖 AI Claim Decision

The system produces one of three outcomes:

```text
APPROVED
REJECTED
MANUAL REVIEW


              ┌─────────────────────┐
              │   Insurance Policy  │
              │     Documents       │
              └──────────┬──────────┘
                         │
                         ▼
                 ┌───────────────┐
                 │   RAG / FAISS │
                 │ Vector Search │
                 └───────┬───────┘
                         │
                         ▼
┌─────────────────────────────────────────┐
│             Claim Documents             │
│                                         │
│  Patient Info + Medical Bill + Report  │
└──────────────────────┬──────────────────┘
                       │
                       ▼
                ┌──────────────┐
                │ Gemini AI    │
                │ Claim Review │
                └──────┬───────┘
                       │
             ┌─────────┼─────────┐
             ▼         ▼         ▼
        ┌────────┐ ┌────────┐ ┌──────────────┐
        │APPROVED│ │REJECTED│ │MANUAL REVIEW │
        └────────┘ └────────┘ └──────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Assessment Report│
              └─────────────────┘


