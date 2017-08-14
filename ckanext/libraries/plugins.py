#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

import ckan.plugins as p
from ckan.lib.navl.dictization_functions import Missing


def _dumps(o):
    if isinstance(o, Missing):
        return o
    return json.dumps(o)


class LibrariesPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.IValidators)
    p.implements(p.IFacets)
    p.implements(p.IPackageController)
    p.implements(p.ITemplateHelpers)

    def update_config(self, config):
        p.toolkit.add_template_directory(config, 'templates')
        p.toolkit.add_public_directory(config, 'public')

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
