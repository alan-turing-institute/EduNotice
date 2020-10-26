"""
Notification/email composition module
"""

def summary(lab_dict, sub_dict, sub_new_list, sub_update_list, from_date=None, to_date=None):
    """


    Arguments:
        lab_dict - lab name /internal id dictionary
        sub_dict - subscription id /internal id dictionary
        sub_new_list - a list of details of new subscriptions
        sub_update_list - a list of tuple (before, after) of subscription details
    Returns:
        success - flag if the action was succesful
        error - error message
        html_content - summary as an html text
    """

    
    html_content = "<html><body>"
    
    html_content += "<p>EduHub activity monitor update from ---- to ---- </p>"

    html_content += "<p><h3>New subscriptions:</h3></p>"

    new_subs = ""
    
    for i, new_sub in enumerate(sub_new_list):
        
        course_name, lab_name = list(lab_dict.keys())[list(lab_dict.values()).index(new_sub.lab_id)]

        new_subs += "<li><b>%s</b> (%s)</li><br>" % (
            new_sub.subscription_name,
            list(sub_dict.keys())[list(sub_dict.values()).index(new_sub.sub_id)])

        new_subs += "&#9 Course: <i>%s</i><br>" % (course_name)
        new_subs += "&#9 Lab: <i>%s</i><br>" % (lab_name)
        new_subs += "&#9 Budget: <i>${:,.2f}</i> <br>".format(new_sub.handout_budget)
        new_subs += "&#9 Expiry date: <i>%s</i><br>" % (new_sub.subscription_expiry_date)
        new_subs += "&#9 Users: <i>%s</i><br><br>" % (new_sub.subscription_users)

    html_content += "<p><ul>" + new_subs + "</ul></p>"

    html_content += "<p>This automated email notification was sent from the Turing RCP Cloud Platform.</p>"

    html_content += "</body></html>"

    return True, None, html_content

