# 🌐 GET YOUR LIVE INTERNET LINK

## Method 1: Ngrok (RECOMMENDED) ⭐

### Step 1: Download Ngrok
- Go to: https://ngrok.com/download
- Click "Download for Windows"
- Extract the zip file to a folder (like Desktop)

### Step 2: Run ORCA
```cmd
# Double-click this file:
C:\Users\SOHAM\Desktop\SIH_2026\RUN_ORCA.bat
```

### Step 3: Start Ngrok
```cmd
# Open new Command Prompt
cd C:\Users\SOHAM\Desktop\ngrok

# Run ngrok (assuming you extracted it to Desktop)
ngrok http 3000
```

### Step 4: Get Your Link
Look for this in the ngrok window:
```
Forwarding    https://abc123xyz.ngrok.io -> http://localhost:3000
```

**`https://abc123xyz.ngrok.io` is your LIVE LINK!**

✅ Share this link with anyone  
✅ Access from any device  
✅ Works anywhere in the world  
✅ HTTPS secure  

---

## Method 2: Localtunnel (Alternative)

### Step 1: Install Node.js
- Download from: https://nodejs.org/
- Install with default settings

### Step 2: Install Localtunnel
```cmd
npm install -g localtunnel
```

### Step 3: Run ORCA
```cmd
C:\Users\SOHAM\Desktop\SIH_2026\RUN_ORCA.bat
```

### Step 4: Start Localtunnel
```cmd
lt --port 3000
```

You'll get: `https://random-word-1234.loca.lt`

**That's your LIVE LINK!**

---

## Method 3: Serveo (No Installation)

### Step 1: Run ORCA
```cmd
C:\Users\SOHAM\Desktop\SIH_2026\RUN_ORCA.bat
```

### Step 2: Run Serveo
```cmd
ssh -R 80:localhost:3000 serveo.net
```

You'll get: `https://random.serveo.net`

**That's your LIVE LINK!**

---

## ⚡ FASTEST METHOD (Ngrok):

**Copy-Paste These Commands:**

```cmd
REM 1. Start ORCA (in one window)
cd C:\Users\SOHAM\Desktop\SIH_2026
RUN_ORCA.bat

REM 2. Download ngrok (download from ngrok.com)

REM 3. Run ngrok (in another window - adjust path if needed)
cd C:\Users\SOHAM\Desktop\ngrok
ngrok http 3000

REM 4. Look for the line that says "Forwarding"
REM That's your link!
```

---

## 📱 Test Your Live Link:

Once you have the link (e.g., `https://abc123.ngrok.io`):

1. **Open it in your browser** ✅
2. **Open it on your phone** ✅
3. **Share with friends** ✅
4. **Access from anywhere** ✅

---

## 🎯 Your Links Will Be:

| Service | Local URL | Public URL (Ngrok) |
|---------|-----------|-------------------|
| **Dashboard** | http://localhost:3000 | https://xxxx.ngrok.io |
| **API** | http://localhost:8000 | https://yyyy.ngrok.io |
| **API Docs** | http://localhost:8000/docs | https://yyyy.ngrok.io/docs |

---

## 💡 Tips:

### Keep Links Active
- **Don't close the ngrok window**
- Each time you restart ngrok, you get a NEW link
- **Paid ngrok** gives you a permanent link

### Share Both Links
- Share the dashboard link (port 3000) for users
- Share the API docs link (port 8000) for developers

### Security
- These are public links - anyone can access
- Add authentication for production
- Don't share your `.env` file!

---

## 🔥 SUPER QUICK START:

**2 Windows Method:**

**Window 1:**
```cmd
cd C:\Users\SOHAM\Desktop\SIH_2026
RUN_ORCA.bat
```
*Wait for services to start...*

**Window 2:**
```cmd
cd C:\Users\SOHAM\Desktop\ngrok
ngrok http 3000
```
*Copy the https:// link!*

**DONE! Share the link!** 🎉

---

## 📸 What Ngrok Looks Like:

```
ngrok

Session Status                online
Account                       Your Name (Plan: Free)
Version                       3.x.x
Region                        India (in)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok.io -> http://localhost:3000

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

**The line you want: `https://abc123.ngrok.io`**

---

## 🌟 Why Ngrok?

✅ **No installation of complex software**  
✅ **HTTPS out of the box**  
✅ **Fast and reliable**  
✅ **Free tier available**  
✅ **Web interface for monitoring**  
✅ **Works behind firewalls**  

---

## 🎓 Ngrok Pro Tips:

### Custom Subdomain (Paid)
```cmd
ngrok http 3000 --subdomain=orca-marine
# Get: https://orca-marine.ngrok.io
```

### Password Protect
```cmd
ngrok http 3000 --basic-auth "user:password"
```

### Monitor Requests
- Open: http://localhost:4040
- See all requests in real-time
- Inspect payloads
- Replay requests

---

## 🚨 Important Notes:

1. **Keep both windows open**
   - ORCA window (API + Frontend)
   - Ngrok window

2. **New link each time**
   - Each time you restart ngrok, you get a new link
   - Send the new link to users

3. **Free tier limits**
   - Ngrok free: 40 connections/minute
   - Good for testing and demos
   - Upgrade if needed

---

## ✅ Success Checklist:

- [ ] ORCA is running (RUN_ORCA.bat)
- [ ] Dashboard opens locally (http://localhost:3000)
- [ ] Ngrok is running
- [ ] Got the https:// link from ngrok
- [ ] Opened link in browser - works!
- [ ] Tested on phone - works!
- [ ] Shared with friend - works!

---

**🎉 You now have a LIVE INTERNET LINK! 🎉**

**Anyone in the world can access your ORCA dashboard!**

---

## 📞 Share This:

**"Check out ORCA - Marine Intelligence Platform:**  
**https://your-link.ngrok.io"**

✨ **It's that simple!** ✨
