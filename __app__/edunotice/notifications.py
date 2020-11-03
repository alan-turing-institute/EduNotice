"""
Notification/email composition module
"""


def email_top(headline):
    """
    Generates the top section with a headline.

    Arguments:
        headline - headline of the top section
    Returns:
        html_content - html code
    """

    html_content = '<html><body>'
    html_content += '<div dir="ltr" style="font-family:verdana;font-size:12px;color:#555555;line-height:14pt">'
    html_content += '<div style="width:590px">'

    html_content += '<div style="background:url(\'https://www.gstatic.com/android/market_images/email/email_top.png\') no-repeat;width:100%;height:75px;display:block">'
    html_content += '<div style="padding-top:30px;padding-left:50px;padding-right:50px;font-size:24px;">'
    
    html_content += '<div>%s</div>' % (headline)

    html_content += '</div>'
    html_content += '</div>'

    return html_content


def email_bottom():
    """
    Generates the bottom section with a headline.

    Returns:
        html_content - html code
    """

    html_content = '<div style="background:url(\'https://www.gstatic.com/android/market_images/email/email_bottom.png\') no-repeat;width:100%;height:50px;display:block"></div>'

    html_content += '</div></div></body></html>'

    return html_content


def email_middle(content):
    """
    Generates the middle section with the provided content.

    Arguments:
        content - html content of the middle section
    Returns:
        html_content - html code
    """

    html_content = '<div style="background:url(\'https://www.gstatic.com/android/market_images/email/email_mid.png\') repeat-y;width:100%;display:block">'
    html_content += '<div style="padding-left:50px;padding-right:50px;padding-bottom:1px">'
    html_content += '<div style="border-bottom:1px solid #ededed"></div>'
    html_content += '<div style="margin:20px 0px;font-size:20px;line-height:30px;text-align:left">'

    html_content += content

    html_content += '</div>'
    html_content += '<div style="text-align:left"></div>'
    html_content += '<div style="border-bottom:1px solid #ededed"></div>'
    html_content += '<br>'
    html_content += '<div>This automated email notification was sent from the Turing Research Compute Platforms cloud platform.</div>'
    html_content += '</div></div>'

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
        html_content = "&#9 %s: <strike><i>%s</i></strike> &rarr; <strong><i>%s</i></strong><br>" % (paramter_name, old_value, new_value)
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

    if ((prev_details.handout_status != new_details.handout_status) or 
        (prev_details.subscription_name != new_details.subscription_name) or
        (prev_details.subscription_status != new_details.subscription_status) or
        (prev_details.subscription_expiry_date != new_details.subscription_expiry_date) or
        (prev_details.handout_budget != new_details.handout_budget) or
        (prev_details.subscription_users != new_details.subscription_users)):

        changed = True

    return changed


