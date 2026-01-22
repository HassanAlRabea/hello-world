# GPU Stock Tracker - Montreal, Canada

A simple Python tool to track GPU availability at Canadian retailers.

**Currently tracking:** ASUS Prime GeForce RTX 5070 Ti 16GB GDDR7 (PRIME-RTX5070TI-16G)

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the tracker (continuous monitoring)
python gpu_tracker.py

# Or run a single check
python gpu_tracker.py --once
```

## Vendors Monitored

| Retailer | Website | Notes |
|----------|---------|-------|
| Canada Computers | canadacomputers.com | Stores in Montreal Downtown, Eaton Centre, Laval, Brossard |
| Best Buy Canada | bestbuy.ca | Multiple Montreal locations |
| Newegg Canada | newegg.ca | Online, ships to Montreal |
| Memory Express | memoryexpress.com | Ships to Quebec |
| Amazon.ca | amazon.ca | Fast shipping |

## Email Notifications (Optional)

To receive email alerts when stock is found, set these environment variables:

```bash
export EMAIL_USER="your-email@gmail.com"
export EMAIL_PASS="your-app-password"
export NOTIFY_EMAIL="where-to-send@email.com"
```

For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833) instead of your regular password.

## Configuration

Edit `config.json` to customize:
- Check interval (default: 5 minutes)
- Enable/disable specific vendors
- Sound and email alert settings

## Running as a Background Service

### Linux (systemd)
```bash
# Create a service file
sudo nano /etc/systemd/system/gpu-tracker.service

# Add:
[Unit]
Description=GPU Stock Tracker
After=network.target

[Service]
ExecStart=/usr/bin/python3 /path/to/gpu_tracker.py
Restart=always
User=yourusername

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable gpu-tracker
sudo systemctl start gpu-tracker
```

### Using cron (run every 5 minutes)
```bash
*/5 * * * * cd /path/to/tracker && python3 gpu_tracker.py --once >> /var/log/gpu-tracker.log 2>&1
```

## About Me

Hello everyone! I am a chemical engineering student who is looking to branch out into software engineering. I'm learning all the basics for now.
