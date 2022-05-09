# coding = utf-8

import os
import sys
import hashlib
import json
from enum import Enum
from peewee import *

# CLASS GUIDS
RULE_CLS_POPULAR_APPS = '{E746292E-C9C2-4533-9410-D50382838CB2}'
RULE_CLS_GAMES = '{D38180F7-6C87-4EE2-AEDA-809B8921861D}'
RULE_CLS_PROGRAMMING = '{376BE542-66CE-47EA-A1C9-609CE97030D6}'
RULE_CLS_PRODUCTIVITY = '{376BE542-66CE-47EA-A1C9-609CE97030D6}'
RULE_CLS_SYSTEM_APPS = '{23E51D07-900A-464D-A7AD-FEA9A4E63ADF}'
RULE_CLS_GENERIC_APPS = '{E746292E-C9C2-4533-9410-D50382838CB2}'
RULE_CLS_OTHERS = '{8051B0E9-BEE5-425E-B168-EE4DFC3D394F}'

CATEGORY_GUID_MAP = {
    "POPULARS": RULE_CLS_POPULAR_APPS,
    "GAMES": RULE_CLS_GAMES,
    "PROGRAMMING": RULE_CLS_PROGRAMMING,
    "PRODUCTIVITY": RULE_CLS_PRODUCTIVITY,
    "SYSTEM": RULE_CLS_SYSTEM_APPS,
    "GENERIC": RULE_CLS_GENERIC_APPS,
    "OTHERS": RULE_CLS_OTHERS
}

work_dir = os.path.dirname(os.path.dirname(__file__))
db: SqliteDatabase = SqliteDatabase(sys.argv[2] if len(sys.argv) > 2 else os.path.join(work_dir, 'the_store.db'))


class SHA1Filed(FixedCharField):
    """
    fixed 40 chars of SHA1 hash string
    """

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 40
        super(SHA1Filed, self).__init__(*args, **kwargs)


class EnumField(CharField):
    """
    This class enable an Enum like field for Peewee
    """

    def __init__(self, choices, *args, **kwargs) -> None:
        super(CharField, self).__init__(*args, **kwargs)
        self.choices = choices
        self.max_length = 255

    def db_value(self, value) -> str:
        return value.name

    def python_value(self, value: str):
        return self.choices[value]


class RuleIcon(Model):
    class IconType(Enum):
        ICO = 0
        SVG = 1

    hash = SHA1Filed(primary_key=True)
    type = EnumField(choices=IconType)
    data = BlobField()

    class Meta:
        database = db


class Rule(Model):
    guid = FixedCharField(max_length=38, primary_key=True)
    cat_guid = FixedCharField(max_length=38)
    name = CharField(max_length=64)
    description = CharField(max_length=256, null=True)
    icon = ForeignKeyField(model=RuleIcon, null=True)

    class Meta:
        database = db


class RuleI18n(Model):
    owner = ForeignKeyField(model=Rule)
    locale = CharField(max_length=12)
    name = CharField(max_length=64)
    description = CharField(max_length=256, null=True)

    class Meta:
        database = db


class RuleExpr(Model):
    owner = ForeignKeyField(model=Rule)
    expr = CharField(max_length=256)

    class Meta:
        database = db


class Processor(object):
    def __init__(self, db_name: str):
        self.icons_dir = os.path.join(work_dir, 'icons')
        self.rules_dir = os.path.join(work_dir, 'rules')

    def start(self):
        for root_dir, dir_list, file_list in os.walk(self.rules_dir):
            for file in file_list:
                filename = os.path.join(root_dir, file)
                try:
                    self._process_single_rule(filename)
                except Exception as e:
                    print(e)

    def _process_single_rule(self, filename: str):
        obj = json.load(open(filename))
        if type(obj) is list:
            for v in obj:
                self._process_single_rule_object(v)
        elif type(obj) is dict:
            self._process_single_rule_object(obj)
        else:
            print("illegal rule source {}".format(filename))

    def _process_single_rule_object(self, obj: dict):
        for filed in ['guid', 'name', 'category', 'rules']:
            if filed not in obj or not obj[filed]:
                return

        cat_guid = CATEGORY_GUID_MAP.get(obj['category'].upper(), None)
        if not cat_guid:
            return

        with db.atomic():
            ico_obj = None
            # create icon object if present
            if 'icon' in obj:
                ico_file = os.path.join(self.icons_dir, obj['icon'])
                if not os.path.isfile(ico_file):
                    print("{} not present".format(ico_file))
                    return
                with open(ico_file, mode='rb') as fd:
                    # get hash
                    ico_data = fd.read()
                    sha1 = hashlib.sha1()
                    sha1.update(ico_data)
                    ico_hash = sha1.hexdigest()
                    ico_obj = RuleIcon.get_or_create(hash=ico_hash,
                                                     type=RuleIcon.IconType.ICO,
                                                     data=ico_data)
            # create rule object
            rule_obj = Rule.create(guid=obj['guid'],
                                   cat_guid=cat_guid,
                                   name=obj['name'],
                                   description=(obj['description'] if 'description' in obj else ''),
                                   icon=ico_obj)

            # create expressions
            expr_list = []
            for r in obj['rules']:
                expr_list.append(RuleExpr(owner=rule_obj,
                                          expr=r))
            RuleExpr.bulk_create(expr_list)


if __name__ == '__main__':
    models = Model.__subclasses__()
    db.create_tables([m for m in models if m.__name__ not in ['VirtualModel']])
    Processor(sys.argv[2] if len(sys.argv) > 2 else '').start()
