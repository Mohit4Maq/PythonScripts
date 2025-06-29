# Email Setup Guide for OTP Functionality

This guide will help you configure real email sending for the OTP (One-Time Password) functionality in your HR Document Q&A system.

## 🚀 Quick Setup

### 1. Set Environment Variables

Add these environment variables to your `.env` file:

```bash
# Enable real email sending
EMAIL_ENABLED=true

# Choose your email provider (gmail, outlook, yahoo, or custom)
EMAIL_PROVIDER=gmail

# Email credentials
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com
EMAIL_FROM_NAME=HR Document Q&A System

# Optional: Customize settings
EMAIL_TIMEOUT=30
EMAIL_MAX_RETRIES=3
```

### 2. Email Provider Setup

#### Gmail (Recommended for testing)

**Step 1: Enable 2-Factor Authentication**
1. Go to your Google Account settings
2. Navigate to Security
3. Enable 2-Step Verification

**Step 2: Generate App Password**
1. Go to Google Account settings
2. Navigate to Security → 2-Step Verification
3. Click on "App passwords"
4. Generate a new app password for "Mail"
5. Use this password as `EMAIL_PASSWORD`

**Step 3: Configure .env file**
```bash
EMAIL_PROVIDER=gmail
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-16-digit-app-password
EMAIL_FROM=your-email@gmail.com
EMAIL_ENABLED=true
```

#### Outlook/Hotmail

**Step 1: Enable 2-Factor Authentication**
1. Go to account.live.com
2. Navigate to Security
3. Enable 2-Step Verification

**Step 2: Generate App Password**
1. Go to account.live.com
2. Navigate to Security → Advanced Security Options
3. Generate an app password
4. Use this password as `EMAIL_PASSWORD`

**Step 3: Configure .env file**
```bash
EMAIL_PROVIDER=outlook
EMAIL_USERNAME=your-email@outlook.com
EMAIL_PASSWORD=your-app-password
EMAIL_FROM=your-email@outlook.com
EMAIL_ENABLED=true
```

#### Yahoo Mail

**Step 1: Enable 2-Factor Authentication**
1. Go to Yahoo Account Security
2. Enable 2-Step Verification

**Step 2: Generate App Password**
1. Go to Yahoo Account Security
2. Generate an app-specific password
3. Use this password as `EMAIL_PASSWORD`

**Step 3: Configure .env file**
```bash
EMAIL_PROVIDER=yahoo
EMAIL_USERNAME=your-email@yahoo.com
EMAIL_PASSWORD=your-app-password
EMAIL_FROM=your-email@yahoo.com
EMAIL_ENABLED=true
```

#### Custom SMTP Server

For other email providers or custom SMTP servers:

```bash
EMAIL_PROVIDER=custom
EMAIL_SMTP_SERVER=your-smtp-server.com
EMAIL_SMTP_PORT=587
EMAIL_USE_TLS=true
EMAIL_USE_SSL=false
EMAIL_USERNAME=your-email@domain.com
EMAIL_PASSWORD=your-password
EMAIL_FROM=your-email@domain.com
EMAIL_ENABLED=true
```

## 🧪 Testing Your Email Configuration

### 1. Test Script

Run the test script to verify your email configuration:

```bash
python test_email_otp.py
```

### 2. Manual Testing

1. Start the application:
   ```bash
   python web_app_hr_bot_auth.py
   ```

2. Go to http://localhost:8080/login

3. Click "Login with Email"

4. Enter your email address

5. Check your email for the OTP (or check console if in demo mode)

## 🔧 Troubleshooting

### Common Issues

#### 1. Authentication Failed
**Error**: `SMTPAuthenticationError: (535, b'5.7.8 Username and Password not accepted')`

**Solutions**:
- Ensure 2-Factor Authentication is enabled
- Use an App Password, not your regular password
- Check that `EMAIL_USERNAME` and `EMAIL_PASSWORD` are correct
- For Gmail, make sure "Less secure app access" is not required (use App Password instead)

#### 2. Connection Timeout
**Error**: `socket.timeout: timed out`

**Solutions**:
- Check your internet connection
- Verify the SMTP server and port are correct
- Try increasing `EMAIL_TIMEOUT` value
- Check if your firewall is blocking the connection

#### 3. SSL/TLS Issues
**Error**: `ssl.SSLError` or `smtplib.SMTPNotSupportedError`

**Solutions**:
- Ensure `EMAIL_USE_TLS=true` for most providers
- For Gmail, use port 587 with TLS
- For custom servers, verify SSL/TLS settings

#### 4. Rate Limiting
**Error**: `smtplib.SMTPDataError: (550, b'5.7.1 Too many requests')`

**Solutions**:
- Wait a few minutes before trying again
- Reduce `EMAIL_MAX_RETRIES` to avoid hitting rate limits
- Consider using a different email provider

### Debug Mode

Enable debug logging by setting:

```bash
EMAIL_DEBUG=true
```

This will show detailed SMTP communication logs.

## 📧 Email Templates

The system uses a simple text email template. You can customize it by modifying the `send_otp_email` function in `web_app_hr_bot_auth.py`.

### Current Template:
```
Hello!

Your OTP (One-Time Password) for HR Document Q&A System login is:

🔐 **123456**

This code will expire in 5 minutes.

If you didn't request this code, please ignore this email.

Best regards,
HR Document Q&A System
```

## 🔒 Security Best Practices

1. **Never commit credentials to version control**
   - Keep your `.env` file in `.gitignore`
   - Use environment variables for production

2. **Use App Passwords**
   - Don't use your main account password
   - Generate app-specific passwords for each service

3. **Enable 2-Factor Authentication**
   - Required for most email providers
   - Provides additional security

4. **Regular Password Rotation**
   - Change app passwords periodically
   - Monitor for suspicious activity

5. **Rate Limiting**
   - Implement rate limiting in production
   - Monitor email sending patterns

## 🚀 Production Deployment

For production deployment:

1. **Use a dedicated email service**
   - Consider services like SendGrid, Mailgun, or AWS SES
   - These provide better deliverability and monitoring

2. **Environment-specific configuration**
   - Use different email settings for development/staging/production
   - Never use personal email accounts in production

3. **Monitoring and logging**
   - Monitor email delivery rates
   - Log email sending attempts and failures
   - Set up alerts for email service issues

4. **Backup email provider**
   - Consider having a backup email service
   - Implement fallback mechanisms

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Run the test script to isolate the problem
3. Check the application logs for detailed error messages
4. Verify your email provider's documentation for specific requirements

## 🔄 Migration from Demo Mode

To migrate from demo mode to real email sending:

1. **Backup your current configuration**
2. **Set up email credentials** following the provider-specific instructions
3. **Test with the test script**
4. **Update your .env file** with `EMAIL_ENABLED=true`
5. **Restart the application**
6. **Test the login flow**

The system will automatically fall back to console output if email sending fails, ensuring your application remains functional during the transition. 