"""
Notification/email composition module
"""


import datetime
from dateutil.tz import tzlocal

from edunotice.constants import (
    CONST_EMAIL_SUBJECT_NEW,
    CONST_EMAIL_SUBJECT_UPD,
    CONST_EMAIL_SUBJECT_EXPIRE,
    CONST_EMAIL_SUBJECT_CANCELLED,
    CONST_EMAIL_SUBJECT_USAGE,
    CONST_SUB_CANCELLED,
    CONST_TIME_ZONE_NAME,
)


def email_top(headline):
    """
    Generates the top section with a headline.

    Arguments:
        headline - headline of the top section
    Returns:
        html_content - html code
    """

    html_content = "<html><body>"
    html_content += '<div dir="ltr" style="font-family:verdana;font-size:12px;color:#555555;line-height:14pt">'
    html_content += '<div style="width:590px">'

    html_content += "<div style=\"background:url('https://www.gstatic.com/android/market_images/email/email_top.png') no-repeat;width:100%;height:75px;display:block\">"
    html_content += '<div style="padding-top:30px;padding-left:50px;padding-right:50px;font-size:24px;">'

    html_content += "<div>%s</div>" % (headline)

    html_content += "</div>"
    html_content += "</div>"

    return html_content


def email_bottom():
    """
    Generates the bottom section with a headline.

    Returns:
        html_content - html code
    """

    html_content = "<div style=\"background:url('https://www.gstatic.com/android/market_images/email/email_bottom.png') no-repeat;width:100%;height:50px;display:block\"></div>"

    html_content += "</div></div></body></html>"

    return html_content


def email_middle(content):
    """
    Generates the middle section with the provided content.

    Arguments:
        content - html content of the middle section
    Returns:
        html_content - html code
    """

    html_content = "<div style=\"background:url('https://www.gstatic.com/android/market_images/email/email_mid.png') repeat-y;width:100%;display:block\">"
    html_content += (
        '<div style="padding-left:50px;padding-right:50px;padding-bottom:1px">'
    )
    html_content += '<div style="border-bottom:1px solid #ededed"></div>'
    html_content += (
        '<div style="margin:20px 0px;font-size:20px;line-height:30px;text-align:left">'
    )

    html_content += content

    html_content += "</div>"
    html_content += '<div style="text-align:left"></div>'
    html_content += '<div style="border-bottom:1px solid #ededed"></div>'
    html_content += "<br>"
    html_content += "<div>This is an automated email notification sent from the Turing Research Compute Platforms cloud platform -  please do not reply to it.</div>"
    html_content += "</div></div>"

    return html_content


def value_change(paramter_name, old_value, new_value):
    """
    Register a change in a value.

    Arguments:
        paramter_name - name of the parameter
        old_value - old parameter value
        new_value - new parameter value
    Return:
        html_content - html code registering a change in a parameter value
    """

    if old_value != new_value:
        html_content = (
            "&#9 %s: <strike><i>%s</i></strike> &rarr; <strong><i>%s</i></strong><br>"
            % (paramter_name, old_value, new_value)
        )
    else:
        html_content = "&#9 %s: <i>%s</i><br>" % (paramter_name, new_value)

    return html_content


def details_changed(prev_details, new_details):
    """
    Checks if at least one of the main details from a subscriptions
        has changed.

    Arguments:
        prev_details - previous details of a subscription
        new_details - new details of a subscription
    Returns:
        changed - True/False
    """

    changed = False

    if (
        (prev_details.handout_status != new_details.handout_status)
        or (prev_details.subscription_name != new_details.subscription_name)
        or (prev_details.subscription_status != new_details.subscription_status)
        or (
            prev_details.subscription_expiry_date
            != new_details.subscription_expiry_date
        )
        or (prev_details.handout_budget != new_details.handout_budget)
        or (prev_details.subscription_users != new_details.subscription_users)
    ):

        changed = True

    return changed


