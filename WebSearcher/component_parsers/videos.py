""" Parsers for video components

Changelog
2021-05-08: added find_all for divs with class 'VibNM'
2021-05-08: added adjustment for new cite and timestamp

"""


def parse_videos(cmpt):
    """Parse a videos component

    These components contain links to videos, frequently to YouTube.
    
    Args:
        cmpt (bs4 object): A videos component
    
    Returns:
        list : list of parsed subcomponent dictionaries
    """
    subs = cmpt.find_all(['g-inner-card'])
    subs = cmpt.find_all('div', {'class': ['VibNM','pwxRSe', 'RzdJxc']}) if not subs else subs
    return [parse_video(sub, sub_rank) for sub_rank, sub in enumerate(subs)]


def parse_video(sub, sub_rank=0):
    """Parse a videos subcomponent
    
    Args:
        sub (bs4 object): A video subcomponent
    
    Returns:
        dict : parsed subresult
    """
    parsed = {'type': 'videos', 'sub_rank': sub_rank}
    # OR Code ---------------------
    # Find all <a> tags within the specific component (e.g., <div class="content">)
    a_tags = sub.find_all('a')
    # Initialize the 'url' variable to store the first link that starts with "http" or "https"
    parsed['url'] = None

    # Loop through all <a> tags and find the first link that starts with "http" or "https"
    for a_tag in a_tags:
        link = a_tag.get('href')
        if link and (link.startswith('http://') or link.startswith('https://')):
            parsed['url'] = link
            break

    # parsed['url'] = sub.find('a')['href']
    try:
        parsed['title'] = sub.find('div', {'role': 'heading'}).text
    except:
        parsed['title'] = sub.find('a').get('aria-label')

    details = sub.find_all('div', {'class': 'MjS0Lc'})
    if details:
        text_div, citetime_div = details
        parsed['text'] = text_div.text if text_div else None

        if citetime_div:
            # Sometimes there is only a cite
            citetime = citetime_div.find('div', {'class': 'zECGdd'})
            citetime = list(citetime.children)
            if len(citetime) == 2:
                cite, timestamp = citetime
                parsed['cite'] = cite.text
                parsed['timestamp'] = timestamp.replace(' - ', '')
            else:
                parsed['cite'] = citetime[0].text
    else:
        try:
            parsed['cite'] = sub.find('span', {'class': 'ocUPSd'}).text
        except:
            pass
        parsed['timestamp'] = get_div_text(sub, {'class': 'rjmdhd'})

    parsed['details'] = {}
    parsed['details']['img_url'] = get_img_url(sub)

    # Check for "key moments" in video
    key_moments_div = sub.find('div', {'class': 'AvBz0e'})
    parsed['details']['key_moments'] = True if key_moments_div else False

    return parsed


def get_div_text(soup, details):
    div = soup.find('div', details)
    return div.text if div else None


def get_img_url(soup):
    """Extract image source"""
    img = soup.find('img')
    if img and 'data-src' in img.attrs:
        return img.attrs['data-src']
