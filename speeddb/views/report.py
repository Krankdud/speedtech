from speeddb import app, forms, mail
from flask import render_template
from flask_mail import Message

@app.route('/report', methods=['POST'])
def report():
    form = forms.ReportForm()
    if form.validate():
        msg = Message(subject="REPORT for clip %d" % form.clip_id.data, recipients=[app.config['REPORT_EMAIL']])
        msg.body = "Clip %d has been reported\nReason: %s\nDescription: %s" % (form.clip_id.data, form.reason.data, form.description.data)
        mail.send(msg)
        return render_template('report_finish.html', success=True)
    return render_template('report_finish.html', success=False)