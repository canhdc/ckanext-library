#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

import ckan.plugins as p
from ckan.lib.navl.dictization_functions import Missing

from bs4 import BeautifulSoup
from datetime import datetime


def _dumps(o):
    if isinstance(o, Missing):
        return o
    return json.dumps(o)


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


def get_recent_short_blog_posts(number=10, exclude=None, length=250, suffix='...'):
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
        blog_entry['publish_date'] = datetime\
            .strptime(blog_entry['publish_date'], '%Y-%m-%dT%H:%M:%S')\
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
            new_content = ' '.join((blog_entry['content'])[:length + 1 - len(suffix)]
                                   .split(' ')[0:-1])
            # since the previous operation is truncating the string to the right,
            # the result string could potentially be the origin string
            blog_entry['truncated'] = new_content[length - len(suffix):] != \
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

    def get_helpers(self):
        return {
            'from_json': json.loads
        }

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
            'datasets': get_datasets,
            'pages': get_pages,
        }
