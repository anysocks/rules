# coding = utf-8

import os
import sys
import hashlib
import json
from enum import Enum
from peewee import *

# CLASS GUIDS
RULE_CLS_POPULAR_APPS = '{e746292e-c9c2-4533-9410-d50382838cb2}'
RULE_CLS_GAMES = '{d38180f7-6c87-4ee2-aeda-809b8921861d}'
RULE_CLS_PROGRAMMING = '{376be542-66ce-47ea-a1c9-609ce97030d6}'
RULE_CLS_PRODUCTIVITY = '{a2d14147-04be-4159-b977-0b0ef0e5f17d}'
RULE_CLS_SYSTEM_APPS = '{23e51d07-900a-464d-a7ad-fea9a4e63adf}'
RULE_CLS_GENERIC_APPS = '{69a4bc26-7668-471d-b01a-1c2db53d57e2}'
RULE_CLS_OTHERS = '{8051b0e9-bee5-425e-b168-ee4dfc3d394f}'

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
db_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(work_dir, 'the_store.db')
if os.path.isfile(db_path):
    os.remove(db_path)
db: SqliteDatabase = SqliteDatabase(db_path)


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
    icon_hash = SHA1Filed(null=True)

    class Meta:
        database = db


class RuleI18n(Model):
    rule_id = FixedCharField(max_length=38, null=False)
    locale = CharField(max_length=12)
    name = CharField(max_length=64)
    description = CharField(max_length=256, null=True)

    class Meta:
        database = db


class RuleDependency(Model):
    rule_id = FixedCharField(max_length=38, null=False)
    depends_on_id = FixedCharField(max_length=38, null=False)

    class Meta:
        database = db


class RuleExpr(Model):
    rule_id = FixedCharField(max_length=38, null=False)
    expr = CharField(max_length=256)

    class Meta:
        database = db


class Processor(object):
    def __init__(self, db_name: str):
        self.icons_dir = os.path.join(work_dir, 'icons')
        self.rules_dir = os.path.join(work_dir, 'rules')
        self.dependency_map = dict()

    def start(self):
        for root_dir, dir_list, file_list in os.walk(self.rules_dir):
            for file in file_list:
                filename = os.path.join(root_dir, file)
                try:
                    self._process_single_rule(filename)
                except Exception as e:
                    print(e)
        self._build_dependency_map()

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
                    ico_obj, ok = RuleIcon.get_or_create(hash=ico_hash,
                                                         type=RuleIcon.IconType.ICO,
                                                         data=ico_data)
                    if not ok:
                        return
            # create rule object
            rule_obj = Rule.create(guid=obj['guid'].lower(),
                                   cat_guid=cat_guid,
                                   name=obj['name'],
                                   description=(obj['description'] if 'description' in obj else ''),
                                   icon_hash=ico_obj.hash)

            # create expressions
            expr_list = []
            for r in obj['rules']:
                expr_list.append(RuleExpr(rule_id=rule_obj.guid,
                                          expr=r))
            RuleExpr.bulk_create(expr_list)

        if 'dependencies' in obj and obj['dependencies']:
            self.dependency_map[obj['guid'].lower()] = obj['dependencies']

    def _build_dependency_map(self):
        for rule_id, dep_list in self.dependency_map.items():
            rule = Rule.get_or_none(guid=rule_id)
            if not rule:
                continue

            dep_entries = []
            no_err = True
            for dep_id in dep_list:
                dep_rule = Rule.get_or_none(guid=dep_id)
                if not dep_rule:
                    no_err = False
                    break
                dep_entries.append(RuleDependency(rule_id=rule.guid,
                                                  depends_on_id=dep_rule.guid))
            if no_err:
                with db.atomic():
                    RuleDependency.bulk_create(dep_entries)


if __name__ == '__main__':
    models = Model.__subclasses__()
    db.create_tables([m for m in models if m.__name__ not in ['VirtualModel']])
    Processor(sys.argv[2] if len(sys.argv) > 2 else '').start()
