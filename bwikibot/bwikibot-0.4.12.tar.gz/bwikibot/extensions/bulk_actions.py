#coding=utf8

from bwikibot.cli import get_wiki, get_secondary_wiki, action


@action('bulk_export')
def bulk_export(*title_prefix):
    ''' Copy pages with given prefix from primary wiki to secondary. '''
    prefix = ' '.join(title_prefix).strip()
    if not prefix:
        print('Need some prefix passed as argument')
        return
    source_wiki = get_wiki()
    dest_wiki = get_secondary_wiki()

    if ':' in prefix:
        namespace, prefix = prefix.split(':', 1)
        ns_id = source_wiki.get_namespace_id(namespace)
        print(ns_id)
        if not ns_id: # back to prefix
            prefix = namespace + ':' + prefix

    comment = 'Автоматичний експорт з {}'.format(
        source_wiki.endpoint.split('/')[2]
    )

    for page in source_wiki.get_pages(prefix=prefix, namespace=ns_id):
        print('Exporting page: {}'.format(page.title))
        dest_page = dest_wiki.page(page.title)
        if not dest_page.exists():
            dest_page.write(page.read(), comment)
        else:
            print('\tPage already exists!')
    print('Done.')

def bulk_delete(wiki_chooser, title_prefix, reason):
    reason = reason or 'Автоматичне видалення всіх з префіксом "{}"'.format(
        title_prefix
    )
    wiki = wiki_chooser()

    for page in wiki.get_pages(prefix=title_prefix):
        print('Deleting page: {}'.format(page.title))
        page.delete(reason)

@action('bulk_delete2')
def bulk_delete2(title_prefix, reason=None):
    ''' Delete all pages of secondary wiki which starts with prefix '''
    bulk_delete(get_secondary_wiki, title_prefix, reason)

@action('bulk_delete')
def bulk_delete1(title_prefix, reason=None):
    ''' Delete all pages of primary wiki which starts with prefix '''
    bulk_delete(get_wiki, title_prefix, reason)