def new_sub_details_html(lab_dict, sub_dict, new_sub, show_expiry_date=False):
    """
    Generates html content for the details of a new subscription.

    Arguments:
        ab_dict - lab name /internal id dictionary
        sub_dict - subscription id /internal id dictionary
        new_sub - details of a new subscriptions
        show_expiry_date - flag to always show expiry date

    Return:
        new_sub_html - html content
    """

    course_name, lab_name = list(lab_dict.keys())[
        list(lab_dict.values()).index(new_sub.lab_id)
    ]

    sub_guid = list(sub_dict.keys())[list(sub_dict.values()).index(new_sub.sub_id)]

    new_sub_html = "&#9 Course: <i>%s</i><br>" % (course_name)
    new_sub_html += "&#9 Lab: <i>%s</i><br>" % (lab_name)
    new_sub_html += "&#9 Handout status: <i>%s</i><br>" % (new_sub.handout_status)

    new_sub_html += "<br>"

    new_sub_html += "&#9 Subscription name: <i>%s</i><br>" % (new_sub.subscription_name)
    new_sub_html += "&#9 Subscription ID: <i>%s</i><br>" % (sub_guid)
    new_sub_html += "&#9 Subscription status: <i>%s</i><br>" % (
        new_sub.subscription_status
    )

    new_sub_html += "<br>"

    if (
        new_sub.subscription_status.lower() != CONST_SUB_CANCELLED.lower()
        or show_expiry_date
    ):

        if isinstance(new_sub.subscription_expiry_date, datetime.datetime):
            new_sub_html += "&#9 Expiry date: <i>%s</i><br>" % (
                new_sub.subscription_expiry_date.date()
            )
        else:
            new_sub_html += "&#9 Expiry date: <i>%s</i><br>" % (
                new_sub.subscription_expiry_date
            )

    new_sub_html += "&#9 Budget: <i>${:,.2f}</i> <br>".format(new_sub.handout_budget)

    new_sub_html += "&#9 Consumed: <i>%s</i><br>" % (
        "${:,.2f}".format(new_sub.handout_consumed)
    )

    new_sub_html += "&#9 Users: <i>%s</i><br><br>" % (new_sub.subscription_users)

    return new_sub_html


def upd_sub_details_html(lab_dict, sub_dict, upd_sub, show_expiry_date=False):
    """
    Generates html content for the details of an updated subscription.

    Arguments:
        ab_dict - lab name /internal id dictionary
        sub_dict - subscription id /internal id dictionary
        upd_sub - tuple (before, after) of subscription details
        show_expiry_date - flag to always show expiry date
    Return:
        upd_sub_html - html content
    """

    prev_details = upd_sub[0]
    new_details = upd_sub[1]

    course_name, lab_name = list(lab_dict.keys())[
        list(lab_dict.values()).index(new_details.lab_id)
    ]

    sub_guid = list(sub_dict.keys())[list(sub_dict.values()).index(new_details.sub_id)]

    upd_sub_html = "&#9 Course: <i>%s</i><br>" % (course_name)
    upd_sub_html += "&#9 Lab: <i>%s</i><br>" % (lab_name)

    upd_sub_html += value_change(
        "Handout status", prev_details.handout_status, new_details.handout_status
    )

    upd_sub_html += "<br>"

    upd_sub_html += value_change(
        "Subscription name",
        prev_details.subscription_name,
        new_details.subscription_name,
    )

    upd_sub_html += "&#9 Subscription ID: <i>%s</i><br>" % (sub_guid)

    upd_sub_html += value_change(
        "Subscription status",
        prev_details.subscription_status,
        new_details.subscription_status,
    )

    upd_sub_html += "<br>"

    prev_expiry_date = prev_details.subscription_expiry_date.strftime("%Y-%m-%d")
    new_expiry_date = new_details.subscription_expiry_date.strftime("%Y-%m-%d")

    if (
        new_details.subscription_status.lower() != CONST_SUB_CANCELLED.lower()
        or show_expiry_date
    ):
        upd_sub_html += value_change("Expiry date", prev_expiry_date, new_expiry_date)

    prev_budget = "${:,.2f}".format(prev_details.handout_budget)
    new_budget = "${:,.2f}".format(new_details.handout_budget)

    upd_sub_html += value_change("Budget", prev_budget, new_budget)

    upd_sub_html += "&#9 Consumed: <i>%s</i><br>" % (
        "${:,.2f}".format(new_details.handout_consumed)
    )

    prev_users = prev_details.subscription_users.split(",")
    new_users = new_details.subscription_users.split(",")

    upd_sub_html += "&#9 Users:"

    user_cnt = 0
    for user in prev_users:
        if user in new_users:
            if user_cnt > 0:
                upd_sub_html += ","
            upd_sub_html += " <i>%s</i>" % (user)
        else:
            if user_cnt > 0:
                upd_sub_html += ","
            upd_sub_html += " <strike><i>%s</i></strike>" % (user)
        user_cnt += 1

    for user in new_users:
        if user not in prev_users:
            if user_cnt > 0:
                upd_sub_html += ","
            upd_sub_html += " <strong><i>%s</i></strong>" % (user)
        user_cnt += 1

    upd_sub_html += "<br>"
    upd_sub_html += "<br>"

    return upd_sub_html


