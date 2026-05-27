
lst = "'a-c','b-b','c-b'"

def format_hashtags(tag_list):
    """
    tag_list: list of comma-separated tags with no spaces.
    """
    tags = tag_list.split(',')
    tags = ['#' + tag.strip().replace(' ', '').replace('-','') for tag in tags]
    return ' '.join(tags)

print(format_hashtags(lst))