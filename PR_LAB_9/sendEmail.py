import smtplib
from email.mime.text import MIMEText
from flask import Flask, render_template, request
from ftplib import FTP

app = Flask(__name__)


@app.route('/api/email', methods=['GET', 'POST'])
def index():
    email_status = None
    if request.method == 'POST':
        sender = 'ingapaladi98@gmail.com'
        recipient = request.form['recipientEmail']
        subject = request.form['subject']
        message_body = request.form['message']

        link = f'<a href="ftp://yourusername:yourusername@138.68.98.108/faf212/inga/{request.form["attachment"]}">Click here to download the attachment</a>'
        message_body += f'<p>{link}</p>'

        message = MIMEText(message_body, 'html')
        message["Subject"] = subject
        message["From"] = sender
        message["To"] = recipient

        try:
            ftp = FTP('138.68.98.108')
            ftp.login(user='yourusername', passwd='yourusername')
            ftp.cwd('faf-212/inga')
            with open(request.form['attachment'], 'rb') as local_file:
                ftp.storbinary(f'STOR {request.form["attachment"]}', local_file)
        except Exception as exc:
            print(f"FTP Error: {exc}")
            pass

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(sender, 'fzbx uatu lday oihm')    # insert password here
                server.sendmail(sender, recipient, message.as_string())
            email_status = 'success'
        except:
            email_status = 'failure'
            return render_template('index.html', email_status=email_status)

    return render_template('index.html', email_status=email_status)


if __name__ == '__main__':
    app.run(debug=True)