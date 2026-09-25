import io
import tarfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from .models import EventRecord


class EventSearchAPITests(TestCase):
    def setUp(self):
        EventRecord.objects.create(
            serialno=1,
            version=2,
            account_id=348935949,
            instance_id='eni-293216456',
            srcaddr='159.62.125.136',
            dstaddr='30.55.177.194',
            srcport=152,
            dstport=23475,
            protocol=8,
            packets=10,
            bytes=3929334,
            starttime=1725850449,
            endtime=1725855086,
            action='REJECT',
            log_status='OK',
            source_file='events_2025.log',
        )
        EventRecord.objects.create(
            serialno=2,
            version=2,
            account_id=348935950,
            instance_id='eni-293216457',
            srcaddr='159.62.125.137',
            dstaddr='30.55.177.195',
            srcport=160,
            dstport=23476,
            protocol=6,
            packets=11,
            bytes=4000000,
            starttime=1725851000,
            endtime=1725855000,
            action='ACCEPT',
            log_status='OK',
            source_file='events_2025.log',
        )

    def test_search_rejects_empty_query(self):
        response = self.client.post('/api/search/', {}, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Provide at least one search field', response.json()['error'])

    def test_search_combines_multiple_filters(self):
        response = self.client.post(
            '/api/search/',
            {'serialno': '1', 'log-status': 'OK'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['count'], 1)
        self.assertEqual(payload['results'][0]['serialno'], 1)
        self.assertIn('search_time', payload)

    def test_upload_archive_indexes_records(self):
        payload = b'1 2 348935949 eni-293216456 159.62.125.136 30.55.177.194 152 23475 8 10 3929334 1725850449 1725855086 REJECT OK\n'
        tar_stream = io.BytesIO()
        with tarfile.open(fileobj=tar_stream, mode='w:gz') as tar:
            info = tarfile.TarInfo('events_2025.log')
            info.size = len(payload)
            tar.addfile(info, io.BytesIO(payload))

        uploaded = SimpleUploadedFile(
            'sample_events.tgz',
            tar_stream.getvalue(),
            content_type='application/gzip',
        )

        response = self.client.post('/api/upload/', {'file': uploaded})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['records'], 1)

    def test_upload_archive_indexes_named_log_files_without_log_extension(self):
        payload = (
            b'1 2 348935949 eni-293216456 159.62.125.136 30.55.177.194 152 23475 8 10 3929334 '
            b'1725850449 1725855086 REJECT OK\n'
        )
        tar_stream = io.BytesIO()
        with tarfile.open(fileobj=tar_stream, mode='w:gz') as tar:
            info = tarfile.TarInfo('events/xon')
            info.size = len(payload)
            tar.addfile(info, io.BytesIO(payload))

        uploaded = SimpleUploadedFile(
            'sample_events.tgz',
            tar_stream.getvalue(),
            content_type='application/gzip',
        )

        response = self.client.post('/api/upload/', {'file': uploaded})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['records'], 1)
