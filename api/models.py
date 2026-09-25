from django.db import models


class EventRecord(models.Model):
    serialno = models.IntegerField(null=True, blank=True)
    version = models.IntegerField(null=True, blank=True)
    account_id = models.BigIntegerField(null=True, blank=True)
    instance_id = models.CharField(max_length=255, null=True, blank=True)
    srcaddr = models.CharField(max_length=255, null=True, blank=True)
    dstaddr = models.CharField(max_length=255, null=True, blank=True)
    srcport = models.IntegerField(null=True, blank=True)
    dstport = models.IntegerField(null=True, blank=True)
    protocol = models.IntegerField(null=True, blank=True)
    packets = models.IntegerField(null=True, blank=True)
    bytes = models.IntegerField(null=True, blank=True)
    starttime = models.BigIntegerField(null=True, blank=True)
    endtime = models.BigIntegerField(null=True, blank=True)
    action = models.CharField(max_length=255, null=True, blank=True)
    log_status = models.CharField(max_length=255, null=True, blank=True)
    source_file = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        app_label = 'api'
