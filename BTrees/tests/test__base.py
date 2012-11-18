##############################################################################
#
# Copyright 2012 Zope Foundation and Contributors.
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
import unittest


def _assertRaises(self, e_type, checked, *args, **kw):
    try:
        checked(*args, **kw)
    except e_type as e:
        return e
    self.fail("Didn't raise: %s" % e_type.__name__)


class Test_Base(unittest.TestCase):

    def _getTargetClass(self):
        from .._base import _Base
        return _Base

    def _makeOne(self, items=None):
        class _Test(self._getTargetClass()):
            def clear(self):
                self._data = {}
            def update(self, d):
                self._data.update(d)
        return _Test(items)

    def test_ctor_wo_items(self):
        base = self._makeOne()
        self.assertEqual(base._data, {})

    def test_ctor_w_items(self):
        base = self._makeOne({'a': 'b'})
        self.assertEqual(base._data, {'a': 'b'})


class Test_BucketBase(unittest.TestCase):

    def _getTargetClass(self):
        from .._base import _BucketBase
        return _BucketBase

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_ctor_defaults(self):
        bucket = self._makeOne()
        self.assertEqual(bucket._keys, [])
        self.assertEqual(bucket._next, None)
        self.assertEqual(len(bucket), 0)
        self.assertEqual(bucket.size, 0)

    def test__deleteNextBucket_none(self):
        bucket = self._makeOne()
        bucket._deleteNextBucket() # no raise
        self.assertTrue(bucket._next is None)

    def test__deleteNextBucket_one(self):
        bucket1 = self._makeOne()
        bucket2 = bucket1._next = self._makeOne()
        bucket1._deleteNextBucket() # no raise
        self.assertTrue(bucket1._next is None)

    def test__deleteNextBucket_two(self):
        bucket1 = self._makeOne()
        bucket2 = bucket1._next = self._makeOne()
        bucket3 = bucket2._next = self._makeOne()
        bucket1._deleteNextBucket() # no raise
        self.assertTrue(bucket1._next is bucket3)

    def test__search_empty(self):
        bucket = self._makeOne()
        self.assertEqual(bucket._search('nonesuch'), -1)

    def test__search_nonempty_miss(self):
        bucket = self._makeOne()
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket._search('candy'), -3)

    def test__search_nonempty_hit(self):
        bucket = self._makeOne()
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket._search('charlie'), 2)

    def test_minKey_empty(self):
        bucket = self._makeOne()
        self.assertRaises(IndexError, bucket.minKey)

    def test_minKey_no_bound(self):
        bucket = self._makeOne()
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket.minKey(), 'alpha')

    def test_minKey_w_bound_hit(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket.minKey('bravo'), 'bravo')

    def test_minKey_w_bound_miss(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket.minKey('candy'), 'charlie')

    def test_minKey_w_bound_fail(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertRaises(ValueError, bucket.minKey, 'foxtrot')

    def test_maxKey_empty(self):
        bucket = self._makeOne()
        self.assertRaises(IndexError, bucket.maxKey)

    def test_maxKey_no_bound(self):
        bucket = self._makeOne()
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket.maxKey(), 'echo')

    def test_maxKey_w_bound_hit(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket.maxKey('bravo'), 'bravo')

    def test_maxKey_w_bound_miss(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket.maxKey('candy'), 'bravo')

    def test_maxKey_w_bound_fail(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertRaises(ValueError, bucket.maxKey, 'abacus')

    def test__range_defaults_empty(self):
        bucket = self._makeOne()
        self.assertEqual(bucket._range(), (0, 0))

    def test__range_defaults_filled(self):
        bucket = self._makeOne()
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket._range(), (0, 5))

    def test__range_defaults_exclude_min(self):
        bucket = self._makeOne()
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket._range(excludemin=True), (1, 5))

    def test__range_defaults_exclude_max(self):
        bucket = self._makeOne()
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket._range(excludemax=True), (0, 4))

    def test__range_w_min_hit(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket._range(min='bravo'), (1, 5))

    def test__range_w_min_miss(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket._range(min='candy'), (2, 5))

    def test__range_w_min_hit_w_exclude_min(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket._range(min='bravo', excludemin=True), (2, 5))

    def test__range_w_min_miss_w_exclude_min(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        # 'excludemin' doesn't fire on miss
        self.assertEqual(bucket._range(min='candy', excludemin=True), (2, 5))

    def test__range_w_max_hit(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket._range(max='delta'), (0, 4))

    def test__range_w_max_miss(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket._range(max='dandy'), (0, 3))

    def test__range_w_max_hit_w_exclude_max(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket._range(max='delta', excludemax=True), (0, 3))

    def test__range_w_max_miss_w_exclude_max(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        # 'excludemax' doesn't fire on miss
        self.assertEqual(bucket._range(max='dandy', excludemax=True), (0, 3))

    def test_keys_defaults_empty(self):
        bucket = self._makeOne()
        self.assertEqual(bucket.keys(), [])

    def test_keys_defaults_filled(self):
        bucket = self._makeOne()
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket.keys(), KEYS[0: 5])

    def test_keys_defaults_exclude_min(self):
        bucket = self._makeOne()
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket.keys(excludemin=True), KEYS[1: 5])

    def test_keys_defaults_exclude_max(self):
        bucket = self._makeOne()
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket.keys(excludemax=True), KEYS[0: 4])

    def test_keys_w_min_hit(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket.keys(min='bravo'), KEYS[1: 5])

    def test_keys_w_min_miss(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket.keys(min='candy'), KEYS[2: 5])

    def test_keys_w_min_hit_w_exclude_min(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket.keys(min='bravo', excludemin=True), KEYS[2: 5])

    def test_keys_w_min_miss_w_exclude_min(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        # 'excludemin' doesn't fire on miss
        self.assertEqual(bucket.keys(min='candy', excludemin=True), KEYS[2: 5])

    def test_keys_w_max_hit(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket.keys(max='delta'), KEYS[0: 4])

    def test_keys_w_max_miss(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket.keys(max='dandy'), KEYS[0: 3])

    def test_keys_w_max_hit_w_exclude_max(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(bucket.keys(max='delta', excludemax=True), KEYS[0: 3])

    def test_keys_w_max_miss_w_exclude_max(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        # 'excludemax' doesn't fire on miss
        self.assertEqual(bucket.keys(max='dandy', excludemax=True), KEYS[0: 3])

    def test_iterkeys_defaults_empty(self):
        bucket = self._makeOne()
        self.assertEqual(list(bucket.iterkeys()), [])

    def test_iterkeys_defaults_filled(self):
        bucket = self._makeOne()
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(list(bucket.iterkeys()), KEYS[0: 5])

    def test_iterkeys_defaults_exclude_min(self):
        bucket = self._makeOne()
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(list(bucket.iterkeys(excludemin=True)), KEYS[1: 5])

    def test_iterkeys_defaults_exclude_max(self):
        bucket = self._makeOne()
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(list(bucket.iterkeys(excludemax=True)), KEYS[0: 4])

    def test_iterkeys_w_min_hit(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(list(bucket.iterkeys(min='bravo')), KEYS[1: 5])

    def test_iterkeys_w_min_miss(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(list(bucket.iterkeys(min='candy')), KEYS[2: 5])

    def test_iterkeys_w_min_hit_w_exclude_min(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(list(bucket.iterkeys(min='bravo', excludemin=True)),
                         KEYS[2: 5])

    def test_iterkeys_w_min_miss_w_exclude_min(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        # 'excludemin' doesn't fire on miss
        self.assertEqual(list(bucket.iterkeys(min='candy', excludemin=True)),
                         KEYS[2: 5])

    def test_iterkeys_w_max_hit(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(list(bucket.iterkeys(max='delta')), KEYS[0: 4])

    def test_iterkeys_w_max_miss(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(list(bucket.iterkeys(max='dandy')), KEYS[0: 3])

    def test_iterkeys_w_max_hit_w_exclude_max(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual(list(bucket.keys(max='delta', excludemax=True)),
                         KEYS[0: 3])

    def test_iterkeys_w_max_miss_w_exclude_max(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        # 'excludemax' doesn't fire on miss
        self.assertEqual(list(bucket.iterkeys(max='dandy', excludemax=True)),
                         KEYS[0: 3])

    def test___iter___empty(self):
        bucket = self._makeOne()
        self.assertEqual([x for x in bucket], [])

    def test___iter___filled(self):
        bucket = self._makeOne()
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertEqual([x for x in bucket], KEYS[0: 5])

    def test___contains___empty(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        self.assertFalse('nonesuch' in bucket)

    def test___contains___filled_miss(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        self.assertFalse('nonesuch' in bucket)

    def test___contains___filled_hit(self):
        bucket = self._makeOne()
        bucket._to_key = lambda x: x
        KEYS = bucket._keys = ['alpha', 'bravo', 'charlie', 'delta', 'echo']
        for key in KEYS:
            self.assertTrue(key in bucket)


class Test_SetIteration(unittest.TestCase):

    assertRaises = _assertRaises

    def _getTargetClass(self):
        from .._base import _SetIteration
        return _SetIteration

    def _makeOne(self, to_iterate, useValues=False, default=None):
        return self._getTargetClass()(to_iterate, useValues, default)

    def test_ctor_w_None(self):
        si = self._makeOne(None)
        self.assertEqual(si.useValues, False)
        self.failIf('key' in si.__dict__)
        self.assertEqual(si.value, None)
        self.assertEqual(si.active, False)
        self.assertEqual(si.position, -1)

    def test_ctor_w_non_empty_list(self):
        si = self._makeOne(['a', 'b', 'c'])
        self.assertEqual(si.useValues, False)
        self.assertEqual(si.key, 'a')
        self.assertEqual(si.value, None)
        self.assertEqual(si.active, True)
        self.assertEqual(si.position, 1)


class BucketTests(unittest.TestCase):

    assertRaises = _assertRaises

    def _getTargetClass(self):
        from .._base import Bucket
        return Bucket

    def _makeOne(self):
        class _Bucket(self._getTargetClass()):
            def _to_key(self, x):
                return x
            def _to_value(self, x):
                return x
        return _Bucket()

    def test_ctor_defaults(self):
        bucket = self._makeOne()
        self.assertEqual(bucket._keys, [])
        self.assertEqual(bucket._values, [])

    def test_setdefault_miss(self):
        bucket = self._makeOne()
        self.assertEqual(bucket.setdefault('a', 'b'), 'b')
        self.assertEqual(bucket._keys, ['a'])
        self.assertEqual(bucket._values, ['b'])

    def test_setdefault_hit(self):
        bucket = self._makeOne()
        bucket._keys.append('a')
        bucket._values.append('b')
        self.assertEqual(bucket.setdefault('a', 'b'), 'b')
        self.assertEqual(bucket._keys, ['a'])
        self.assertEqual(bucket._values, ['b'])

    def test_pop_miss_no_default(self):
        bucket = self._makeOne()
        self.assertRaises(KeyError, bucket.pop, 'nonesuch')

    def test_pop_miss_w_default(self):
        bucket = self._makeOne()
        self.assertEqual(bucket.pop('nonesuch', 'b'), 'b')

    def test_pop_hit(self):
        bucket = self._makeOne()
        bucket._keys.append('a')
        bucket._values.append('b')
        self.assertEqual(bucket.pop('a'), 'b')
        self.assertEqual(bucket._keys, [])
        self.assertEqual(bucket._values, [])

    def test_update_value_w_iteritems(self):
        bucket = self._makeOne()
        bucket.update({'a': 'b'})
        self.assertEqual(bucket._keys, ['a'])
        self.assertEqual(bucket._values, ['b'])

    def test_update_value_w_items(self):
        bucket = self._makeOne()
        class Foo(object):
            def items(self):
                return [('a', 'b')]
        bucket.update(Foo())
        self.assertEqual(bucket._keys, ['a'])
        self.assertEqual(bucket._values, ['b'])

    def test_update_value_w_invalid_items(self):
        bucket = self._makeOne()
        class Foo(object):
            def items(self):
                return ('a', 'b', 'c')
        self.assertRaises(TypeError, bucket.update, Foo())

    def test_update_sequence(self):
        bucket = self._makeOne()
        bucket.update([('a', 'b')])
        self.assertEqual(bucket._keys, ['a'])
        self.assertEqual(bucket._values, ['b'])

    def test___setitem___incomparable(self):
        bucket = self._makeOne()
        def _should_error():
            bucket[object()] = 'b'
        self.assertRaises(TypeError, _should_error)

    def test___setitem___comparable(self):
        bucket = self._makeOne()
        bucket['a'] = 'b'
        self.assertEqual(bucket['a'], 'b')

    def test___setitem___replace(self):
        bucket = self._makeOne()
        bucket['a'] = 'b'
        bucket['a'] = 'c'
        self.assertEqual(bucket['a'], 'c')

    def test___delitem___miss(self):
        bucket = self._makeOne()
        def _should_error():
            del bucket['nonesuch']
        self.assertRaises(KeyError, _should_error)

    def test___delitem___hit(self):
        bucket = self._makeOne()
        bucket._keys.append('a')
        bucket._values.append('b')
        del bucket['a']
        self.assertEqual(bucket._keys, [])
        self.assertEqual(bucket._values, [])

    def test_clear_filled(self):
        bucket = self._makeOne()
        bucket['a'] = 'b'
        bucket['c'] = 'd'
        bucket.clear()
        self.assertEqual(len(bucket._keys), 0)
        self.assertEqual(len(bucket._values), 0)

    def test_clear_empty(self):
        bucket = self._makeOne()
        bucket.clear()
        self.assertEqual(len(bucket._keys), 0)
        self.assertEqual(len(bucket._values), 0)

    def test_get_miss_no_default(self):
        bucket = self._makeOne()
        self.assertEqual(bucket.get('nonesuch'), None)

    def test_get_miss_w_default(self):
        bucket = self._makeOne()
        self.assertEqual(bucket.get('nonesuch', 'b'), 'b')

    def test_get_hit(self):
        bucket = self._makeOne()
        bucket._keys.append('a')
        bucket._values.append('b')
        self.assertEqual(bucket.get('a'), 'b')

    def test___getitem___miss(self):
        bucket = self._makeOne()
        def _should_error():
            return bucket['nonesuch']
        self.assertRaises(KeyError, _should_error)

    def test___getitem___hit(self):
        bucket = self._makeOne()
        bucket._keys.append('a')
        bucket._values.append('b')
        self.assertEqual(bucket['a'], 'b')

    def test__split_empty(self):
        bucket = self._makeOne()
        next_b = bucket._next = self._makeOne()
        new_b = bucket._split()
        self.assertEqual(len(bucket._keys), 0)
        self.assertEqual(len(bucket._values), 0)
        self.assertEqual(len(new_b._keys), 0)
        self.assertEqual(len(new_b._values), 0)
        self.assertTrue(bucket._next is new_b)
        self.assertTrue(new_b._next is next_b)

    def test__split_filled_default_index(self):
        bucket = self._makeOne()
        next_b = bucket._next = self._makeOne()
        for i, c in enumerate('abcdef'):
            bucket[c] = i
        new_b = bucket._split()
        self.assertEqual(list(bucket._keys), ['a', 'b', 'c'])
        self.assertEqual(list(bucket._values), [0, 1, 2])
        self.assertEqual(list(new_b._keys), ['d', 'e', 'f'])
        self.assertEqual(list(new_b._values), [3, 4, 5])
        self.assertTrue(bucket._next is new_b)
        self.assertTrue(new_b._next is next_b)

    def test_keys_empty_no_args(self):
        bucket = self._makeOne()
        self.assertEqual(bucket.keys(), [])

    def test_keys_filled_no_args(self):
        bucket = self._makeOne()
        for i, c in enumerate('abcdef'):
            bucket[c] = i
        self.assertEqual(bucket.keys(),
                         ['a', 'b', 'c', 'd', 'e', 'f'])

    def test_keys_filled_w_args(self):
        bucket = self._makeOne()
        for i, c in enumerate('abcdef'):
            bucket[c] = i
        self.assertEqual(bucket.keys(min='b', excludemin=True,
                                     max='f', excludemax=True), ['c', 'd', 'e'])

    def test_iterkeys_empty_no_args(self):
        bucket = self._makeOne()
        self.assertEqual(list(bucket.iterkeys()), [])

    def test_iterkeys_filled_no_args(self):
        bucket = self._makeOne()
        for i, c in enumerate('abcdef'):
            bucket[c] = i
        self.assertEqual(list(bucket.iterkeys()),
                         ['a', 'b', 'c', 'd', 'e', 'f'])

    def test_iterkeys_filled_w_args(self):
        bucket = self._makeOne()
        for i, c in enumerate('abcdef'):
            bucket[c] = i
        self.assertEqual(list(bucket.iterkeys(
                                   min='b', excludemin=True,
                                   max='f', excludemax=True)), ['c', 'd', 'e'])

    def test_values_empty_no_args(self):
        bucket = self._makeOne()
        self.assertEqual(bucket.values(), [])

    def test_values_filled_no_args(self):
        bucket = self._makeOne()
        for i, c in enumerate('abcdef'):
            bucket[c] = i
        self.assertEqual(bucket.values(), range(6))

    def test_values_filled_w_args(self):
        bucket = self._makeOne()
        for i, c in enumerate('abcdef'):
            bucket[c] = i
        self.assertEqual(bucket.values(min='b', excludemin=True,
                                       max='f', excludemax=True), [2, 3, 4])

    def test_itervalues_empty_no_args(self):
        bucket = self._makeOne()
        self.assertEqual(list(bucket.itervalues()), [])

    def test_itervalues_filled_no_args(self):
        bucket = self._makeOne()
        for i, c in enumerate('abcdef'):
            bucket[c] = i
        self.assertEqual(list(bucket.itervalues()), range(6))

    def test_itervalues_filled_w_args(self):
        bucket = self._makeOne()
        for i, c in enumerate('abcdef'):
            bucket[c] = i
        self.assertEqual(list(bucket.itervalues(
                                       min='b', excludemin=True,
                                       max='f', excludemax=True)), [2, 3, 4])

    def test_items_empty_no_args(self):
        bucket = self._makeOne()
        self.assertEqual(bucket.items(), [])

    def test_items_filled_no_args(self):
        bucket = self._makeOne()
        EXPECTED = []
        for i, c in enumerate('abcdef'):
            bucket[c] = i
            EXPECTED.append((c, i))
        self.assertEqual(bucket.items(), EXPECTED)

    def test_items_filled_w_args(self):
        bucket = self._makeOne()
        EXPECTED = []
        for i, c in enumerate('abcdef'):
            bucket[c] = i
            EXPECTED.append((c, i))
        self.assertEqual(bucket.items(min='b', excludemin=True,
                                       max='f', excludemax=True),
                        EXPECTED[2:5])

    def test_iteritems_empty_no_args(self):
        bucket = self._makeOne()
        self.assertEqual(list(bucket.iteritems()), [])

    def test_iteritems_filled_no_args(self):
        bucket = self._makeOne()
        EXPECTED = []
        for i, c in enumerate('abcdef'):
            bucket[c] = i
            EXPECTED.append((c, i))
        self.assertEqual(list(bucket.iteritems()), EXPECTED)

    def test_iteritems_filled_w_args(self):
        bucket = self._makeOne()
        EXPECTED = []
        for i, c in enumerate('abcdef'):
            bucket[c] = i
            EXPECTED.append((c, i))
        self.assertEqual(list(bucket.iteritems(min='b', excludemin=True,
                                               max='f', excludemax=True)),
                        EXPECTED[2:5])

    def test___getstate___empty_no_next(self):
        bucket = self._makeOne()
        self.assertEqual(bucket.__getstate__(), ((),))

    def test___getstate___empty_w_next(self):
        bucket = self._makeOne()
        bucket._next = next_b = self._makeOne()
        self.assertEqual(bucket.__getstate__(), ((), next_b))

    def test___getstate___non_empty_no_next(self):
        bucket = self._makeOne()
        EXPECTED = ()
        for i, c in enumerate('abcdef'):
            bucket[c] = i
            EXPECTED += (c, i)
        self.assertEqual(bucket.__getstate__(), (EXPECTED,))

    def test___getstate___non_empty_w_next(self):
        bucket = self._makeOne()
        bucket._next = next_b = self._makeOne()
        EXPECTED = ()
        for i, c in enumerate('abcdef'):
            bucket[c] = i
            EXPECTED += (c, i)
        self.assertEqual(bucket.__getstate__(), (EXPECTED, next_b))

    def test___setstate___w_non_tuple(self):
        bucket = self._makeOne()
        self.assertRaises(TypeError, bucket.__setstate__, (None,))

    def test___setstate___w_empty_no_next(self):
        bucket = self._makeOne()
        bucket._next = next_b = self._makeOne()
        for i, c in enumerate('abcdef'):
            bucket[c] = i
        bucket.__setstate__(((),))
        self.assertEqual(len(bucket.keys()), 0)
        self.assertTrue(bucket._next is None)

    def test___setstate___w_non_empty_w_next(self):
        bucket = self._makeOne()
        next_b = self._makeOne()
        ITEMS = ()
        EXPECTED = []
        for i, c in enumerate('abcdef'):
            ITEMS += (c, i)
            EXPECTED.append((c, i))
        bucket.__setstate__((ITEMS, next_b))
        self.assertEqual(bucket.items(), EXPECTED)
        self.assertTrue(bucket._next is next_b)

    def test__p_resolveConflict_x_on_com_next(self):
        from ..Interfaces import BTreesConflictError
        bucket = self._makeOne()
        N_NEW = object()
        s_old = ((), None)
        s_com = ((), N_NEW)
        s_new = ((), None)
        e = self.assertRaises(BTreesConflictError,
                              bucket._p_resolveConflict, s_old, s_com, s_new)
        self.assertEqual(e.reason, 0)

    def test__p_resolveConflict_x_on_new_next(self):
        from ..Interfaces import BTreesConflictError
        bucket = self._makeOne()
        N_NEW = object()
        s_old = ((), None)
        s_com = ((), None)
        s_new = ((), N_NEW)
        e = self.assertRaises(BTreesConflictError,
                              bucket._p_resolveConflict, s_old, s_com, s_new)
        self.assertEqual(e.reason, 0)

    def test__p_resolveConflict_x_on_com_empty(self):
        from ..Interfaces import BTreesConflictError
        bucket = self._makeOne()
        s_old = (('a', 'b', 'c', 'd'), None)
        s_com = ((), None)
        s_new = (('a', 'b'), None)
        e = self.assertRaises(BTreesConflictError,
                              bucket._p_resolveConflict, s_old, s_com, s_new)
        self.assertEqual(e.reason, 12)

    def test__p_resolveConflict_x_on_new_empty(self):
        from ..Interfaces import BTreesConflictError
        bucket = self._makeOne()
        s_old = (('a', 0, 'b', 1), None)
        s_com = (('a', 0), None)
        s_new = ((), None)
        e = self.assertRaises(BTreesConflictError,
                              bucket._p_resolveConflict, s_old, s_com, s_new)
        self.assertEqual(e.reason, 12)

    def test__p_resolveConflict_x_both_update_same_key(self):
        from ..Interfaces import BTreesConflictError
        bucket = self._makeOne()
        s_old = (('a', 0), None)
        s_com = (('a', 5, 'b', 1, 'c', 2), None)
        s_new = (('a', 6, 'd', 3), None)
        e = self.assertRaises(BTreesConflictError,
                              bucket._p_resolveConflict, s_old, s_com, s_new)
        self.assertEqual(e.reason, 1)

    def test__p_resolveConflict_x_on_del_first_com_x(self):
        from ..Interfaces import BTreesConflictError
        bucket = self._makeOne()
        s_old = (('a', 0, 'b', 1, 'c', 2), None)
        s_com = (('b', 1), None)
        s_new = (('a', 0, 'b', 1), None)
        e = self.assertRaises(BTreesConflictError,
                              bucket._p_resolveConflict, s_old, s_com, s_new)
        self.assertEqual(e.reason, 13)

    def test__p_resolveConflict_x_on_del_first_new_x(self):
        from ..Interfaces import BTreesConflictError
        bucket = self._makeOne()
        s_old = (('a', 0, 'b', 1, 'c', 2), None)
        s_com = (('a', 0, 'b', 1), None)
        s_new = (('b', 1), None)
        e = self.assertRaises(BTreesConflictError,
                              bucket._p_resolveConflict, s_old, s_com, s_new)
        self.assertEqual(e.reason, 13)

    def test__p_resolveConflict_x_on_del_first_new(self):
        from ..Interfaces import BTreesConflictError
        bucket = self._makeOne()
        s_old = (('a', 0, 'b', 1), None)
        s_com = (('a', 1, 'b', 2, 'c', 3), None)
        s_new = (('b', 4), None)
        e = self.assertRaises(BTreesConflictError,
                              bucket._p_resolveConflict, s_old, s_com, s_new)
        self.assertEqual(e.reason, 2)

    def test__p_resolveConflict_x_on_del_first_com(self):
        from ..Interfaces import BTreesConflictError
        bucket = self._makeOne()
        s_old = (('a', 0, 'b', 1), None)
        s_com = (('b', 4), None)
        s_new = (('a', 1, 'b', 2, 'c', 3), None)
        e = self.assertRaises(BTreesConflictError,
                              bucket._p_resolveConflict, s_old, s_com, s_new)
        self.assertEqual(e.reason, 3)

    def test__p_resolveConflict_x_on_ins_same_after_del(self):
        from ..Interfaces import BTreesConflictError
        bucket = self._makeOne()
        s_old = (('a', 0, 'b', 1), None)
        s_com = (('a', 0, 'c', 2), None)
        s_new = (('a', 0, 'c', 2, 'd', 3), None)
        e = self.assertRaises(BTreesConflictError,
                              bucket._p_resolveConflict, s_old, s_com, s_new)
        self.assertEqual(e.reason, 4)

    def test__p_resolveConflict_x_on_del_same(self):
        from ..Interfaces import BTreesConflictError
        bucket = self._makeOne()
        s_old = (('a', 0, 'b', 1, 'c', 2), None)
        s_com = (('a', 0, 'c', 2), None)
        s_new = (('a', 0, 'd', 3, 'e', 4), None)
        e = self.assertRaises(BTreesConflictError,
                              bucket._p_resolveConflict, s_old, s_com, s_new)
        self.assertEqual(e.reason, 5)

    def test__p_resolveConflict_x_on_append_same(self):
        from ..Interfaces import BTreesConflictError
        bucket = self._makeOne()
        s_old = (('a', 0, ), None)
        s_com = (('a', 0, 'b', 1), None)
        s_new = (('a', 0, 'b', 1, 'c', 2), None)
        e = self.assertRaises(BTreesConflictError,
                              bucket._p_resolveConflict, s_old, s_com, s_new)
        self.assertEqual(e.reason, 6)

    def test__p_resolveConflict_x_on_new_deletes_all_com_adds(self):
        from ..Interfaces import BTreesConflictError
        bucket = self._makeOne()
        s_old = (('a', 0, 'b', 1, 'c', 2), None)
        s_com = (('a', 0, 'd', 3, 'e', 4, 'f', 5), None)
        s_new = (('a', 0, ), None)
        e = self.assertRaises(BTreesConflictError,
                              bucket._p_resolveConflict, s_old, s_com, s_new)
        self.assertEqual(e.reason, 7)

    def test__p_resolveConflict_x_on_com_deletes_all_new_adds(self):
        from ..Interfaces import BTreesConflictError
        bucket = self._makeOne()
        s_old = (('a', 0, 'b', 1, 'c', 2), None)
        s_com = (('a', 0, ), None)
        s_new = (('a', 0, 'd', 3, 'e', 4, 'f', 5), None)
        e = self.assertRaises(BTreesConflictError,
                              bucket._p_resolveConflict, s_old, s_com, s_new)
        self.assertEqual(e.reason, 8)

    def test__p_resolveConflict_x_on_com_deletes_all_new_deletes(self):
        from ..Interfaces import BTreesConflictError
        bucket = self._makeOne()
        s_old = (('a', 0, 'b', 1, 'c', 2), None)
        s_com = (('a', 0, ), None)
        s_new = (('a', 0, 'b', 1), None)
        e = self.assertRaises(BTreesConflictError,
                              bucket._p_resolveConflict, s_old, s_com, s_new)
        self.assertEqual(e.reason, 9)

    def test__p_resolveConflict_ok_both_add_new_max(self):
        bucket = self._makeOne()
        s_old = (('a', 0), None)
        s_com = (('a', 0, 'b', 1), None)
        s_new = (('a', 0, 'c', 2), None)
        result = bucket._p_resolveConflict(s_old, s_com, s_new)
        self.assertEqual(result, (('a', 0, 'b', 1, 'c', 2),))

    def test__p_resolveConflict_ok_com_updates(self):
        bucket = self._makeOne()
        s_old = (('a', 0), None)
        s_com = (('a', 5), None)
        s_new = (('a', 0, 'd', 3), None)
        result = bucket._p_resolveConflict(s_old, s_com, s_new)
        self.assertEqual(result, (('a', 5, 'd', 3),))

    def test__p_resolveConflict_ok_new_updates(self):
        bucket = self._makeOne()
        s_old = (('a', 0), None)
        s_com = (('a', 0, 'd', 3), None)
        s_new = (('a', 5), None)
        result = bucket._p_resolveConflict(s_old, s_com, s_new)
        self.assertEqual(result, (('a', 5, 'd', 3),))

    def test__p_resolveConflict_ok_com_inserts_new_adds(self):
        bucket = self._makeOne()
        s_old = (('a', 0, 'c', 2), None)
        s_com = (('a', 0, 'b', 1, 'c', 2), None)
        s_new = (('a', 0, 'c', 2, 'd', 3), None)
        result = bucket._p_resolveConflict(s_old, s_com, s_new)
        self.assertEqual(result, (('a', 0, 'b', 1, 'c', 2, 'd', 3),))

    def test__p_resolveConflict_ok_com_adds_new_inserts(self):
        bucket = self._makeOne()
        s_old = (('a', 0, 'c', 2), None)
        s_com = (('a', 0, 'c', 2, 'd', 3), None)
        s_new = (('a', 0, 'b', 1, 'c', 2), None)
        result = bucket._p_resolveConflict(s_old, s_com, s_new)
        self.assertEqual(result, (('a', 0, 'b', 1, 'c', 2, 'd', 3),))

    def test__p_resolveConflict_ok_com_adds_new_deletes(self):
        bucket = self._makeOne()
        s_old = (('a', 0, 'b', 1, 'c', 2), None)
        s_com = (('a', 0, 'b', 1, 'c', 2, 'd', 3), None)
        s_new = (('a', 0, 'e', 4), None)
        result = bucket._p_resolveConflict(s_old, s_com, s_new)
        self.assertEqual(result, (('a', 0, 'd', 3, 'e', 4),))

    def test__p_resolveConflict_ok_com_deletes_new_adds(self):
        bucket = self._makeOne()
        s_old = (('a', 0, 'b', 1, 'c', 2), None)
        s_com = (('a', 0, 'e', 4), None)
        s_new = (('a', 0, 'b', 1, 'c', 2, 'd', 3), None)
        result = bucket._p_resolveConflict(s_old, s_com, s_new)
        self.assertEqual(result, (('a', 0, 'd', 3, 'e', 4),))

    def test__p_resolveConflict_ok_both_insert_new_lt_com(self):
        bucket = self._makeOne()
        s_old = (('a', 0, 'd', 3), None)
        s_com = (('a', 0, 'c', 2, 'd', 3), None)
        s_new = (('a', 0, 'b', 1, 'd', 3), None)
        result = bucket._p_resolveConflict(s_old, s_com, s_new)
        self.assertEqual(result, (('a', 0, 'b', 1, 'c', 2, 'd', 3),))

    def test__p_resolveConflict_ok_both_insert_new_gt_com(self):
        bucket = self._makeOne()
        s_old = (('a', 0, 'd', 3), None)
        s_com = (('a', 0, 'b', 1, 'd', 3), None)
        s_new = (('a', 0, 'c', 2, 'd', 3), None)
        result = bucket._p_resolveConflict(s_old, s_com, s_new)
        self.assertEqual(result, (('a', 0, 'b', 1, 'c', 2, 'd', 3),))

    def test__p_resolveConflict_ok_new_insert_then_com_append(self):
        bucket = self._makeOne()
        s_old = (('a', 0, 'd', 3), None)
        s_com = (('a', 0, 'e', 4), None)
        s_new = (('a', 0, 'b', 1, 'd', 3), None)
        result = bucket._p_resolveConflict(s_old, s_com, s_new)
        self.assertEqual(result, (('a', 0, 'b', 1, 'e', 4),))

    def test__p_resolveConflict_ok_com_insert_then_new_append(self):
        bucket = self._makeOne()
        s_old = (('a', 0, 'd', 3), None)
        s_com = (('a', 0, 'b', 1, 'd', 3), None)
        s_new = (('a', 0, 'e', 4), None)
        result = bucket._p_resolveConflict(s_old, s_com, s_new)
        self.assertEqual(result, (('a', 0, 'b', 1, 'e', 4),))

    def test__p_resolveConflict_ok_new_deletes_tail_com_inserts(self):
        bucket = self._makeOne()
        s_old = (('a', 0, 'b', 1, 'd', 3), None)
        s_com = (('a', 0, 'b', 1, 'c', 2, 'd', 3), None)
        s_new = (('a', 0), None)
        result = bucket._p_resolveConflict(s_old, s_com, s_new)
        self.assertEqual(result, (('a', 0, 'c', 2),))

    def test__p_resolveConflict_ok_com_deletes_tail_new_inserts(self):
        bucket = self._makeOne()
        s_old = (('a', 0, 'b', 1, 'd', 3), None)
        s_com = (('a', 0), None)
        s_new = (('a', 0, 'b', 1, 'c', 2, 'd', 3), None)
        result = bucket._p_resolveConflict(s_old, s_com, s_new)
        self.assertEqual(result, (('a', 0, 'c', 2),))


class SetTests(unittest.TestCase):

    assertRaises = _assertRaises

    def _getTargetClass(self):
        from .._base import Set
        return Set

    def _makeOneXXX(self):
        class _TestSet(self._getTargetClass()):
            def __setstate__(self, state):
                self._keys, self._next = state
            def clear(self):
                self._keys, self._next = [], None
            def __len__(self):
                return len(self._keys)
            def __iter__(self):
                return iter(self._keys)
        return _TestSet()

    def _makeOne(self):
        class _Set(self._getTargetClass()):
            def _to_key(self, x):
                return x
        return _Set()

    def test_add_not_extant(self):
        _set = self._makeOne()
        _set.add('not_extant')
        self.assertEqual(list(_set), ['not_extant'])

    def test_add_extant(self):
        _set = self._makeOne()
        _set.add('extant')
        _set.add('extant')
        self.assertEqual(list(_set), ['extant'])

    def test_insert(self):
        _set = self._makeOne()
        _set.insert('inserted')
        self.assertEqual(list(_set), ['inserted'])

    def test_remove_miss(self):
        _set = self._makeOne()
        self.assertRaises(KeyError, _set.remove, 'not_extant')

    def test_remove_extant(self):
        _set = self._makeOne()
        _set.add('one')
        _set.add('another')
        _set.remove('one')
        self.assertEqual(list(_set), ['another'])

    def test_update(self):
        _set = self._makeOne()
        _set.update(['one', 'after', 'another'])
        self.assertEqual(sorted(_set), ['after', 'another', 'one'])

    def test___getstate___empty_no_next(self):
        _set = self._makeOne()
        self.assertEqual(_set.__getstate__(), ((),))

    def test___getstate___empty_w_next(self):
        _set = self._makeOne()
        _set._next = next_s = self._makeOne()
        self.assertEqual(_set.__getstate__(), ((), next_s))

    def test___getstate___non_empty_no_next(self):
        _set = self._makeOne()
        EXPECTED = ()
        for c in 'abcdef':
            _set.add(c)
            EXPECTED += (c,)
        self.assertEqual(_set.__getstate__(), (EXPECTED,))

    def test___getstate___non_empty_w_next(self):
        _set = self._makeOne()
        _set._next = next_s = self._makeOne()
        EXPECTED = ()
        for c in 'abcdef':
            _set.add(c)
            EXPECTED += (c,)
        self.assertEqual(_set.__getstate__(), (EXPECTED, next_s))

    def test___setstate___w_non_tuple(self):
        _set = self._makeOne()
        self.assertRaises(TypeError, _set.__setstate__, (None,))

    def test___setstate___w_empty_no_next(self):
        _set = self._makeOne()
        _set._next = next_s = self._makeOne()
        for c in 'abcdef':
            _set.add(c)
        _set.__setstate__(((),))
        self.assertEqual(len(_set), 0)
        self.assertTrue(_set._next is None)

    def test___setstate___w_non_empty_w_next(self):
        _set = self._makeOne()
        next_s = self._makeOne()
        ITEMS = ()
        EXPECTED = []
        for c in 'abcdef':
            ITEMS += (c,)
            EXPECTED.append(c)
        _set.__setstate__((ITEMS, next_s))
        self.assertEqual(sorted(_set), EXPECTED)
        self.assertTrue(_set._next is next_s)

    def test___getitem___out_of_bounds(self):
        _set = self._makeOne()
        self.assertRaises(IndexError, _set.__getitem__, 1)

    def test___getitem___hit_bounds(self):
        _set = self._makeOne()
        _set.add('b')
        _set.add('a')
        _set.add('c')
        self.assertEqual(_set[0], 'a')
        self.assertEqual(_set[1], 'b')
        self.assertEqual(_set[2], 'c')

    def test__split_empty(self):
        _set = self._makeOne()
        next_b = _set._next = self._makeOne()
        new_b = _set._split()
        self.assertEqual(len(_set._keys), 0)
        self.assertEqual(len(new_b._keys), 0)
        self.assertTrue(_set._next is new_b)
        self.assertTrue(new_b._next is next_b)

    def test__split_filled_default_index(self):
        _set = self._makeOne()
        next_b = _set._next = self._makeOne()
        for c in 'abcdef':
            _set.add(c)
        new_b = _set._split()
        self.assertEqual(list(_set._keys), ['a', 'b', 'c'])
        self.assertEqual(list(new_b._keys), ['d', 'e', 'f'])
        self.assertTrue(_set._next is new_b)
        self.assertTrue(new_b._next is next_b)

    def test__p_resolveConflict_x_on_com_next(self):
        from ..Interfaces import BTreesConflictError
        _set = self._makeOne()
        N_NEW = object()
        s_old = ((), None)
        s_com = ((), N_NEW)
        s_new = ((), None)
        e = self.assertRaises(BTreesConflictError,
                              _set._p_resolveConflict, s_old, s_com, s_new)
        self.assertEqual(e.reason, 0)

    def test__p_resolveConflict_x_on_new_next(self):
        from ..Interfaces import BTreesConflictError
        _set = self._makeOne()
        N_NEW = object()
        s_old = ((), None)
        s_com = ((), None)
        s_new = ((), N_NEW)
        e = self.assertRaises(BTreesConflictError,
                              _set._p_resolveConflict, s_old, s_com, s_new)
        self.assertEqual(e.reason, 0)

    def test__p_resolveConflict_x_on_com_empty(self):
        from ..Interfaces import BTreesConflictError
        _set = self._makeOne()
        s_old = (('a', 'b'), None)
        s_com = ((), None)
        s_new = (('a',), None)
        e = self.assertRaises(BTreesConflictError,
                              _set._p_resolveConflict, s_old, s_com, s_new)
        self.assertEqual(e.reason, 12)

    def test__p_resolveConflict_x_on_new_empty(self):
        from ..Interfaces import BTreesConflictError
        _set = self._makeOne()
        s_old = (('a', 'b'), None)
        s_com = (('a',), None)
        s_new = ((), None)
        e = self.assertRaises(BTreesConflictError,
                              _set._p_resolveConflict, s_old, s_com, s_new)
        self.assertEqual(e.reason, 12)

    def test__p_resolveConflict_x_on_del_first_com(self):
        from ..Interfaces import BTreesConflictError
        _set = self._makeOne()
        s_old = (('a','b'), None)
        s_com = (('b',), None)
        s_new = (('a', 'b', 'c'), None)
        e = self.assertRaises(BTreesConflictError,
                              _set._p_resolveConflict, s_old, s_com, s_new)
        self.assertEqual(e.reason, 13)

    def test__p_resolveConflict_x_on_del_first_new(self):
        from ..Interfaces import BTreesConflictError
        _set = self._makeOne()
        s_old = (('a', 'b'), None)
        s_com = (('a', 'b', 'c'), None)
        s_new = (('b',), None)
        e = self.assertRaises(BTreesConflictError,
                              _set._p_resolveConflict, s_old, s_com, s_new)
        self.assertEqual(e.reason, 13)

    def test__p_resolveConflict_x_on_ins_same_after_del(self):
        from ..Interfaces import BTreesConflictError
        _set = self._makeOne()
        s_old = (('a', 'b'), None)
        s_com = (('a', 'c'), None)
        s_new = (('a', 'c', 'd'), None)
        e = self.assertRaises(BTreesConflictError,
                              _set._p_resolveConflict, s_old, s_com, s_new)
        self.assertEqual(e.reason, 4)

    def test__p_resolveConflict_x_on_del_same(self):
        from ..Interfaces import BTreesConflictError
        _set = self._makeOne()
        s_old = (('a', 'b', 'c'), None)
        s_com = (('a', 'c'), None)
        s_new = (('a', 'd', 'e'), None)
        e = self.assertRaises(BTreesConflictError,
                              _set._p_resolveConflict, s_old, s_com, s_new)
        self.assertEqual(e.reason, 5)

    def test__p_resolveConflict_x_on_append_same(self):
        from ..Interfaces import BTreesConflictError
        _set = self._makeOne()
        s_old = (('a',), None)
        s_com = (('a', 'b'), None)
        s_new = (('a', 'b', 'c'), None)
        e = self.assertRaises(BTreesConflictError,
                              _set._p_resolveConflict, s_old, s_com, s_new)
        self.assertEqual(e.reason, 6)

    def test__p_resolveConflict_x_on_new_deletes_all_com_adds(self):
        from ..Interfaces import BTreesConflictError
        _set = self._makeOne()
        s_old = (('a', 'b', 'c'), None)
        s_com = (('a', 'd', 'e', 'f'), None)
        s_new = (('a',), None)
        e = self.assertRaises(BTreesConflictError,
                              _set._p_resolveConflict, s_old, s_com, s_new)
        self.assertEqual(e.reason, 7)

    def test__p_resolveConflict_x_on_com_deletes_all_new_adds(self):
        from ..Interfaces import BTreesConflictError
        _set = self._makeOne()
        s_old = (('a', 'b', 'c'), None)
        s_com = (('a',), None)
        s_new = (('a', 'd', 'e', 'f'), None)
        e = self.assertRaises(BTreesConflictError,
                              _set._p_resolveConflict, s_old, s_com, s_new)
        self.assertEqual(e.reason, 8)

    def test__p_resolveConflict_x_on_com_deletes_all_new_deletes(self):
        from ..Interfaces import BTreesConflictError
        _set = self._makeOne()
        s_old = (('a', 'b', 'c'), None)
        s_com = (('a',), None)
        s_new = (('a', 'b'), None)
        e = self.assertRaises(BTreesConflictError,
                              _set._p_resolveConflict, s_old, s_com, s_new)
        self.assertEqual(e.reason, 9)

    def test__p_resolveConflict_ok_both_add_new_max(self):
        _set = self._makeOne()
        s_old = (('a',), None)
        s_com = (('a', 'b', 'c'), None)
        s_new = (('a', 'd'), None)
        result = _set._p_resolveConflict(s_old, s_com, s_new)
        # Note that _SetBase uses default __getstate__
        self.assertEqual(result, (('a', 'b', 'c', 'd'),))

    def test__p_resolveConflict_add_new_gt_old_com_lt_old(self):
        _set = self._makeOne()
        s_old = (('a', 'b', 'c'), None)
        s_com = (('a', 'b', 'bb', 'c'), None)
        s_new = (('a', 'b', 'c', 'd'), None)
        result = _set._p_resolveConflict(s_old, s_com, s_new)
        self.assertEqual(result, (('a', 'b', 'bb', 'c', 'd'),))


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test_Base),
        unittest.makeSuite(Test_BucketBase),
        unittest.makeSuite(Test_SetIteration),
        unittest.makeSuite(BucketTests),
        unittest.makeSuite(SetTests),
    ))
