#email_filters


from datetime import datetime, timedelta


def build_search_query(days=7, target_email=None, from_email=None, unread_only=False):
    filters = []

    date_since = (datetime.now() - timedelta(days=days)).strftime("%d-%b-%Y")
    filters.append(f'SINCE {date_since}')

    if target_email:
        filters.append(f'TO "{target_email}"')
    if from_email:
        filters.append(f'FROM "{from_email}"')
    if unread_only:
        filters.append("UNSEEN")

    return f'({" ".join(filters)})'


