import win32com.client


def send_email(email, cc, attch, body):
    ol = win32com.client.Dispatch("Outlook.Application")
    
    avgteam = None
    for acct in ol.Session.Accounts:
        if acct.SmtpAddress == "avgteam@americanveterinarygroup.com":
            avgteam = acct
            break

    msg = ol.CreateItem(0)

    if avgteam:
        msg._oleobj_.Invoke(*(64209, 0, 8, 0, avgteam))  # Msg.SendUsingAccount = oacctouse

        msg.To = email
        msg.CC = cc

        msg.HTMLBody = body
        msg.Subject = f'February 2024 Automated Production Report'
        msg.Attachments.Add(attch)
        msg.Send()
    else:
        print(f"ERROR: {email}")