def contact_us_html():
    """
    Generates contact us html content.

    """

    # Contact us
    return (
        "<div>If the information presented in this email does not match your"
        + " expectations or if you have questions related to this service, please contact"
        + ' us by submiting a ticket on <a href="https://turingcomplete.topdesk.net/tas/public/'
        + "ssp/content/serviceflow?unid=0d44e83330e54fac9984742ab85b4e8f&from=7edfe644-ac0d-4895"
        + '-af98-acd425ee0b19&openedFromService=true">Turing Complete</a>.</div>'
    )


def disabled_html():
    """
    Generates contact us html content.

    """
    return (
        "<div>Once a subscription is cancelled (i.e. expires) Microsoft will <b>"
        + '<a href="https://docs.microsoft.com/en-us/microsoft-365/commerce/subscriptions/what-if-my-subscription-expires?view=o365-worldwide"'
        + ">permanently delete all data after 90 days</a></b>. If you wish to access data on your cancelled subscription, "
        + "you should get in touch with us via "
        + '<a href="https://turingcomplete.topdesk.net/tas/public/'
        + "ssp/content/serviceflow?unid=0d44e83330e54fac9984742ab85b4e8f&from=7edfe644-ac0d-4895"
        + '-af98-acd425ee0b19&openedFromService=true">Turing Complete</a> '
        + "as soon as possible.<br><br>Please also note that <b>we will not be able to extend your "
        + "subscription beyond <span style='color:red'>11 October 2021</span></b>. We strongly advise you to transfer your information "
        + "from the subscription in advance of the 11 October 2021 deadline, otherwise you risk "
        + "of losing access to data and Azure resources associated with the subscription.</div>"
    )


