import inspect
import json
import os
import sys
from django.core import serializers
from django.db import transaction
from apps.utils import Result

MODEL_DATA_PATH = 'modelData'


def export_to_JSON(queryset):
    query_class = queryset.model
    query_class_name = query_class.__name__
    fields = [f.name for f in query_class._meta.local_fields]
    fields.remove("id")
    qs_json = list(queryset.values(*fields))

    if not os.path.exists(MODEL_DATA_PATH):
        os.makedirs(MODEL_DATA_PATH)

    with open(f'{MODEL_DATA_PATH}/{query_class_name}.json', 'w') as f:
        json.dump(list(qs_json), f, indent=2)


def bulk_upsert_from_json(model_class, json_data, unique_field):
    existing_objects = {getattr(obj, unique_field): obj for obj in model_class.objects.filter(
        **{f'{unique_field}__in': [item[unique_field] for item in json_data]})}

    objects_to_create = []
    objects_to_update = []
    fields_to_update = []

    for item in json_data:
        unique_value = item[unique_field]

        if unique_value in existing_objects:
            # Update existing object if any field has changed
            existing_obj = existing_objects[unique_value]
            is_change = False
            for key, value in item.items():
                if key != unique_field and getattr(existing_obj, key) != value:
                    fields_to_update.append(key)  # Add field name to bulk_update fields changed list
                    setattr(existing_obj, key, value)
                    is_change = True
            if is_change:
                objects_to_update.append(existing_obj)
        else:
            # Create a new object if it doesn't exist
            objects_to_create.append(model_class(**item))

    with transaction.atomic():
        # Check if there are objects to create before attempting bulk create
        if objects_to_create:
            model_class.objects.bulk_create(objects_to_create)

        # Check if there are objects to update before attempting bulk update
        if objects_to_update:
            model_class.objects.bulk_update(objects_to_update, fields=fields_to_update)
    return True, {'update': len(objects_to_update), 'insert': len(objects_to_create)}


def load_from_JSON(model):
    result = Result()
    model_name = model.__name__

    path = f'{MODEL_DATA_PATH}/{model_name}.json'
    if os.path.isfile(path):
        try:
            with open(path, 'r') as f:
                data = json.load(f)

            bulk_status, result = bulk_upsert_from_json(model, data, unique_field="global_key")
            if bulk_status:
                result.set_success()
                content = f"Updated {result['update']} records and created {result['insert']} records"
                result.set_message(content)
            return result
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

            result.set_message(e)
            return result

    else:
        content = f'Path {path} does not exists'
        result.set_message(content)
        return result
