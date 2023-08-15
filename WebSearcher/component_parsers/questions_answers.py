def parse_questions_and_answers(cmpt, ctype='questions_and_answers'):
    subs = cmpt.find_all('div', {'class': 'BmkBMc'})
    return [parse_q_and_a(sub, ctype, sub_rank) for sub_rank, sub in enumerate(subs)]


def parse_q_and_a(sub, ctype, sub_rank):
    parsed = {'type': ctype, 'sub_rank': sub_rank, 'url': sub.find('a')['href']}
    return parsed