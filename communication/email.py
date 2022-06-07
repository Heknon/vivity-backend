import os

import yagmail

from database import Order
from singleton import Singleton


# TODO: Not lower account security
# https://developers.google.com/gmail/api/quickstart/python
# https://blog.macuyiko.com/post/2016/how-to-send-html-mails-with-oauth2-and-gmail-in-python.html
# https://github.com/kootenpv/yagmail#oauth2


class Email(metaclass=Singleton):
    def __init__(self):
        self.yag: yagmail.SMTP = yagmail.SMTP("vivity.noreply@gmail.com", password=os.getenv("noreply_password"))

    def send_email(self, to: str, subject: str, body: str = None, html: str = None, image: str = None):
        send_arr = list(filter(lambda x: x is not None, [body, html, image]))

        return self.yag.send(
            to=to,
            subject=subject,
            contents=send_arr
        )

    def send_forgot_password(self, email: str, reset_url):
        self.FORGOT_PASSWORD_HTML.replace("FORGOT_PASSWORD_FULL_URL", reset_url)

        return self.send_email(
            to=email,
            subject="Reset your password",
            body="",
            html=self.FORGOT_PASSWORD_HTML.replace("FORGOT_PASSWORD_FULL_URL", reset_url)
        )

    def send_order_success(self, email: str, order: Order):
        return self.send_email(
            to=email,
            subject=f"An order you made on Vivity was processed | {order.id}",
            body=f"Transaction for {order.total} was made.\nOrder ID: {order.id}\nSub-total: {order.subtotal}\nCupon discount: {order.cupon_discount}\nShipping: {order.shipping_cost}\n-------------\nTOTAL: {order.total}",
        )

    FORGOT_PASSWORD_HTML = """<div class=""><div class="aHl"></div><div id=":om" tabindex="-1"></div><div id=":1ak" class="ii gt" jslog="20277; u014N:xr6bB; 4:W251bGwsbnVsbCxbXV0."><div id=":on" class="a3s aiL msg2383094738974891212"><u></u> <div style="background-color:#eff2f3;margin:0;width:100%"> <table role="presentation" width="100%" align="left" border="0" cellpadding="0" cellspacing="0" style="width:100%;background-color:#eff2f3;margin:0" bgcolor="#EFF2F3"> <tbody><tr> <td align="left" width="100%" valign="top" style="color:#2e3b42;font-family:-apple-system,BlinkMacSystemFont,“Segoe UI”,Roboto,Helvetica,Arial,sans-serif;font-size:16px;line-height:24px"> <div style="margin:0 auto;max-width:600px;width:100%"> <table role="presentation" border="0" align="center" cellpadding="0" cellspacing="0" width="100%"> <tbody><tr> <td width="100%" align="left" valign="top"> <div class="m_2383094738974891212block" style="width:100%;padding:16px 0"> <table role="presentation" border="0" align="center" cellpadding="0" cellspacing="0" width="100%"> <tbody><tr> <td class="m_2383094738974891212block__cell" width="100%" align="left" valign="top" style="padding:16px 0"> <center><img alt="Vivity" src="https://i.imgur.com/LyJkov7.png" border="0" style="text-decoration:none;padding:0;outline:none;line-height:100%;border:0;display:block;max-width:100%;margin:0 auto;height:40px" height="40" class="CToWUd"></center> </td></tr></tbody></table> </div><div class="m_2383094738974891212card m_2383094738974891212block" style="width:100%;background-color:#ffffff;border-radius:8px;box-sizing:border-box;padding:0 20px;margin-bottom:16px"> <table role="presentation" border="0" align="center" cellpadding="0" cellspacing="0" width="100%"> <tbody><tr> <td class="m_2383094738974891212block__cell" width="100%" align="left" valign="top" style="background-color:#ffffff;border-radius:8px;box-sizing:border-box;padding:0 20px" bgcolor="#FFFFFF"> <h1 id="m_2383094738974891212forgot-your-password" style="color:#2e3b42;font-family:-apple-system,BlinkMacSystemFont,“Segoe UI”,Roboto,Helvetica,Arial,sans-serif;font-size:28px;line-height:40px;margin:40px 0 24px;text-align:center;font-weight:600">Forgot your password?</h1> <p style="display:block;color:#2e3b42;font-family:-apple-system,BlinkMacSystemFont,“Segoe UI”,Roboto,Helvetica,Arial,sans-serif;font-size:16px;line-height:24px;margin:40px 0">No worries. Let’s get you to your account settings so you can choose a new one.</p><p style="display:block;color:#2e3b42;font-family:-apple-system,BlinkMacSystemFont,“Segoe UI”,Roboto,Helvetica,Arial,sans-serif;font-size:16px;line-height:24px;margin:40px 0"> </p><div> <table role="presentation" width="100%" align="left" border="0" cellpadding="0" cellspacing="0"> <tbody><tr> <td> <table role="presentation" width="auto" align="center" border="0" cellspacing="0" cellpadding="0" style="margin:16px auto 40px"> <tbody><tr> <td align="center" style="background-color:#00ad9f;border-radius:4px;min-width:144px;padding:8px 12px" bgcolor="#00AD9F"><a href="FORGOT_PASSWORD_FULL_URL" style="color:#ffffff;text-decoration:none;font-weight:500;background-color:#00ad9f;text-align:center;display:inline-block" target="_blank"><span style="color:#ffffff;text-decoration:none">Reset password</span></a></td></tr></tbody></table> </td></tr></tbody></table> </div><p></p><p style="display:block;color:#2e3b42;font-family:-apple-system,BlinkMacSystemFont,“Segoe UI”,Roboto,Helvetica,Arial,sans-serif;font-size:16px;line-height:24px;margin:40px 0;margin-bottom:40px">Didn’t request this change? You can ignore this email and get back to business as usual.</p></td></tr></tbody></table> </div></td></tr></tbody></table> </div></td></tr></tbody></table> <div style="display:none;white-space:nowrap;font-size:15px;line-height:0">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; </div></div></div></div><div id=":1aw" class="ii gt" style="display:none"><div id=":1ax" class="a3s aiL "></div></div><div class="hi"></div></div>"""
