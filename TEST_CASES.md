# Phishing Detector Test Cases

Use these examples to test your Phishing Detector Widget. Open them in a browser, text editor, or email client, then click the "Scan" button.

## ✅ SAFE Examples (Should show "SAFE" / "LOW RISK")

### Example 1: Normal Email
```
Subject: Meeting Reminder
From: john.doe@company.com

Hi team,
Just a reminder about our meeting tomorrow at 2 PM.
See you there!

Best regards,
John
```

### Example 2: Legitimate Website
```
Welcome to Amazon.com
Your order #123456789 has been confirmed.
Track your package: https://amazon.com/orders/123456789
```

### Example 3: Bank Notification (Legitimate)
```
Dear Customer,
Your account statement is ready.
Log in securely at: https://chase.com
```

---

## ⚠️ PHISHING Examples (Should show "PHISHING" / "HIGH RISK")

### Example 1: Urgent Account Suspension
```
URGENT: Your account will be suspended in 24 hours!
Click here immediately: http://secure-bank-verify.com/login
Verify your identity now or lose access forever!
```

### Example 2: Suspicious Email with Fake Link
```
Congratulations! You've won $10,000!
Claim your prize now: http://prize-winner-claim.net/claim?id=12345
Act fast - offer expires in 2 hours!
```

### Example 3: Fake PayPal Email
```
PayPal Security Alert
Your account has been locked due to suspicious activity.
Verify your account: http://paypal-security-verify.com/login
Do not ignore this message!
```

### Example 4: Phishing with Suspicious Domain
```
Microsoft Account Security
Your account needs verification.
Click here: http://microsoft-account-verify.xyz/login
This is urgent!
```

### Example 5: Fake Amazon Order
```
Amazon Order Confirmation
Your order #987654321 is ready.
Track here: http://amazon-order-track.com?id=987654321
```

---

## 🔍 Test URLs (Copy these into a browser or text editor)

### Safe URLs:
- https://www.google.com
- https://github.com
- https://stackoverflow.com
- https://www.microsoft.com

### Suspicious URLs (Should trigger warnings):
- http://secure-bank-verify.com (HTTP, not HTTPS)
- http://paypal-security-verify.com
- http://amazon-order-track.com
- http://microsoft-account-verify.xyz
- http://prize-winner-claim.net

---

## 📝 How to Test:

1. **Open a text editor** (Notepad, VS Code, etc.)
2. **Copy and paste one of the examples above**
3. **Click the "Scan" button** on your widget
4. **Check the result** - it should detect phishing patterns

### For URL Testing:
1. Open a browser
2. Navigate to one of the test URLs (or type it in the address bar)
3. Click "Scan" to analyze the page content

### For Email Testing:
1. Open your email client (Outlook, Gmail, etc.)
2. Create a new email or open an existing one
3. Paste one of the test examples
4. Click "Scan" to analyze

---

## Expected Results:

- **Safe examples** → Should show: "SAFE" with "LOW" risk
- **Phishing examples** → Should show: "PHISHING" with "HIGH" or "CRITICAL" risk
- **Suspicious URLs** → Should be flagged in the "Suspicious Elements" section
- **Fake domains** → Should be detected and listed

---

## Quick Test Checklist:

- [ ] Test safe content → Should be SAFE
- [ ] Test phishing content → Should be PHISHING
- [ ] Test suspicious URLs → Should be flagged
- [ ] Test fake email → Should detect phishing patterns
- [ ] Test legitimate website → Should be SAFE
- [ ] Test "Close" button → Should close modal
- [ ] Test "Scan Again" button → Should start new scan

