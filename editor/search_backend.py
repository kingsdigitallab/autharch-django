from haystack.backends import elasticsearch2_backend as es2_backend


class AsciifoldingElasticsearch2SearchBackend(
        es2_backend.Elasticsearch2SearchBackend):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        analyzer = {
            'ascii_analyzer': {
                'tokenizer': 'standard',
                'filter': ['standard', 'asciifolding', 'lowercase']
            },
            'ngram_analyzer': {
                'type': 'custom',
                'tokenizer': 'standard',
                'filter': ['haystack_ngram', 'asciifolding', 'lowercase']
            },
            'edgengram_analyzer': {
                'type': 'custom',
                'tokenizer': 'standard',
                'filter': ['haystack_edgengram', 'asciifolding', 'lowercase']
            },
        }
        self.DEFAULT_SETTINGS['settings']['analysis']['analyzer'] = analyzer

    def build_schema(self, fields):
        content_field_name, mapping = super().build_schema(fields)
        for field_name, field_class in fields.items():
            field_mapping = mapping[field_class.index_fieldname]
            if field_mapping['type'] == 'string' and field_class.indexed:
                if not hasattr(field_class, 'facet_for') and \
                   field_class.field_type not in ('ngram', 'edge_ngram'):
                    field_mapping['analyzer'] = 'ascii_analyzer'
            mapping.update({field_class.index_fieldname: field_mapping})
        return (content_field_name, mapping)


class AsciifoldingElasticsearch2SearchEngine(
        es2_backend.Elasticsearch2SearchEngine):

    backend = AsciifoldingElasticsearch2SearchBackend
