# Email Spam Detector Documentation - 2026

## Title Page

- **Full Name:** Fathima R  
- **Title/Role:** Email Spam Detector / Student  
- **Department:** BCA  
- **Register No:** DA2231006010004  
- **GitHub Username:** afathima-1080  
- **Year:** 2026  
- **Email:**  
- **College:** Same as existing PDF  
- **Supervisor/Guide:** Same as existing PDF  

---

## Abstract
Brief overview of the project, highlighting the need for an email spam detector and the technologies used in its implementation.

## Problem Statement
Identification of spam emails in a user’s inbox to prevent phishing attacks and unsolicited content.

## Objectives
- Develop a reliable spam detection system using machine learning.  
- Implement a web application using Flask for easy access to features.

## Scope
Discuss the impact and potential applications of the email spam detector in various domains.

## System Requirements
- **Hardware:**
  - Minimum 4GB RAM
  - 2GHz Dual-core Processor

- **Software:**
  - Python 3.x
  - PostgreSQL
  - Flask

## Technology Stack
- Python (Flask)
- PostgreSQL
- Machine Learning with Scikit-learn

## Architecture
1. **Flask App**: The web interface for users to interact with the spam detector.
2. **PostgreSQL Tables**:  
   - Users  
   - Emails  
   - Predictions  
3. **ML Training Pipeline**: Script to train the model located in `train.py`.
4. **Model Artifacts**: Saved ML model for predictions.

## Database Schema
```sql
CREATE TABLE users (id SERIAL PRIMARY KEY, username VARCHAR(50), password VARCHAR(255));  
CREATE TABLE emails (id SERIAL PRIMARY KEY, user_id INT, email_content TEXT, is_spam BOOLEAN);
CREATE TABLE predictions (id SERIAL PRIMARY KEY, email_id INT, predicted_label BOOLEAN);
```

## ML Methodology
1. **normalize_text**: Function to preprocess email content.
2. **TF-IDF**: Method to convert text data into numerical features.
3. **MultinomialNB**: Model used for classification.
4. **Evaluation Metrics**: Accuracy, precision, recall, and F1 score to evaluate model performance.

## Modules/Pages
- **Register**: User registration page
- **Login**: Authentication page 
- **Inbox**: View received emails
- **View**: Display email content
- **Compose**: Send new emails
- **Help**: FAQ and support

## Setup & Installation
1. Clone the repository: `git clone <repo-url>`.
2. Install required packages: `pip install -r requirements.txt`.
3. Set up the database: Refer to the database setup in `README`/`SETUP`/`TESTING`.

## Testing
- Conduct manual test cases as discussed in the project documentation.
- Verify database integrity and consistency after operations.

## Results
Present example outputs of the model predicting spam/non-spam emails.

## Future Enhancements
Discuss potential features to improve the spam detection system.

## Conclusion
Summarize the findings and importance of the project.

## References
- Link to relevant academic papers, articles, and resources used in the project.

---

*Date: 2026-04-25*