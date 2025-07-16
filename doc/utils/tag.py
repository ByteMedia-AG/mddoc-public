from itertools import groupby


def get_tags_grouped(tags):
    """
    Von jedem Anfangsbuchstaben werden jeweils nur die 5 häufigsten zur Anzeige gebracht.
    """
    try:
        grouped = []
        tags_sorted = sorted(tags, key=lambda t: (t.slug[0].upper(), -getattr(t, 'num_times', 0)))
        for first_letter, group in groupby(tags_sorted, key=lambda t: t.slug[0].upper()):
            group_list = list(group)
            top_tags = sorted(group_list[:5], key=lambda t: t.slug.lower())  # alphabetisch sortieren nach Begrenzung
            for i, tag in enumerate(top_tags):
                tag.is_last_in_group = (i == len(top_tags) - 1)
            grouped.append((first_letter, top_tags))
        return grouped
    except Exception as e:
        return []
