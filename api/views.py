import io
import re
import tarfile
import time
from pathlib import Path

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view

from .models import EventRecord

FIELDS = [
    'serialno', 'version', 'account-id', 'instance-id', 'srcaddr', 'dstaddr',
    'srcport', 'dstport', 'protocol', 'packets', 'bytes', 'starttime', 'endtime',
    'action', 'log-status'
]

FIELD_MAP = {
    'account-id': 'account_id',
    'instance-id': 'instance_id',
    'log-status': 'log_status',
}

EXPECTED_KEYS = [
    'serialno', 'version', 'account-id', 'instance-id', 'srcaddr', 'dstaddr',
    'srcport', 'dstport', 'protocol', 'packets', 'bytes', 'starttime', 'endtime',
    'action', 'log-status'
]


def _normalize_field_name(raw):
    key = (raw or '').strip()
    return FIELD_MAP.get(key, key.replace('-', '_'))


def _parse_value(raw, field):
    if raw is None:
        return None
    value = str(raw).strip()
    if value == '':
        return None
    if field in {'serialno', 'version', 'srcport', 'dstport', 'protocol', 'packets', 'bytes', 'starttime', 'endtime'}:
        try:
            return int(value)
        except ValueError:
            return None
    return value


def _coerce_log_rows(content):
    if not content or not content.strip():
        return []

    rows = []
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        tokens = re.split(r'\s+', line)
        if len(tokens) < 15:
            continue
        rows.append(tokens[:15])
    return rows


def _to_event_dict(record):
    data = {}
    for field in FIELDS:
        db_field = _normalize_field_name(field)
        data[field] = getattr(record, db_field, None)
    data['file'] = record.source_file
    return data


@csrf_exempt
@require_http_methods(['POST'])
def upload_archive(request):
    uploaded = request.FILES.get('file')
    if not uploaded:
        return JsonResponse({'error': 'No file uploaded'}, status=400)

    if not uploaded.name.lower().endswith(('.tgz', '.gz')):
        return JsonResponse({'error': 'Only .tgz archives are supported'}, status=400)

    storage_dir = Path(settings.MEDIA_ROOT)
    storage_dir.mkdir(parents=True, exist_ok=True)
    archive_path = storage_dir / uploaded.name

    with open(archive_path, 'wb+') as f:
        for chunk in uploaded.chunks():
            f.write(chunk)

    EventRecord.objects.all().delete()
    indexed = 0
    batch = []
    try:
        with tarfile.open(archive_path, 'r:gz') as tar:
            for member in tar.getmembers():
                if not member.isfile():
                    continue
                extracted = tar.extractfile(member)
                if not extracted:
                    continue
                text = extracted.read().decode('utf-8', errors='replace')
                for tokens in _coerce_log_rows(text):
                    row = dict(zip(EXPECTED_KEYS, tokens))
                    if not row:
                        continue
                    event = {'source_file': member.name}
                    for key, value in row.items():
                        event[_normalize_field_name(key)] = _parse_value(value, key)
                    batch.append(EventRecord(**event))
                    indexed += 1
                    if len(batch) >= 1000:
                        EventRecord.objects.bulk_create(batch)
                        batch = []
        if batch:
            EventRecord.objects.bulk_create(batch)
    except tarfile.TarError:
        return JsonResponse({'error': 'Uploaded archive is not a valid .tgz file'}, status=400)

    return JsonResponse({'message': 'Archive uploaded and indexed', 'records': indexed, 'file': uploaded.name})


@csrf_exempt
@api_view(['POST'])
def search_events(request):
    if not isinstance(request.data, dict) or len(request.data) == 0:
        return JsonResponse({'error': 'Provide at least one search field'}, status=400)

    start_time = time.perf_counter()
    filters = {}
    for field in FIELDS:
        value = request.data.get(field)
        if value is None or value == '':
            continue
        db_field = _normalize_field_name(field)
        if isinstance(value, str):
            filters[f'{db_field}__iexact'] = value.strip()
        else:
            filters[f'{db_field}__exact'] = value

    if not filters:
        return JsonResponse({'error': 'Provide at least one search field'}, status=400)

    queryset = EventRecord.objects.filter(**filters)
    results = [_to_event_dict(row) for row in queryset]
    latency_seconds = time.perf_counter() - start_time
    return JsonResponse({'results': results, 'search_time': round(latency_seconds, 4), 'count': len(results)})
