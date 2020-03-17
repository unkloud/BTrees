##############################################################################
#
# Copyright Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
Support functions to eliminate the boilerplate involved in defining
BTree modules.
"""
import sys
from zope.interface import directlyProvides


def _create_classes(
        module_name, key_datatype, value_datatype,
):
    from ._base import Bucket
    from ._base import MERGE # Won't always want this.
    from ._base import Set
    from ._base import Tree
    from ._base import TreeSet
    from ._base import _TreeIterator
    from ._base import _fix_pickle

    classes = {}

    prefix = key_datatype.prefix_code + value_datatype.prefix_code

    for base in (
            Bucket,
            Set,
            (Tree, 'BTree'),
            TreeSet,
            (_TreeIterator, 'TreeIterator'),
    ):
        if isinstance(base, tuple):
            base, base_name = base
        else:
            base_name = base.__name__

        # XXX: Consider defining these with their natural names
        # now and only aliasing them to 'Py' instead of the
        # opposite. That should make pickling easier.
        name = prefix + base_name + 'Py'
        cls = type(name, (base,), dict(
            _to_key=key_datatype,
            _to_value=value_datatype,
            MERGE=MERGE,
            MERGE_WEIGHT=value_datatype.apply_weight,
            MERGE_DEFAULT=value_datatype.multiplication_identity,
            max_leaf_size=key_datatype.bucket_size_for_value(value_datatype),
            max_internal_size=key_datatype.tree_size,
        ))
        cls.__module__ = module_name

        classes[cls.__name__] = cls
        # Importing the C extension does this for the non-py
        # classes.
        # TODO: Unify that.
        classes[base_name + 'Py'] = cls

    for cls in classes.values():
        cls._mapping_type = classes['BucketPy']
        cls._set_type = classes['SetPy']

        if 'Set' in cls.__name__:
            cls._bucket_type = classes['SetPy']
        else:
            cls._bucket_type = classes['BucketPy']

    return classes

def _create_set_operations(module_name, key_type, value_type, set_type):
    from ._base import set_operation

    from ._base import difference
    from ._base import intersection
    from ._base import multiunion
    from ._base import union
    from ._base import weightedIntersection
    from ._base import weightedUnion

    ops = {
        op.__name__ + 'Py': set_operation(op, set_type)
        for op in (
            difference, intersection,
            union,
        ) + (
            (weightedIntersection, weightedUnion,)
            if value_type.supports_value_union()
            else ()
        ) + (
            (multiunion,)
            if key_type.supports_value_union()
            else ()
        )
    }

    for key, op in ops.items():
        op.__module__ = module_name
        op.__name__ = key

    # TODO: Pickling. These things should be looked up by name.
    return ops

def _create_globals(module_name, key_datatype, value_datatype):
    classes = _create_classes(module_name, key_datatype, value_datatype)
    set_type = classes['SetPy']
    set_ops = _create_set_operations(module_name, key_datatype, value_datatype, set_type)

    classes.update(set_ops)
    return classes


def populate_module(mod_globals,
                    key_datatype, value_datatype,
                    interface, module=None):
    from ._compat import import_c_extension
    from ._base import _fix_pickle

    module_name = mod_globals['__name__']
    mod_globals.update(_create_globals(module_name, key_datatype, value_datatype))

    # XXX: Maybe derive this from the values we create.
    mod_all = (
        'Bucket', 'Set', 'BTree', 'TreeSet',
        'union', 'intersection', 'difference',
        'weightedUnion', 'weightedIntersection', 'multiunion',
    )
    prefix = key_datatype.prefix_code + value_datatype.prefix_code

    mod_all += tuple(prefix + c for c in ('Bucket', 'Set', 'BTree', 'TreeSet'))

    mod_globals['__all__'] = tuple(c for c in mod_all if c in mod_globals)

    mod_globals['using64bits'] = key_datatype.using64bits or value_datatype.using64bits

    import_c_extension(mod_globals)
    # XXX: We can probably do better than fix_pickle now;
    # we can know if we're going to be renaming classes
    # ahead of time.
    _fix_pickle(mod_globals, module_name)
    directlyProvides(module or sys.modules[module_name], interface)

def create_module(prefix):
    import types
    from . import _datatypes as datatypes
    from . import Interfaces

    mod = types.ModuleType('BTrees.' + prefix + 'BTree')

    key_type = getattr(datatypes, prefix[0])()
    val_type = getattr(datatypes, prefix[1])().as_value_type()

    iface_name = 'I' + key_type.long_name + val_type.long_name + 'BTreeModule'

    iface = getattr(Interfaces, iface_name)

    populate_module(vars(mod), key_type, val_type, iface, mod)
    return mod