def summary(lab_dict, sub_dict, new_sub_list, upd_sub_list, sent_noti_list, from_date, to_date):
    """
    Generates summary email content as an html document. It includes information about new
        and updated subscriptions.

    Arguments:
        lab_dict - lab name /internal id dictionary
        sub_dict - subscription id /internal id dictionary
        new_sub_list - a list of details of new subscriptions
        upd_sub_list - a list of tuple (before, after) of subscription details
        sent_noti_list - a list of sent notifications as details entries
        from_date - timestamp of the previous successful eduhub log update
        to_date - timestamp of the current successful eduhub log update
    Returns:
        success - flag if the action was succesful
        error - error message
        html_content - summary as an html text
    """

    sub_update_details_list = []

    # check which subsciptions have chaged details
    for _, sub_update in enumerate(upd_sub_list):

        prev_details = sub_update[0]
        new_details = sub_update[1]

        if details_changed(prev_details, new_details):
            sub_update_details_list.append((prev_details, new_details))

    html_content = email_top("EduHub Activity Update")

    html_middle = '<div style="font-size:18px;line-height:16px;text-align:left">'

    to_date_str = to_date.astimezone(tzlocal()).strftime("%Y-%m-%d %H:%M")
    if from_date is None:
        html_middle += "%s" % (to_date_str)
    else:
        from_date_str = from_date.astimezone(tzlocal()).strftime("%Y-%m-%d %H:%M")
        html_middle += "%s - %s" % (from_date_str, to_date_str)

    html_middle += " (%s)</div><br>" % (CONST_TIME_ZONE_NAME)
    html_middle += '<div style="border-bottom:1px solid #ededed"></div>'

    # no updates
    if len(new_sub_list) == 0 and len(sub_update_details_list) == 0:
        html_middle += "No new subscriptions or updates."

    # new subscriptions
    if len(new_sub_list) > 0:

        html_middle += "New subscriptions (%d):" % (len(new_sub_list))
        html_middle += '<div style="font-size:12px;line-height:16px;text-align:left">'

        new_subs = ""

        for _, new_sub in enumerate(new_sub_list):

            sub_guid = list(sub_dict.keys())[
                list(sub_dict.values()).index(new_sub.sub_id)
            ]

            new_subs += "<li><b>%s</b> (%s)</li><br>" % (
                new_sub.subscription_name,
                sub_guid,
            )

            new_subs += new_sub_details_html(
                lab_dict, sub_dict, new_sub, show_expiry_date=True
            )

        html_middle += "<p><ul>" + new_subs + "</ul></p>"

        html_middle += "</div>"

    # middle line between new subscriptions and updates
    if len(new_sub_list) > 0 and len(sub_update_details_list) > 0:
        html_middle += '<div style="border-bottom:1px solid #ededed"></div>'

    # updates
    if len(sub_update_details_list) > 0:

        html_middle += "Updates (%d):" % (len(sub_update_details_list))
        html_middle += '<div style="font-size:12px;line-height:16px;text-align:left">'

        sub_updates = ""

        for _, sub_update in enumerate(sub_update_details_list):

            prev_details = sub_update[0]
            new_details = sub_update[1]

            sub_guid = list(sub_dict.keys())[
                list(sub_dict.values()).index(new_details.sub_id)
            ]

            sub_updates += "<li><b>%s</b> (%s)</li><br>" % (
                new_details.subscription_name,
                sub_guid,
            )

            sub_updates += upd_sub_details_html(
                lab_dict, sub_dict, sub_update, show_expiry_date=True
            )

        html_middle += "<p><ul>" + sub_updates + "</ul></p>"

        html_middle += "</div>"

    # Notifications sent
    if len(sent_noti_list) > 0:
        noti_sent_html = ""

        html_middle += '<div style="border-bottom:1px solid #ededed"></div><br>'
        html_middle += "Notifications sent (%d):" % (len(sent_noti_list))
        html_middle += '<div style="font-size:12px;line-height:16px;text-align:left">'

        prev_sub_guid = None

        for _, sent_noti in enumerate(sent_noti_list):

            sub_guid = list(sub_dict.keys())[
                list(sub_dict.values()).index(sent_noti.sub_id)
            ]

            if sub_guid != prev_sub_guid:
                noti_sent_html += "<li><b>%s</b> (%s)</li><br>" % (
                    sent_noti.subscription_name,
                    sub_guid,
                )

            if sent_noti.new_notice_sent:
                noti_sent_html += "<div>%s: %s (%s)</div><br>" % (
                    CONST_EMAIL_SUBJECT_NEW,
                    sent_noti.new_notice_sent.strftime("%Y-%m-%d %H:%M:%S"),
                    CONST_TIME_ZONE_NAME,
                )

            if sent_noti.update_notice_sent:
                noti_sent_html += "<div>%s: %s (%s)</div><br>" % (
                    CONST_EMAIL_SUBJECT_UPD,
                    sent_noti.update_notice_sent.strftime("%Y-%m-%d %H:%M:%S"),
                    CONST_TIME_ZONE_NAME,
                )

            if sent_noti.expiry_notice_sent:
                noti_sent_html += "<div>%s (%d): %s (%s)</div><br>" % (
                    CONST_EMAIL_SUBJECT_EXPIRE,
                    sent_noti.expiry_code,
                    sent_noti.expiry_notice_sent.strftime("%Y-%m-%d %H:%M:%S"),
                    CONST_TIME_ZONE_NAME,
                )

            if sent_noti.usage_notice_sent:
                noti_sent_html += "<div>%s (%d): %s (%s)</div><br>" % (
                    CONST_EMAIL_SUBJECT_USAGE,
                    sent_noti.usage_code,
                    sent_noti.usage_notice_sent.strftime("%Y-%m-%d %H:%M:%S"),
                    CONST_TIME_ZONE_NAME,
                )

            prev_sub_guid = sub_guid

        html_middle += "<p><ul>" + noti_sent_html + "</ul></p>"

        html_middle += "</div>"

    html_content += email_middle(html_middle)

    html_content += email_bottom()

    return True, None, html_content


