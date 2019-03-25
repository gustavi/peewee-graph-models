#!/usr/bin/env python

import argparse
import importlib
import inspect

from graphviz import Source


GRAPH_TEMPLATE = '''digraph peewee_models {{
    fontname = "Helvetica"
    fontsize = 8
    splines = true
    node [
        fontname = "Helvetica"
        fontsize = 8
        shape = "plaintext"
    ]
    edge [
        fontname = "Helvetica"
        fontsize = 8
    ]
    {models}
    {relations}
}}'''

MODEL_TEMPLATE = '''{name}
[label=<
    <TABLE BGCOLOR="{color_bg}" BORDER="0" CELLBORDER="0" CELLSPACING="0">
    <TR><TD COLSPAN="2" CELLPADDING="4" ALIGN="CENTER" BGCOLOR="{color_main}">
    <FONT FACE="Helvetica Bold" COLOR="white">
    {name}
    </FONT></TD></TR>
    {fields}
    </TABLE>
>]'''


FIELD_TEMPLATE = '''
    <TR><TD ALIGN="LEFT" BORDER="0">
    <FONT COLOR="{color}" FACE="Helvetica{args}">{name}</FONT>
    </TD><TD ALIGN="LEFT">
    <FONT COLOR="{color}" FACE="Helvetica{args}">{type}</FONT>
    </TD></TR>'''


RELATION_TEMPLATE = '{model} -> {target_model} [label="{field}"] ' \
                    '[arrowhead=empty, arrowtail=none, dir=both];'


def export_models(mod, main_color, bg_color, export_file, export_format, view,
                  peewee_module):
    """
    Export peewee models to JPG, PDF, etc.

    :param str mod: module, named as imported
    :param str main_color: main color (in hex format, starting with #)
    :param str bg_color: background color (in hex format, starting with #)
    :param str export_file: name of the file to export, without extension
    :param str export_format: extension for the file to export
    :param bool view: display file after generation
    :param str peewee_module: Peewee module to load
    :return: nothing
    """
    # Import peewee
    peewee = importlib.import_module(peewee_module)

    def is_peewee_model(pyobj):
        """
        Check if the object is a peewee model.

        :param pyobj: a Python object
        :return: True if the object is a peewee model
        :rtype: bool
        """
        return inspect.isclass(pyobj) \
            and issubclass(pyobj, peewee.Model) \
            and not pyobj == peewee.Model

    # Import module to parse
    mod_imported = importlib.import_module(mod)
    models = inspect.getmembers(mod_imported, predicate=is_peewee_model)

    models_dot = ''
    relations_dot = ''

    for name, model in models:
        fields_dot = ''

        for field, obj in model._meta.fields.items():

            # Generate field dot data
            field_dot_args = ''

            if obj.primary_key or isinstance(obj, peewee.ForeignKeyField):
                field_dot_args += ' Bold'

            fields_dot += FIELD_TEMPLATE.format(
                name=field,
                type=type(obj).__name__,
                args=field_dot_args,
                color=main_color
            )

            # Generate relations
            if isinstance(obj, peewee.ForeignKeyField):
                relations_dot += RELATION_TEMPLATE.format(
                    model=name,
                    target_model=obj.rel_model.__name__,
                    field=field
                )

        models_dot += MODEL_TEMPLATE.format(
            name=name,
            fields=fields_dot,
            color_bg=bg_color,
            color_main=main_color
        )

    graph_dot = GRAPH_TEMPLATE.format(
        models=models_dot,
        relations=relations_dot
    )

    # Render graph
    src = Source(graph_dot)
    src.render(
        export_file,
        format=export_format,
        cleanup=True,
        view=view
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Peewee model visualization')
    parser.add_argument(
        'module',
        action='store',
        help='Module to parse'
    )
    parser.add_argument(
        '--main-color',
        action='store',
        default='#0b7285',
        help='Main color used for models background and fields name'
    )
    parser.add_argument(
        '--bg-color',
        action='store',
        default='#e3fafc',
        help='Background of models'
    )
    parser.add_argument(
        '--export-file',
        action='store',
        default='peewee_models',
        help='Name of the file for export (without extension)'
    )
    parser.add_argument(
        '--export-format',
        action='store',
        default='png',
        help='Format to export (PDF, PNG, etc.)'
    )
    parser.add_argument(
        '--view',
        action='store_true',
        help='Display file after generation'
    )
    parser.add_argument(
        '--peewee',
        action='store',
        help='Peewee module to load'
    )

    args = parser.parse_args()
    export_models(
        mod=args.module,
        main_color=args.main_color,
        bg_color=args.bg_color,
        export_file=args.export_file,
        export_format=args.export_format,
        view=args.view,
        peewee_module=args.peewee
    )

