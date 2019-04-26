# Generated by Django 2.1.7 on 2019-04-26 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('archival', '0047_add_default_rights_declaration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='archivalrecord',
            name='rights_declaration',
            field=models.TextField(default='\n<p>\nImages: © HM Queen Elizabeth II - <a\nhref="https://creativecommons.org/licenses/by-nc-sa/4.0/">CC BY-NC-SA 4.0</a>\n</p>\n<p>\nMetadata: <a\nhref="https://creativecommons.org/share-your-work/public-domain/cc0/">CC0</a>\n</p>\n<p xmlns:dct="http://purl.org/dc/terms/"\nxmlns:vcard="http://www.w3.org/2001/vcard-rdf/3.0#">\n<a rel="license"\nhref="http://creativecommons.org/publicdomain/zero/1.0/">\n<img src="http://i.creativecommons.org/p/zero/1.0/88x31.png"\nstyle="border-style: none;" alt="CC0" />\n</a>\n<br />\nTo the extent possible under law,\n<a rel="dct:publisher"\nhref="https://georgianpapers.com/">\n<span property="dct:title">the Georgian Papers Programme</span></a>\nhas waived all copyright and related or neighboring rights to\nthis work.\nThis work is published from:\n<span property="vcard:Country" datatype="dct:ISO3166"\ncontent="GB" about="https://georgianpapers.com/">\nUnited Kingdom</span>.\n</p>\n\nOther copyright considerations: Check Public Permission field for copyright\nstatements for those items that are not under Crown copyright, for example\nunpublished manuscripts by non-royals.\n'),
        ),
    ]
