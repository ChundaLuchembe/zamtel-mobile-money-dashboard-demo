# 🔐 Dashboard Login Information

## Default Credentials

**Username:** `admin`  
**Password:** `admin123`

---

## Features

✅ **Secure Login Page**
- Professional design with gradient background
- Password masking for security
- Error messages for invalid credentials
- Session-based authentication

✅ **User Experience**
- Clean, modern interface
- Responsive design
- Smooth animations
- Clear visual feedback

✅ **Security**
- Password input hidden
- Session storage for login state
- Logout requires closing browser session

---

## How to Login

1. **Open the dashboard** in your browser
2. **Enter credentials:**
   - Username: `admin`
   - Password: `admin123`
3. **Click "Login" button**
4. You'll be redirected to the dashboard

---

## Customization

### To Change Credentials

Edit the `app.py` file, lines 21-22:

```python
USERNAME = "admin"      # Change to your username
PASSWORD = "admin123"   # Change to your password
```

### To Add Multiple Users

For production use, consider:
- **dash-auth** package for basic authentication
- **flask-login** for advanced user management
- Database-backed user authentication
- OAuth integration (Google, Microsoft)

---

## Security Notes

⚠️ **Important for Production:**

1. **Change default credentials** immediately
2. **Use environment variables** for passwords:
   ```python
   USERNAME = os.environ.get('DASH_USERNAME', 'admin')
   PASSWORD = os.environ.get('DASH_PASSWORD', 'admin123')
   ```
3. **Consider using HTTPS** for secure transmission
4. **Implement password hashing** for stored credentials
5. **Add rate limiting** to prevent brute force attacks

---

## Logout

Currently, logout happens when:
- Browser session ends
- Browser cache is cleared
- Page is refreshed (session expires)

To add a logout button, we can implement it in future updates.

---

## Troubleshooting

**Problem:** Can't login with correct credentials  
**Solution:** Check browser console for errors, clear browser cache

**Problem:** Login page not showing  
**Solution:** Check that all files are uploaded, especially `app.py`

**Problem:** Error message shows but credentials are correct  
**Solution:** Verify USERNAME and PASSWORD constants in app.py match exactly (case-sensitive)

---

## Future Enhancements

Possible improvements:
- [ ] Multiple user support
- [ ] Password reset functionality
- [ ] "Remember me" option
- [ ] Logout button
- [ ] Session timeout
- [ ] Activity logging
- [ ] Two-factor authentication (2FA)
