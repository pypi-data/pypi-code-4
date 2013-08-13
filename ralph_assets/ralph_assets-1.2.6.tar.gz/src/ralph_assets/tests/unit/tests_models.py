# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
from django.test import TestCase

from ralph_assets.api_pricing import get_assets, get_asset_parts
from ralph_assets.models_assets import PartInfo, AssetModel
from ralph_assets.tests.util import create_asset


class TestModelAsset(TestCase):
    def setUp(self):
        self.asset = create_asset(
            sn='1111-1111-1111-1111',
            invoice_date=datetime.date(2012, 11, 28),
            support_period=1,
            deprecation_rate=1.00,
        )
        self.asset2 = create_asset(
            sn='1111-1111-1111-1112',
            invoice_date=datetime.date(2012, 11, 28),
            support_period=120,
            deprecation_rate=0.50,
        )

    def test_is_deperecation(self):
        self.assertEqual(self.asset.get_deprecation_months(), 12)
        self.assertEqual(self.asset2.get_deprecation_months(), 24)
        self.assertEqual(self.asset.is_deprecated(), True)


class TestApiAssets(TestCase):
    def setUp(self):
        self.asset = create_asset(
            sn='1111-1111-1111-1111',
            invoice_date=datetime.date(2012, 11, 28),
            support_period=1,
            slots=12.0,
            price=100,
        )
        part_info = PartInfo(device=self.asset)
        part_info.save()
        self.asset2 = create_asset(
            sn='1111-1111-1111-11132',
            invoice_date=datetime.date(2012, 11, 28),
            support_period=1,
            slots=12.0,
            price=100,
            part_info=part_info,
        )

    def tests_api_asset(self):
        for item in get_assets():
            self.assertEqual(item['asset_id'], self.asset.id)
            self.assertEqual(
                item['ralph_id'], self.asset.device_info.ralph_device_id,
            )
            self.assertEqual(item['slots'], self.asset.slots)
            self.assertEqual(item['price'], self.asset.price)
            self.assertEqual(item['is_deprecated'], self.asset.is_deprecated())
            self.assertEqual(item['sn'], self.asset.sn)
            self.assertEqual(item['barcode'], self.asset.barcode)

    def tests_api_asset_part(self):
        for item in get_asset_parts():
            self.assertEqual(item['price'], 100)
            self.assertEqual(item['is_deprecated'], False)
            model = AssetModel.objects.get(name="Model1")
            self.assertEqual(item['model'], model.name)
            self.assertEqual(item['asset_id'], self.asset2.id)
            self.assertEqual(item['sn'], self.asset.sn)
            self.assertEqual(item['barcode'], self.asset.barcode)
