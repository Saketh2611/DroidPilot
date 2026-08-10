import uiautomator2 as u2
import time


print("Connecting to phone...")

device = u2.connect()

print("Connected:", device.info["productName"])

# Open Google Chrome
print("Opening Chrome...")
device.app_start("com.android.chrome")

time.sleep(3)

# Click the address/search bar
print("Clicking address bar...")
device(resourceId="com.android.chrome:id/url_bar").click()

# Type the search query
print("Searching for iQOO...")
device.send_keys("iqoo")

# Press Enter
device.press("enter")

print("Search completed!")

time.sleep(5)

# Save screenshot
device.screenshot("google_iqoo.png")

print("Screenshot saved as google_iqoo.png")