def indiv_email_new(lab_dict, sub_dict, new_sub):
    """
    Generates new subscription email content as an html document.

    Arguments:
        lab_dict - lab name /internal id dictionary
        sub_dict - subscription id /internal id dictionary
        new_sub - details of a new subscription
    Returns:
        success - flag if the action was succesful
        error - error message
        html_content - summary as an html text
    """

    # # Check if the subscription is cancelled
    # if new_sub.subscription_status.lower() == CONST_SUB_CANCELLED.lower():
    #     html_content = email_top(CONST_EMAIL_SUBJECT_CANCELLED)
    # else:
    html_content = email_top(CONST_EMAIL_SUBJECT_NEW)

    html_middle = '<div style="font-size:12px;line-height:16px;text-align:left">'
    html_middle += (
        "<div>You are receiving this email because a subscription has been"
        + " registered on EduHub notification service (<b>EduNotice</b>)"
    )

    if new_sub.subscription_status.lower() == CONST_SUB_CANCELLED.lower():
        html_middle += " as <b>cancelled</b>"

    html_middle += " and you are listed as its user.</div>"
    html_middle += '<br><div style="border-bottom:1px solid #ededed"></div><br>'

    # Subscription details
    html_middle += "<div><b>Subscription details:</b></div><br>"
    html_middle += new_sub_details_html(lab_dict, sub_dict, new_sub)
    html_middle += '<div style="border-bottom:1px solid #ededed"></div><br>'

    # Check if the subscription is cancelled
    if new_sub.subscription_status.lower() == CONST_SUB_CANCELLED.lower():
        html_middle += disabled_html()
        html_middle += '<br><div style="border-bottom:1px solid #ededed"></div><br>'

    # Communications
    html_middle += "<div><b>Communications:</b> EduNotice will send the following communications</div>"
    html_middle += "<div><ul>"
    html_middle += "<li><b>Confirmation:</b> an email denoting the registration of the subscription.</li><br>"
    html_middle += "<li><b>Updates:</b> notification emails denoting changes in the subscription details.</li><br>"
    html_middle += "<li><b>Time-based:</b> notification emails denoting the amount of time remaining in the subscription duration according to the following schedule.</li>"
    html_middle += "<ul>"
    html_middle += "<li>Notification 1: 30 days before end</li>"
    html_middle += "<li>Notification 2: 7 days before end</li>"
    html_middle += "<li>Notification 3: 1 day before end</li>"
    html_middle += "</ul><br>"
    html_middle += "<li><b>Usage-based:</b> notification emails denoting the monetary amount remaining in the subscription according to the following schedule.</li>"
    html_middle += "<ul>"
    html_middle += "<li>Notification 1: 50% of monetary credit has been used</li>"
    html_middle += "<li>Notification 2: 75% of monetary credit has been used</li>"
    html_middle += "<li>Notification 3: 90% of monetary credit has been used</li>"
    html_middle += "<li>Notification 4: 95% of monetary credit has been used</li>"
    html_middle += "</ul>"
    html_middle += "</ul></div>"
    html_middle += '<br><div style="border-bottom:1px solid #ededed"></div><br>'

    # Disclaimer
    html_middle += (
        "<div><b>Disclaimer:</b> EduNotice is only for"
        + " demonstration purposes and we make no warranties of any kind, express or implied,"
        + " about the completeness, accuracy, reliability, suitability or availability with"
        + " respect to the information and service. However, we endeavour to make reasonable"
        + " effort to keep the information and service up to date and correct. </div>"
    )

    html_middle += '<br><div style="border-bottom:1px solid #ededed"></div><br>'

    # Contact us
    html_middle += contact_us_html()

    html_middle += "</div>"

    html_content += email_middle(html_middle)

    html_content += email_bottom()

    return True, None, html_content


