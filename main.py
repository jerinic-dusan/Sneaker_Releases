import json
import requests
import smtplib
from datetime import date, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def check_new_releases():
    with open("settings.json") as f:
        settings = json.load(f)

    base_url = r"https://api.thesneakerdatabase.com/v1/sneakers?limit=100"
    today = date.today()
    release_date_url = f"&releaseDate=gte:{today}&releaseDate=lte:{today + timedelta(days=1)}"
    gender_url = f"&gender={settings['gender']}"
    brands_url = f""

    for brand in settings['brands']:
        brands_url += "&brand=" + brand

    main_url = base_url + release_date_url + gender_url + brands_url
    request_object = requests.get(main_url)
    result = request_object.json()
    # print(json.dumps(result, indent=4, sort_keys=True))
    if len(result['results']) > 0:
        send_mail(settings['sender'], settings['receiver'], settings['sender_password'], result['results'])


def send_mail(sender, receiver, password, results):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(sender, password)

    message = MIMEMultipart("alternative")
    message["Subject"] = "Fresh new releases 🔥🔥🔥"
    message["From"] = sender
    message["To"] = receiver
    text = "Here are today's releases:\n\n"
    for res in results:
        text += f"Sneaker Name: {res['title']}\n"
        text += f"Retail Price: {res['retailPrice']}$\n\n"

    html = """\
    <html>
        <body>
    """
    html_end = """
        </body>
    </html>
    """
    for res in results:
        html += f"""
            <div class="container" style="display: flex;">
              <div class="left" style="margin-right:1%;">
                <img src="{res['media']['thumbUrl']}" alt="image" width="140" height="100" />
              </div>
              <div class="right">
                <p><b>{res['title']}</b></p>
                <p><b>Retail Price: {res['retailPrice']}$</b></p>
              </div>
            </div>
        """
    html += html_end

    message.attach(MIMEText(text, "plain"))
    message.attach(MIMEText(html, "html"))
    server.sendmail(sender, receiver, message.as_string())
    server.close()


if __name__ == '__main__':
    check_new_releases()
