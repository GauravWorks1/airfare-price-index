import subprocess
import os

test_html = 'test_slide.html'
with open(test_html, 'w', encoding='utf-8') as f:
    f.write('<!DOCTYPE html><html><body style="background:#1a448e; color:white; font-size:40px; display:flex; align-items:center; justify-content:center; height:100vh; margin:0;">Test Slide Successful</body></html>')

chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
cmd = [chrome_path, '--headless', '--disable-gpu', '--screenshot=test_slide.png', '--window-size=1920,1080', test_html]
res = subprocess.run(cmd, capture_output=True)
if os.path.exists('test_slide.png'):
    print('SUCCESS: Screenshot generated! Size:', os.path.getsize('test_slide.png'))
    os.remove('test_slide.png')
else:
    print('FAILED:', res.stderr.decode('utf-8', errors='ignore'))

if os.path.exists(test_html):
    os.remove(test_html)