def indiv_email_upd(lab_dict, sub_dict, upd_sub):
    """
    Generates subscription update email content as an html document.

    Arguments:
        lab_dict - lab name /internal id dictionary
        sub_dict - subscription id /internal id dictionary
        upd_sub - tuple (before, after) of subscription details
    Returns:
        success - flag if the action was succesful
        error - error message
        html_content - summary as an html text
    """

    # if upd_sub[1].subscription_status.lower() == CONST_SUB_CANCELLED.lower():
    #     html_content = email_top(CONST_EMAIL_SUBJECT_CANCELLED)
    # else:
    html_content = email_top(CONST_EMAIL_SUBJECT_UPD)

    html_middle = '<div style="font-size:12px;line-height:16px;text-align:left">'
    html_middle += (
        "<div>You are receiving this email because a subscription has been "
    )

    if upd_sub[1].subscription_status.lower() == CONST_SUB_CANCELLED.lower():
        html_middle += "<b>cancelled</b>"
    else:
        html_middle += "updated"

    html_middle += " and you are listed as its user.</div>"
    html_middle += '<br><div style="border-bottom:1px solid #ededed"></div><br>'

    # Details
    html_middle += upd_sub_details_html(lab_dict, sub_dict, upd_sub)
    html_middle += '<br><div style="border-bottom:1px solid #ededed"></div><br>'

    # Check if the subscription is cancelled
    if upd_sub[1].subscription_status.lower() == CONST_SUB_CANCELLED.lower():
        html_middle += disabled_html()
        html_middle += '<br><div style="border-bottom:1px solid #ededed"></div><br>'

    # Contact us
    html_middle += contact_us_html()

    html_middle += "</div>"

    html_content += email_middle(html_middle)

    html_content += email_bottom()

    return True, None, html_content


def indiv_email_expiry_notification(lab_dict, sub_dict, sub_details, remain_days):
    """
    Generates time-based notification content as an html document.

    Arguments:
        lab_dict - lab name /internal id dictionary
        sub_dict - subscription id /internal id dictionary
        sub_details - subscription details
        remain_days - number of remaining days
    Returns:
        success - flag if the action was succesful
        error - error message
        html_content - summary as an html text
    """

    html_content = email_top("%s %d day(s)" % (CONST_EMAIL_SUBJECT_EXPIRE, remain_days))

    html_middle = '<div style="font-size:12px;line-height:16px;text-align:left">'

    html_middle += (
        "<div>You are receiving this email because a subscription will expire "
        + "in %d days and you are listed as its user.</div>" % (remain_days)
    )

    html_middle += '<br><div style="border-bottom:1px solid #ededed"></div><br>'

    # Important notice
    html_middle += disabled_html()

    html_middle += '<br><div style="border-bottom:1px solid #ededed"></div><br>'

    # Subscription details
    html_middle += "<div><b>Subscription details:</b></div><br>"

    html_middle += new_sub_details_html(lab_dict, sub_dict, sub_details)

    html_middle += '<div style="border-bottom:1px solid #ededed"></div><br>'

    # Contact us
    html_middle += contact_us_html()

    html_middle += "</div>"

    html_content += email_middle(html_middle)

    html_content += email_bottom()

    return True, None, html_content


def indiv_email_usage_notification(lab_dict, sub_dict, sub_details, usage_code):
    """
    Generates usage-based notification content as an html document.

    Arguments:
        lab_dict - lab name /internal id dictionary
        sub_dict - subscription id /internal id dictionary
        sub_details - subscription details
        usage_code - usage code
    Returns:
        success - flag if the action was succesful
        error - error message
        html_content - summary as an html text
    """

    html_content = email_top("%s %d%%" % (CONST_EMAIL_SUBJECT_USAGE, usage_code))

    html_middle = '<div style="font-size:12px;line-height:16px;text-align:left">'

    html_middle += (
        "<div>You are receiving this email because a subscription has reached &#8805; "
        + "%d%% utilisation and you are listed as its user. Once a subscription utilises its budget, it will be cancelled.</div>"
        % (usage_code)
    )

    html_middle += '<br><div style="border-bottom:1px solid #ededed"></div><br>'

    # Important notice
    html_middle += disabled_html()

    html_middle += '<br><div style="border-bottom:1px solid #ededed"></div><br>'

    # Subscription details
    html_middle += "<div><b>Subscription details:</b></div><br>"

    html_middle += new_sub_details_html(lab_dict, sub_dict, sub_details)

    html_middle += '<div style="border-bottom:1px solid #ededed"></div><br>'

    # Contact us
    html_middle += contact_us_html()

    html_middle += "</div>"

    html_content += email_middle(html_middle)

    html_content += email_bottom()

    return True, None, html_content