def summary(lab_dict, sub_dict, sub_new_list, sub_update_list, from_date, to_date):
    """
    Generates summary email content as an html document. It includes information about new 
        and updated subscriptions.

    Arguments:
        lab_dict - lab name /internal id dictionary
        sub_dict - subscription id /internal id dictionary
        sub_new_list - a list of details of new subscriptions
        sub_update_list - a list of tuple (before, after) of subscription details
        from_date - timestamp of the previous successful eduhub log update
        to_date - timestamp of the current successful eduhub log update
    Returns:
        success - flag if the action was succesful
        error - error message
        html_content - summary as an html text
    """

    sub_update_details_list = []

    # check which subsciptions have chaged details
    for i, sub_update in enumerate(sub_update_list):
        
        prev_details = sub_update[0]
        new_details = sub_update[1]

        if details_changed(prev_details, new_details):
            sub_update_details_list.append((prev_details, new_details))

    html_content = email_top("EduHub Activity Update")
    
    html_middle = '<div style="font-size:18px;line-height:16px;text-align:left">'

    to_date_str = to_date.strftime("%Y-%m-%d %H:%M")
    if from_date is None:
        html_middle += "%s" % (to_date_str)
    else:
        from_date_str = from_date.strftime("%Y-%m-%d %H:%M")
        html_middle += "%s - %s" % (from_date_str, to_date_str)
    
    html_middle += " (UTC)</div><br>"
    html_middle += '<div style="border-bottom:1px solid #ededed"></div>'

    # no updates
    if len(sub_new_list) == 0 and len(sub_update_details_list) == 0:
        html_middle += "No new subscriptions or updates."

    # new subscriptions
    if len(sub_new_list) > 0:

        html_middle += "New subscriptions (%d):" % (len(sub_new_list))
        html_middle += '<div style="font-size:12px;line-height:16px;text-align:left">'
        
        new_subs = ""

        for i, new_sub in enumerate(sub_new_list):
            
            course_name, lab_name = list(lab_dict.keys())[list(lab_dict.values()).index(new_sub.lab_id)]

            sub_guid = list(sub_dict.keys())[list(sub_dict.values()).index(new_sub.sub_id)]

            new_subs += "<li><b>%s</b> (%s)</li><br>" % (new_sub.subscription_name, sub_guid)

            new_subs += "&#9 Course: <i>%s</i><br>" % (course_name)
            new_subs += "&#9 Lab: <i>%s</i><br>" % (lab_name)
            new_subs += "&#9 Handout status: <i>%s</i><br>" % (new_sub.handout_status)

            new_subs += "<br>"

            new_subs += "&#9 Subscription name: <i>%s</i><br>" % (new_sub.subscription_name)
            new_subs += "&#9 Subscription ID: <i>%s</i><br>" % (sub_guid)
            new_subs += "&#9 Subscription status: <i>%s</i><br>" % (new_sub.subscription_status)

            new_subs += "<br>"

            new_subs += "&#9 Expiry date: <i>%s</i><br>" % (new_sub.subscription_expiry_date)
            new_subs += "&#9 Budget: <i>${:,.2f}</i> <br>".format(new_sub.handout_budget)
            new_subs += "&#9 Users: <i>%s</i><br><br>" % (new_sub.subscription_users)

        html_middle += "<p><ul>" + new_subs + "</ul></p>"

        html_middle += '</div>'

    # middle line between new subscriptions and updates
    if len(sub_new_list) > 0 and len(sub_update_details_list) > 0:
        html_middle += '<div style="border-bottom:1px solid #ededed"></div>'

    if len(sub_update_details_list) > 0:

        html_middle += "Updates (%d):" % (len(sub_update_details_list))
        html_middle += '<div style="font-size:12px;line-height:16px;text-align:left">'
        
        sub_updates = ""

        for i, sub_update in enumerate(sub_update_details_list):
            
            prev_details = sub_update[0]
            new_details = sub_update[1]

            course_name, lab_name = list(lab_dict.keys())[list(lab_dict.values()).index(new_details.lab_id)]

            sub_guid = list(sub_dict.keys())[list(sub_dict.values()).index(new_details.sub_id)]

            sub_updates += "<li><b>%s</b> (%s)</li><br>" % (
                new_details.subscription_name, sub_guid)

            sub_updates += "&#9 Course: <i>%s</i><br>" % (course_name)
            sub_updates += "&#9 Lab: <i>%s</i><br>" % (lab_name)

            sub_updates += value_change("Handout status", 
                prev_details.handout_status, new_details.handout_status)

            sub_updates += "<br>"

            sub_updates += value_change("Subscription name", 
                prev_details.subscription_name, new_details.subscription_name)
            
            sub_updates += "&#9 Subscription ID: <i>%s</i><br>" % (sub_guid)

            sub_updates += value_change("Subscription status", 
                prev_details.subscription_status, new_details.subscription_status)

            sub_updates += "<br>"

            prev_expiry_date = prev_details.subscription_expiry_date.strftime("%Y-%m-%d")
            new_expiry_date = new_details.subscription_expiry_date.strftime("%Y-%m-%d")

            sub_updates += value_change("Expiry date", prev_expiry_date, new_expiry_date)

            prev_budget = "${:,.2f}".format(prev_details.handout_budget)
            new_budget = "${:,.2f}".format(new_details.handout_budget)

            sub_updates += value_change("Budget", prev_budget, new_budget)

            sub_updates += "&#9 Consumed: <i>%s</i><br>" % ("${:,.2f}".format(new_details.handout_consumed))
            
            prev_users = prev_details.subscription_users.split(",")
            new_users = new_details.subscription_users.split(",")

            sub_updates += "&#9 Users:"

            user_cnt = 0
            for user in prev_users:
                if user in new_users:
                    if user_cnt > 0:
                        sub_updates += ","
                    sub_updates += " <i>%s</i>" % (user)
                else:
                    if user_cnt > 0:
                        sub_updates += ","
                    sub_updates += " <strike><i>%s</i></strike>" % (user)
                user_cnt += 1

            for user in new_users:
                if user not in prev_users:
                    if user_cnt > 0:
                        sub_updates += ","
                    sub_updates += " <strong><i>%s</i></strong>" % (user)
                user_cnt += 1
            
            sub_updates += "<br>"
            sub_updates += "<br>"

        html_middle += "<p><ul>" + sub_updates + "</ul></p>"

        html_middle += '</div>'

    html_content += email_middle(html_middle)

    html_content += email_bottom()

    return True, None, html_content