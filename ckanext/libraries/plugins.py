#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

from pylons import config
import ckan.plugins as p
from ckan.lib.navl.dictization_functions import Missing
from ckan.common import request
import ckan.lib.helpers as h

import urllib
from bs4 import BeautifulSoup
from datetime import datetime
import random


def _dumps(o):
    if isinstance(o, Missing):
        return o
    return json.dumps(o)


def recently_changed_packages(limit, offset):
    packages = p.toolkit.get_action('recently_changed_packages_activity_list')(
        data_dict={
            'offset': offset,
            'limit': min(limit, len(get_datasets())),
        }
    )

    return [package['data'].get('package') or package['data'].get('dataset')
            for package in packages]


def dynamic_content():
    def _dataset(token, text):
        return text.replace(token, '[%d](%s)' % (
            len(get_datasets()),
            h.url_for(controller='package', action='search'))
        )

    return {
        '[datasets#]': _dataset,
    }


# if we ever were to change to a wysiwyg for the intro text
def render_html_with_dynamic_content(html):
    changes = dynamic_content()
    for token in changes:
        if token in html:
            html = changes[token](token, html)
    return html


def render_markdown_with_dynamic_content(markdown):
    # Honestly, there probably will never be any use of plain [dataset#]
    # as a pure string, so for now I won't provide an escape for the sub
    changes = dynamic_content()
    for token in changes:
        if token in markdown:
            print 'found %s' % token
            markdown = changes[token](token, markdown)
    markdown = h.render_markdown(markdown)

    return markdown


# placeholder
def get_featured_package_ids():
    # right now there is no metadata allowing to find only the featured items
    return [
        'lac-4447345',
        'lac-4318720',
        'lac-4318716',
        'lac-4309188',
        'lac-4309169'
    ]


def get_random_image():
    ids = get_featured_package_ids()
    return p.toolkit.get_action('package_show')(
        data_dict={
            'id': random.choice(ids)
         })


def build_canada_libraries_lang_tab():
    supported_languages = p.toolkit.aslist(
        config.get(
            'ckanext.canada_libraries.supported_languages',
            ['en', 'fr']
        )
    )

    output = ' '
    for lang in supported_languages:
        if lang == h.lang():
            continue

        current_url = urllib.unquote(request.environ['CKAN_CURRENT_URL'])
        link = h.url_for(current_url, locale=lang)
        item = h.literal('<a href="%s">%s</a>' % (link, lang.upper()))
        output = output + h.literal('<li>') + item + h.literal('</li>')

    return output


def get_datasets():
    datasets = p.toolkit.get_action('package_list')(
        data_dict={}
    )
    return datasets


def get_pages(page_type=None, private=False, order=None):
    pages = p.toolkit.get_action('ckanext_pages_list')(
        data_dict={
            'order_publish_date': order,
            'page_type': page_type,
            'private': private,
        }
    )
    return pages


def get_recent_short_blog_posts(number=10, exclude=None, length=250,
                                suffix='...'):
    """
    Returns a shortened version of the ckanext-page content
    type specified, limited by a specific size
    :param suffix: The suffix to be added if the string is truncated
    :param exclude: Entry to be excluded
    :param length: The maximum length of content allowed
    :param number: The maximum number of elements to be returned
    :return: An array of the objects (hashes), with the
    parameter truncated added, specifying if the content add
    to be truncated
    """
    blog_list = get_pages(page_type='blog', order=True)

    for i, blog_entry in enumerate(blog_list):
        if i >= number:
            break
        if exclude and blog_entry == exclude:
            continue
        # else the blog_entry is fetched and added to the list
        blog_entry['publish_date'] = datetime \
            .strptime(blog_entry['publish_date'], '%Y-%m-%dT%H:%M:%S') \
            .strftime('%B %-d, %Y')
        # the contents can be html, so it needs to be converted to pure text
        soup = BeautifulSoup(blog_entry['content'])
        # removes titles, subtitles and lists from the text
        for tag in ['h1', 'h2', 'h3', 'h4', 'h5' 'li', 'ul', 'ol']:
            for x in soup.find_all(tag):
                x.decompose()
        blog_entry['content'] = soup.get_text()

        if len(blog_entry['content']) > length:
            # truncates to the last word inside the length,
            # it shouldn't cut words
            new_content = ' '.join((
                                       blog_entry['content'])[
                                   :length + 1 - len(suffix)]
                                   .split(' ')[0:-1]
                                   )
            # since the previous operation is truncating the string to the
            # right, the result string could potentially be the origin string
            blog_entry['truncated'] = \
                new_content[length - len(suffix):] != \
                (blog_entry['content'])[length - len(suffix):]
            if blog_entry['truncated']:
                blog_entry['content'] = new_content + suffix

        else:
            blog_entry['truncated'] = False

        yield blog_entry


class LibrariesPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.IValidators)
    p.implements(p.IFacets)
    p.implements(p.IPackageController)
    p.implements(p.ITemplateHelpers)

    def update_config(self, config):
        p.toolkit.add_template_directory(config, 'templates')
        p.toolkit.add_public_directory(config, 'public')
        p.toolkit.add_resource('fanstatic', 'canada_libraries_theme')

    def get_validators(self):
        return {
            'json_output': json.loads,
            'jsonify': _dumps
        }

    def dataset_facets(self, facets_dict, package_type):
        facets_dict.clear()
        facets_dict['language'] = p.toolkit._('Language')
        if package_type == 'item':
            facets_dict['level'] = p.toolkit._('Level')
        else:
            facets_dict['organization'] = p.toolkit._('Organizations')
            facets_dict['author'] = p.toolkit._('Author')
            facets_dict['publisher'] = p.toolkit._('Publisher')
            facets_dict['format'] = p.toolkit._('Format')
            facets_dict['keywords'] = p.toolkit._('Keywords')
        return facets_dict

    def organization_facets(self, facets_dict, organization_type,
                            package_type):
        return self.dataset_facets(facets_dict, package_type)

    def before_index(self, data_dict):
        # kw = json.loads(data_dict.get('extras_keywords', '{}'))
        # data_dict['keywords'] = kw.get('en', [])
        return data_dict

    def read(self, entity):
        pass

    def create(self, entity):
        pass

    def edit(self, entity):
        pass

    def authz_add_role(self, object_role):
        pass

    def authz_remove_role(self, object_role):
        pass

    def delete(self, entity):
        pass

    def after_delete(self, context, data_dict):
        return data_dict

    def after_show(self, context, data_dict):
        return data_dict

    def update_facet_titles(self, facet_titles):
        return facet_titles

    def before_view(self, pkg_dict):
        return pkg_dict

    def after_create(self, context, data_dict):
        return data_dict

    def after_update(self, context, data_dict):
        return data_dict

    def after_search(self, search_results, search_params):
        return search_results

    def before_search(self, search_params):
        return search_params

    def get_helpers(self):
        return {
            'canada_libraries_recent_short_blog': get_recent_short_blog_posts,
            'recently_changed_packages': recently_changed_packages,
            'canada_render_html_with_subs': render_html_with_dynamic_content,
            'canada_libraries_random_image': get_random_image,
            'lang_list': build_canada_libraries_lang_tab,
            'canada_render_markdown_with_subs':
                render_markdown_with_dynamic_content,
            'datasets': get_datasets,
            'from_json': json.loads,
            'pages': get_pages,
        }
