from django.db import models
from django.utils.timezone import now


class Block(models.Model):

    id = models.PositiveIntegerField(
        primary_key=True,
        verbose_name="Blocknummer",
        unique=True,
        null=False,
        editable=False,
    )
    acceptedAt = models.DateTimeField(
        verbose_name="verifiziert am", auto_now_add=True, null=True, editable=False
    )
    timestamp = models.DateTimeField(
        verbose_name="erstellt am", null=True, editable=False
    )
    transactionsIncluded = models.TextField(
        verbose_name="beinhaltete Transaktionen", null=True, editable=False
    )
    transactionsCount = models.PositiveIntegerField(
        verbose_name="Anzahl der Transaktionen", null=True, editable=False
    )
    transactionsValueTotal = models.DecimalField(
        verbose_name="Gesamtvolumen",
        max_digits=15,
        decimal_places=7,
        null=True,
        editable=False,
    )
    miner = models.GenericIPAddressField(
        verbose_name="Miner (IP)", null=True, editable=False
    )
    size = models.PositiveIntegerField(
        verbose_name="Größe (Byte)", null=True, editable=False
    )
    nonce = models.PositiveBigIntegerField(
        verbose_name="Nonce", null=True, editable=False
    )
    currHash = models.CharField(
        verbose_name="Hash des Blocks", max_length=128, null=True, editable=False
    )
    prevHash = models.CharField(
        verbose_name="Hash des Vorgängerblocks",
        max_length=128,
        null=True,
        editable=False,
    )

    def __str__(self):
        return self.id


class Transaction(models.Model):

    id = models.CharField(
        primary_key=True,
        verbose_name="Transaktions-Id",
        max_length=128,
        unique=True,
        null=False,
        editable=False,
    )
    blockContained = models.ForeignKey(
        Block,
        verbose_name="enthalten in Block",
        on_delete=models.DO_NOTHING,
        null=True,
        default=None,
    )
    createdAt = models.DateTimeField(
        verbose_name="erstellt am", auto_now_add=True, null=True, editable=False
    )
    sender = models.TextField(verbose_name="Sender", null=True, editable=False)
    senderValue = models.TextField(
        verbose_name="Sender-Betrag", null=True, editable=False
    )
    recipient = models.TextField(verbose_name="Empfänger", null=True, editable=False)
    recipientValue = models.TextField(
        verbose_name="Empfänger-Betrag", null=True, editable=False
    )
    fee = models.DecimalField(
        verbose_name="Gebühren",
        max_digits=15,
        decimal_places=7,
        null=True,
        editable=False,
    )
    totalValue = models.DecimalField(
        verbose_name="Gebühren",
        max_digits=15,
        decimal_places=7,
        null=True,
        editable=False,
    )

    def __str__(self):
        return self.id

class CalculationRange(models.Model):
    TODO = "Todo"
    FINISHED = "Fini"

    STATE_CHOICES = [
        (TODO, "To be done"),
        (FINISHED, "Finished"),
    ]

    state = models.CharField(max_length=4, choices=STATE_CHOICES, default=TODO)
    timestamp = models.DateTimeField(default=now)
    lowerBound = models.IntegerField()
