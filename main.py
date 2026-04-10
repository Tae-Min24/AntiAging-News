import feedparser
import anthropic
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 1. ดึงข้อมูลจาก RSS
feeds = [
    "https://www.lifespan.io/feed/",
    "https://longevity.technology/feed/"
]

def get_news():
    news_items = []
    for url in feeds:
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]: # ดึงแค่ 3 ข่าวล่าสุดต่อเว็บเพื่อประหยัด Token
            news_items.append(f"Title: {entry.title}\nSummary: {entry.description}\n")
    return "\n".join(news_items)

# 2. ให้ Claude สรุป
def summarize_news(text):
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    response = client.messages.create(
        model="claude-3-haiku-20240307", # ใช้ตัวประหยัดเงิน
        max_tokens=1500,
        messages=[{"role": "user", "content": f"ในฐานะผู้เชี่ยวชาญ Anti-Aging ช่วยสรุปข่าวเหล่านี้เป็นภาษาไทยแบบเจาะลึกสำหรับเจ้าของโรงงาน OEM และนักวิจัย ป.เอก:\n\n{text}"}]
    )
    return response.content[0].text

# 3. ส่งอีเมล
def send_email(content):
    msg = MIMEMultipart()
    msg['From'] = "teerasak.surapha@gmail.com"
    msg['To'] = "teerasak.surapha@gmail.com"
    msg['Subject'] = "[Daily Anti-Aging Update] ข้อมูลวิจัยและโอกาสธุรกิจประจำวัน"
    msg.attach(MIMEText(content, 'plain'))

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(msg['From'], os.environ["GMAIL_PASSWORD"])
        server.send_message(msg)

if __name__ == "__main__":
    raw_news = get_news()
    summary = summarize_news(raw_news)
    send_email(summary)
