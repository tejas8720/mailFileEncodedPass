from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
import urllib.parse
import sqlalchemy
import os
from PyPDF2 import PdfFileReader, PdfFileWriter
from datetime import datetime
import time
import pandas as pd
import hashlib

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import maskpass

h = hashlib.blake2b(key=b'pseudorandom key', digest_size=16)
password = urllib.parse.quote_plus("Tejas@8720")  # '123%40456'
tablename = 'encryptedFiles'
engine = create_engine(f'mysql+pymysql://root:{password}@localhost/sql_training')
meta = MetaData()

sender_address = 'tejaschaturbhuj8720@gmail.com'
sender_pass = maskpass.askpass(prompt="Password:", mask="#")

if sqlalchemy.inspect(engine).has_table(tablename):
    pass
else:
    tb = Table(tablename, meta,
                      Column('id', Integer, primary_key=True, autoincrement=True),
                      Column('name', String(60), nullable=False),
                      Column('size', String(60), nullable=False),
                      Column('time', String(60), nullable=False),
                      )
    tb.create(engine)

df = pd.read_csv('email.csv')
files = list(df.iloc[:,1])
email = list(df.iloc[:,2])
i=1

for f,e in zip(files,email):
    with open('./pdf/'+f, "rb") as in_file:
        input_pdf = PdfFileReader(in_file)
        output_pdf = PdfFileWriter()
        output_pdf.appendPagesFromReader(input_pdf)
        h.update(b"{f}")-
        pas = h.hexdigest()
        output_pdf.encrypt(pas)
        filename1 = datetime.now().strftime("%Y_%m_%d-%H:%M:%S")
        file_size = os.path.getsize('./pdf/'+f)
        tm = datetime.now().strftime("%H:%M:%S")
        fname=f+'_'+filename1
        engine.execute("INSERT INTO  `encryptedFiles` VALUES ('{}','{}','{}','{}')".format(i,fname,str(file_size)+' bytes', tm))
        with open('./pdf/'+f+'_'+filename1, "wb") as out_file:
            output_pdf.write(out_file)

        mail_content = '''Hello,
        Your Encrypted File is {}.
        Your Encoded Password is {}.
        Thank You
        '''.format(fname,pas)
        receiver_address = e

        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = receiver_address
        message['Subject'] = 'Encrypted File with encoded Password'

        message.attach(MIMEText(mail_content, 'plain'))
        attach_file_name = fname
        attach_file = open('./pdf/'+fname, 'rb')
        payload = MIMEBase('application', 'octate-stream')
        payload.set_payload((attach_file).read())
        encoders.encode_base64(payload)

        payload.add_header('Content-Decomposition', 'attachment', filename=attach_file_name)
        message.attach(payload)

        session = smtplib.SMTP('smtp.gmail.com', 587)
        session.starttls()
        session.login(sender_address, sender_pass)
        text = message.as_string()
        session.sendmail(sender_address, receiver_address, text)
        session.quit()
        print('Mail Sent to '+receiver_address)

        time.sleep(2)
        i+=1
